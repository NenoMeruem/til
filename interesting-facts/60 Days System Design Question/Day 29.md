
Nodes: [[60 Days System Design Question]]
Tags: #system-design

### You have an AI product with 4 specialized agents: a Planner, a Researcher, a Coder, and a Reviewer.


![[Pasted image 20260819171830.png]]



Bạn đang sở hữu một sản phẩm AI gồm 4 specialized agents (tác vụ thông minh chuyên biệt): một **Planner** (Lập kế hoạch), một **Researcher** (Thu thập dữ liệu), một **Coder** (Lập trình viên) và một **Reviewer** (Kiểm duyệt mã nguồn).

*   **Planner** phân rã task (công việc).
*   **Researcher** fetch (truy vấn) context (ngữ cảnh).
*   **Coder** implementation (hiện thực hóa code).
*   **Reviewer** catch bug (phát hiện lỗi).

Trên lý thuyết thì rất đơn giản. Nhưng khi đưa lên **production** (môi trường vận hành thực tế), hệ thống lại (sập) toàn tập.

Vấn đề đang xảy ra như sau:

*   **Race condition (Xung đột tiến trình):** Đôi khi **Researcher** trả kết quả về trước khi **Planner** chạy xong $\rightarrow$ **Coder** nhận được incomplete context (ngữ cảnh thiếu sót).
*   **Thiếu cơ chế fault tolerance (Khả năng chịu lỗi):** **Reviewer** flag (đánh dấu) các issue (vấn đề) $\rightarrow$ nhưng lại không có **retry loop** (vòng lặp thử lại), kết quả là bug vẫn được ship (đưa vào sản phẩm).
*   **Cascading failure (Lỗi dây chuyền):** Chỉ cần một agent bị timeout (quá thời gian chờ), nó sẽ hang (treo) toàn bộ **pipeline** trong suốt 40 giây.
*   **Black-box monitoring (Thiếu khả năng quan sát):** Bạn hoàn toàn "mù thông tin" (no visibility) về việc agent nào đã fail (lỗi) hoặc nguyên nhân do đâu.

Bạn cần phải **redesign** (thiết kế lại) tầng **orchestration layer** (tầng điều phối). Bạn sẽ làm gì?

*   **A) Centralized orchestrator (Trình điều phối tập trung):** Một controller (bộ điều khiển) trung tâm gọi lần lượt từng agent theo sequence (trực tuyến/tuần tự), chịu trách nhiệm về **retry logic** (logic thử lại), track state (theo dõi trạng thái) trong DB, và set timeout riêng biệt cho từng step (bước).
*   **B) Choreography via event bus (Phối hợp phi tập trung qua Event Bus):** Các agent pub/sub (phát hành/đăng ký) event (sự kiện), không cần controller trung tâm, mỗi agent tự động trigger (kích hoạt) agent tiếp theo một cách autonomous (tự trị).
*   **C) DAG-based execution (Thực thi dựa trên đồ thị có hướng không chu trình - DAG):** Mô hình hóa pipeline thành một **DAG**, chạy parallel (song song) các step độc lập, chỉ block (chặn) khi gặp các dependency (phụ thuộc) thực tế.
*   **D) Supervisor pattern (Mẫu Giám sát):** Một meta-agent giám sát tất cả các agent còn lại, detect (phát hiện) lỗi, quyết định xem nên **retry** (thử lại), **reroute** (định tuyến lại), hay **escalate** (leo thang/chuyển cho con người xử lý).

Cả 4 mô hình này đều tồn tại trong các hệ thống AI production. Nhưng chỉ có **một** mô hình giải quyết được triệt để các failure mode (kiểu lỗi) cụ thể của bạn mà không đẻ thêm các lỗi mới.

Hãy chọn một phương án — **A, B, C hay D** — và giải thích tại sao. Phân tích chi tiết sẽ có ở phần comment.

Nếu bạn đang build các **agentic systems** (hệ thống đa tác tử), hãy share bài viết này. Hầu hết các dev team đều vướng phải chính xác những vấn đề này vào tháng thứ 2.



**Đáp án đúng: C — Thực thi dựa trên DAG (Directed Acyclic Graph - Đồ thị có hướng không có chu trình)**

![[Pasted image 20260819172052.png]]

Pipeline (luồng xử lý) của bạn có các hard dependency (phụ thuộc cứng: Coder bắt buộc phải đợi **CẢ** Planner VÀ Researcher) **VÀ** cần có vòng lặp retry (Reviewer quay vòng lại Coder nếu xử lý thất bại).

Mô hình DAG thể hiện rõ điều này:

Planner ──┐
          ├──► Coder ──► Reviewer
Researcher┘              │
              ◄───────── (retry khi thất bại)

Những vấn đề mà DAG giải quyết triệt để:

