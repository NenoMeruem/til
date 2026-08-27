Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your e-commerce platform just crossed 2M daily active users. 70% are in the US, 30% in Europe.


![[Pasted image 20260827104323.png]]




Nền tảng thương mại điện tử của bạn vừa án mốc 2 triệu Daily Active Users (DAU) — với 70% đến từ US và 30% từ Châu Âu.

Các phàn nàn về **latency ( độ trễ)** từ user Châu Âu đang chồng chất: trung bình mất tới 380ms Round-Trip Time (RTT) để gọi về region `us-east`. Support ticket tăng vọt 40%. Trong khi đó, Black Friday chỉ còn 6 tuần nữa là diễn ra.

**Hạ tầng hiện tại của bạn:**
* Chạy đơn region (single-region) trên AWS `us-east-1`.
* RDS PostgreSQL (Primary DB).
* Redis Cache.
* 12 Microservices đứng sau API Gateway.

**Mục tiêu:** Kéo độ trễ của user Châu Âu xuống dưới 80ms.

**Ràng buộc (Constraints):** 
* Không đủ thời gian/nguồn lực để **rewrite** toàn bộ database.
* Phải **ship** (phát hành) tính năng này trước Black Friday.

Đội ngũ Engineering đang tranh cãi về 4 phương án sau:

* **A) Active-Active Multi-Region:** Deploy toàn bộ stack sang `eu-west-1`, sử dụng Distributed Database (như CockroachDB hoặc Aurora Global), định ướng (route) user về region gần nhất. Write (ghi) đồng thời xuống cả 2 region.
* **B) Active-Passive với Read Replicas:** Giữ `us-east-1` làm Primary, dựng thêm `eu-west-1` làm Hot Standby kèm Read Replica. Các câu Read (đọc) của user Châu Âu sẽ được xử lý tại local, nhưng Write vẫn phải vòng về US. Failover sang region mới chỉ mất vài phút nếu US sập.
* **C) CDN + Edge Caching:** Giữ nguyên single-region, đẩy static assets và các API response có thể cache được lên CloudFront Edge Nodes tại Châu Âu. Không cần thay đổi gì ở tầng Database.
* **D) Active-Active với Evental Consistency (Nhất quán cuối cùng):** Deploy toàn bộ stack ở cả 2 region, cho phép mỗi region tự xử lý Write của mình và đồng bộ bất đồng bộ (async). Chấp nhận việc user Châu Âu có thể thấy dữ liệu Write từ US chậm hơn 200ms.

Trong số này, có 3 phương án là design pattern thực tế mà các production team hay dùng. Nhưng chỉ có **1 phương án duy nhất** giải quyết được bài toán của bạn — thỏa mãn đúng các ràng buộc và kịp thời hạn trước Black Friday.

Bạn sẽ chọn phương án nào — **A, B, C hay D**? Hãy đưa ra lựa chọn và giải thích lý do dưới phần bình luận. 

Nếu team của bạn cũng từng tranh luận về bài toán tương tự, hãy share ngay cho họ. Cuối cùng, **Trade-offs (sự đánh đổi)** mới là thứ quyết định tất cả!



 **Tại sao phương án B giành chiến thắng:**

![[Pasted image 20260827104549.png]]

**Constraint (Ràng buộc)** chính là chìa khóa giải quyết vấn đề. Bạn không được phép **rewrite (viết lại từ đầu)** database, và bạn chỉ có vỏn vẹn 6 tuần.

Người dùng ở châu Âu đang kêu ca về **read latency ( độ trễ đọc dữ liệu)** — khi duyệt sản phẩm, kiểm tra trạng thái đơn hàng, và tải trang cá nhân. Đó đều là các **read query (truy vấn đọc)**. Việc dựng một **RDS read replica (bản sao đọc)** ở region `eu-west-1` chỉ tốn khoảng 1–2 ngày cấu hình **infra (hạ tầng)**, nhưng sẽ kéo thời gian phản hồi cho user châu Âu xuống mức ~15ms thay vì 380ms như trước. 

Trong khi đó, các **write query (ghi dữ liệu)** vẫn được trỏ về `us-east-1` (hoàn toàn chấp nhận được — người dùng sẵn sàng bỏ qua độ trễ hơi cao một chút ở khâu thanh toán - checkout). **Replication lag (độ trễ đồng bộ dữ liệu)** thường chưa tới 100ms.

Thêm vào đó, mô hình **active-passive (chủ động - bị động)** này mang lại một **failover strategy (chiến lược chuyển đổi dự phòng)** thực tế: Khi cụm US gặp sự cố (down) $\rightarrow$ ta chỉ cần **promote (nâng cấp)** bản replica ở EU lên thành node chính chỉ trong vòng vài phút.


**Tại sao phương án A là một "cạm bẫy" (Active-Active kết hợp Database phân tán):**

Đây là kiểu trả lời "chuẩn mô hình lớn" nhưng lại bóp chết team engineering trước thềm sự kiện lớn (như Black Friday). Việc migration (di chuyển dữ liệu) từ RDS PostgreSQL sang CockroachDB hay Aurora Global chỉ trong deadline 6 tuần thực chất là một project kéo dài vài quý — nó đòi hỏi xử lý distributed transactions (giao dịch phân tán), giải quyết bài toán global clock skew (lệch đồng hồ toàn cầu), và phải test các failure modes (trường hợp lỗi) hoàn toàn mới. Đây có thể là kiến trúc đúng cho dài hạn, nhưng lại là đáp án sai cho bài toán đang đặt ra.

**Tại sao phương án C là sai (CDN kết hợp Edge Caching):**

CDN chỉ giải quyết độ trễ cho các static asset (tài nguyên tĩnh) như hình ảnh, file JS, CSS. Nó hoàn toàn vô tác dụng với các dynamic reads (truy vấn dữ liệu động - giỏ hàng, lịch sử đơn hàng, thông tin tài khoản) và bằng không đối với write latency (độ trễ ghi dữ liệu). CDN chỉ là một layer (lớp) được gắn thêm *vào trên* một giải pháp thực thụ, chứ không phải để thay thế nó. Đây chỉ là phương án đúng một phần, không phải đáp án chúng ta cần.

**Tại sao phương án D rất nguy hiểm (Active-Active kết hợp Eventual Consistency - Nhất quán cuối cùng):**

Đây là mô hình đa vùng (multi-region) sát với thực tế nhất — nhưng cũng nguy hiểm nhất nếu đem ra deploy mà không chuẩn bị kỹ. Eventual consistency (tính nhất quán cuối cùng) giữa các region đồng nghĩa với việc: một user ở Châu Âu vừa đặt đơn hàng, nhưng region ở Mỹ của bạn vẫn thấy lượng tồn kho khác trong vòng 200ms. Hậu quả là gì? Nếu là hàng giới hạn = oversell (bán quá số lượng). Nếu là thanh toán = duplicate charges (trừ tiền trùng lặp). Việc conflict resolution (giải quyết xung đột dữ liệu) thực chất là một bài toán product (sản phẩm) đội lốt bài toán infra (hạ tầng).