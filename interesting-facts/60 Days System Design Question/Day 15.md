### You’re running a content recommendation feed. 50M users.

![[Pasted image 20260626113331.png]]

### Bài toán: Tối ưu hóa API kiểm tra "đã xem bài viết" khi database quá tải

Mỗi một API call đều phải thực hiện truy vấn: *"User này đã xem post X chưa?"*

Hiện tại, hệ thống của bạn đang thực hiện `SELECT` trực tiếp vào Postgres cho mọi yêu cầu kiểm tra. Bảng `user_seen_posts` đã phình to lên tới 80 tỷ bản ghi. Độ trễ **p99 latency** cho endpoint "feed" vừa vượt mốc 600ms, và DBA (quản trị viên cơ sở dữ liệu) của bạn đang gửi cho bạn ảnh chụp màn hình biểu đồ CPU báo động lúc 2 giờ sáng.

**Thông số hệ thống:**
*   **Feed service:** Node.js, đạt đỉnh ~120K RPS (yêu cầu mỗi giây).
*   **Cơ chế kiểm tra:** Truy vấn `SELECT` vào Postgres cho mỗi post được đề xuất.
*   **Cấu trúc bảng:** `user_seen_posts(user_id, post_id, seen_at)` (đã **partitioning**, đã đánh **index**, nhưng vẫn chậm).
*   **Cache hit ratio:** Đang ở mức ổn. Vấn đề nằm ở "long tail" của các truy vấn **cold lookups** (truy vấn vào dữ liệu không có sẵn trong cache).
*   **Yêu cầu nghiệp vụ:** Chấp nhận **false positives** (báo đã xem dù chưa xem) trong một phạm vi nhỏ. **False negatives** (hiển thị trùng bài đã xem) là điều không mong muốn nhưng vẫn chấp nhận được.

**Mục tiêu:** Đưa p99 latency xuống dưới 100ms. Bạn chỉ có 1 sprint để thực hiện. Bạn sẽ làm gì?

*   **A)** Sử dụng **Bloom filter** cho mỗi user trên Redis. Kiểm tra "chắc chắn chưa xem" với độ trễ dưới 1ms, chỉ fallback về Postgres khi có kết quả "có thể đã xem" (hit).
*   **B)** Cache toàn bộ tập hợp `user_seen_posts` của từng user vào một `SET` trên Redis. Kết quả chính xác tuyệt đối, không có false positive.
*   **C)** Chuyển toàn bộ dữ liệu sang **Cassandra**. Cấu trúc **wide-column store** sẽ xử lý tốt hơn với tập dữ liệu hàng tỷ bản ghi.
*   **D)** Thêm **Postgres read replica** và sử dụng **connection pooler**. Giữ nguyên dữ liệu, chỉ tăng sức mạnh phần cứng.

Trong thực tế, 3 phương án có thể được dùng cho các bài toán tương tự, nhưng chỉ có **duy nhất một phương án** phù hợp với các ràng buộc khắt khe của bạn.

**Bạn chọn phương án nào (A, B, C, hay D) và tại sao?** Hãy phân tích kỹ thuật (đặc biệt là cái "bẫy" dành cho các Senior Engineer).

Nếu team của bạn đang tranh luận về **Probabilistic Data Structures** (cấu trúc dữ liệu xác suất) so với **Exact Data Structures** (cấu trúc dữ liệu chính xác), hãy gửi bài này cho họ. Sự tranh luận đó quan trọng hơn chính nội dung bài viết này.

### Giải pháp tối ưu: Sử dụng Bloom Filter trên Redis cho từng User

Bloom Filter đưa ra một cam kết mang tính khẳng định: **"Item này CHẮC CHẮN KHÔNG nằm trong tập hợp"**. Nếu filter trả về `false` → bạn có thể bỏ qua việc truy vấn Postgres ngay lập tức. Nếu trả về `maybe` (có thể có) → bạn mới cần truy vấn sâu vào database để xác nhận.

**Tại sao đây là phương án tối ưu?**
*   **Tối ưu hiệu năng (Performance):** Khoảng 97% yêu cầu kiểm tra feed là các bài viết mà user chưa hề xem. Bloom Filter trên Redis trả về kết quả "chắc chắn không" với độ trễ dưới 1ms, giúp giảm tải hoàn toàn cho Postgres.
*   **Tiết kiệm bộ nhớ (Memory footprint):** 
    *   Với 10.000 bài viết/user và tỷ lệ sai số (false-positive) là 1%, Bloom Filter chỉ tốn **12 KB**.
    *   Cùng lượng dữ liệu đó nếu lưu bằng Redis `SET` sẽ tốn hơn **80 KB** và tăng trưởng tuyến tính theo số lượng item.
*   **Scale hệ thống:** Với quy mô 50 triệu user:
    *   Bloom Filter tốn tổng cộng **~600 GB**.
    *   Redis `SET` tốn tới **~4 TB**. Đây là sự khác biệt cực lớn về chi phí hạ tầng.
