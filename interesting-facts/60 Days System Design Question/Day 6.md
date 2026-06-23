Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Khi Distributed Locking (Khóa phân tán) phản chủ: Bạn đang chọn phương án nào?


![[Pasted image 20260623145226.png]]


Hệ thống Job Scheduler của bạn đang chạy trên 3 instances nằm sau một ALB (Application Load Balancer). Cứ mỗi 5 phút, một tiến trình Cron lại kích hoạt job "generate-daily-report". Vấn đề là cả 3 instances đều cố gắng tranh giành để thực thi job này cùng lúc.

Giải pháp kinh điển bạn nghĩ đến ngay: **Redis SETNX**.
`SET job:daily-report locked NX EX 300` → Chỉ một instance giành được quyền thực thi. Xong!

Mọi thứ chạy ổn định trong một tháng. Cho đến 2 giờ sáng thứ Bảy...

**Sự cố xảy ra:**
1. Instance B giành được lock và bắt đầu xử lý job.
2. 60 giây sau, Pod bị **OOM-killed** (hết RAM). Nhưng Lock vẫn nằm đó trên Redis với TTL (Time-To-Live) là 300 giây.
3. Job được lập lịch 5 phút/lần. Trong 4 phút tới, không có gì xảy ra cả.
4. Sau khi Instance B khởi động lại (restart), Instance A cũng bắt đầu chạy job. Kết quả: Cả hai instance cùng thực hiện xử lý công việc.

**Tồi tệ hơn:** Instance A gặp tình trạng **GC (Garbage Collection) pause** quá lâu, khiến lock hết hạn (TTL) trong khi nó vẫn đang xử lý. Redis âm thầm cấp lock cho Instance C. Giờ đây, cả A và C đều "tự cho rằng" mình đang sở hữu lock. Cả hai cùng ghi dữ liệu vào database, gây ra xung đột nghiêm trọng.

**Đâu là Pattern (mẫu thiết kế) đúng để xử lý vấn đề này?**

*   **A) Redis SETNX + TTL ngắn + Fencing Token:** Dùng một "token" tăng dần theo thời gian. Resource ở hạ tầng phía sau (database/storage) sẽ kiểm tra token này trước mỗi thao tác ghi (write).
*   **B) Redlock:** Thực hiện acquire lock trên 5 Redis nodes độc lập, yêu cầu đa số (majority) chấp thuận mới được cấp quyền.
*   **C) DB-based Pessimistic Lock:** Sử dụng `SELECT … FOR UPDATE` trên bảng jobs; transaction sẽ giữ lock cho đến khi hoàn tất.
*   **D) Optimistic Concurrency:** Không cần lock. Mỗi instance cố gắng insert kết quả với một unique key; nếu trùng, DB sẽ tự động từ chối (reject).

Cả 4 phương án trên đều là những cách tiếp cận thực tế. Tuy nhiên, chỉ một trong số đó thực sự "sống sót" trước các kịch bản lỗi nêu trên. Đáng chú ý, có một phương án từng bị Martin Kleppmann (tác giả cuốn "Designing Data-Intensive Applications") công khai chỉ trích gay gắt trong một bài phân tích nổi tiếng từ 8 năm trước.

**Bạn chọn phương án nào? Hãy cùng thảo luận!**

1. **Tại sao phương pháp (SETNX + TTL + Fencing Token) lại giành chiến thắng?**
![[Pasted image 20260623145204.png]]

Trong hệ thống phân tán, việc chỉ sử dụng một **Distributed Lock (khóa phân tán)** là không đủ để bảo vệ tài nguyên. Bạn luôn phải giả định rằng instance đang giữ khóa có thể đã bị "chết" (crash), bị treo (paused) hoặc mất kết nối mạng (network partition). Hệ quả là: khóa có thể bị cấp lại (reassign) cho một tiến trình khác trong khi chủ sở hữu cũ vẫn lầm tưởng rằng mình đang nắm giữ quyền truy cập. Đây chính là kịch bản "thảm họa": **GC (Garbage Collection) pause** xảy ra, **TTL (Time-to-live)** của khóa hết hạn, Redis cấp khóa cho một instance khác, và instance cũ "tỉnh dậy" rồi tiếp tục thực hiện lệnh ghi dữ liệu như bình thường.

