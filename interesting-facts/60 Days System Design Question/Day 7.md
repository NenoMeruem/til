Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Bài toán: Khi Event-Driven Architecture gặp lỗi "Out-of-order"

![[Pasted image 20260623145334.png]]

Service đặt hàng của bạn publish 3 events cho mỗi order: `created`, `paid`, `cancelled`.

Hệ thống đang dùng **Standard SQS queue**, 5 consumers, đạt peak ~2K orders/phút.

Đêm qua, môi trường Production báo lỗi: 47 đơn hàng bị kẹt ở trạng thái "cancelled" mà không có record "created". Khách hàng được refund cho những đơn hàng... chưa từng được ghi nhận là đã đặt thành công. Team Tài chính đang rất không hài lòng.

Bạn bắt tay vào debug. Hóa ra đơn hàng đó được tạo, thanh toán và hủy chỉ trong vòng 400ms. Ba message cùng đổ vào SQS. Ba consumer lấy chúng ra xử lý song song. Event `cancelled` lại được xử lý trước. **State machine** từ chối `created` vì cho rằng đây là trạng thái không hợp lệ. Dữ liệu bị vỡ (inconsistent).

**Cấu trúc hệ thống:**
`OrderService` → `SQS (Standard)` → 5 workers → `Postgres`

**Luồng sự kiện:** `order.created` → `order.paid` → `order.cancelled`

**Vấn đề:** Các workers xử lý song song, SQS Standard không đảm bảo thứ tự (ordering), dẫn đến việc state machine ở phía hạ nguồn (downstream) bị lỗi khi các event đến sai trình tự.

Bạn có thời hạn đến thứ Hai. Bạn sẽ làm gì?

*   **A)** Chuyển sang **SQS FIFO** + dùng `MessageGroupId` là `order_id` — để AWS lo việc đảm bảo thứ tự cho từng order.
*   **B)** Giữ SQS Standard, thêm **sequence number** + **reorder buffer** ở phía consumer — tạm giữ các event đến sớm/sai thứ tự cho đến khi event tiền nhiệm đến nơi.
*   **C)** Thay thế event stream bằng mô hình **Saga** — mỗi bước phải chờ tín hiệu hoàn thành của bước trước đó mới được kích hoạt bước tiếp theo.
*   **D)** Thêm **version/timestamp** vào event và thiết kế lại state machine theo kiểu **idempotent** + **order-agnostic** — từ chối các transition cũ (stale), chấp nhận xử lý bất kể thứ tự arrival.

Cả 4 phương án trên đều là những pattern tôi từng thấy trong các hệ thống production thực tế. Nhưng chỉ có một phương án thực sự giải quyết triệt để vấn đề này. Một trong số đó là "cái bẫy" mà các Senior Engineer thường mắc phải khi thảo luận trên bảng trắng.

**Bạn chọn đáp án nào? A, B, C hay D?** Hãy cho biết lý do.

Nếu team của bạn từng tranh cãi nảy lửa về "ordering guarantees" lúc 2 giờ sáng, hãy gửi bài này cho họ. Những cuộc tranh luận đó chính là nơi những bài học thực chiến được đúc kết.


1. **✅ Đáp án: A — SQS FIFO kết hợp với `MessageGroupId` theo `order_id`.**

![[Pasted image 20260623145751.png]]

**Tại sao phương án A tối ưu?**

