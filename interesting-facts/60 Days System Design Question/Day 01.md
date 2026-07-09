Nodes: [[60 Days System Design Question]]
Tags: #system-design

**Ứng dụng di động của chúng ta hiện đang kết nối trực tiếp với 3 backend service. Một service thứ 4 sẽ được triển khai vào sprint tới, và team mobile hiện đang "ngập đầu" trong khối lượng công việc.**

Mỗi khi thêm một service mới, đồng nghĩa với việc chúng ta phải whitelist một domain mới, cấu hình lại cơ chế xác thực (auth scheme), và xử lý cấu trúc dữ liệu lỗi (error shape) mới. Bạn được yêu cầu phải giảm sự phụ thuộc (reduce coupling) trước khi `NotificationService` được tích hợp.

**Kiến trúc hiện tại:**
*   Mobile → `UserService` (users.api.com)
*   Mobile → `OrderService` (orders.api.com)
*   Mobile → `PaymentService` (payments.api.com)
*   ...và `NotificationService` vào sprint tới.

![[Pasted image 20260622165239.png]]

**Vấn đề:** Client (ứng dụng di động) đang đảm nhận vai trò định tuyến (routing) – công việc lẽ ra thuộc về phía backend. Bạn sẽ làm gì?
*   **A) Thêm API Gateway:** Tạo một điểm truy cập duy nhất, tất cả các service nằm sau một domain.
*   **B) Xây dựng BFF (Backend for Frontend):** Tạo một lớp trung gian tổng hợp (aggregation layer) được thiết kế riêng cho ứng dụng di động.
*   **C) Đặt Load Balancer phía trước các service:** Cung cấp một IP duy nhất, phân phối traffic tới các service.
*   **D) Chuyển sang GraphQL Federation:** Sử dụng một schema thống nhất mà client truy vấn thông qua đó.

Trong số này, có 3 phương án là các mô hình (pattern) thực tế vẫn được dùng trong môi trường production. Tuy nhiên, chỉ có **duy nhất một phương án** giải quyết đúng bài toán mà bạn đang gặp phải.

**Hãy chọn một phương án A, B, C hoặc D và giải thích lý do.** Tôi sẽ đưa ra phân tích chi tiết bên dưới (bao gồm cả lý do tại sao hai trong số các câu trả lời sai lại dễ đánh lừa cả những senior engineer).

Để dịch đoạn văn này một cách chuyên nghiệp và dễ hiểu cho dân lập trình, chúng ta cần sử dụng các thuật ngữ như *pattern, payload, backend, domain, coupling*.



### Tại sao nên sử dụng API Gateway?

![[Pasted image 20260622165353.png]]

**Một domain, một luồng xác thực (auth flow), một cấu trúc phản hồi lỗi (error contract).**

Client không còn cần bận tâm việc `UserService`, `OrderService` hay `PaymentService` đang nằm trên các host khác nhau — API Gateway đóng vai trò làm lớp trung gian (proxy), ẩn đi các chi tiết hạ tầng đằng sau đường dẫn chung: `api.yourapp.com/users`, `/orders`, `/payments`. 

Khi `NotificationService` được deploy ở sprint tiếp theo, bạn chỉ cần thêm một route duy nhất tại Gateway. Phía mobile app hoàn toàn không phải thay đổi bất kỳ dòng code nào. Đây mới chính là ý nghĩa thực sự của việc "tối ưu cho tương lai" (future-proof) ở tầng giao thức (transport layer): các service mới được thêm vào mà không gây tốn kém chi phí bảo trì hay cập nhật trên phía Client.

Ngoài ra, nó giúp tập trung hóa các nghiệp vụ mà bạn không muốn phải cài đặt rải rác trên hàng tá codebase khác nhau: **Authentication/Authorization (xác thực/phân quyền), Rate Limiting (giới hạn lưu lượng), Request Logging, TLS Termination (giải mã SSL), và Versioning (quản lý phiên bản API).**

Đó là lý do tại sao những "ông lớn" như Netflix, Stripe và mọi hệ thống Fintech trưởng thành đều đang áp dụng mô hình này dưới một hình thức nào đó.

### Tại sao phương án B lại là một "cái bẫy" (BFF)?

**BFF (Backend-for-Frontend)** là một *design pattern* hoàn toàn hợp lệ — thậm chí nó đủ thuyết phục để đánh lừa cả những *senior engineer* dày dặn kinh nghiệm. Tuy nhiên, bản chất của BFF là giải quyết một bài toán khác: **tối ưu hóa cấu trúc dữ liệu theo từng loại client.**

Cụ thể, ứng dụng di động (mobile) cần một *payload* tinh gọn, trong khi ứng dụng web lại cần dữ liệu phong phú hơn. BFF giải quyết vấn đề này bằng cách cung cấp cho mỗi *client* một *backend* riêng để tổng hợp (*aggregate*) và định hình lại (*reshape*) dữ liệu.

Nhưng trong trường hợp này, vấn đề thực sự chúng ta đang gặp phải không nằm ở cấu trúc *payload*, mà nằm ở **sự phân tán miền nghiệp vụ (domain sprawl)** và **tính kết nối quá chặt chẽ (tight coupling)**.

Việc áp dụng mô hình BFF ở đây chẳng khác nào đánh đổi 4 URL lấy 1 URL cộng thêm một *service* mới mà bạn lại phải tự quản lý từ A-Z. Đó rõ ràng là một sự đánh đổi sai lầm.