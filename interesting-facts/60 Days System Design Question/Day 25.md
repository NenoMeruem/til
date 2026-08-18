
Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your order processing service runs on SQS.


![[Pasted image 20260817141118.png]]



Dịch vụ xử lý đơn hàng (order processing service) của bạn đang chạy trên nền tảng **SQS** (Simple Queue Service).

* **Tải thông thường (Normal load):** 200 đơn hàng/phút. Các **consumer** (tiêu thụ message) xử lý mượt mà, không gặp vấn đề gì.
* **Sự cố:** Ngày Black Friday ập đến. Các **producer** (tạo message) bắt đầu bắn 4.000 đơn hàng/phút lên hệ thống. **Queue depth** (độ sâu của hàng đợi) tăng vọt lên tới 80.000 message chỉ trong vòng 20 phút. **Downstream Database** (Cơ sở dữ liệu hạ nguồn) của bạn đang chạm ngưỡng 95% CPU. Các **consumer** đang bị quá tải (falling behind) và bạn đang bất lực nhìn **queue backlog** lớn dần lên theo thời gian thực.

Bạn cần xử lý tình trạng **backpressure** (áp lực ngược từ hệ thống phía sau) này như thế nào?

* **A) Scale out (mở rộng quy mô theo chiều ngang) cho consumer** — tăng thêm số lượng **Lambda function** hoặc **EC2 worker** để "ngấu nghiến" lượng **backlog** (tồn đọng) nhanh hơn.
* **B) Cấu hình visibility timeout** (thời gian ẩn message) và **route** (định tuyến) các message thất bại sang **Dead-Letter Queue (DLQ)** để phòng thủ trước các **poison pill** (message lỗi gây crash hệ thống).
* **C) Rate-limit (giới hạn tốc độ) producer ngay tại nguồn** — áp dụng thuật toán **token bucket** hoặc **sliding window** (cửa sổ trượt) để chặn trần tốc độ đẩy message vào hàng đợi.
* **D) Chuyển sang SQS delay queues** — trì hoãn thời gian hiển thị message nhằm giãn cách tần suất phân phối và giảm áp lực cho consumer.

Có 3 trong số các phương án trên là **design pattern** (mẫu thiết kế) thực tế mà các kỹ sư thường dùng. Nhưng **chỉ có duy nhất một phương án thực sự giải quyết được bài toán backpressure**.

Hãy chọn một đáp án — **A, B, C, hoặc D** — và giải thích tại sao. Phân tích chi tiết sẽ có ở phần bình luận.

Nếu bài viết này khiến bạn phải suy nghĩ lại về trực giác kiến trúc của mình, hãy chia sẻ nó — rất có thể ai đó trong team của bạn đang thiết kế bài toán này ngay lúc này đấy.


**Vì sao C (Cơ chế này) thắng thế, và vì sao nó không làm hỏng UX**

![[Pasted image 20260817141524.png]]


Hàng đợi (queue) ngày càng phình to vì bên producer (tiến trình sản xuất message) đang áp đảo bên consumer (tiến trình tiêu thụ). 4.000 bản ghi được đẩy vào, nhưng chỉ có 200 bản ghi được xử lý xong. Bạn có scale (mở rộng) bao nhiêu consumer đi chăng nữa thì khoảng cách đó cũng không thể tự thu hẹp lại được, nhất là khi database (DB) đã ngốn tới 95% CPU.

Cách giải quyết nằm ở đầu nguồn (upstream). Hãy áp dụng rate-limiting (giới hạn tốc độ) đối với producer bằng thuật toán **token bucket** hoặc **sliding window**. Trên AWS, bạn có thể dùng API Gateway usage plans, Lambda reserved concurrency, hoặc viết middleware throttle trực tiếp bên trong service. Lúc này, độ sâu của hàng đợi (queue depth) sẽ ổn định trở lại, các consumer bắt kịp tiến độ một cách tự nhiên, và DB sẽ hạ nhiệt.

Tư duy cốt lõi ở đây là: **hãy vặn nhỏ vòi nước lại, đừng chỉ lo đi khoét rộng thêm lỗ thoát nước.** ( Slow the tap, don’t just widen the drain )

Và bây giờ là phần mà biểu đồ kiến trúc thường lờ đi: “producer” không phải là người dùng của bạn.

Trong hầu hết các hệ thống thực tế, luồng xử lý đơn hàng (order flow) được **decouple** (tách rời). Người dùng bấm đặt hàng, dữ liệu được ghi vào DB, và họ nhận ngay phản hồi thành công (success response). Một tiến trình xử lý độc lập khác sẽ đọc các sự kiện đó (thông qua **polling** hoặc **CDC - Change Data Capture**) rồi đẩy chúng vào queue. Chính cái tiến trình phát sự kiện (emitter) đó mới là producer mà bạn cần throttle.