*   **Xử lý theo ngữ cảnh (Per-order ordering):** Bạn không cần thiết phải áp đặt thứ tự xử lý trên toàn hệ thống (global ordering), mà chỉ cần đảm bảo tính tuần tự theo từng đơn hàng cụ thể. Việc thiết lập `MessageGroupId = order_id` sẽ giải quyết bài toán này.
*   **Cơ chế của FIFO:** SQS FIFO đảm bảo rằng các message có cùng `MessageGroupId` sẽ luôn được gửi đến consumer theo đúng trình tự (in exact send order). Đồng thời, nó đảm bảo tại một thời điểm, chỉ một consumer được phép xử lý group đó, giúp tránh race condition.
*   **Thông lượng (Throughput) được duy trì:** Với lưu lượng 2.000 đơn hàng/phút, hệ thống vẫn sẽ dàn trải tải (fan-out) trên 5 workers. Do các `order_id` khác nhau sẽ rơi vào các group khác nhau, nên việc xử lý song song vẫn diễn ra bình thường mà không bị bottleneck.
*   **Tính nhất quán dữ liệu:** Chuỗi trạng thái `created` → `paid` → `cancelled` của cùng một mã đơn hàng (ví dụ: #12345) chắc chắn sẽ được xử lý tuần tự.
*   **Chi phí:** Đánh đổi bằng một độ trễ (latency) cực nhỏ (vài ms). Mọi thứ đã sẵn sàng để deploy vào thứ Hai tới.


2. **Tại sao B (Reorder Buffer - Bộ đệm sắp xếp lại) là một cái bẫy:**
Đây là phương án thường đánh lừa các kỹ sư Senior khi thiết kế trên whiteboard. Nếu chọn cách này, bạn sẽ phải tự build: *in-memory buffer* cho từng `order_id` + logic *TTL (Time-to-Live)* + *dead-letter queue* để xử lý các khoảng trống (gaps) + cơ chế *crash recovery* + hệ thống *monitoring* để phát hiện các buffer bị kẹt.

Kết quả là bạn đang tự build lại một cơ chế **FIFO (First-In-First-Out)** thủ công ngay trong tầng *application*. Hệ thống sẽ chứa đầy bug, và bạn phải chịu trách nhiệm cho mọi *edge case*. Phương án B chỉ hợp lệ khi bạn **bắt buộc** không thể sử dụng FIFO (ví dụ: Kafka bị *bottleneck* do *partition key* bị chiếm dụng). Nhưng trường hợp này không phải như vậy.

3. **Tại sao C (Saga Pattern) là sai:**
*Saga pattern* được thiết kế cho các giao dịch phân tán (distributed transactions) kéo dài, cần các hành động bù trừ (compensating actions) – ví dụ: đặt vé máy bay → trừ tiền thẻ → đặt phòng khách sạn.

Vấn đề của bạn là xử lý một **stream trạng thái cho một thực thể (entity)**, chứ không phải giao dịch đa dịch vụ. Việc cố tình áp dụng Saga sẽ biến các *async events* thành các *sync RPC*, làm tăng độ phụ thuộc (*coupling*) giữa các service, mà quan trọng nhất là: nó vẫn không giải quyết được bài toán thứ tự (*ordering*).

4. **Tại sao D (Event Versioning) là sai:**
Cách này chỉ hoạt động một phần, nhưng bạn sẽ gặp rủi ro **loại bỏ (drop) các event hợp lệ**. Hãy tưởng tượng event "cancelled" đến trước, đẩy trạng thái về "đã hủy", sau đó event "created" đến sau lại bị từ chối do xung đột version. Kết quả là DB sẽ có một đơn hàng ở trạng thái "cancelled" nhưng lại không có record "created" nào cả.

Để phương án D hoạt động chính xác, bạn cần triển khai toàn bộ hệ thống theo hướng **Event Sourcing** – đây là một dự án refactor kéo dài 6 tháng, chứ không phải là một task sửa lỗi nhanh trong ngày thứ Hai.

### **Lời khuyên thêm:**
Nếu bạn đang đối mặt với bài toán đảm bảo thứ tự sự kiện, thay vì dùng các cách tiếp cận phức tạp trên, hãy cân nhắc:
1. **Dựa vào hạ tầng:** Sử dụng đúng *partition key* trong Kafka/Message Queue để đảm bảo thứ tự cho từng `order_id`.
2. **Optimistic Locking:** Sử dụng version trong DB để xử lý các xung đột thay vì quản lý luồng sự kiện ở tầng ứng dụng.
3. **Idempotency:** Đảm bảo mọi consumer đều có tính lũy đẳng để khi event đến sai thứ tự hoặc lặp lại, hệ thống vẫn giữ được trạng thái nhất quán.