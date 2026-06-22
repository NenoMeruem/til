Node: [[article]]
Tags: #system-design

Trong bài viết này, chúng ta sẽ cùng tìm hiểu cách xây dựng hệ thống định vị và theo dõi xe (tracking system), cụ thể là dành cho xe đưa đón học sinh. Thiết kế của hệ thống này cho phép giám sát lộ trình của xe buýt trên quy mô lớn, áp dụng được cho nhiều cơ sở giáo dục khác nhau. Bên cạnh đó, chúng ta sẽ tích hợp thêm tính năng thông báo (notification feature) cho hệ thống.

Tính năng này sẽ gửi cảnh báo đến phụ huynh khi xe buýt chuẩn bị tới gần điểm đón/trả hoặc khi học sinh đã xuống xe thành công. Xuyên suốt bài viết, tôi sẽ đi sâu vào các khía cạnh kỹ thuật đa dạng trong quá trình phát triển (development) và triển khai (implementation) hệ thống này.

### Tìm hiểu các Yêu cầu Chức năng (Functional Requirements)

Chúng ta cần thiết kế một hệ thống giám sát vị trí xe buýt đưa đón học sinh. Hệ thống này bao gồm nhiều trường học, và mỗi trường quản lý danh sách nhiều học sinh. Dưới đây là các yêu cầu nghiệp vụ cụ thể cho từng trường:

*  **Tần suất cập nhật vị trí (Frequent Location Updates):** Hệ thống phải cập nhật và hiển thị vị trí thời gian thực (real-time) của xe buýt với tần suất cao để đảm bảo độ chính xác của dữ liệu tracking.
*  **Hiển thị trực quan cho Stakeholders:** Cần xây dựng giao diện hiển thị vị trí xe buýt trên bản đồ theo thời gian thực, cho phép phụ huynh và ban quản lý nhà trường truy cập.
*  **Thông báo dựa trên khoảng cách (Proximity Notifications):** Hệ thống tự động gửi thông báo khi xe buýt tiến gần đến nhà học sinh. Mặc dù trọng tâm hiện tại là **Push Notifications**, kiến trúc (architecture) cần đảm bảo tính mở rộng (extensible) để tích hợp thêm các kênh khác như SMS trong tương lai.
*  **Phân lập dữ liệu giữa các trường (Data Isolation):** Mỗi trường chỉ được phép truy cập dữ liệu của đội xe (fleet) thuộc quyền quản lý, đảm bảo tính riêng tư (data privacy) và toàn vẹn dữ liệu (system integrity).

### Các Yêu cầu Phi chức năng (Non-functional Requirements)

Dựa trên mục tiêu kinh doanh, chúng ta xác định các yêu cầu phi chức năng quan trọng sau:

*   **Khả năng mở rộng (Scalability):** Hệ thống phải đảm bảo xử lý hiệu quả khi số lượng xe buýt truyền dữ liệu vị trí tăng lên và số lượng phụ huynh truy cập đồng thời (concurrent users) lớn.
*   **Tính sẵn sàng cao (High Availability):** Đảm bảo dịch vụ vận hành liên tục, không bị gián đoạn trong việc theo dõi thời gian thực.
*   **Tính tin cậy (Reliability):** Đảm bảo không bị mất thông báo (Zero message loss). Mọi cảnh báo, đặc biệt là thông báo xe gần đến nhà, phải đến được tay người nhận.
*   **Bảo mật (Security):** Áp dụng các biện pháp bảo mật chặt chẽ để chống lại việc truy cập trái phép và các nguy cơ rò rỉ dữ liệu.
*   **Quyền riêng tư (Privacy):** Thực thi các cơ chế kiểm soát quyền truy cập nghiêm ngặt để đảm bảo người dùng chỉ xem được vị trí xe buýt liên quan trực tiếp đến con em họ.


### Ước tính quy mô (Back-of-the-Envelope Estimation)

Để hiểu rõ hơn về tải của hệ thống, hãy cùng thực hiện các tính toán sơ bộ:

#### 1. Lưu lượng cập nhật vị trí (Requests Per Second - RPS)
*   **Tổng số xe:** 2.000 trường × 10 xe/trường = 20.000 xe.
*   **Tần suất cập nhật:** 2 giây/lần/xe.
*   **Tính toán RPS:**
    *   Tổng số request trong 2 giây là 20.000.
    *   **RPS = 20.000 / 2 = 10.000 RPS.**
    *   Đây là mức lưu lượng write rất cao, đòi hỏi tài nguyên backend (cơ sở hạ tầng) mạnh mẽ để xử lý tải.

#### 2. Lưu lượng truy cập từ phía Phụ huynh (Parent App Usage)
*   **Tổng số học sinh:** 2.000 trường × 300 học sinh/trường = 600.000 học sinh.
*   **Tần suất kiểm tra (giả định):** 180.000 phụ huynh truy cập mỗi 2 phút.
*   **Lượt kiểm tra mỗi phút:** 180.000 / 2 = 90.000 requests/phút.
*   **Lượt kiểm tra mỗi giây (RPS):** 90.000 / 60 = **1.500 RPS.**
*   Mặc dù lưu lượng đọc (read) dữ liệu khá lớn, nhưng hoàn toàn nằm trong khả năng xử lý của các database hiện đại và không phải là trở ngại quá lớn đối với hệ thống

### Đề xuất Thiết kế Tổng thể (High-Level Design)

Kiến trúc tổng thể (High-level design) của hệ thống theo dõi xe bus đưa đón học sinh bao gồm các thành phần cốt lõi sau:

*   **Thiết kế API:** Giao diện lập trình ứng dụng.
*   **Thuật toán định vị nhà học sinh:** Logic xử lý vị trí.
*   **Cập nhật vị trí xe bus:** Cơ chế đồng bộ dữ liệu thời gian thực.
*   **Mô hình dữ liệu (Data Model):** Cấu trúc lưu trữ thông tin.

#### 1. Thiết kế API
Chúng tôi sẽ sử dụng kiến trúc **RESTful API** để xây dựng một backend tinh gọn và hiệu quả, đảm bảo khả năng xử lý việc cập nhật và truy vấn vị trí xe bus.

**Endpoint:** `GET /v1/buses/locations`

