
Node: [[article]]
Tags: #system-design


**AWS Lambda** đã trở thành "xương sống" cho các ứng dụng **serverless** hiện đại. Công nghệ này cho phép các lập trình viên thực thi code mà không cần quản lý hạ tầng server, đồng thời tự động **scale** (mở rộng quy mô) để đáp ứng hàng nghìn **concurrent requests** (yêu cầu đồng thời). Mỗi **Lambda function** chạy trong một môi trường **isolated** (cô lập) riêng biệt, bao gồm đầy đủ **runtime**, bộ nhớ (**memory**) và **temporary storage** (lưu trữ tạm thời).

Tuy nhiên, đi cùng với sức mạnh đó là những thách thức mới: Làm thế nào để thiết kế các function sao cho dễ **maintain** (bảo trì), bảo mật và khả năng mở rộng tối ưu?

Đó chính là lúc các **Lambda design patterns** (mẫu thiết kế) phát huy tác dụng. Đây không phải là những quy tắc cứng nhắc, mà là những phương pháp đã được kiểm chứng để cấu trúc các function, giúp chúng xử lý tốt các bài toán thực tế phức tạp. Dù bạn là người mới bắt đầu làm quen với **serverless**, một chuyên gia đang thiết kế hệ thống **enterprise** (doanh nghiệp), hay một nhà khởi nghiệp đang muốn xây dựng sản phẩm theo hướng **lean** (tinh gọn), thì việc nắm vững các **design patterns** này sẽ giúp bạn tiết kiệm thời gian, chi phí và tránh được nhiều rắc rối không đáng có.

Với nền tảng này, hãy cùng chúng tôi khám phá các **architecture patterns** (mẫu kiến trúc) của AWS Lambda được sử dụng phổ biến nhất trong các hệ thống **production** hiện nay.

### 1. Fan-Out Pattern (Mô hình Fan-out)

Fan-out là một trong những pattern mạnh mẽ và được sử dụng phổ biến nhất trong kiến trúc AWS Lambda. Cơ chế này cho phép một sự kiện (event) đơn lẻ kích hoạt nhiều tiến trình hạ nguồn (downstream processes) chạy song song (in parallel). Kỹ thuật này thường được triển khai thông qua các dịch vụ như **SNS (Simple Notification Service)** hoặc **EventBridge**, nơi một sự kiện được publish lên sẽ kích hoạt nhiều subscriber cùng lúc.

![[Pasted image 20260622142059.png]]

#### Ví dụ về Fan-Out Pattern với AWS Lambda:

1. **Khởi tạo:** Một yêu cầu đặt chỗ (Reservation) được gửi đến một hàm Lambda. Hàm này chịu trách nhiệm xử lý yêu cầu (theo cơ chế đồng bộ hoặc bất đồng bộ).
2. **Fan-out:** Thay vì xử lý trực tiếp, Lambda gửi sự kiện đó đến các dịch vụ Fan-out (SNS hoặc EventBridge). Các dịch vụ này sẽ tự động "phát tán" sự kiện đến các downstream consumer (là các hàm Lambda khác) để xử lý song song.
3. **Độc lập:** Các downstream consumer được kích hoạt, và hàm Lambda ban đầu không cần phải biết về sự tồn tại của bất kỳ consumer nào (cũ hay mới).

#### Tại sao mô hình này hiệu quả?

*  **Tăng hiệu năng:** Các workload được chạy song song, giúp tối ưu hóa thời gian thực thi (execution time).
*  **Khả năng mở rộng độc lập:** Bạn có thể scale riêng biệt từng thành phần (ví dụ: cấp nhiều tài nguyên hơn cho tiến trình encode, và ít hơn cho việc tạo thumbnail).
*  **Decouple (Phi ghép nối):** Tách rời Producer (bên tạo sự kiện) với các Downstream Consumer (bên xử lý), giúp hệ thống linh hoạt và dễ bảo trì hơn.

