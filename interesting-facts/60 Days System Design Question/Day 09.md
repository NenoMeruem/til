Nodes: [[60 Days System Design Question]]
Tags: #system-design


### Dịch vụ `Orders` của bạn đang chạy trên một `Postgres monolith` với lưu lượng 8K `write/min` (ghi) và 40K `read/min` (đọc).

![[Pasted image 20260623165759.png]]

Cùng một bộ bảng (tables), cùng một `schema`. Mọi thứ đang bắt đầu quá tải (`grinding`).

Phía `write` (ghi) cần một `normalized schema` (bảng được chuẩn hóa) — tách biệt `orders`, `line_items`, `payments`, `shipments`, `addresses`. Cần các `Foreign Key` (khóa ngoại) chặt chẽ, đảm bảo tính `ACID` và tránh dữ liệu thừa (`duplicated data`). Trong khi đó, phía `read` (đọc) lại muốn điều ngược lại — `dashboard` phải `join` tới 7 bảng chỉ để render một thẻ `order`, và các câu lệnh `reporting` đang đẩy `CPU` lên ngưỡng 85% vào mỗi 9 giờ sáng.

Bạn đã tối ưu `index` (chỉ mục), đã thêm `caching`. Vấn đề cốt lõi không nằm ở phần cứng — mà là `read model` và `write model` đang yêu cầu các "hình thái" dữ liệu khác nhau, nhưng bạn lại đang cố ép chúng dùng chung một `schema` suốt 2 năm qua.

Đây là các phương án đang đặt trên bàn:

**A) Full CQRS:** Tách biệt `read model` và `write model`. `Project` (đổ) dữ liệu từ phía ghi sang một `read store` đã được `denormalized` (phi chuẩn hóa) như `ElasticSearch` hoặc một `Postgres read DB` riêng biệt. Chấp nhận `eventual consistency` (tính nhất quán cuối cùng) giữa hai bên.

**B) Thêm Read Replicas:** Chuyển hướng các tác vụ `dashboard` và `report` sang `replica`, giữ lại các tác vụ ghi trên `primary node`.

**C) Giữ nguyên 1 DB, 1 model:** Thực hiện `denormalize` trực tiếp trên `write schema` (ví dụ: `flatten` bảng `line_items` vào `orders`, dư thừa hóa dữ liệu khách hàng) để giảm thiểu các câu lệnh `join` khi đọc.

**D) Giữ nguyên schema, thêm GraphQL + DataLoader:** Giải quyết vấn đề `N+1` tại tầng truy vấn (`query layer`), giữ nguyên cấu trúc DB.

Cả 4 phương án đều là các `pattern` thực tế bạn sẽ thấy trong môi trường `production`. Ba trong số đó chỉ đang "né" vấn đề thực sự — và một trong số đó chính là "cái bẫy" dành cho các `Senior Engineer`, nhìn thì rất đúng đắn trong khoảng 6 tháng đầu cho đến khi nó "sập".

Hãy chọn một — A, B, C hoặc D — và giải thích lý do tại sao. Phân tích chi tiết sẽ ở phần bình luận.

Nếu team của bạn từng tranh cãi về bài toán đánh đổi (`tradeoff`) này vào lúc 11 giờ đêm trước ngày `release`, hãy chia sẻ với họ. Những cuộc tranh luận này sẽ giúp bạn làm chủ các `design pattern` tốt hơn.

Hãy để lại câu trả lời của bạn 👇




1. **Câu trả lời: Đáp án A — Full CQRS (Command Query Responsibility Segregation)**

![[Pasted image 20260623170030.png]]

**Tại sao A là lựa chọn tối ưu:**

Vấn đề cốt lõi không nằm ở việc "tốc độ đọc chậm" — mà là sự xung đột giữa nhu cầu của hai phía: **Write side** (phía ghi) cần một Schema đã được **chuẩn hóa (normalized)** để đảm bảo toàn vẹn dữ liệu, trong khi **Read side** (phía đọc) lại cần một Schema **phi chuẩn hóa (denormalized)** để truy vấn nhanh. Việc ép buộc cả hai dùng chung một cấu trúc dữ liệu chính là nguyên nhân gây ra tắc nghẽn. Bạn không thể dùng phần cứng để giải quyết một thiết kế Schema không tương thích (mismatch).