*   **Case study thực tế:** Được ứng dụng trong tính năng "bạn đã đọc bài này chưa" trên Medium, cơ chế short-circuit (ngắt mạch sớm) trong SSTable của Cassandra, hay các ví SPV của Bitcoin.

**Lưu ý về kỹ thuật:**
Tỷ lệ 1% false-positive (dương tính giả) ở đây có nghĩa là: đôi khi hệ thống sẽ vô tình bỏ qua một bài viết mà user chưa xem (coi như đã xem rồi). Team Product đã đánh giá đây là mức độ chấp nhận được. Quan trọng nhất, Bloom Filter **không bao giờ xảy ra false-negative** (nghĩa là không bao giờ xảy ra trường hợp hiển thị trùng lặp bài viết đã xem) — yếu tố vốn là yêu cầu bắt buộc (dealbreaker) của tính năng này.

### B — Redis SET cho mỗi người dùng (Cái bẫy của Senior Engineer)

Trên lý thuyết, cách này trông có vẻ tối ưu: độ phức tạp thời gian **O(1)**, độ chính xác tuyệt đối, không có **false positive** (dương tính giả). Lệnh `SISMEMBER` cũng đã được kiểm chứng qua nhiều môi trường thực tế (**battle-tested**).

**Cái bẫy:** **Memory (bộ nhớ) sẽ "nổ tung" với các Power User.** Một người dùng đã xem 50.000 bài viết sẽ chiếm khoảng 3–4 MB trong một Redis SET. Chỉ cần 5% nhóm người dùng tích cực nhất cũng đủ để làm sập cả cụm Redis cluster. Lúc này, bạn sẽ phải chọn một trong hai phương án: hoặc là **over-provision** (cấu hình dư thừa, gây lãng phí tài chính), hoặc là bắt đầu **evict** (xóa bỏ) dữ liệu của những người dùng "hot" (điều này đi ngược lại mục đích ban đầu của hệ thống).

**Quy tắc ngón tay cái:** Chỉ dùng Redis SET khi **cardinality** (số lượng phần tử duy nhất) nhỏ (<1K trên mỗi key) hoặc khi hệ thống yêu cầu độ chính xác tuyệt đối. Hãy chuyển sang dùng **Bloom Filter** khi cardinality lớn và chấp nhận được sai số ở mức "có lẽ là không".

### C — Chuyển sang Cassandra (Đúng pattern, sai bài toán)

Cassandra xử lý tốt dữ liệu dạng **wide-column** và số lượng bản ghi (row) cực lớn. Nhưng vấn đề ở đây không phải là **storage** (khả năng lưu trữ) — bản thân Postgres nếu được **partitioning** (phân vùng) hợp lý hoàn toàn xử lý được 80 tỷ dòng. Vấn đề cốt lõi là **read latency** (độ trễ đọc) khi chịu tải cao.

Việc thay đổi **storage engine** không giải quyết được **read pattern**. Bạn vẫn đang thực hiện các lệnh **point lookup** (truy vấn đến một điểm dữ liệu duy nhất) cho mỗi đề xuất. Đổi lại, bạn phải đối mặt với một dự án migration kéo dài nhiều quý, cộng thêm việc phải đào tạo kỹ năng vận hành (ops) mới – tất cả chỉ để giải quyết bài toán mà lẽ ra có thể xử lý trong một Sprint với chỉ 12 KB mỗi người dùng trên Redis.

Cassandra chỉ là giải pháp khi nút thắt nằm ở **write throughput** (tốc độ ghi) hoặc các tác vụ **wide-row scan**. Nó không dành cho hệ thống cần 120.000 **point lookup/giây** trên **hot path** (luồng xử lý chính).

### D — Postgres Read Replica + Connection Pooler (Capacity không đồng nghĩa với Cost)

**Read replica** giúp tăng **horsepower** (sức mạnh xử lý), chứ không tăng sự hiệu quả. Bạn vẫn phải truy cập đĩa cứng (disk) cho mỗi lần kiểm tra, vẫn phải thực hiện **B-tree lookup**, và vẫn tốn chi phí cho mỗi **round-trip** (lượt đi-về giữa client và server). Với 3 replica, bạn chỉ tăng được khoảng 2.5 lần **read throughput** trước khi gặp phải **replication lag** (độ trễ sao chép) và giới hạn kết nối.

Để đạt được chỉ số **p99 < 100ms** ở mức 120.000 **RPS** (request/giây), bạn không cần "nhiều database hơn" — bạn cần **tránh việc truy vấn vào database** đối với 97% các request mà kết quả trả về là "không".

Đây là giải pháp thường được chọn bởi những đội ngũ coi mọi vấn đề hiệu năng đều là vấn đề về **capacity** (công suất/tài nguyên).