#### Phù hợp nhất cho:

*   Các workflow cần kích hoạt nhiều tác vụ độc lập từ cùng một sự kiện đầu vào.
*   Kiến trúc **Event-Driven (hướng sự kiện)** thời gian thực.
*   Các ứng dụng quy mô lớn đòi hỏi năng lực xử lý song song cao.

### 2. Messaging Pattern (Mô hình hướng sự kiện - Event-Driven)

Đây là một thiết kế **bất đồng bộ (asynchronous)**. Cơ chế giao tiếp này chủ yếu phục vụ mô hình **một-nhiều (one-to-many)** và cơ chế **xuất bản/đăng ký (publish/subscribe)**, cho phép dữ liệu được gửi đến nhiều bên nhận cùng lúc.

Trong mô hình này, các **producer** (bên tạo tin nhắn) sẽ đẩy message vào một **queue** (hàng đợi) hoặc **stream** (luồng dữ liệu) như AWS SQS, SNS, hoặc Kinesis; sau đó, các hàm **Lambda** sẽ đóng vai trò là **consumer** (bên tiêu thụ) để xử lý các message này một cách bất đồng bộ. Cách làm này giúp **decouple** (phi ghép nối) các dịch vụ, xử lý hiệu quả các đợt **traffic burst** (lưu lượng truy cập đột biến) và đảm bảo tính tin cậy thông qua cơ chế **retry** (thử lại).

Về bản chất, AWS Lambda được thiết kế để phục vụ các ứng dụng **event-driven** (hướng sự kiện). Một "sự kiện" có thể là việc upload file lên S3, một tin nhắn mới trong SQS, hoặc một request từ API Gateway. Mô hình này tận dụng triệt để đặc tính của Lambda để duy trì sự **loosely coupled** (kết nối lỏng lẻo) cho hệ thống.

![[Pasted image 20260622142152.png]]

Thay vì viết các **monolithic service** (dịch vụ nguyên khối) cồng kềnh, bạn chia nhỏ logic thành các hàm riêng biệt phản hồi theo sự kiện.

**Ví dụ:**
1. Người dùng upload một bức ảnh lên S3.
2. Sự kiện này kích hoạt (trigger) một hàm Lambda để tạo ảnh thumbnail.
3. Một hàm Lambda khác sẽ index các metadata của ảnh đó vào OpenSearch.

**Tại sao mô hình này hiệu quả?**
*   **Single Responsibility (Trách nhiệm đơn nhất):** Mỗi hàm chỉ tập trung xử lý một nhiệm vụ cụ thể.
*   **Isolation (Cô lập lỗi):** Khi một phần bị lỗi, các thành phần khác không bị ảnh hưởng.
*   **Dễ bảo trì:** Việc thêm hoặc xóa tính năng trở nên đơn giản mà không làm ảnh hưởng đến cấu trúc tổng thể của hệ thống.

**Phù hợp nhất cho:**
*   Các khối lượng công việc (workloads) không ổn định hoặc khó dự đoán trước.
*   Cô lập các dịch vụ hạ nguồn (downstream services) đang chạy chậm hoặc không ổn định.
*   Chuyển các tác vụ nặng (heavy tasks) ra khỏi luồng xử lý request đồng bộ (synchronous request path) để tăng tốc độ phản hồi.
*   Đảm bảo dữ liệu được xử lý ít nhất một lần (**at-least-once delivery**) với sự hỗ trợ của cơ chế thử lại và **Dead-letter queue (DLQ)** (hàng đợi cho các tin nhắn lỗi).

### 3. Strangler Pattern (Mô hình "Bóp nghẹt")

Khi hiện đại hóa các hệ thống **Legacy** (hệ thống cũ), **Strangler Pattern** giúp bạn chuyển đổi dần dần từng phần thay vì phải **rewrite** (viết lại) toàn bộ hệ thống từ đầu.

