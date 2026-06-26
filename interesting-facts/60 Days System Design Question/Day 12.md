### Your events table on PostgreSQL 15 just crossed 200M rows.

Khi bảng `events` trên PostgreSQL 15 của bạn chạm mốc 200 triệu dòng...

![[Pasted image 20260626103948.png]]

Tốc độ Ingestion (nạp dữ liệu) đang duy trì ở mức 8K writes/sec từ Kafka consumer. Trước đây, P99 write latency chỉ là 12ms, nhưng hiện tại đã vọt lên 140ms và vẫn đang tiếp tục tăng.

Team Dashboard đang "kêu cứu". Các câu lệnh Query của họ lọc theo bộ lọc `(tenant_id, event_type, created_at)` và đang phải quét (scan) tới 40 triệu dòng mỗi request. Họ yêu cầu phải có Index ngay lập tức.

Bạn kiểm tra `pg_stat_user_indexes`. Bảng này hiện đã có 4 Index. Mỗi thao tác ghi (write) đều phải cập nhật toàn bộ các Index này. Nếu thêm Index thứ 5, Ingestion lag sẽ biến thành Ingestion failure.

Tuy nhiên, có một điểm mấu chốt: 92% truy vấn của Dashboard chỉ tập trung vào dữ liệu của một `tenant` trong 7 ngày gần nhất. Đó chỉ là một phần rất nhỏ (hot slice) của toàn bộ bảng.

**Bạn sẽ làm gì?**
*   **A) Thêm Composite B-tree Index trên `(tenant_id, event_type, created_at)`:** Giải pháp tiêu chuẩn, giải quyết được bài toán query.
*   **B) Thêm Covering Index với `INCLUDE (user_id, payload)`:** Để truy vấn thực hiện Index-only scan, không cần phải truy cập vào Heap (table data).
*   **C) Không thêm Index trên Primary:** Spin-up một Read Replica và điều hướng các query của Dashboard sang đó. Giữ cho tiến trình ghi ở Primary luôn "gọn nhẹ".
*   **D) Thêm Partial Index:** Vẫn dùng các cột đó, nhưng thêm điều kiện `WHERE event_type = ‘signup’ AND created_at > now() - interval ‘7 days’`. Chỉ index phần dữ liệu "nóng".

Cả 4 phương án đều là các pattern thực tế trong Production. Ba trong số đó giúp Dashboard của bạn chạy nhanh. Nhưng chỉ một trong số đó giúp bạn đạt mục tiêu mà không làm "bay màu" Write throughput.

**Hãy chọn một đáp án — A, B, C, hoặc D — và giải thích lý do.**

Dưới đây là bản dịch bài viết sang tiếng Việt, sử dụng các thuật ngữ chuyên ngành lập trình/cơ sở dữ liệu để giúp người đọc chuyên môn dễ tiếp cận:

**Đáp án: D — Partial Index (Chỉ mục từng phần) ✅**

Dưới đây là lý do tại sao phương án này thắng thế, và tại sao ba phương án còn lại dễ gây "bẫy" ngay cả với các kỹ sư dày dạn kinh nghiệm.

![[Pasted image 20260626103937.png]]

### Tại sao D (Partial Index) là lựa chọn tối ưu?

Giả sử 92% các truy vấn (queries) của bạn nhắm vào dữ liệu của một tenant (khách hàng) trong 7 ngày gần nhất. Một **Partial Index** chỉ đánh chỉ mục (index) cho các dòng (rows) thỏa mãn điều kiện `WHERE` cụ thể — mọi dữ liệu không khớp sẽ được ghi vào bảng (table) mà hoàn toàn không ảnh hưởng đến chỉ mục này.

**Bài toán hiệu năng:**
Nếu các sự kiện đăng ký (signup events) chỉ chiếm ~4% luồng dữ liệu, và cửa sổ thời gian 7 ngày chỉ chiếm ~5% tổng dung lượng bảng, thì Partial Index của bạn chỉ phải index khoảng 0,2% số lượng hàng. Với các lệnh `INSERT` không khớp với điều kiện lọc (predicate), bạn không tốn bất kỳ chi phí nào cho index này. **Write amplification (khuếch đại ghi)** gần như được loại bỏ hoàn toàn.