* **Race condition (Điều kiện tranh chấp):** DAG sẽ chặn (block) Coder lại cho đến khi cả hai node upstream (nút phía trên) hoàn thành. Không cần viết code kiểm tra thủ công.
* **Timeout làm treo pipeline:** Mỗi node có một deadline (thời hạn) riêng. Việc một agent bị timeout sẽ không làm đóng băng toàn bộ hệ thống.
* **Không có vòng lặp retry:** Thao tác retry được thiết kế như một edge (cạnh/đường nối) bậc nhất nằm ngay trong đồ thị, chứ không phải là đoạn logic chắp vá bên ngoài.
* **Thiếu khả năng quan sát (Visibility):** Các engine chạy DAG cung cấp cho bạn một execution trace (dấu vết thực thi) đầy đủ cho mỗi lần chạy (run).

**Các implementation thực tế:** LangGraph, Temporal, AWS Step Functions, Prefect, Dagster. Tất cả đều hội tụ về mô hình này vì nó giúp các phần phụ thuộc trở nên trực quan (visible), lỗi được cô lập tại chỗ (local) và việc thực thi dễ dàng được test hơn.

**A — Centralized Orchestrator (Bẫy của Senior Engineer)**

Đây là phương án sai nhưng lại... giống đáp án đúng nhất. Một *Central Controller* (Bộ điều khiển trung tâm) có cơ chế *timeout* cho từng bước và lưu *state* (trạng thái) vào DB trông có vẻ rất hợp lý — nó có cấu trúc, có logic *retry* (thử lại) và có khả năng *observability* (khả năng quan sát/giám sát).

Vấn đề nằm ở chỗ: nó **mặc định chạy tuần tự (sequential)**. Planner (Lập kế hoạch) và Researcher (Nghiên cứu) vẫn chạy nối tiếp nhau trừ khi bạn viết thêm logic để chạy song song (*parallel execution*). Thực chất, bạn đang tự tay code một cái *DAG* (Đồ thị có hướng không có chu trình) theo kiểu mệnh lệnh (*imperative*), và bạn sẽ làm nó rất tệ. Cứ mỗi *dependency* (phụ thuộc) mới phát sinh lại đồng nghĩa với một lần phải sửa code.

Lý do nó bẫy được các lập trình viên kỳ cựu: trông nó giống một "kiến trúc chuẩn chỉ", nhưng thực chất nó chỉ là *imperative orchestration* (điều phối theo mệnh lệnh) kèm theo vô số thủ tục rườm rà không cần thiết.


**B — Choreography thông qua Event Bus**

Mô hình này hoạt động rất tốt với các *pipeline* lỏng lẻo (loosely coupled) theo kiểu "bắn và quên" (fire-and-forget), ví dụ: *đặt hàng thành công -> tạo hóa đơn -> gửi email*. Nhưng luồng xử lý (pipeline) của bạn lại có **các ràng buộc phụ thuộc chặt chẽ (tight dependencies)** — Coder (Lập trình viên) tuyệt đối không thể bắt đầu nếu thiếu kết quả từ cả Planner VÀ Researcher.

Nếu dùng thuần túy *Choreography* (Điều phối phi tập trung), sẽ không có sẵn một *primitive* (khái niệm nguyên thủy) tự nhiên nào kiểu "chờ hai tác vụ này xong nhé". Bạn sẽ phải tự code logic phối hợp **bên trong chính các agent**. Lúc này, con agent Coder của bạn lại phải gánh thêm việc điều phối (orchestration). Như thế còn tệ hơn vấn đề ban đầu của bạn.

Quy tắc ngón tay cái (Rule of thumb): Dùng *Choreography* cho tính độc lập, dùng *Orchestration* cho tính phụ thuộc.


**D — Supervisor Pattern (Mô hình Giám sát)**

Một *meta-agent* đóng vai trò *Supervisor* (Người giám sát) có chức năng theo dõi, phát hiện lỗi và định  (route) lại là một **lớp bổ trợ tuyệt vời nằm trên** phương án C — dùng để leo thang xử lý cho con người (*human escalation*), phát hiện bất thường (*anomaly detection*), hoặc định tuyến động khi DAG không xử lý nổi.

Còn nếu dùng nó làm *mô hình điều phối cốt lõi (base orchestration model)* thì sao? Nó sẽ làm tăng *latency* (độ trễ vì mọi quyết định đều phải đi qua supervisor), tạo ra *single point of failure* (điểm lỗi đơn lẻ), và hoàn toàn không giải quyết được bài toán phụ thuộc. Bản thân Supervisor vẫn phải biết thứ tự thực thi — hóa ra nó lại là một cái DAG ẩn nằm ngay trong "não" của Supervisor mà thôi.

Hãy dùng nó như một lớp tăng cường khả năng chịu lỗi (resilience) nằm trên C, chứ đừng dùng nó để thay thế C.