**Cơ chế hoạt động:**
Thay vì thay thế toàn bộ **Monolithic application** (ứng dụng nguyên khối), bạn sẽ "bóp nghẹt" nó bằng cách điều hướng (route) các **feature** (tính năng) cụ thể sang các **Lambda function** (kiến trúc serverless), trong khi hệ thống cũ vẫn tiếp tục vận hành song song. Theo thời gian, hệ thống cũ sẽ dần bị thu hẹp lại cho đến khi chỉ còn lại phiên bản mới hoàn toàn trên nền tảng Serverless.

![[Pasted image 20260622142236.png]]

**Ví dụ:**
*   Một trang thương mại điện tử ban đầu xử lý đơn hàng trong một **Monolith**.
*   Bạn tách tính năng "gửi email thông báo" sang một Lambda.
*   Sau đó, bạn tiếp tục **migrate** (di chuyển) tính năng "xử lý thanh toán" và "cập nhật kho hàng" sang các Lambda riêng biệt.

**Tại sao phương pháp này hiệu quả?**
*   **Giảm thiểu rủi ro khi migration:** Việc chuyển đổi từng phần giúp kiểm soát lỗi tốt hơn so với việc thay thế toàn bộ hệ thống (Big Bang migration).
*   **Tận dụng lợi ích của Serverless ngay lập tức:** Bạn không cần phải chờ đến khi hoàn tất việc viết lại toàn bộ mã nguồn mới bắt đầu thấy được hiệu năng của serverless.
*   **Stakeholder (các bên liên quan) thấy được tiến độ rõ ràng:** Việc triển khai từng phần giúp minh chứng hiệu quả của dự án sớm hơn.

**Phù hợp nhất cho:**
*   Các **Legacy system** đang cần tích hợp thêm các tính năng mới.
*   Các doanh nghiệp không thể chấp nhận **downtime** (thời gian chết) hoặc không muốn thực hiện những khoản đầu tư khổng lồ ngay từ đầu.
*   Các hệ thống cần di chuyển hoặc phát triển tính năng mới nhằm tận dụng khả năng **scalability** (khả năng mở rộng) tự động của AWS Lambda.

### 4. Command Pattern (Mẫu thiết kế Command)

Trong mô hình này, một Lambda function đóng vai trò là **Command Handler** (bộ xử lý lệnh). Nó có trách nhiệm tiếp nhận **Trigger** (sự kiện kích hoạt), **Validate** (xác thực) request, áp dụng các **Business Rules** (quy tắc nghiệp vụ) và thực hiện **Orchestration** (điều phối) các tác vụ ở hạ tầng bên dưới (downstream). Lambda này tập trung hóa mọi quyết định logic (decision-making) và ủy thác các tác vụ thực thi cụ thể cho các Lambda hoặc dịch vụ khác.

![[Pasted image 20260622142430.png]]

**Ví dụ:**
Một Lambda chuyên xử lý việc "Đặt hàng" (Order Submission) sẽ thực hiện kiểm tra tính hợp lệ của đơn hàng, lưu thông tin vào Database, sau đó kích hoạt các "Worker Lambda" khác để xử lý thanh toán, gửi thông báo (notification) và cập nhật dữ liệu cho các hệ thống bên thứ ba.

**Tại sao mô hình này hiệu quả?**
*   **Đơn giản hóa các luồng nghiệp vụ phức tạp:** Giúp cấu trúc code gọn gàng hơn.
*   **Tăng khả năng quan sát (Visibility):** Dễ dàng theo dõi luồng thực thi (execution flow) của toàn bộ quy trình.
*   **Giảm thiểu "Glue Code":** Loại bỏ các đoạn code chắp vá, trung gian mà bạn thường phải viết để kết nối các phần của hệ thống.