**Cơ chế hoạt động:**
Trình lập kế hoạch (Planner) của PostgreSQL sẽ sử dụng Partial Index cho bất kỳ truy vấn nào có mệnh đề `WHERE` là tập con (subset) của điều kiện trong index. Nhờ đó, truy vấn từ dashboard của bạn được tối ưu hóa hoàn toàn: tốc độ đọc (read) vẫn nhanh, và hiệu suất ghi (write) vẫn đảm bảo.

**Điểm cần lưu ý (The catch):**
Nếu đội ngũ làm Dashboard thay đổi yêu cầu từ 7 ngày lên 30 ngày, bạn sẽ cần phải rebuild (xây dựng lại) lại index. Đây là một chi phí vận hành có thể dự báo trước, không phải là một "cái bẫy" ẩn giấu.

### Tại sao phương án B là một "cái bẫy"? (Covering Index kết hợp với INCLUDE)

Đây là lỗi khiến ngay cả các Senior Engineer cũng dễ bị đánh lừa hơn bất kỳ phương án nào khác. Khi xem kết quả của lệnh `EXPLAIN`, bạn thấy `Index Only Scan` trông rất tối ưu, nhưng vấn đề nằm ở dữ liệu bạn "nhồi" vào mệnh đề `INCLUDE`.

Hãy hình dung cột `payload` thường là một JSONB blob có dung lượng trung bình vài KB. Bây giờ, mỗi khi có một câu lệnh `INSERT`, hệ thống không chỉ ghi row vào **Heap** mà còn phải ghi thêm một index entry "phì nhiêu" chứa toàn bộ nội dung `payload` đó. Mỗi khi `UPDATE` cột `user_id` hoặc `payload`, hệ thống lại phải ghi đè (rewrite) lên index entry này. Bạn không hề giảm chi phí ghi (write cost) mà thực tế là đã nhân nó lên gấp nhiều lần.

Với tần suất 8.000 lượt ghi/giây (8K writes/sec) trên một bảng vốn đã có quá nhiều index, việc dùng `Covering Index` chứa dữ liệu JSONB chính là lý do khiến chỉ số **p99 latency** từ 140ms vọt lên 800ms. `INCLUDE` chỉ là lựa chọn đúng đắn cho các cột có dung lượng nhỏ (narrow columns) trên những bảng ưu tiên đọc (read-heavy). Đằng này, trường hợp của bạn không thuộc nhóm đó.

### Tại sao phương án A là sai lầm? (Full composite B-tree)

Một index dạng `(tenant_id, event_type, created_at)` sẽ giúp dashboard của bạn chạy nhanh. Tuy nhiên, nó cũng sẽ đánh index cho tất cả 8.000 lượt ghi/giây, bất kể `tenant` hay `event_type` nào. Bạn đang phải trả cái giá rất đắt cho việc duy trì index chỉ để phục vụ cho một truy vấn (query) mà thực tế chỉ quét qua 0,2% dữ liệu. Đó chính là định nghĩa của một sự đánh đổi tồi tệ.

### Tại sao phương án C không giải quyết được vấn đề? (Read replica)

Các index này vẫn phải tồn tại ở đâu đó. Nếu bạn đẩy chúng sang **Read Replica**, nó sẽ bị "hụt hơi" khi phải liên tục **replay WAL** (Write Ahead Log) để duy trì cấu trúc index. Nếu để trên **Primary**, bạn lại quay về bài toán "nút thắt cổ chai" ban đầu.

Cần lưu ý: Read Replica chỉ giải quyết bài toán "Primary không đủ tài nguyên để phục vụ toàn bộ các truy vấn đọc". Chúng không giải quyết được bài toán "hiệu năng đường dẫn ghi (write path) bị nghẽn do quá trình bảo trì index".

