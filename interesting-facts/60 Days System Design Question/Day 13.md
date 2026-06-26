
### You’re running 3 workloads against the same Postgres RDS instance. max_connections = 300

![[Pasted image 20260626110337.png]]

### Bài toán: Khi tài nguyên DB không đủ gánh workload

Bạn đang vận hành 3 **workload** khác nhau trên cùng một instance **Postgres RDS**. Cấu hình `max_connections` bị giới hạn cứng ở mức 300. Cả 3 ứng dụng đều cần **connection pool**, nhưng không bên nào chịu nhường bên nào.

**Cấu hình hiện tại:**

*   **NestJS REST API trên ECS Fargate:** Các **short-lived transaction**, lưu lượng 800 **RPS**. Với 10 **tasks**, mỗi task cấu hình **pool size** 40 → tổng cộng "gõ cửa" yêu cầu tới 400 connections.
*   **Background job workers:** Chạy các **analytics query** tốn thời gian. Mỗi connection bị "chiếm dụng" từ 30–90 giây.
*   **Lambda functions:** Traffic dạng **bursty** (tăng đột biến), phụ thuộc vào **cold-start**, số lượng **concurrent invocations** dao động từ 0–200.

**Kết quả:** 3 client, 1 database, 300 slots. Bài toán này không có lời giải nếu không tối ưu. Bạn cần **pooling** mà không làm sập hệ thống. Hãy chọn giải pháp:

*   **A) PgBouncer ở chế độ `transaction mode` cho tất cả:** Đặt một **single pooler** trước RDS để tối đa hóa khả năng **multiplexing**.
*   **B) PgBouncer `session mode` cho workers + `transaction mode` cho REST API:** Chia cấu hình pooler theo loại workload. Lambda sẽ đi qua một trong hai cổng này.
*   **C) RDS Proxy cho Lambda + PgBouncer `transaction mode` cho ECS:** Kiến trúc lai (hybrid). Định tuyến kết nối dựa trên loại client.
*   **D) Tách riêng Read Replica cho analytics workers + PgBouncer `transaction mode` cho REST & Lambda:** Cách ly workload ở tầng Database.

Trong 4 phương án trên, có 3 cái giúp bạn ngủ ngon sau giờ làm, 1 cái sẽ âm thầm "bóp chết" hệ thống vào lúc 3 giờ sáng và bạn sẽ mất cả tuần để debug nguyên nhân.

Đây không phải là câu hỏi kiểu "PgBouncer là hiển nhiên rồi". Mọi phương án đều có những Senior Engineer sẵn sàng tranh luận trên bảng trắng — và chắc chắn có một phương án sai theo cách cực kỳ tinh vi, chỉ lộ diện khi các worker bắt đầu bị **dropped** giữa chừng lúc đang query.

**Bạn chọn phương án nào (A, B, C, hay D)? Tại sao?** Hãy giải thích logic của bạn.

Nếu team bạn từng rơi vào cảnh "cháy nhà" vì lỗi `Postgres: too many connections`, hãy share bài này cho họ. Cuộc thảo luận bên dưới mới là bài học đắt giá nhất.

**Phản hồi của bạn bên dưới 👇**


### Đáp án: B — Cấu hình PgBouncer chế độ *Session* cho Worker + chế độ *Transaction* cho REST API ✅

![[Pasted image 20260626111218.png]]

Đây chính là câu hỏi giúp phân biệt giữa những kỹ sư đã thực chiến vận hành PgBouncer trên môi trường Production và những người chỉ đọc tài liệu lý thuyết. Dưới đây là phân tích chi tiết:

#### Tại sao đáp án B lại tối ưu? (Chia tách pool theo kiểu tải - workload)

Bản chất của PgBouncer là **multiplexing** (ghép kênh) — cho phép nhiều client kết nối tới một kết nối vật lý duy nhất với Postgres. Tuy nhiên, việc này chỉ an toàn khi kết nối được trả về pool ngay sau khi kết thúc transaction (giao dịch). Đó chính là **Transaction mode**.

*   **Tại sao REST API (NestJS) dùng Transaction mode?**
    API có đặc thù là các giao dịch ngắn, tần suất cao (800 RPS), không duy trì session state, không dùng `SET LOCAL`, không giữ advisory locks xuyên suốt các query, và không phụ thuộc vào các prepared statements kéo dài. Ở chế độ này, 400 kết nối từ client sẽ được "nén" (collapse) xuống chỉ còn khoảng 30–50 kết nối vật lý với Postgres. Bài toán tài nguyên được giải quyết triệt để.

*   **Tại sao Transaction mode lại là "thảm họa" với Analytics Worker?**
    Các worker này chạy những câu query kéo dài từ 30–90 giây và trải dài qua nhiều transaction. Chúng thường xuyên sử dụng session state, temp tables, `SET search_path` hoặc cursors. Nếu bạn sử dụng Transaction mode, sau mỗi giao dịch, PgBouncer sẽ thu hồi kết nối và trả cho tiến trình khác — toàn bộ state (trạng thái) của worker sẽ bị mất sạch. Tồi tệ hơn, với tải 800 RPS từ API, khả năng một worker nhận lại đúng kết nối cũ là gần như bằng 0. Kết quả là worker sẽ lỗi một cách âm thầm (silently break).

*   **Giải pháp:** Hãy dành riêng cho các worker một pool PgBouncer chạy ở **Session mode** — ở đây, 1 kết nối client = 1 kết nối backend trong suốt phiên làm việc. Worker có thể có ít kết nối hơn, nhưng chúng được "giữ chặt" (hold), đúng với nhu cầu thực tế của chúng.