*   **Cơ chế xác thực (Authentication):** Sử dụng header `X-Authorization` kèm theo **JWT (JSON Web Token)** để xác thực phiên làm việc của người dùng.
*   **Chức năng:** Endpoint này thực hiện truy vấn để xác định các xe bus được phân quyền cho con của người dùng, sau đó trả về **tọa độ (coordinates)** vị trí hiện tại của các xe đó.

**Response Body**

```json
{  
  "buses": [  
    {  
      "bus_id": "e3d54bd9-bbbc-4d8e-a653-a937c7c4a215",  
      "driver": {  
        "id": "a23e80d5-679d-4041-96bd-20d3954099ff",  
        "name": "Rosella Huel"  
      },  
      "children": [  
        {  
          "id": "0d95d921-97ba-48a9-8f5d-73b54c4318f5",  
          "name": "Herminia Rippin"  
        }  
      ],  
      "location": {  
        "latitude": 40.712776,  
        "longitude": -74.005974  
      }  
    }  
  ]  
}
```


### Endpoint: `WebSocket /v1/buses/{bus_id}/location`

**Chức năng (Functionality):**  
Mỗi xe buýt sẽ đẩy (push) dữ liệu vị trí hiện tại của mình thông qua kết nối **WebSocket**. Cơ chế này cho phép duy trì một **luồng dữ liệu thời gian thực (continuous data flow)** liên tục giữa client và server, giúp tối ưu hóa hiệu năng bằng cách loại bỏ chi phí **overhead** khi phải liên tục mở/đóng các kết nối **HTTP**mới cho mỗi lần cập nhật.

**Các tham số yêu cầu (Request Parameters):**

- **`bus_id` (Path Parameter):** Định danh duy nhất (Unique ID) của xe buýt. Tham số này được truyền trực tiếp trên đường dẫn (path) để xác định ngữ cảnh của kết nối.

```json
{  
	"latitude": ...,  
	"longitude": ...,  
	"timestamp": ...  
}
```

### Các thuật toán xác định vị trí nhà học sinh

Mục tiêu của chúng tôi là xây dựng một cơ sở dữ liệu bao gồm danh sách toàn diện các địa điểm nhà học sinh. Các vị trí này cần được cấu trúc tối ưu để hệ thống có thể kích hoạt thông báo (notification) gửi tới phụ huynh trước khi xe buýt đến điểm đón khoảng 2 phút.

Để giải quyết bài toán này, chúng ta sẽ sử dụng các phương pháp **đánh chỉ mục không gian địa lý (geospatial indexing)**. Dưới đây là hai hướng tiếp cận chính được minh họa trong hình bên dưới:


![[Pasted image 20260622162053.png]]


### Phương pháp phân mảnh lưới đều (Evenly Divided Grid)

Một cách tiếp cận đơn giản và hiệu quả là chia không gian bản đồ thành các ô lưới (grid) nhỏ, có kích thước bằng nhau. Trong hệ thống này, mỗi ô lưới có thể chứa nhiều căn nhà, và mọi căn nhà trên bản đồ sẽ được gán (assign) vào một ô lưới cụ thể.

![[Pasted image 20260622162113.png]]


Tuy nhiên, phương pháp này có thể không phù hợp với các **business requirements** (yêu cầu nghiệp vụ) hiện tại do một hạn chế lớn: sự phân bổ dữ liệu về các căn hộ (house distribution) có sự chênh lệch rất lớn. Chúng ta cần khả năng kiểm soát **granularity** (độ phân mảnh) của các lưới (grids) một cách chính xác hơn để đảm bảo các **notification latency** (độ trễ thông báo) đạt đúng mục tiêu đề ra.

### Geohash

Geohash là một giải pháp tối ưu hơn so với việc chia lưới đều (evenly divided grid). Cơ chế hoạt động của nó là **encode** (mã hóa) dữ liệu tọa độ hai chiều (kinh độ và vĩ độ) thành một chuỗi ký tự (string) một chiều gồm chữ và số. Thuật toán Geohash vận hành bằng cách **recursively** (đệ quy) chia nhỏ bản đồ thành các lưới có kích thước ngày càng tinh gọn theo từng bit được thêm vào. Sau đây là cái nhìn tổng quan về cách thức hoạt động của Geohash:

Đầu tiên, thuật toán sẽ chia bề mặt Trái đất thành bốn **quadrants** (phần tư) dựa trên kinh tuyến gốc và đường xích đạo.

![[Pasted image 20260622162158.png]]


**Quy tắc phân vùng tọa độ:**

- Dải vĩ độ (Latitude) `[-90, 0]` được biểu diễn bằng bit **0**.
- Dải vĩ độ `[0, 90]` được biểu diễn bằng bit **1**.
- Dải kinh độ (Longitude) `[-180, 0]` được biểu diễn bằng bit **0**.
- Dải kinh độ `[0, 180]` được biểu diễn bằng bit **1**.

**Thuật toán chia nhỏ lưới (Grid partitioning):**  
Tiếp theo, ta chia mỗi lưới (grid) hiện tại thành bốn lưới nhỏ hơn (sub-grids). Mỗi lưới con này sẽ được định danh bằng cách đan xen (interleaving) giữa bit kinh độ và bit vĩ độ.


Tiếp tục thực hiện việc phân chia (subdivision) này cho đến khi kích thước lưới (grid size) đạt đến độ chính xác mong muốn. Geohash thường sử dụng biểu diễn hệ cơ số 32 (base32). Hãy cùng xem xét hai ví dụ sau đây.

Geohash của trụ sở Google (độ dài = 6)

```
1001 10110 01001 10000 11011 11010 (base32 in binary) → 9q9hvu (base32)
```

**Mã Geohash của trụ sở Facebook (với độ dài chuỗi là 6 ký tự)**

```
1001 10110 01001 10001 10000 10111 (base32 in binary) → 9q9jhr (base32)
```

Geohash bao gồm 12 cấp độ phân giải (precision levels) như được trình bày trong bảng. Độ phân giải này quyết định kích thước của các lưới (grid size) trong hệ thống tọa độ. Trong phạm vi bài toán này, chúng ta chỉ quan tâm đến các Geohash có độ dài từ 6 đến 7 ký tự. Lý do là vì nếu độ dài lớn hơn 8, kích thước lưới sẽ trở nên quá nhỏ (gây thừa thãi tài nguyên), trong khi nếu độ dài nhỏ hơn 7, kích thước lưới lại quá lớn, khiến cơ chế gửi thông báo (notification approach) của chúng ta mất đi tính tối ưu và hiệu năng.