**Phù hợp nhất cho:**
*  Các luồng công việc (workflows) quy mô từ nhỏ đến trung bình, nơi mà việc sử dụng **AWS Step Functions** trở nên quá cồng kềnh và dư thừa.
*  Các kịch bản yêu cầu một **Single Entry Point** (điểm truy cập duy nhất) để áp dụng các bộ quy tắc kiểm duyệt trước khi ủy thác nhiệm vụ cho các thành phần khác.
*  Các ứng dụng cần sự phân tách rõ ràng giữa **Control Logic** (logic điều khiển) và **Worker Logic** (logic thực thi tác vụ).

### 5. Mô hình RESTful Microservices

Đây là mô hình **Giao tiếp đồng bộ (Synchronous Communication)** dành cho các Microservices dựa trên kiến trúc RESTful. Đây là mô hình web service cơ bản và là trường hợp sử dụng (use-case) tiêu chuẩn nhất của AWS Lambda khi đóng vai trò là backend service. Thông thường, Client sẽ giao tiếp với các backend service thông qua REST API, trong đó các lệnh đồng bộ được thực hiện theo cơ chế **Request/Response (Yêu cầu/Phản hồi)**.

![[Pasted image 20260622142531.png]]
#### Mô hình RESTful Microservices
Trong mô hình đồng bộ, Client gửi đi một request và bắt buộc phải đợi server xử lý rồi trả về response.

**Ví dụ:**
* Một hàm Lambda được định nghĩa thông qua một **Endpoint** (ví dụ: `/order`, `/customer`) và một **HTTP Method** (POST, GET, v.v.).
* Người dùng thực hiện request thông qua **API Gateway** hoặc bất kỳ lớp **Proxy** trung gian nào.
* Hàm Lambda được **Invoke** (kích hoạt) và thực thi, sau đó kết quả xử lý được trả ngược về cho Client.
* Client sẽ ở trạng thái chờ cho đến khi Lambda thực thi xong và nhận được kết quả.

#### Tại sao mô hình này hiệu quả?
* **Mô hình đơn giản:** Dựa trên các **HTTP Verbs** (động từ HTTP) và **JSON Contract** (giao diện trao đổi dữ liệu JSON) đã được quy định trước.
* **Tự động mở rộng (Auto-scaling):** Có khả năng scale tự động khi lưu lượng truy cập (traffic) tăng cao.
* **Serverless hoàn toàn:** Bạn chỉ phải trả chi phí dựa trên số lượng request thực tế nhận được (**Pay-per-request**).
#### Phù hợp nhất cho:
* Các **CRUD API** (Create, Read, Update, Delete) và các **Query API** yêu cầu thời gian thực thi ngắn (dưới 1 giây).
* Các hệ thống Backend cho Mobile/Web cần cơ chế đồng bộ (Request/Response) và muốn tận dụng lợi ích từ tính chất serverless của AWS Lambda.
* Bất kỳ thao tác hoặc request nào yêu cầu server phải trả về kết quả ngay lập tức (Immediate response) sau khi xử lý.


### **Kết luận**

AWS Lambda là một công cụ cực kỳ mạnh mẽ, được ứng dụng rộng rãi trên toàn cầu với vô số các use case (trường hợp sử dụng) và architecture pattern (mô hình kiến trúc) đa dạng. Chúng tôi đã cố gắng tổng hợp một vài mô hình tiêu biểu; hy vọng rằng mỗi khi cân nhắc tích hợp Lambda function vào kiến trúc hệ thống, bạn sẽ có sẵn một "bản danh sách" các pattern để linh hoạt lựa chọn.

Tuy nhiên, hãy coi đây là những tài liệu tham khảo mang tính định hướng: các pattern này hoàn toàn có thể được kết hợp, tùy biến hoặc tái cấu trúc tùy theo nhu cầu thực tế. Điều quan trọng nhất vẫn là bạn cần nắm vững bản chất: dùng ở đâu và dùng như thế nào để tối ưu hóa triệt để sức mạnh của kiến trúc Serverless mà AWS Lambda mang lại.


ref: https://joudwawad.medium.com/aws-lambda-patterns-da5007b72a00