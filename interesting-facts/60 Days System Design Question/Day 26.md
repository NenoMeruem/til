
Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your cache and DB are out of sync. Again.


![[Pasted image 20260817141836.png]]



**Cache và DB của bạn lại lệch dữ liệu rồi. Lại thế nữa.**

Một user cập nhật trang cá nhân. Cache vẫn trả về cái tên cũ trong suốt 10 phút tiếp theo. Bộ phận Support nhận được ticket phàn nàn. Bạn xử lý nhanh bằng cách xóa cache thủ công (`cache flush`). Tuần sau, chuyện đó lặp lại.

Sếp yêu cầu bạn phải giải quyết dứt điểm bài toán **tính nhất quán khi ghi dữ liệu (write consistency)** trước khi nó trở thành một sự cố ảnh hưởng trực tiếp đến khách hàng.

**Ngữ cảnh hiện tại của hệ thống:**
*   Stack: **NestJS API → PostgreSQL (Source of truth - Nguồn sự thật duy nhất) + Redis (Cache)**
*   Traffic giờ cao điểm: **~600 request đọc/giây, ~80 request ghi/giây**
*   Design pattern hiện tại: Ghi vào DB, sau đó xóa cache thủ công (`invalidate cache key`) khi ghi thành công.
*   Thống kê: 3 sự cố trong tháng này — tất cả đều bắt nguồn từ **stale cache (cache cũ)** sau khi ghi dữ liệu.

Bạn cần một chiến lược có khả năng sống sót trước **race condition (tình trạng tranh chấp dữ liệu)**, cơ chế **retry (thử lại)** và **partial failure (lỗi một phần)**.

**Bạn sẽ thay đổi gì?**

*   **A) Write-through** — Ghi đồng thời vào cache và DB một cách đồng bộ (synchronously). Cache luôn warm (có sẵn dữ liệu) và luôn consistent (nhất quán).
*   **B) Write-behind (Write-back)** — Ghi vào cache trước, sau đó bất đồng bộ (async) đẩy xuống DB sau. Tốc độ ghi cực nhanh, nhưng tính bền vững dữ liệu là eventual consistency (nhất quán cuối cùng).
*   **C) Write-around** — Bỏ qua hoàn toàn cache khi ghi. Chỉ ghi trực tiếp vào DB. Cache sẽ được lấp đầy ở lần đọc tiếp theo nếu xảy ra cache miss.
*   **D) Dual-write kết hợp Outbox Pattern** — Ghi vào DB + publish một event (sự kiện). Một consumer sẽ đọc event log đó để cập nhật lại cache.

Cả 4 phương án trên đều được áp dụng trong môi trường production. Nhưng chỉ có **một** phương án thực sự chịu được các dạng lỗi (failure modes) trong mô hình này.

Hãy chọn một đáp án — **A, B, C, hoặc D** — và giải thích lý do tại sao. Mình sẽ đăng bài phân tích chi tiết ở phần bình luận (bao gồm cả phương án trông có vẻ an toàn nhất nhưng sẽ "gây cháy nhà" khi hệ thống scale lớn).

Nếu team của bạn hay tranh cãi về vấn đề này trong các buổi design review, hãy chia sẻ bài viết này cho họ. Thảo luận kỹ vẫn hơn là để sự cố ép mình phải sửa.


**Đáp án: D — Dual-write (Ghi song song) kết hợp với Outbox Pattern**

![[Pasted image 20260817142100.png]]


Bản chất của bài toán không nằm ở việc *"phải ghi vào đâu trước"* — mà là *"điều gì sẽ xảy ra nếu một thao tác ghi thành công nhưng thao tác còn lại thất bại?"*

**Lý do D là lựa chọn tối ưu:** Mọi giải pháp ghi song song (dual-write) theo cách "ngây thơ" (naive) đều vướng phải một lỗi **race condition** (điều kiện tranh đua): ghi vào Database (DB) thành công, nhưng chưa kịp ghi vào Cache thì hệ thống bị **crash** (sập) $\rightarrow$ dẫn đến việc cache bị **stale** (lỗi thời/lệch pha) vĩnh viễn. 

Mô hình **Outbox** biến việc cập nhật cache thành một hệ quả tất yếu của thao tác ghi DB, chứ không phải là một thao tác độc lập đứng cạnh nhau. Tất cả nằm trong một **atomic transaction** (giao dịch nguyên tử) duy nhất tại DB: vừa lưu dữ liệu chính, vừa ghi sự kiện vào bảng outbox. Sau đó, một **consumer** (tiến trình tiêu thụ) sẽ đọc sự kiện này để cập nhật lại Redis. 

Cách làm này đồng thời cung cấp khả năng **replay** (phát lại sự kiện) — ví dụ, nếu Redis sập rồi hồi phục, hệ thống chỉ cần xử lý lại các sự kiện từ bảng outbox là mọi thứ đồng bộ trở lại.

**Lý do Mô hình A thất bại (Write-through - Ghi đồng bộ qua Cache):** Trông thì có vẻ an toàn nhất, nhưng lại nguy hiểm nhất khi hệ thống scale (mở rộng quy mô). 
* Gây ra tận 2 thao tác I/O đồng bộ (synchronous I/O) cho mỗi lần ghi (vừa ghi vào Database, vừa ghi vào Cache). 
* Nếu Redis chậm, API ghi dữ liệu của bạn cũng sẽ bị chậm theo. 
* Nếu Redis "sập", bạn sẽ xử lý thế nào? Chặn người dùng luôn à? Vô tình bạn đã biến Redis thành một **hard dependency (phụ thuộc cứng)** nằm chết cứng trên đường đi của dữ liệu ghi (write path).


**Lý do Mô hình B thất bại (Write-behind / Write-back - Ghi bất đồng bộ):** Tốc độ rất nhanh, nhưng nhược điểm là: nếu async worker ( tiến trình ngầm) bị crash trước khi kịp flush (đẩy) dữ liệu xuống Database, thì dữ liệu đó vĩnh viễn biến mất. 
* Kiểu này dùng cho bộ đếm analytics (thống kê) thì chấp nhận được. 
* Nhưng tuyệt đối **không bao giờ được dùng** cho nơi lưu trữ dữ liệu gốc (source of truth).


**Lý do Mô hình C chỉ là giải pháp chắp vá (Write-around - Ghi thẳng vào DB, bỏ qua Cache):** Khắc phục được lỗi stale cache (cache cũ/lỗi thời) bằng cách hoàn toàn không ghi dữ liệu vào cache khi tạo mới. Nghe thì sạch sẽ đấy — nhưng tính năng **read-after-write (đọc ngay sau khi ghi)** sẽ bị hỏng do độ trễ của replica (replica lag), và các workload (tác vụ) ghi với tần suất cao sẽ làm **cache hit rate (tỷ lệ cache trả về dữ liệu thành công)** rơi thảm hại.