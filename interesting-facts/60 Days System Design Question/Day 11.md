Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Pod của bạn đang trong trạng thái restart, Webhook bị timeout. Stripe sẽ retry — và giờ bạn đang phải chạy đua với chính hệ thống của mình."

![[Pasted image 20260624074543.png]]

**Bối cảnh:**  
Bạn có một NestJS API chạy trên ECS (AWS), với 4 tasks nằm sau một ALB (Application Load Balancer). Stripe gửi các event `charge.succeeded` qua POST request tới endpoint `/webhooks/stripe`. Bạn có khoảng 10 giây để trả về HTTP 200 trước khi Stripe báo timeout và đưa request đó vào hàng đợi retry. Vào dịp Black Friday, bạn phải gánh khoảng 80 webhooks/giây.

**Ba kịch bản lỗi (failure modes) đang xảy ra trên production:**

1. **Pod restart trong quá trình deploy:** Webhook bị mất -> Stripe retry -> Bạn xử lý request thứ hai, nhưng pod đầu tiên cũng đã xử lý request cũ -> Gửi nhầm 2 email xác nhận thanh toán.
2. **Database bị nghẽn lúc cao điểm:** Handler xử lý mất 12 giây -> Stripe timeout -> Stripe retry -> Bây giờ bạn đang xử lý cùng một event hai lần trong khi request đầu tiên vẫn chưa kết thúc (Race condition).
3. **Stripe gửi `charge.succeeded` và `charge.refunded` cách nhau 200ms:**Hàng đợi (queue) đẩy message sai thứ tự -> Hệ thống đánh dấu đơn hàng là "đã thanh toán" SAU KHI nó đã được hoàn tiền.

Handler hiện tại chỉ là một function 30 dòng, hoạt động ổn 99% thời gian. Nhưng 1% lỗi còn lại đang "giết chết" hệ thống của bạn.

**Bạn làm gì?**

- **A) Idempotency Key + Dedup table:** Lưu lại `event ID` khi nhận được, kiểm tra nếu đã tồn tại thì bỏ qua.
- **B) Retry với Exponential Backoff + Dead-letter Queue:** Đảm bảo không mất webhook, xử lý theo cơ chế _at-least-once_.
- **C) Verify signature, trả về 200 ngay lập tức, đẩy vào Internal Queue:**Tách biệt (decouple) việc tiếp nhận (ingestion) và việc xử lý (processing).
- **D) Sequence numbers + Reorder buffer:** Giữ các event lại cho đến khi event trước đó hoàn tất, đảm bảo xử lý theo đúng trình tự (strict order).

Đây là 4 pattern mà các Senior Engineer thường tranh luận trong các buổi Design Review. Nhưng chỉ có **một** giải pháp thực sự giải quyết triệt để vấn đề trên.

**Hãy chọn một — A, B, C, hoặc D — và giải thích lý do.**

Nếu team của bạn từng triển khai webhook handler trong trạng thái "cầu nguyện", hãy gửi bài này cho họ. Cuộc thảo luận này còn giá trị hơn cả bài đăng.


**Đáp án: C — Xác thực chữ ký (Verify signature), trả về mã 200 ngay lập tức, sau đó đẩy sự kiện vào một hàng đợi nội bộ (internal queue). ✅**

![[Pasted image 20260623171836.png]]

Dưới đây là lý do tại sao cách làm này hiệu quả và tại sao các phương án còn lại dễ khiến các kỹ sư "sập bẫy":

1. **Tại sao phương án C thắng thế? (Kết hợp xử lý đồng bộ khi nhận và bất đồng bộ khi thực thi):**

Vấn đề cốt lõi ở đây là: **Clock (thời gian xử lý)** của Stripe và của Webhook Handler phía bạn không đồng bộ với nhau. Stripe chỉ cho bạn khoảng 10 giây để gửi tín hiệu ACK (Acknowledgement). Các tác vụ như ghi Database, kiểm tra gian lận (fraud check), hay gửi email... tất cả đều **không bao giờ** được phép nằm trong khoảng thời gian 10 giây đó.

**Design Pattern được khuyên dùng:**
1. **Xác thực HMAC signature:** Phải cực nhanh, dưới 5ms.
2. **Persistence:** Đẩy raw payload vào một Message Queue như **SQS, Kafka hoặc Redis Streams**.
3. **ACK:** Trả về HTTP 200 ngay lập tức.

**Tại sao cách này tối ưu?**
* **Tách biệt luồng xử lý:** Webhook endpoint của bạn giờ đây chỉ phụ thuộc vào độ trễ của mạng và tốc độ xác thực chữ ký, hoàn toàn không bị ảnh hưởng bởi hiệu năng của các hạ tầng phía sau (downstream services).
* **Đảm bảo tính toàn vẹn dữ liệu (Durability):** Nếu Pod bị restart giữa chừng khi đang xử lý, không vấn đề gì cả! Message đã được lưu trữ an toàn trong Queue, một worker khác sẽ tự động lấy ra và xử lý tiếp.
* **Chống chịu quá tải:** Database đang bị "lag"? Không sao cả, Webhook endpoint vẫn phản hồi 200 chỉ trong 8ms, đảm bảo phía đối tác (Stripe) không bị timeout và không gửi lại (retry) webhook liên tục.

Đây chính là mô hình chuẩn mà tài liệu kỹ thuật của các nền tảng lớn như Stripe, Shopify và GitHub đều yêu cầu bạn thực hiện.