| Geohash Length | Grid Width x Height     |
| -------------- | ----------------------- |
| 1              | 5,009.4 km x 4,992.6 km |
| 2              | 1,252.3 km x 624.1 km   |
| 3              | 156.5 km x 156 km       |
| 4              | 39.1 km x 19.5 km       |
| 5              | 4.9 km x 4.9 km         |
| 6              | 1.2 km x 609.4 m        |
| 7              | 152.9 m x 152.4 m       |
| 8              | 38.2 m x 19 m           |
| 9              | 4.8 m x 4.8 m           |
| 10             | 1.2 m x 59.5 cm         |
| 11             | 14.9 cm x 14.9 cm       |
| 12             | 3.7 cm x 1.9 cm         |

Làm thế nào để lựa chọn độ chính xác (precision) phù hợp? Mục tiêu của chúng ta là xác định độ dài Geohash tối thiểu sao cho nó bao phủ toàn bộ phạm vi hình tròn được tạo bởi bán kính (radius) do người dùng thiết lập. Mối tương quan giữa bán kính và độ dài Geohash được thể hiện trong bảng dưới đây.

| Radius (Kilometers)   | Geohash Length |
| --------------------- | -------------- |
| 2 km (1.24 mile)      | 5              |
| 1 km (0.62 mile) \|   | 5              |
| 0.5 km (0.31 mile)    | 6              |
| 0.086 km (0.05 mile)  | 7              |
| 0.015 km (0.009 mile) |                |


