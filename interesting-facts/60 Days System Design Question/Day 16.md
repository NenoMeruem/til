
Nodes: [[60 Days System Design Question]]
Tags: #system-design

### You’re running a multi-tenant analytics pipeline on DynamoDB



![[Pasted image 20260707155618.png]]

### Khi hệ thống "sập" vì Hot Partition trên DynamoDB

Bạn đang vận hành một **pipeline phân tích (analytics pipeline)** đa người thuê (**multi-tenant**) trên DynamoDB với 200 tenants và tổng lưu lượng đạt 12K lượt ghi mỗi giây (**writes/sec**). Mọi thứ vẫn ổn — cho đến khi nó không còn ổn nữa.

Một tenant đột ngột có thêm một khách hàng khổng lồ, khiến volume sự kiện tăng vọt gấp 100 lần. Giờ đây, riêng tenant đó đã chiếm tới 9K writes/sec trên cùng một **partition key**. 199 tenant còn lại thì vẫn "nhàn rỗi".

Lỗi **`ProvisionedThroughputExceeded`** bắt đầu xuất hiện dày đặc. **P99 write latency** (độ trễ ghi ở phân vị 99) nhảy vọt từ 8ms lên 400ms. Kỹ sư trực ca (**on-call**) nhận cảnh báo. Toàn bộ hệ thống bị **throttle** (bóp nghẹt) chỉ vì một key duy nhất.

**Cấu hình hệ thống:**
*   **Table:** `events` (DynamoDB, chế độ **on-demand capacity**)
*   **PK (Partition Key):** `tenant_id`
*   **SK (Sort Key):** `event_timestamp`
*   **Hot tenant:** ~9K WPS
*   **Các tenant khác:** ~15 WPS mỗi tenant
*   **Vấn đề:** Một **partition key** đơn lẻ đang gánh toàn bộ 9K lượt ghi — và nó đã đụng trần giới hạn throughput trên mỗi partition của DynamoDB.

Đây là kịch bản kinh điển của lỗi **Hot Partition**. Bạn sẽ làm gì?

**A)** **Write sharding:** Thêm hậu tố ngẫu nhiên vào PK (ví dụ: `tenant_id#0` đến `tenant_id#9`).
**B)** **Jitter the writes:** Thêm độ trễ ngẫu nhiên (0–500ms) tại client phía producer.
**C)** **Partition splitting:** Tăng **WCU (Write Capacity Units)** để ép DynamoDB tự chia tách (auto-split) partition đang quá tải.
**D)** **Time-bucket the key:** Thay đổi PK thành `tenant_id#YYYY-MM-DD-HH`.

Cả 4 giải pháp trên đều thường xuyên xuất hiện trong các buổi **post-mortem** (họp rút kinh nghiệm sau sự cố). Ba trong số đó sẽ thất bại thảm hại vào lúc 3 giờ sáng. Một trong số đó là cái "bẫy" đối với các **Senior Engineer** — nhìn thì rất hợp lý trong bản thiết kế, nhưng lại đổ vỡ hoàn toàn khi vào "phòng chiến đấu" (war room).

**Hãy chọn một đáp án — A, B, C, hoặc D — và giải thích tại sao.**
**Còn bạn, bạn chọn đáp án nào?** 👇


### A  Kỹ thuật Write Sharding (Giải pháp tối ưu)

![[Pasted image 20260707160136.png]]

DynamoDB sử dụng hàm băm (hash function) trên **Partition Key (PK)** để xác định **Physical Shard** (phân đoạn vật lý) nào sẽ tiếp nhận lệnh ghi. Quy tắc mặc định là: 1 giá trị PK = 1 Shard = 1 giới hạn throughput (thường là 1K - 3K WPS tùy cấu hình). Khi một Tenant (khách hàng) đẩy lượng ghi lên tới 9K WPS, Shard đó sẽ bị quá tải (cap out).

**Giải pháp:** Áp dụng kỹ thuật **Write Sharding** bằng cách gắn thêm một hậu tố ngẫu nhiên (random suffix) vào PK tại thời điểm ghi — ví dụ: `tenant_id#0` đến `tenant_id#9`. 