**Fencing token (token rào chắn)** chính là giải pháp triệt để cho vấn đề này:
1. **Cơ chế cấp phát:** Mỗi khi một instance request được khóa, Redis (hoặc Lock Service) sẽ cấp một số thứ tự tăng dần (monotonically increasing) – ví dụ: 42, 43, 44... Số này đóng vai trò là một **fencing token**.
2. **Cơ chế kiểm soát:** Tài nguyên hạ nguồn (như Database, hệ thống lưu trữ, hoặc Message Queue) sẽ lưu lại giá trị token cao nhất mà nó từng ghi nhận. Bất kỳ lệnh ghi nào chứa token nhỏ hơn giá trị này đều sẽ bị từ chối.

**Kết quả:** Khi instance A "tỉnh dậy" sau quãng thời gian bị **GC pause** với token 42, lúc này instance C đã thực hiện ghi dữ liệu với token 43. Khi A gửi lệnh ghi tới Database, Database sẽ từ chối vì 42 < 43. Lúc này, **tài nguyên (Database) mới là nguồn sự thật duy nhất (source of truth)**, thay vì phụ thuộc hoàn toàn vào dịch vụ khóa.

Đây chính là cơ chế mà **Google Chubby** đang áp dụng. Đây cũng là phương pháp được **Martin Kleppmann** đề xuất trong tài liệu *"How to do distributed locking"*. Đây là pattern duy nhất trong danh sách này thực sự an toàn trước các rủi ro liên quan đến hiện tượng dừng tiến trình (process pauses).


2. **Tại sao B là "bẫy" (Redlock):**

Redlock là mô hình (pattern) mà hầu hết các Senior Engineer đều nghĩ tới đầu tiên vì nó trông có vẻ rất chặt chẽ. Tuy nhiên, Martin Kleppmann đã có một bài viết nổi tiếng (từ năm 2016) chứng minh rằng **Redlock không an toàn** trong các kịch bản thực tế: bất kỳ process nào cũng có thể bị "pause" (do GC pause hoặc context switch) đủ lâu để mất lock mà không hề hay biết.

Quan trọng hơn, nếu thiếu **fencing token** (token rào chắn), Redlock cũng mắc phải lỗ hổng cơ bản giống hệt như lệnh `SETNX`. Nếu tài nguyên (resource) của bạn không thể xác thực token khi ghi dữ liệu, thì Redlock hoàn toàn vô dụng. Bạn đang lãng phí công sức vận hành tới 5 Redis cluster cho một vấn đề mà lẽ ra chỉ cần dùng 1 fencing token là giải quyết xong.

3.  **Tại sao C sai (DB Pessimistic Lock):**

Dùng `SELECT … FOR UPDATE` trong một transaction có hiệu quả — nhưng chỉ với các **critical section** (đoạn mã tới hạn) cực ngắn. Lock này sẽ tự giải phóng khi transaction kết thúc hoặc khi connection bị ngắt.

Vấn đề nằm ở chỗ lock này bị "giam" trong phạm vi của một database transaction. Nếu job của bạn là "tạo báo cáo hàng ngày" mất 60 giây để ghi dữ liệu xuống S3 và gọi API ngoại vi, bạn đang giữ một **row lock** trên DB chính suốt 60 giây đó. Kết quả là **connection pool bị cạn kiệt**, tất cả các câu query khác sẽ bị block và xếp hàng chờ đợi, gây nghẽn toàn bộ hệ thống.

4. **Tại sao D không phù hợp trong trường hợp này (Optimistic Concurrency):**

**Optimistic concurrency** (xử lý đồng thời lạc quan) rất tuyệt vời khi nó phù hợp — bạn không cần dịch vụ quản lý lock, không cần người giữ lock và không bao giờ lo về vấn đề **stale-lock** (lock bị treo). Các instance cứ thoải mái thực hiện thao tác, và **unique constraint** của DB sẽ loại bỏ các "kẻ thua cuộc".

Tuy nhiên, nó sẽ thất bại nếu tác vụ của bạn **không có tính idempotent** (không có tính lũy đẳng) hoặc không phải là một lệnh ghi đơn lẻ. Ví dụ: nếu có 3 instance cùng chạy đua, bạn sẽ vô tình thực hiện: 3 lần ghi S3, 3 lần bắn thông báo lên Slack, và tốn kém gấp 3 lần chi phí tài nguyên tính toán (compute cost).