*   **Xử lý lưu lượng từ Lambda:** Vì Lambda cũng là dạng stateless, thời gian sống ngắn (tương tự API), nên nó sẽ đi qua pool ở Transaction mode của REST API.

**Kết quả cuối cùng:** Bạn triển khai một instance PgBouncer duy nhất nhưng với hai cấu hình pool (pool config) và hai cổng kết nối (listening ports) riêng biệt. PgBouncer hỗ trợ sẵn cơ chế này.

**Tổng kết:** API tận dụng được khả năng multiplexing, các worker không bị thiếu hụt tài nguyên, tổng số kết nối backend tới Postgres được kiểm soát dưới 300, và hệ thống vận hành trơn tru. Đây chính là giải pháp "nhàm chán" nhưng chuẩn mực nhất giúp bạn ngủ ngon sau những ca trực (on-call).


Dưới đây là bản dịch bài viết sang tiếng Việt, sử dụng các thuật ngữ chuyên ngành lập trình và quản trị cơ sở dữ liệu để đảm bảo tính chính xác và dễ tiếp cận với các kỹ sư:


### **Tại sao A là một cái bẫy (Dùng PgBouncer chế độ `transaction` cho mọi đối tượng):**

Đây là lựa chọn mà hầu hết các kỹ sư hướng tới vì tư duy: "Transaction mode = multiplexing (ghép kênh) tối ưu nhất". Nó hoạt động rất tốt với các API, nhưng lại "âm thầm giết chết" các worker (tiến trình xử lý nền).

Ngay khi một truy vấn phân tích (analytics query) cần bất kỳ thứ gì không nằm gọn trong một transaction — như bảng tạm (temp table), biến phiên (session variable), `SET LOCAL`, câu lệnh được chuẩn bị (`prepared statement`) hay con trỏ (`cursor`) tồn tại lâu hơn một transaction — PgBouncer sẽ thu hồi kết nối và trả về pool. Truy vấn tiếp theo? Nó sẽ được gán sang một backend connection khác. Mọi trạng thái (state) cũ đều mất sạch. Kết quả là truy vấn thất bại, hoặc tệ hơn, trả về dữ liệu sai lệch.

Kiểu lỗi này cực kỳ nguy hiểm: nó chạy ổn ở môi trường dev (độ đồng thời thấp, nhờ may mắn nên luôn nhận đúng connection), chạy ổn ở staging (tải nhẹ), nhưng lại "chết đứng" ở production khi API bắt đầu "xả" request liên tục vào pool khiến các worker không thể giữ được một kết nối ổn định. Bạn sẽ phải đối mặt với nó vào lúc 3 giờ sáng trong đợt chốt sổ tài chính.

### **Tại sao C là giải pháp sai (RDS Proxy cho Lambda + PgBouncer cho ECS):**

Trên lý thuyết, phương án này nghe có vẻ hợp lý. RDS Proxy thực sự rất tốt cho Lambda — nó xử lý hiệu quả "cơn bão kết nối" khi cold-start, quản lý xác thực IAM và tích hợp VPC tốt. Nếu bài toán chỉ là "Lambda + Postgres", thì C đúng.

Nhưng C không giải quyết được vấn đề của các worker. Chúng vẫn là các tiến trình chạy dài hơi (long-running), vẫn cần duy trì session state, và giờ đây bạn lại phải gánh thêm một tầng pooling nữa để vận hành, giám sát và chi trả chi phí. RDS Proxy đắt hơn PgBouncer tính trên mỗi giờ kết nối và nó không hỗ trợ "session pinning" (ghim phiên) giữa các transaction như cách PgBouncer chế độ `session` thực hiện.

C chỉ giải quyết được phần dễ nhất trong ba bài toán và bỏ mặc phần khó nhất.

### **Tại sao D là "cái bẫy dành cho senior engineer" (Dùng Read Replica cho các worker):**

Đây là lựa chọn đánh lừa các kỹ sư dày dạn kinh nghiệm, bởi nó khớp với pattern "cô lập tải" (isolate the workload). Việc tách biệt các truy vấn phân tích (analytics) khỏi hệ thống OLTP ở tầng Database là một ý tưởng rất hay — nhưng dành cho một bài toán khác.

D giải quyết vấn đề **mở rộng khả năng đọc (read scaling)** và **người hàng xóm ồn ào (noisy neighbor)** gây ảnh hưởng tới query plan, cache hoặc IO. Nhưng nó **không giải quyết** được bài toán về giới hạn kết nối (connection math). Read replica của bạn vẫn có giới hạn `max_connections` riêng. Các worker của bạn vẫn chiếm dụng kết nối từ 30–90 giây. Bạn chỉ đơn giản là đẩy vấn đề "cạn kiệt kết nối" từ primary instance sang replica, đồng thời phải trả thêm tiền cho một instance RDS mới.

Nếu bài toán của bạn là "các truy vấn phân tích đang làm nghẽn tài nguyên của OLTP", thì D là lựa chọn đúng. Nhưng bài toán ở đây là "chúng ta không đủ kết nối". Nỗi đau khác nhau thì giải pháp phải khác nhau.

D chỉ là việc bạn nên làm **sau khi** đã triển khai thành công phương án B và nhận ra rằng các truy vấn phân tích đang tranh chấp tài nguyên IOPS và buffer cache với hệ thống chính.