Do đó, việc áp dụng rate-limiting hoàn toàn không chạm gì đến luồng thanh toán (checkout). Người dùng đã nhận được **ack** (phản hồi xác nhận) từ thao tác write trước đó rồi. Bạn chỉ đang chặn tốc độ các event đổ vào queue, chứ không chặn tốc độ đặt hàng của người dùng. Trải nghiệm người dùng (UX) vẫn vẹn nguyên; chỉ là queue không còn chạy nhanh hơn tốc độ xử lý của consumer nữa.

Đó mới thực chất là **backpressure** (áp lực ngược): hệ thống ở hạ nguồn (downstream) báo hiệu cho thượng nguồn (upstream) giảm tốc độ lại. Độ sâu của queue chính là tín hiệu đó, và bạn cần phản ứng lại nó ngay từ đầu nguồn.

**Tại sao đáp án A là một "cái bẫy" (Scale số lượng consumer - tăng worker):**

Đây là phản xạ tự nhiên nhất của lập trình viên, và nó đủ sức đánh lừa cả những Senior Engineer.

Đúng là có thêm nhiều consumer thì **throughput (lưu lượng xử lý)** sẽ tăng. Nhưng bạn đang nhầm lẫn giữa **rate mismatch (lệch tốc độ sản xuất/tiêu thụ)** với **capacity problem (vấn đề về dung lượng/tài nguyên)**. Nếu producer (bên gửi) luôn generate (sinh) dữ liệu nhanh hơn tốc độ mà consumer (bên nhận) có thể process (xử lý) — và trong các dịp cao điểm như Black Friday, chuyện này chắc chắn xảy ra — thì bạn đang tham gia một cuộc đua vũ trang mà bạn cầm chắc phần thua. Bạn scale-out lên gấp 10 lần số lượng Lambda function, để rồi chạm trán giới hạn write throughput của DynamoDB, làm cạn kiệt (hammer) connection pool của RDS, trong khi hàng đợi (queue) vẫn cứ dài ra. Chỉ là chậm hơn một chút, và giờ thì hóa đơn hạ tầng (infra bill) của bạn đã nhân đôi.

Việc scale consumer chỉ phát huy tác dụng khi nút thắt cổ chai (bottleneck) nằm ở tài nguyên tính toán (compute). Nó vô tác dụng khi gốc rễ vấn đề là tốc độ của producer vượt quá tầm kiểm soát (unbounded producer rate).

**Tại sao đáp án B sai (Visibility timeout + DLQ - Dead Letter Queue):**

Đây là cơ chế xử lý lỗi (failure handling), chứ không phải **backpressure (áp lực ngược / cơ chế kìm hãm)**.

DLQ dùng để gom các **poison pill** — những message bị lỗi xử lý liên tục và nếu không chặn lại, chúng sẽ lặp vô hạn. Còn **Visibility timeout** quyết định thời gian một message bị ẩn đi sau khi được một consumer lấy xử lý (nhằm tránh việc bị double-processing / xử lý trùng lặp). Không cái nào trong số này có chuyện làm chậm producer lại hay ngăn queue depth (độ dài hàng đợi) tăng lên cả.

Nhầm lẫn giữa cơ chế **backpressure** với **retry/error handling (xử lý lỗi/thử lại)** là một trong những lỗi kiến trúc phổ biến nhất mà tôi từng thấy. Chúng giải quyết hai bài toán hoàn toàn khác nhau.

**Tại sao đáp án D là sai (SQS delay queues):**

Delay queue chỉ trì hoãn thời gian **hiển thị (visibility)** của message chứ không chặn được việc **tạo ra (creation)** message. Producer của bạn vẫn cứ đẩy đều 4.000 msg/phút vào hệ thống. Các message này chất đống ở trạng thái "tàng hình", rồi đột ngột xuất hiện ồ ạt (in bursts) khi hết thời gian delay. Bạn chẳng hề giảm tải được áp lực ngược (backpressure) nào cả — bạn chỉ hoãn nó lại và làm cho biểu đồ tải (delivery pattern) trở nên giật cục, gai góc hơn mà thôi.

Cố dùng cách này chẳng khác nào lấy nắp đậy cái bồn rửa đang bị tràn nước rồi tự lừa mình là đã khắc phục xong. Nước ở bên dưới vẫn đang dâng lên...