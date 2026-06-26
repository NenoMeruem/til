

### You’re shipping a rewrite of your checkout write path on Friday.

![[Pasted image 20260626143036.png]]


Bạn chuẩn bị **deploy** một phiên bản **rewrite** cho luồng **checkout (write path)** vào thứ Sáu.

Hệ thống chạy **Node.js trên ECS Fargate**, **peak load** khoảng 3,000 RPS. CSDL là **Postgres** với cơ chế **row-level locking** trên bảng `orders`. Thay đổi này tác động trực tiếp vào đoạn code xử lý thanh toán thẻ: từ dùng **Stripe Charges API** (cũ) chuyển sang **PaymentIntents với 3DS** (mới).

Môi trường **QA** đã **green**. **Load test** đã qua. **Staff engineer** đã **sign-off**.

Nhưng đây là luồng thanh toán. Nếu nó "toang", doanh thu sẽ bị ảnh hưởng. Và quan trọng nhất, bạn không thể **roll back** một giao dịch thẻ đã thực sự trừ tiền.

Hãy chọn chiến lược **deploy**:

**A) Blue/Green:** Khởi tạo một môi trường "green" song song chạy code mới, thực hiện **smoke-test**, sau đó trỏ **load balancer** sang. **Rollback** tức thì bằng cách trỏ ngược lại.

**B) Canary:** Định tuyến 1% **live traffic** sang phiên bản mới, giám sát **error rates** và **p99 latency** trong 30 phút, sau đó tăng dần 5% → 25% → 100%.

**C) Rolling:** Thay thế từng **ECS task** một. Phiên bản cũ và mới cùng chạy song song cho đến khi toàn bộ được cập nhật.

**D) Feature Flag:** **Deploy** code mới cho 100% các **task** nhưng ẩn sau một **flag** mặc định là OFF. Sau đó bật dần cho **internal users** → 1% khách hàng → 10% → 100%, có kèm **kill switch** tức thì.

Cả bốn phương án trên đều là những **production patterns** thực tế. Nhưng có 3 phương án tồn tại lỗ hổng tiềm ẩn khi đụng đến các nghiệp vụ liên quan đến tiền tệ.

Bạn chọn phương án nào (A, B, C, hay D)? Và tại sao? Phân tích chi tiết ở phần bình luận.

Nếu team bạn từng tranh luận gay gắt về vấn đề này lúc 4 giờ chiều thứ Sáu, hãy chia sẻ bài viết này cho họ. Mục đích chính là cuộc tranh luận này đây.

Cho tôi câu trả lời của bạn ở bên dưới nhé 👇


**Đáp án: D — Feature Flag (Cờ tính năng) ✅**

![[Pasted image 20260626145043.png]]

Dưới đây là lý do tại sao phương án D chiến thắng, và tại sao ba phương án còn lại trông có vẻ hợp lý nhưng thực chất lại tiềm ẩn rủi ro lớn khi liên quan đến hệ thống thanh toán (tiền tệ):

**Tại sao D là lựa chọn tối ưu (Feature Flag):**

Feature flag giúp **decouple** (tách biệt) quá trình **deploy** (triển khai code) ra khỏi quá trình **release** (phát hành tính năng). Code mới được đẩy lên 100% các **ECS tasks** của bạn — nhưng nó ở trạng thái "ngủ đông" (dormant). Không có logic nào được thực thi cho đến khi bạn bật flag.

*   **Rollback (hoàn tác) cực nhanh:** Việc rollback chỉ là một thao tác **config push** (cập nhật cấu hình), không phải là một đợt deploy lại. Thời gian thực thi dưới một giây. Không cần restart ECS, không cần chờ **LB drain** (cạn kết nối trên Load Balancer), cũng không cần bận tâm về **DNS TTL**.
*   **Targeting chính xác:** Bạn được quyền chỉ định đích danh đối tượng nào sẽ sử dụng tính năng mới, thay vì dựa vào tỷ lệ % lưu lượng truy cập ngẫu nhiên. Người dùng mua gói $0.99 và khách hàng doanh nghiệp $40K không nên bị đối xử như nhau bằng cách tung đồng xu may rủi — đó không phải là chiến lược, đó là "cầu nguyện".
*   **Kiểm soát rủi ro:** Bạn có thể giữ đường chạy code cũ (old code path) chạy song song trong nhiều tuần. Giả sử có một **edge case** (trường hợp hi hữu) liên quan đến giao thức 3DS của một ngân hàng cụ thể tại Brazil? Bạn chỉ cần bật lại flag cho riêng nhóm người dùng đó để họ quay về code cũ, trong khi tất cả những người khác vẫn tiếp tục sử dụng v2.


**Tại sao Canary Deployment (Phương án B) lại là một cái bẫy?**

1. **Routing theo request chứ không theo customer (khách hàng):** Hãy tưởng tượng một job xử lý billing B2B gọi vào 1% các node canary của bạn 50 lần trong một giờ. Nếu có bug liên quan đến loại thẻ của khách hàng đó, bạn đã thực hiện thanh toán sai 50 lần trước khi các dashboard giám sát kịp phát hiện ra.
2. **Payment failure không hiển thị dưới dạng 5xx:** Các lỗi thanh toán thường không trả về HTTP 5xx (Server Error). Thay vào đó, hệ thống trả về mã 200 OK nhưng lại ghi nhận số tiền sai lệch. Do đó, các cảnh báo (alert) dựa trên tỷ lệ lỗi (error-rate) của bạn sẽ không bao giờ được kích hoạt.

**Tại sao Blue/Green Deployment (Phương án A) là sai lầm?**

Vấn đề nằm ở cơ chế **"Instant cutover" (chuyển đổi tức thì)**. Ngay khoảnh khắc bạn trỏ Load Balancer (LB) sang phiên bản mới, 100% traffic sẽ đổ dồn vào code mới — bao gồm cả các **Stripe webhooks** xác nhận các `PaymentIntents` vốn được tạo ra bởi phiên bản code cũ. Điều này gây ra **Race condition (xung đột tài nguyên)** giữa các version trên dữ liệu thực tế (tiền thật). Và quan trọng nhất: **Rollback (hoàn tác)** không thể hoàn trả lại các giao dịch đã thực hiện sai.

**Tại sao Rolling Deployment (Phương án C) không khả thi?**

Trong khoảng 5–10 phút triển khai, cả version cũ và mới đều đồng thời xử lý quy trình checkout. Tình huống xảy ra là: Request "Tạo đơn hàng" gọi vào v1, nhưng 800ms sau, webhook "Xác nhận thanh toán" lại gọi vào v2. Hậu quả là **Inconsistent state (trạng thái dữ liệu không nhất quán)** do sự phối hợp giữa hai phiên bản code chưa từng được test cùng nhau.