**Giải pháp với Full CQRS:**

*   **Write side (Command side):** Giữ cấu trúc dữ liệu sạch, chuẩn hóa (normalized). Các bảng như `orders`, `line_items`, `payments` tuân thủ nguyên tắc **ACID** và được kiểm soát chặt chẽ bởi **Foreign Keys (FK)**.
*   **Read side (Query side):** Là một dạng **projection** (hình chiếu) dữ liệu. Bạn tạo một bảng phẳng kiểu `order_view` (hoặc index trên **Elasticsearch**), nơi mọi thông tin của đơn hàng nằm gọn trong một row duy nhất. Kết quả là: không cần **JOIN** bảng, tốc độ truy vấn cực nhanh.
*   **Đồng bộ dữ liệu:** Bạn sử dụng một **Projector** để giữ cho hai phía đồng bộ thông qua các cơ chế như: **Outbox Pattern** → **Kafka** → **Read-model updater**, hoặc sử dụng **CDC** (Change Data Capture) từ Database.
*   **Đánh đổi:** Bạn chấp nhận **Eventual Consistency** (nhất quán cuối cùng). Dữ liệu trên dashboard có thể trễ vài trăm mili giây. Với 95% các tác vụ đọc (xem báo cáo, dashboard, tìm kiếm), độ trễ này là không đáng kể. Với 5% các tác vụ đòi hỏi **Strong Consistency** (ví dụ: hiển thị xác nhận đơn hàng ngay lập tức cho người dùng sau khi thanh toán), bạn chỉ cần thực hiện query trực tiếp từ phía **Write side**.


2. **Tại sao phương án B là một cái bẫy (Read Replicas)**

Phương án B giải quyết được vấn đề **read load** (tải đọc), nhưng không giải quyết được **read shape** (cấu trúc câu truy vấn). Một câu truy vấn **7-table join** (kết nối 7 bảng) vẫn là 7-table join — nó chỉ đơn thuần chạy trên một phần cứng khác mà thôi. Bạn chỉ đang chuyển dịch hóa đơn chi phí CPU sang nơi khác chứ không hề loại bỏ nó. Độ trễ (**latency**) có thể giảm trong 6 tháng đầu khi lưu lượng truy cập tăng, nhưng sau đó bạn sẽ quay lại điểm xuất phát với 3 bản sao (**replicas**) cùng phải gánh những câu lệnh join đắt đỏ đó. Phương án B chỉ đúng khi cấu trúc các câu join đã tối ưu nhưng **primary database** bị quá tải. Nó hoàn toàn sai nếu bản thân các câu join mới là vấn đề cốt lõi.

3. **Tại sao phương án C là sai (Denormalize the write model)**

Việc khử chuẩn hóa (**denormalization**) khiến mỗi thay đổi ở một dòng hàng hóa (**line-item**) giờ đây phải ghi đè lại toàn bộ dòng đơn hàng (**order row**). Mọi cập nhật địa chỉ sẽ kéo theo hiệu ứng dây chuyền trên mọi đơn hàng đã từng đặt. **Write amplification** (sự khuếch đại ghi) sẽ tích tụ dần ở mức 8.000 lượt ghi/phút. **Schema** trở nên xơ cứng (**ossified**) — việc thêm một trường dữ liệu vào `line_items` đồng nghĩa với việc bạn phải **migrate** hàng triệu dòng đã được khử chuẩn hóa. Đây là chiêu bài kinh điển để "né tránh việc thảo luận về kiến trúc". Nó giúp bạn đổi lấy một quý thảnh thơi nhưng sẽ phải trả giá đắt cho hai quý sau đó.

4. **Tại sao phương án D là sai (GraphQL + DataLoader)**

**DataLoader** thực hiện cơ chế **batching** các lời gọi API, chứ không phải tối ưu hóa các câu join. Câu truy vấn 7-table join vẫn thực thi tại **database**, không phải tại **application**. Sau 3 tháng cật lực **migrate** sang GraphQL, kết quả đọc dữ liệu vẫn chậm y như lúc ban đầu. Đây là câu trả lời đúng khi vấn đề nằm ở phía client (gọi quá nhiều request), nhưng là giải pháp sai lầm khi vấn đề nằm ở chính **DB schema**.