Khi đó, hàm băm sẽ coi đây là 10 khóa (keys) khác nhau và phân tán dữ liệu ghi lên 10 **Logical Partitions** (phân đoạn logic). Kết quả là mỗi phân đoạn chỉ chịu tải khoảng 900 WPS, nằm trong ngưỡng an toàn. Hiện tượng **Throttling** (nghẽn cổ chai) biến mất, độ trễ **P99** (độ trễ tại phân vị 99) giảm xuống còn vài mili giây.

**Đánh đổi (Trade-off):** Khi đọc dữ liệu (Query), bạn phải thực hiện kỹ thuật **Scatter-Gather** (phân tán truy vấn đến tất cả 10 hậu tố rồi tổng hợp kết quả lại). Đối với các luồng dữ liệu **Write-heavy** (ghi là chủ yếu) như hệ thống Analytics, đây là sự đánh đổi hoàn toàn xứng đáng.

Đây chính là pattern "kinh điển" được AWS tài liệu hóa để xử lý vấn đề **Hot Partition** (phân đoạn nóng) trong kiến trúc cơ sở dữ liệu NoSQL.

Dưới đây là bản dịch bài viết sang tiếng Việt, sử dụng các thuật ngữ chuyên ngành lập trình/hệ thống để bạn đọc dễ dàng nắm bắt các "cái bẫy" khi thiết kế hệ thống với DynamoDB:

### C — Chia tách Partition (Cái bẫy dành cho Senior Engineer)

DynamoDB có cơ chế **auto-split partition** (tự động chia tách phân vùng) — nên về lý thuyết, giải pháp này nghe có vẻ hợp lý. Tuy nhiên, việc chia tách dựa trên **throughput** (lưu lượng), chứ không phải **key cardinality** (độ phân bổ của khóa). Nếu một giá trị **PK (Partition Key)** duy nhất tạo ra 9.000 **WPS (Writes Per Second)**, thì sau khi phân vùng được chia tách, tất cả các yêu cầu ghi đó vẫn bị **hash** vào cùng một đích đến. Bạn không thể chia một khóa đơn lẻ ra hai **physical shard** (phân vùng vật lý) khác nhau.

Kết quả là: Bạn thấy partition được chia tách trên CloudWatch, lầm tưởng rằng vấn đề đã được giải quyết, để rồi 10 phút sau lại nhận được thông báo "pager" (cảnh báo lỗi). Đây chính là kiểu giải pháp "sống sót" trên tài liệu thiết kế (design doc) nhưng lại "chết yểu" trong phòng chiến lược (war room).

### B — "Jitter" các yêu cầu ghi (Add Jitter)

**Jitter** (tạo độ trễ ngẫu nhiên) là một **pattern** thực tế — nó giải quyết được bài toán **thundering herd** (hiệu ứng đám đông), nơi mà hàng loạt client cùng gửi request tại cùng một mili-giây, gây ra hiện tượng **spike** (đột biến lưu lượng). Việc rải rác các request này trong khoảng 500ms giúp làm phẳng (smooth) các đợt bùng nổ dữ liệu.

Tuy nhiên, **hot partition** (phân vùng bị quá tải) là một vấn đề mang tính **sustained** (duy trì liên tục) ở mức 9.000 WPS, chứ không phải một đợt bùng nổ tức thời. Việc thêm độ trễ (delay) không làm giảm tổng lưu lượng — DynamoDB vẫn thấy 9.000 WPS đổ dồn vào cùng một partition đó. Bạn chỉ đang làm cho mỗi thao tác ghi trở nên chậm hơn mà chẳng mang lại lợi ích gì.

### D — "Time-bucket" khóa (Time-bucket the key)

Cấu trúc `tenant_id#2026-05-21-14` là một **pattern** phổ biến cho dữ liệu **time-series** — nó giúp giữ cho kích thước mỗi **bucket** nằm trong ngưỡng quản lý được và hỗ trợ **TTL (Time To Live)** để xóa dữ liệu cũ hiệu quả.

Nhưng trong bất kỳ khung giờ nào, bạn vẫn có một **Partition Key** duy nhất phải "gánh" toàn bộ 9.000 WPS cho tenant đó. Bạn chỉ đang đổi tên từ "hot partition" thành "hot time bucket" mà thôi. Vấn đề vẫn còn đó, chỉ là mang cái tên mới. Chưa kể, bây giờ các thao tác **read** (đọc dữ liệu) của bạn sẽ trở nên phức tạp hơn khi phải truy vấn trên 24 **PK** khác nhau mới lấy được dữ liệu của một ngày.
