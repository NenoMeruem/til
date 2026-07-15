
Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your Kafka consumer is processing 800 events/sec.

![[Pasted image 20260708165407.png]]



Consumer Kafka của bạn đang xử lý 800 events/giây.

Nhưng Producer vừa đẩy tốc độ lên 5.000 events/giây và chưa có dấu hiệu dừng lại.

Biểu đồ **Consumer Lag** đang báo chậm 12 phút và vẫn tiếp tục tăng. **Memory** của Consumer đang ở mức 89% và tăng dần. Alert hệ thống vừa kích hoạt. Bạn chỉ còn khoảng 4 phút trước khi **JVM** rơi vào trạng thái **GC-thrashing** (Garbage Collection liên tục) và **Pod** bị **OOM-killed** (Out of Memory).

**Kiến trúc hệ thống:**
*   Producer → Kafka Topic (5K events/giây, đang tăng).
*   Consumer → `spring-kafka` với `@KafkaListener`, `batch=500`, xử lý được ~800 events/giây.
*   Downstream → Ghi vào Postgres + gọi HTTP bên ngoài (đây chính là **bottleneck** - điểm nghẽn).
*   **SLA**: Phải xử lý hết event, không được bỏ sót (no dropping).

Consumer không theo kịp tốc độ, còn Producer thì không hề biết điều đó. Bạn sẽ làm gì?

**A) Bỏ qua event (Drop events):** Thất bại nhanh (fail fast), phản hồi sớm, để Consumer từ từ giải quyết lượng Lag tồn đọng. Hệ thống vẫn "sống".

**B) Chặn Producer (Backpressure):** Yêu cầu Producer "chạy chậm lại", áp dụng cơ chế **backpressure** ngược lên thượng nguồn cho đến khi Consumer bắt kịp.

**C) Tăng bộ đệm (Buffer harder):** Tăng kích thước hàng đợi trong bộ nhớ, tăng **batch size**, scale-up Consumer để hấp thụ lượng spike (tăng đột biến).

**D) Giới hạn tốc độ + Phân loại tải (Rate-limit + load-shed):** Giới hạn tốc độ tiêu thụ, chuyển hướng phần tràn (overflow) sang **DLQ** (Dead Letter Queue) hoặc một Topic phụ để xử lý lại sau.

Ba trong số bốn phương án trên là các mô hình thực tế trong Production. Tuy nhiên, chỉ có duy nhất một phương án phù hợp với "stack" công nghệ này và SLA đã nêu.

Bạn chọn phương án nào (A, B, C, hay D) và tại sao? Tôi sẽ giải thích chi tiết ở phần bình luận (bao gồm cả việc tại sao hai trong số các phương án sai lại dễ dàng đánh lừa cả những kỹ sư đã có kinh nghiệm làm việc với Kafka).

Nếu team của bạn thường tranh luận về **backpressure** trong các buổi stand-up, hãy share bài viết này cho họ. Đáp án đúng phụ thuộc vào nền tảng (platform-specific) và hầu hết các bài viết khác đều giải thích sai.

Hãy đưa ra lựa chọn của bạn 👇

Để dịch đoạn này sang tiếng Việt một cách chuyên nghiệp và sát với thuật ngữ ngành, chúng ta có thể chuyển ngữ như sau:


### Tại sao giải pháp D lại giành chiến thắng?
![[Pasted image 20260708170219.png]]

Thỏa thuận mức dịch vụ (SLA) yêu cầu các sự kiện (events) phải được xử lý — không được làm mất (dropped) cũng không được gây tắc nghẽn (blocked). Yêu cầu này loại bỏ ngay lập tức phương án A và B.

Chiến lược ở đây là: Giới hạn lưu lượng đầu vào (intake) của consumer ở mức ~1K sự kiện/giây với một khoảng dự phòng (headroom), đồng thời điều hướng phần quá tải (overflow) sang một **durable secondary topic** (ví dụ: `events.overflow`). Tại đây, một **consumer group** riêng biệt sẽ xử lý phần dữ liệu này vào khung giờ thấp điểm.

Với cách tiếp cận này:
* **Producer** vẫn duy trì tốc độ ghi dữ liệu bình thường.
* **Primary consumer** giữ được "nhịp tim" (heartbeat) ổn định.
* Dữ liệu quá tải sẽ được xử lý bất đồng bộ sau đó.

Đây chính là kỹ thuật **graceful degradation** (suy giảm chức năng có kiểm soát) để đảm bảo hệ thống vẫn vận hành ổn định khi gặp tải đột biến. Các "ông lớn" như Stripe hay Shopify đều đã chia sẻ về việc áp dụng kiến trúc này trong các bài blog kỹ thuật của họ.

### Tại sao đáp án B là một "cái bẫy":

Đây là lỗi kinh điển mà ngay cả các Senior Engineer cũng thường mắc phải. Cơ chế **Backpressure (áp lực ngược)** hoạt động theo kiểu chặn luồng (blocking) rất hiệu quả trong Reactor, RxJava hay Akka vì các framework này có giao thức (protocol) truyền tải tín hiệu ngược. 

Tuy nhiên, Kafka hoạt động theo mô hình **pull-based (kéo dữ liệu)** và có tính **decoupled (phi tập trung/tách rời)**. Producer hoàn toàn không biết đến sự tồn tại của Consumer. Không hề có tín hiệu backpressure nào ở tầng socket được truyền ngược lên phía trên (upstream). Các kỹ sư quen làm việc với gRPC streaming hoặc RxJava thường chọn đáp án B vì họ áp dụng tư duy "lối mòn" từ các hệ thống cũ. Trong một hệ thống dựa trên log, có broker và tách rời như Kafka, cơ chế này không áp dụng được.

### Tại sao đáp án A sai:

Đáp án này dẫn đến việc **drop events (mất dữ liệu)**. Trong khi SLA (Thỏa thuận mức dịch vụ) yêu cầu khắt khe: “dữ liệu bắt buộc phải được xử lý, không được phép âm thầm hủy bỏ”. Với yêu cầu đó, phương án này bị loại ngay lập tức.

### Tại sao đáp án C sai:

**Buffering (đệm dữ liệu)** chỉ là giải pháp trì hoãn. Một bộ đệm lớn có thể "nuốt" được các đợt spike (tăng đột biến) trong 30 giây, nhưng không thể giải quyết bài toán throughput lâu dài khi tốc độ input là 5.000 event/giây trong khi consumer chỉ xử lý được 800 event/giây. 

Hãy làm bài toán đơn giản: mỗi giây bạn đang nợ (lag) 4.200 events. Một bộ đệm chứa được 1 triệu events cũng chỉ giúp bạn cầm cự thêm khoảng 4 phút. Sau đó, bạn vẫn rơi vào tình trạng quá tải ban đầu, nhưng lúc này hệ thống còn đối mặt thêm với nguy cơ **OOM (Out of Memory - cạn kiệt bộ nhớ)**. 

Hơn nữa, **bottleneck (nút thắt cổ chai)** thực sự nằm ở lệnh gọi HTTP ra bên ngoài. Việc scaling (mở rộng) số lượng consumer lên gấp 5 lần cũng vô nghĩa nếu hệ thống hạ nguồn (downstream) áp đặt cơ chế **rate-limit** ngay tại request thứ 51.