Để hiểu rõ hơn về cơ chế hoạt động của GeoHash, bạn có thể tham khảo trang web này. (https://www.movable-type.co.uk/scripts/geohash.html)

```javascript
const geohash = require('ngeohash');  
  
// Example coordinates for a location  
const latitude = 40.6892; // Latitude for Statue of Liberty  
const longitude = -74.0445; // Longitude for Statue of Liberty  
  
// Generate the GeoHash  
const geohashCode = geohash.encode(latitude, longitude, 7);  
console.log("GeoHash code:", geohashCode);
```


Cách tiếp cận này rất hiệu quả với **stack** hiện tại của chúng ta, dù vẫn còn một vài vấn đề nhỏ liên quan đến **boundary definitions**. Tuy nhiên, điều này sẽ không gây ảnh hưởng đến **framework** hiện có.

### Tìm hiểu về Quadtree

**Quadtree** là một cấu trúc dữ liệu (data structure) thường được dùng để phân vùng (partition) không gian hai chiều (2D). Cơ chế hoạt động của nó là đệ quy (recursively) chia không gian thành 4 góc phần tư (quadrants hay grids) cho đến khi các grid này thỏa mãn một tiêu chí nhất định (criteria). 

Ví dụ: Bạn có thể quy định việc chia nhỏ sẽ tiếp tục diễn ra cho đến khi số lượng thực thể trong mỗi grid không vượt quá 100. Con số này hoàn toàn linh hoạt (arbitrary) và có thể tùy chỉnh dựa trên nhu cầu nghiệp vụ (như số lượng căn nhà trong mỗi grid).

Với Quadtree, chúng ta xây dựng một cấu trúc cây (tree structure) nằm trên bộ nhớ chính (in-memory) để xử lý các truy vấn (queries). Cần lưu ý rằng: Quadtree là một cấu trúc dữ liệu in-memory chứ không phải là một giải pháp cơ sở dữ liệu (database solution). Nó chạy trên mỗi server và được khởi tạo (build) tại thời điểm server bắt đầu khởi chạy (start-up time).

Hình ảnh dưới đây mô phỏng quá trình phân vùng thế giới thành một cấu trúc Quadtree. Giả sử thế giới này chứa 200 triệu căn nhà (đây chỉ là con số giả định để minh họa cách sử dụng).

![[Pasted image 20260622162930.png]]

Node gốc (root node) đại diện cho toàn bộ bản đồ thế giới. Node này được chia đệ quy (recursively) thành 4 góc phần tư (quadrants) cho đến khi không còn node nào chứa quá 100 doanh nghiệp.

![[Pasted image 20260622162948.png]]


### Cách truy vấn các doanh nghiệp lân cận bằng Quadtree

**1. Xây dựng Quadtree trên bộ nhớ (In-memory)**  
Tiến hành khởi tạo và xây dựng cấu trúc dữ liệu Quadtree trên RAM (in-memory).

**2. Chiến lược tìm kiếm**  
Sau khi Quadtree đã được xây dựng, quá trình tìm kiếm sẽ bắt đầu từ **nút gốc (root node)** và thực hiện **duyệt cây (traversing)** cho đến khi tìm thấy **nút lá (leaf node)** chứa tọa độ điểm gốc cần tìm. 

- Nếu nút lá đó chứa đủ 100 doanh nghiệp, ta trả về kết quả từ nút đó.
- Nếu không đủ, ta thực hiện truy vấn thêm từ các **nút lân cận (neighbor nodes)** cho đến khi thu thập đủ số lượng doanh nghiệp yêu cầu.

**3. Ví dụ thực tế về Quadtree**  
Yext cung cấp một minh họa về cách xây dựng Quadtree tại khu vực Denver. Mục tiêu của chúng ta là tối ưu hóa không gian: tạo ra các **lưới (grids)** nhỏ hơn, chi tiết hơn cho các khu vực có **mật độ cao (dense areas)** và các lưới lớn hơn cho các khu vực có **mật độ thấp (sparse areas)**.

![[Pasted image 20260622163013.png]]


### Phân tích hạn chế của Quadtree

Nếu bỏ qua các yếu tố về **operational considerations** (các cân nhắc vận hành), thì việc sử dụng Quadtree sẽ phát sinh hai vấn đề lớn:

1. **Chi phí cập nhật (Update overhead):** Khi số lượng căn nhà (nodes) mới được thêm vào bản đồ, việc cập nhật lại cấu trúc cây sẽ rất tốn kém về thời gian.
2. **Thiếu sự linh hoạt trong phân mảnh (Grid granularity):** Chúng ta không kiểm soát được kích thước của các **grids** (lưới) được chia nhỏ, vì thuật toán này dựa vào mật độ hoặc số lượng nhà thay vì dựa vào diện tích thực tế. Điều này gây khó khăn khi cần tối ưu hóa truy vấn trên bản đồ.

### Google S2 Geometry

Thư viện **Google S2 Geometry** là một giải pháp thay thế mạnh mẽ trong lĩnh vực này. Tương tự như Quadtree, nó là một giải pháp hoạt động **in-memory** (lưu trữ trên bộ nhớ chính).

Cơ chế của S2 là ánh xạ (map) các tọa độ trên mặt cầu (sphere) về một **1D index** (chỉ mục một chiều) dựa trên **Hilbert curve** (đường cong lấp đầy không gian - space-filling curve). Hilbert curve sở hữu một đặc tính tối quan trọng: hai điểm nằm gần nhau trên đường cong này thì cũng sẽ nằm gần nhau trong không gian 1D. Nhờ đó, các thao tác **search** (tìm kiếm) trên không gian 1D đạt hiệu năng cao hơn rất nhiều so với không gian 2D truyền thống. (Bạn có thể trải nghiệm công cụ trực tuyến về Hilbert curve để hiểu rõ hơn về cách nó hoạt động).

Dù S2 là một thư viện khá phức tạp, nhưng nhờ vào độ tin cậy và hiệu năng đã được kiểm chứng qua việc sử dụng rộng rãi tại các ông lớn công nghệ như Google, Tinder... nên đây là lựa chọn hàng đầu cho bài toán xử lý tọa độ.

### Ứng dụng trong Geofencing

S2 cực kỳ hiệu quả trong bài toán **Geofencing** (hàng rào địa lý) nhờ khả năng bao phủ các vùng diện tích tùy ý với nhiều **levels** (cấp độ phân giải) khác nhau. Geofencing cho phép chúng ta thiết lập các đường biên bao quanh các khu vực quan tâm (area of interest) và kích hoạt các **notifications** (thông báo) tới người dùng ngay khi họ nằm trong phạm vi đó.

Một ưu điểm khác của S2 là thuật toán **Region Cover** (bao phủ vùng). Khác với GeoHash sử dụng một **level** (độ phân giải/cấp độ) cố định, S2 cho phép chúng ta tùy chỉnh linh hoạt **min level**, **max level** và **max cells**. Kết quả trả về từ S2 mang tính **granular** (chi tiết/phân mảnh) hơn nhờ vào kích thước các **cell** (ô lưới) có khả năng thay đổi tùy biến. Nếu muốn tìm hiểu sâu hơn, bạn có thể tham khảo thêm [công cụ S2 tại đây].

### Khuyến nghị

Để đi đến kết luận, chúng ta cần cân nhắc kỹ lưỡng giữa việc sử dụng GeoHash hay Google S2, vì cả hai đều cung cấp đầy đủ các tính năng đáp ứng yêu cầu của ứng dụng hiện tại.

Tuy nhiên, có một điểm quan trọng cần lưu ý: trong khi một bên là giải pháp thiên về xử lý ở tầng **database** (cơ sở dữ liệu), thì bên còn lại chủ yếu vận hành như một giải pháp **in-memory** (lưu trữ và xử lý trực tiếp trên RAM). Để đơn giản hóa hệ thống và phù hợp với phạm vi bài viết này, chúng tôi sẽ ưu tiên chọn giải pháp GeoHash.



### Tối ưu hóa cập nhật vị trí xe buýt (Bus Location Update)

Mỗi xe buýt sẽ truyền dữ liệu cập nhật vị trí với tần suất khoảng hai giây một lần. Do đặc thù của dữ liệu vị trí là **write-heavy** (tần suất ghi rất lớn), việc ghi trực tiếp vào cơ sở dữ liệu (database) có thể thực hiện được nhưng lại không phải là phương án tối ưu về hiệu năng.

Một giải pháp thay thế hiệu quả hơn là lưu trữ vị trí mới nhất của các xe buýt vào **Redis Cache**, trong khi vẫn duy trì một **historical log** (nhật ký lịch sử) về lộ trình di chuyển của xe trong database. Cách tiếp cận này giúp cải thiện đáng kể khả năng **scalability** (khả năng mở rộng) cho các thao tác ghi dữ liệu của hệ thống.

Ngoài ra, cần cân nhắc cơ chế để ứng dụng dành cho phụ huynh (Parents app) nhận được các bản cập nhật này. Thay vì thực hiện **query** trực tiếp vào database liên tục để làm mới vị trí xe buýt, chúng ta có thể tận dụng **Redis Pub/Sub** (cơ chế Publish/Subscribe) để đẩy thông báo theo thời gian thực (real-time). Điều này giúp giảm tải cho database và tối ưu hóa trải nghiệm người dùng.

### Tìm hiểu về Redis Pub/Sub

Redis Pub/Sub hoạt động như một **message bus** (bus truyền tin) hiệu quả và gọn nhẹ. Các **channel** (kênh), hay còn gọi là **topic** (chủ đề), rất tiết kiệm tài nguyên và dễ dàng khởi tạo. Một server Redis hiện đại với dung lượng RAM lớn có thể hỗ trợ lên tới hàng triệu channel cùng lúc.

#### Kiến trúc của Redis Pub/Sub

Trong thiết kế của chúng tôi, các bản cập nhật vị trí (location updates) được nhận thông qua **WebSocket server**, sau đó được **publish** (xuất bản) vào một channel cụ thể của **bus** trên server Redis Pub/Sub. Các bản cập nhật mới này sau đó sẽ được **republish** (tái xuất bản) ngay lập tức tới tất cả các **subscriber**(người đăng ký/đối tượng lắng nghe) của bus đó, giúp đảm bảo việc cập nhật vị trí theo thời gian thực (real-time) trên bản đồ.

![[Pasted image 20260622163231.png]]

#### Cơ chế truyền tải dữ liệu vị trí (Location Update Delivery)

Xét đến tần suất cập nhật cao từ mỗi bus, việc sử dụng **RESTful API** để nhận dữ liệu sẽ không tối ưu và gây tốn kém hiệu năng. Một giải pháp hiệu quả hơn là sử dụng **WebSockets**. Công nghệ này duy trì **persistent connection** (kết nối bền vững), cho phép truyền tải dữ liệu liên tục mà không cần phải thực hiện lại **TCP handshake** (bắt tay TCP) mỗi vài giây, từ đó giảm thiểu đáng kể độ trễ và tải cho hệ thống.

### Mô hình dữ liệu (Data Model)

Trong phần này, chúng ta sẽ thảo luận về **tỷ lệ đọc/ghi (read/write ratio)** và **thiết kế lược đồ (schema design)** cho ứng dụng.

#### Tỷ lệ đọc/ghi

Hệ thống của chúng ta có **lưu lượng ghi (write volume)** rất cao, do dữ liệu vị trí từ các xe buýt được đẩy lên liên tục mỗi 2 giây. Do đó, số lượng thao tác ghi (write) vượt trội hoàn toàn so với các truy vấn đọc từ phía phụ huynh khi họ kiểm tra vị trí học sinh. Với đặc thù **ghi nhiều hơn đọc (write-heavy)**, việc sử dụng cơ sở dữ liệu **NoSQL** là lựa chọn tối ưu. Trong bài viết này, chúng ta sẽ sử dụng **DynamoDB**.

#### DynamoDB là lựa chọn cơ sở dữ liệu

DynamoDB là một cơ sở dữ liệu có khả năng **mở rộng (scalable)** và **độ sẵn sàng cao (highly available)**, được thiết kế để xử lý khối lượng dữ liệu đọc/ghi lớn. Dù yêu cầu quá trình thiết kế schema phải cực kỳ cẩn thận, nhưng bù lại, DynamoDB cung cấp các tính năng mạnh mẽ rất phù hợp với trường hợp sử dụng (use case) của chúng ta.

Chúng ta đề xuất tạo ba bảng chính:

1. **Parent Table** (Bảng Phụ huynh)
2. **Students Table** (Bảng Học sinh)
3. **Bus Location History Table** (Bảng Lịch sử vị trí xe buýt)

Trong DynamoDB, mỗi bảng bao gồm một **Khóa chính (Primary Key - PK)** và một **Khóa sắp xếp (Sort Key - SK)** tùy chọn. Sự kết hợp duy nhất giữa PK và SK (hoặc chỉ PK nếu không dùng SK) là yếu tố bắt buộc để tránh trùng lặp bản ghi (**duplicate records**). Việc truy vấn dữ liệu thường bị giới hạn trong các khóa này; đối với các truy vấn sử dụng thuộc tính khác, chúng ta có thể tận dụng **Local Secondary Index (LSI)** hoặc **Global Secondary Index (GSI)**.

Dựa trên các phân tích trước đó, chúng ta sẽ sử dụng **GeoHash** để phục vụ các truy vấn về vị trí. Việc xác định rõ ràng các câu truy vấn trước khi thiết kế schema là bước sống còn, nhằm đảm bảo cơ sở dữ liệu được tối ưu hóa tốt nhất cho các yêu cầu vận hành thực tế.

**Parent Table**

![[Pasted image 20260622163332.png]]

### Tối ưu hóa dữ liệu và thiết kế Schema trong DynamoDB

Bảng này được chuẩn hóa (normalize) bằng cách sử dụng `student_ids_` _nhằm giảm thiểu khối lượng truy vấn (query volume) khi cần truy xuất vị trí các con của phụ huynh. Schema này cho phép thực hiện **caching** (lưu trữ đệm) các `bus`_`ids` liên kết với mỗi phụ huynh để tối ưu hóa hiệu năng (performance).

- **Key:** `parent_id`
- **Value:** `bus_ids`

#### Bảng Student (Student Table)

Bảng này bao gồm một trường **GeoHash** để xác định block địa lý mà học sinh thuộc về. Ngoài ra, các trường **Latitude** (Vĩ độ) và **Longitude** (Kinh độ) thể hiện vị trí nhà của học sinh, được sử dụng để tính toán khoảng cách ước tính đến điểm đến.

![[Pasted image 20260622163404.png]]

Hơn nữa, cần thiết lập một **Global Secondary Index (GSI)** với `geohash` là **Partition Key (PK)** và `bus_id` là **Sort Key (SK)**. GSI này giúp hỗ trợ các truy vấn nhắm vào những khu vực địa lý cụ thể cho một tuyến xe buýt nhất định. Đồng thời, nó cũng được sử dụng để thông báo cho phụ huynh về thời điểm xe buýt đến (như sẽ đề cập chi tiết trong phần "Lưu trữ lịch sử vị trí xe buýt").

#### Bảng Lịch sử vị trí xe buýt (Bus Location History Table)
![[Pasted image 20260622163412.png]]

Bảng này tách biệt các thuộc tính vĩ độ và kinh độ để hiển thị vị trí xe buýt trên bản đồ một cách chính xác nhất, đáp ứng nhu cầu theo dõi của phụ huynh.

**Lưu ý:** Mặc dù việc gộp tất cả dữ liệu vào một bảng duy nhất là một phương pháp phổ biến trong DynamoDB để đơn giản hóa cấu trúc (single-table design), nhưng bài viết này sẽ minh họa cách sử dụng các bảng riêng biệt nhằm giúp người đọc làm rõ và nắm vững các khái niệm hệ thống.

### Thiết kế hệ thống (System Design): Luồng dữ liệu xe buýt (Bus Flow)

Sau khi đã phân tích từng thành phần (component) của hệ thống, chúng ta sẽ bắt đầu xây dựng sơ đồ thiết kế kiến trúc (architecture diagram) ban đầu cho ứng dụng. Dưới đây là các điểm mấu chốt cần lưu ý trong quá trình thiết kế:

1. **Thông báo từ xe buýt (Bus Notification):** Xe buýt sẽ thực hiện gửi các bản cập nhật vị trí (location updates) theo chu kỳ 2 giây một lần thông qua kết nối **WebSocket** tới server của chúng ta.
2. **Xử lý dữ liệu (Data Handling):** Thay vì ghi trực tiếp vào Database, server sẽ đẩy các bản cập nhật này vào một nền tảng lưu trữ bền vững (durable storage) như **Message Queue** (Ví dụ: Kafka, RabbitMQ) để thực hiện xử lý bất đồng bộ (**Async processing**). Điều này giúp hệ thống chịu tải tốt hơn.
3. **Bộ nhớ đệm vị trí (Location Caching):** Vị trí gần nhất của xe buýt sẽ được lưu trữ (cache) trên **Redis** để đảm bảo tốc độ truy xuất cực nhanh.
4. **Xuất bản dữ liệu thời gian thực (Real-time Publishing):** Vị trí sau khi cập nhật sẽ được đẩy (publish) tới các phụ huynh đang đăng ký theo dõi (**subscribe**) kênh dữ liệu của xe buýt đó thông qua cơ chế **Pub/Sub**.
5. **Cập nhật cơ sở dữ liệu (Database Updates):** Sau cùng, dữ liệu vị trí sẽ được lưu trữ bền vững vào **Database** (dạng lịch sử hành trình).
6. **Nhận diện vị trí địa lý (Geo-Location Awareness):** Khi xe buýt di chuyển vào một vùng **GeoHash** mới, hệ thống sẽ tự động kích hoạt thông báo cho tất cả phụ huynh đang sinh sống hoặc theo dõi trong khu vực đó.

![[Pasted image 20260622163448.png]]

1. **WebSocket Gateway:** Chúng tôi sử dụng AWS Managed WebSocket Gateway để thiết lập kết nối song công (full-duplex) qua WebSocket, cho phép đẩy (push) các bản cập nhật vị trí theo chu kỳ 2 giây/lần.

2. **API Gateway và Lambda:** Mỗi khi có message gửi đến, API Gateway sẽ trigger (kích hoạt) một hàm Lambda. Hàm này đóng vai trò là producer, forward (chuyển tiếp) dữ liệu vào các nền tảng streaming như Kafka hoặc Kinesis.

3. **Tính bền vững của dữ liệu (Data Durability):** Dữ liệu sẽ được lưu trữ (persist) trong stream cho đến khi được consumer xử lý hoàn tất.

Kiến trúc nêu trên đã giải quyết hiệu quả các mục tiêu ban đầu của chúng tôi. Giờ đây, hãy cùng chuyển trọng tâm sang điểm thứ ba và thứ tư trong thiết kế: quản lý vị trí hiện tại (current location) và cơ chế thông báo cho phụ huynh (parent notifications).

### Kiến trúc cập nhật vị trí xe buýt và thông báo cho người dùng

![[Pasted image 20260622163556.png]]

**Quy trình xử lý luồng dữ liệu (Data Stream) và thông báo:**

1. **Đổ dữ liệu vào Redis:** Dữ liệu vị trí từ luồng (stream) Kafka hoặc Kinesis sẽ được một **Worker** xử lý và lưu vào instance Redis. Tại đây, chúng ta thiết lập **TTL (Time to Live)** cho dữ liệu để đảm bảo dữ liệu cũ tự động bị loại bỏ, tối ưu hóa bộ nhớ.
2. **Cơ chế Redis Pub/Sub:** Ngay sau khi cache thành công, tọa độ mới sẽ được **publish** lên một kênh (channel) Pub/Sub chuyên biệt tương ứng với từng xe buýt (ví dụ: `bus#uuid`). Cơ chế này cho phép đẩy thông báo theo thời gian thực (**real-time**) đến tất cả các client đang kết nối.
3. **Hàng đợi (Queue) xử lý bất đồng bộ:** Sau khi đã pub/sub, dữ liệu được đẩy vào hàng đợi SQS để thực hiện các tác vụ xử lý **bất đồng bộ (asynchronous)** và lưu trữ lâu dài vào Database (DB).

**Lưu ý về tối ưu hóa:**  
Khi đẩy dữ liệu vào Queue, cần bao gồm cả vị trí vừa nhận được và vị trí gần nhất đang lưu trong Redis Cache. Ngoài ra, việc duy trì một **in-memory HashMap** giúp giảm thiểu số lượng truy vấn (**read calls**) đến Redis, từ đó cải thiện đáng kể hiệu suất (performance) của hệ thống.

**Tổng kết:**  
Đến bước này, chúng ta đã hoàn thiện luồng xử lý: tiếp nhận cập nhật vị trí từ xe buýt, lưu trữ trạng thái hiện tại (current location) và các cập nhật mới nhất vào Redis Cache. Toàn bộ dữ liệu này sau đó được đồng bộ hóa liền mạch tới ứng dụng người dùng, cho phép khách hàng theo dõi vị trí xe buýt một cách chính xác.

### Kiến trúc Lưu trữ Lịch sử Vị trí Xe buýt

![[Pasted image 20260622163622.png]]

**Quy trình xử lý dữ liệu từ SQS:**  
Dữ liệu vị trí được đẩy vào hàng đợi (queue) sẽ được một **Lambda worker** tiêu thụ (consume). Sau đó, worker này thực hiện lưu trữ vào cơ sở dữ liệu (Database) bao gồm các trường thông tin: ID của xe buýt và tọa độ (kinh độ - vĩ độ).

**Cơ chế Thông báo có điều kiện (Conditional Notifications):**  
Để tối ưu hóa hiệu năng của hệ thống thông báo, chúng ta thực hiện một bước kiểm tra (check) xem giá trị **GeoHash** của vị trí mới có thay đổi so với vị trí gần nhất được ghi nhận hay không. 

- Nếu có sự thay đổi: Hệ thống sẽ truy vấn để xác định danh sách các phụ huynh (parents) đang theo dõi khu vực (GeoHash) đó.
- Sau đó, hệ thống sẽ đẩy các thông báo tương ứng vào hàng đợi **SQS** để xử lý phân phối (dispatch).



### Thiết kế luồng Thông báo (Notification Flow Design)
![[Pasted image 20260622163658.png]]

#### Kiến trúc luồng Thông báo (Notification Flow Architecture)

1. **Truy xuất dữ liệu (Data Retrieval):** Khi hệ thống cần kích hoạt thông báo, bước đầu tiên là truy vấn thông tin khách hàng từ **Cache** (bộ nhớ đệm) để tối ưu tốc độ. Nếu dữ liệu không tồn tại (cache miss), hệ thống sẽ thực hiện truy vấn trực tiếp vào **Database** (cơ sở dữ liệu).
2. **Phân tán thông báo với SNS (Fan-out pattern):** Hệ thống sử dụng **Amazon SNS** (Simple Notification Service) để thực hiện cơ chế **Fan-out** (phân tán thông điệp). SNS sẽ điều phối và gửi thông báo dựa trên các tùy chọn (preferences) và phân khúc người dùng đã được thiết lập.
3. **Xử lý cuối (End Processing):** Các thông điệp sau đó được đưa vào hàng đợi (**Queue**) bằng **Amazon SQS** (Simple Queue Service). Tại đây, các **Lambda functions** sẽ đảm nhận việc xử lý bất đồng bộ để thực hiện tác vụ cuối cùng: gửi thông báo đến thiết bị của người dùng.

Thiết kế này đảm bảo khả năng truyền tin theo thời gian thực (**Real-time update dissemination**) và quản lý dữ liệu hiệu quả đối với các thông báo dựa trên vị trí địa lý (**Location-based notifications**). Hãy xem kỹ sơ đồ kiến trúc tổng thể (**End-to-end architecture diagram**) để hiểu rõ sự tương tác giữa các thành phần (**components**).


#### Kiến trúc tổng thể (End-to-End Architecture)

![[Pasted image 20260622163705.png]]

Kiến trúc này thoạt nhìn có vẻ phức tạp do bao gồm nhiều tầng xử lý, vì vậy bạn nên dành thời gian nghiên cứu kỹ từng thành phần để nắm bắt luồng dữ liệu (**data flow**) và cơ chế vận hành của toàn hệ thống.

**Thiết kế hệ thống (Luồng chức năng của ứng dụng phụ huynh):**  
Kiến trúc của ứng dụng phụ huynh có độ phức tạp thấp hơn so với luồng chức năng của xe buýt (Bus Flow) và có thể được minh họa trực quan qua một sơ đồ khối duy nhất.

![[Pasted image 20260622163758.png]]


### Quy trình xử lý khi ứng dụng khởi chạy

Khi người dùng mở ứng dụng, hệ thống sẽ thực hiện ba tác vụ chính:

1. **Thiết lập kết nối WebSocket ban đầu:** Ứng dụng khởi tạo một kết nối với **WebSocket Gateway** để duy trì kênh giao tiếp thời gian thực.
2. **Truy vấn Bus ID hiện tại:** Ứng dụng thực hiện truy vấn các **Bus ID** (mã định danh xe buýt) từ **Redis Cache**. Dữ liệu này giúp ứng dụng lấy được thông tin vị trí mới nhất và hiển thị các xe buýt lên bản đồ.
3. **Đăng ký (Subscribe) các kênh Bus:** Dựa trên danh sách các Bus ID đã truy xuất, ứng dụng sẽ đăng ký vào các **Channel** (kênh) tương ứng ở phía **ECS**(Elastic Container Service). Cơ chế này đảm bảo rằng mọi cập nhật vị trí mới đều được truyền qua **Redis Pub/Sub** và được đẩy tới điện thoại người dùng thông qua WebSocket Gateway.

### Logic phía Server khi xử lý kết nối

Việc hiểu cách thức hoạt động của ECS khi có một kết nối mới được thiết lập là cực kỳ quan trọng, bởi đây chính là nền tảng kiến trúc của **Parent App** (Ứng dụng phụ huynh).

Khi người dùng kết nối tới WebSocket Gateway, hệ thống sẽ kích hoạt một tiến trình trong ECS và gọi một **function** (hàm) chuyên dụng. Hàm này sẽ truy vấn danh sách các **Student ID** (mã định danh học sinh) từ **DynamoDB**, sau đó cấu hình để instance ECS hiện tại bắt đầu lắng nghe các kênh tương ứng với những học sinh đó.

Dưới đây là đoạn mã ví dụ mô tả quá trình này:

```javascript
const redis = require('redis');  
  
// Create a Redis client  
const subscriber = redis.createClient({  
url: 'redis://localhost:6379'  
});  
  
subscriber.on('error', (err) => {  
console.log('Redis Client Error', err);  
});  
  
subscriber.connect();  
  
// Function to subscribe to a new channel  
function subscribeToChannel(channelName) {  
subscriber.subscribe(channelName, (message, channel) => {  
console.log(`Received message: ${message} from channel: ${channel}`);  
});  
console.log(`Subscribed to ${channelName}`);  
}  
  
// Initially subscribe to a default channel  
subscribeToChannel('initialChannel');  
  
// Example of subscribing to a new channel dynamically based on some event or condition  
setTimeout(() => {  
// Simulating a new channel subscription trigger after 10 seconds  
subscribeToChannel('bus#uuid1');  
}, 10000);
```

Mỗi khi có cập nhật mới từ các kênh (channel) đã đăng ký, dữ liệu sẽ được đồng bộ hóa tức thì (instantly reflected) trên các instance ECS. Thông qua AWS SDK, ECS sẽ đẩy các cập nhật thời gian thực (live updates) tới ứng dụng di động thông qua WebSocket Gateway.

Để tối ưu hóa hiệu năng, chúng tôi duy trì một `HashMap` trên bộ nhớ (in-memory) cho các kênh đã đăng ký trên mỗi instance ECS. Cách tiếp cận này giúp quản lý việc đăng ký kênh hiệu quả và loại bỏ các yêu cầu đăng ký trùng lặp (duplicate subscriptions). Bên cạnh đó, chúng tôi lưu trữ ID của WebSocket Gateway kết hợp với Channel ID của người dùng ngay trên bộ nhớ đệm (in-memory). Cơ chế này giúp tinh giản quy trình gửi thông báo (notification process), loại bỏ hoàn toàn việc phải truy vấn cơ sở dữ liệu (database query) liên tục.

Ngoài ra, ứng dụng client được tích hợp logic tự động kết nối lại (auto-reconnect) với WebSocket Gateway trong trường hợp mất kết nối, đảm bảo duy trì đường truyền liên lạc thông suốt giữa server và ứng dụng di động.
Dưới đây là bản dịch bài viết sang tiếng Việt, sử dụng thuật ngữ chuyên ngành công nghệ thông tin để đảm bảo tính chính xác và dễ tiếp cận với các kỹ sư, kiến trúc sư hệ thống:

### Chuyên đề: Khai thác chuyên sâu về Khả năng mở rộng (Scalability)

Sau khi đã chốt thiết kế cho từng thành phần ứng dụng, chúng ta sẽ cùng phân tích các chiến lược để mở rộng độc lập (independent scalability). Cần lưu ý rằng một số thành phần được quản lý trực tiếp bởi AWS, cung cấp sẵn các cơ chế mở rộng tự động (out-of-the-box).

#### 1. WebSocket Servers
Các WebSocket server có thể được **auto-scale** (tự động mở rộng) dựa trên lưu lượng truy cập. Với các dịch vụ được quản lý như **API Gateway WebSocket**, AWS sẽ tự động xử lý việc scale. **ECS** và **Lambda** đóng vai trò thực thi logic nghiệp vụ khi có tin nhắn từ WebSocket và việc scale cũng rất linh hoạt:
*   **Lambda:** Scale thông qua việc cấu hình **concurrency settings** (giới hạn thực thi đồng thời).
*   **ECS:** Scale dựa trên các **metrics** về mức sử dụng CPU và RAM.

#### 2. DynamoDB
DynamoDB cung cấp tính sẵn sàng (availability) và khả năng mở rộng cao với hai chế độ: **On-Demand** và **Provisioned Capacity**.
*   **On-Demand:** Tự động scale dựa trên lưu lượng truy cập thực tế.
*   **Provisioned Capacity:** Cho phép thiết lập mức công suất định trước, phù hợp khi cần kiểm soát hiệu năng ổn định và tối ưu chi phí.
Việc **monitoring** (giám sát) là cực kỳ quan trọng để đảm bảo hiệu năng tối ưu dựa trên mô hình truy vấn của hệ thống.

#### 3. Cache & Pub/Sub (Redis)
**AWS ElastiCache** cung cấp dịch vụ Redis được quản lý với khả năng auto-scaling mạnh mẽ. Đặc biệt, **ElastiCache Serverless** có thể tự động thích ứng với khối lượng công việc (workload) bằng cách liên tục giám sát mức sử dụng tài nguyên. Hệ thống sẽ tự động **scale-out** (mở rộng theo chiều ngang), tự động tạo thêm **shards** và phân phối lại dữ liệu mà không gây ra **downtime** (thời gian gián đoạn).

#### 4. Data Streaming (Kafka/Kinesis)
Cả Kafka và Kinesis đều là các dịch vụ được quản lý bởi AWS, hỗ trợ khả năng mở rộng tuyệt vời nếu được cấu hình đúng. Dù chọn nền tảng nào, AWS cũng giúp chúng ta giảm bớt gánh nặng về **operational concerns** (vận hành hạ tầng).

#### 5. SQS (Simple Queue Service)
AWS cung cấp hai loại SQS: **FIFO** (First-In-First-Out) và **Unordered Queue** (không thứ tự), mỗi loại đều có những hạn mức (quota) riêng:

*   **FIFO Queues:** Hỗ trợ tối đa 300 giao dịch/giây cho mỗi API action. Khi sử dụng kỹ thuật **batching** (gộp tin nhắn), con số này có thể lên tới 3,000 tin nhắn/giây (300 API call, mỗi call chứa 10 tin nhắn).
*   **Thách thức về mở rộng:** Dựa trên các ước tính thô (**Back-Of-Envelope Estimation**), hệ thống của chúng ta dự kiến có mức ghi lên đến 10,000 request/giây (RPS). Với mức này, việc dùng FIFO Queue – ngay cả khi có batching – sẽ không đạt hiệu năng tối ưu.

**Các giải pháp thay thế:**
1.  **Unordered Queue:** Chuyển sang sử dụng queue không thứ tự và xử lý logic loại bỏ dữ liệu trùng lặp (**deduplication**) ngay tại tầng ứng dụng (application layer).
2.  **Data Streaming Platform:** Thay thế hoàn toàn SQS bằng các nền tảng streaming như Kafka hoặc Kinesis (đặc biệt phù hợp cho các luồng thông báo). Chỉ sử dụng SQS kết hợp với SNS cho các tiến trình thông báo đơn giản.
3.  **Over-Provisioning Queues:** Chia nhỏ tải (load) bằng cách tạo nhiều queue và triển khai logic **Consistent Hashing** (băm nhất quán) để phân phối dữ liệu vào các queue này, giúp xử lý mức độ ghi cao một cách hiệu quả.


### Giải pháp thay thế Redis Pub/Sub: Erlang

Erlang được xem là một phương án thay thế khả thi cho Redis Pub/Sub trong các tác vụ định tuyến (routing), đặc biệt được đánh giá cao nhờ khả năng tối ưu cho các ứng dụng có tính phân tán (distributed) và đồng thời (concurrent) cao. Lợi thế này đến từ hệ sinh thái Erlang, bao gồm ngôn ngữ lập trình Erlang hoặc Elixir, máy ảo BEAM và các thư viện runtime OTP. Điểm mạnh cốt lõi của Erlang nằm ở cách quản lý các **lightweight process** (tiến trình nhẹ): việc khởi tạo và quản lý chúng cực kỳ ít tốn tài nguyên, cho phép hàng triệu tiến trình chạy đồng thời trên một server duy nhất với chi phí vận hành tối thiểu.

Trong thực tế triển khai, việc sử dụng Erlang đồng nghĩa với việc thay thế mô hình Redis Pub/Sub bằng một hệ thống Erlang phân tán, nơi mỗi người dùng được đại diện bởi một tiến trình riêng biệt. Các tiến trình này có thể quản lý hiệu quả các cập nhật thời gian thực (real-time updates) – như thay đổi tọa độ địa lý – và tạo ra mạng lưới truyền tin giữa bạn bè của người dùng. Erlang chính là ứng viên sáng giá cho các hệ thống đòi hỏi khả năng mở rộng (scalability) và truyền tải dữ liệu thời gian thực, với điều kiện đội ngũ kỹ thuật có chuyên môn về ngôn ngữ này.

### Tổng kết

Trong bài viết chuyên sâu này, chúng ta đã đi sâu vào nhiều khía cạnh của kiến trúc hệ thống, tập trung vào cơ chế caching, pub/sub và kỹ thuật xử lý lưu lượng ghi (write volume) lớn. Chúng ta đã phân tích chi tiết hai luồng kiến trúc (architecture flows) khác nhau, đồng thời làm rõ chức năng và sự tương tác giữa các thành phần trong hệ thống.

Hơn nữa, chúng ta cũng đã thảo luận kỹ lưỡng về các chiến lược mở rộng, nhấn mạnh tầm quan trọng của việc có thể scale từng thành phần một cách độc lập. Bằng cách tận dụng các dịch vụ được quản lý (managed services) và áp dụng các best practices, hệ thống của chúng ta được thiết kế để có khả năng mở rộng và độ sẵn sàng (high availability) cao, đáp ứng linh hoạt các biến động về nhu cầu và đảm bảo hiệu năng ổn định.

Tôi khuyến khích các bạn dành thời gian nghiên cứu kỹ bài viết này. Nếu có bất kỳ câu hỏi hoặc góp ý nào để cải thiện, hãy chia sẻ dưới phần bình luận. Mọi phản hồi của các bạn đều vô cùng quý giá để giúp tôi nâng cao chất lượng nội dung và mang lại nhiều giá trị hơn cho cộng đồng.


ref: https://joudwawad.medium.com/school-bus-tracker-system-architecture-6dd3307e3860