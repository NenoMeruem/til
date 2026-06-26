Nodes: [[60 Days System Design Question]]
Tags: #system-design
### Order #4471 just hit your system at 14:02


![[Pasted image 20260623171229.png]]

**Order #4471 vừa đổ vào hệ thống lúc 14:02. Luồng xử lý như sau:**

1. **OrderService** khởi tạo đơn hàng (Postgres) ✅
2. **PaymentService** trừ tiền khách $89.50 qua Stripe ✅
3. **InventoryService** thử reserve (giữ hàng) mã SKU → Thất bại (hết hàng, thiếu 3 đơn vị) ❌
4. **ShippingService** chưa bao giờ được gọi.

**Hệ quả:** Bạn đang giữ tiền của khách, không có hàng để ship, và đơn hàng bị kẹt ở trạng thái **PENDING**. Trong kiến trúc **Monolith**, bạn chỉ cần bọc cả 4 bước trong một **Transaction** và thực hiện **ROLLBACK**. Nhưng bạn không thể làm vậy với 4 **Microservices** dùng 4 **Database** riêng biệt.

**Bạn sẽ chọn giải pháp nào?**

*   **A) Choreography Saga:** Mỗi service tự publish **events**, service kế tiếp lắng nghe và phản hồi. Nếu thất bại, các service tự kích hoạt **compensating events** (giao dịch bù trừ) ngược lại chuỗi.
*   **B) Orchestration Saga:** Một **central orchestrator** (bộ điều phối trung tâm - đóng vai trò **State Machine**) gọi lần lượt từng service và điều phối việc rollback/bù trừ khi có lỗi.
*   **C) Two-Phase Commit (2PC):** Một **coordinator** khóa tất cả 4 service ở trạng thái **PREPARE**, sau đó thực hiện **commit** đồng nhất (atomic) hoặc **abort** (hủy bỏ) toàn bộ.
*   **D) Outbox Pattern + Eventual Consistency:** Mỗi service ghi dữ liệu vào local DB + một bảng **Outbox**, sau đó một **relay** sẽ publish event bất đồng bộ (async), các service phía sau dần dần đồng bộ dữ liệu với nhau.

Cả 4 pattern trên đều đang được triển khai thực tế trong production. Chỉ có một giải pháp là tối ưu nhất cho quy trình checkout 4 bước này, nơi các bước phải chạy tuần tự và mỗi bước cần cơ chế **compensating transaction** cụ thể.

**Bạn chọn phương án nào (A, B, C, hay D) và tại sao?** Hãy phân tích chi tiết bên dưới.

Nếu đội ngũ của bạn đã từng tranh cãi nảy lửa lúc 2 giờ sáng về **Choreography vs. Orchestration**, hãy chia sẻ bài viết này với họ. Cuộc tranh luận đó còn giá trị hơn cả nội dung bài viết này.


**Đáp án: B — Orchestration Saga (Mẫu thiết kế Saga theo cơ chế Điều phối)**

![[Pasted image 20260623171240.png]]

**Tại sao phương án B tối ưu nhất?**

Quy trình thanh toán (checkout) gồm 4 bước với thứ tự thực thi nghiêm ngặt, đi kèm cơ chế xử lý lỗi hoàn tác (compensating transaction) ở từng bước chính là bài toán điển hình mà **Orchestrator** (bộ điều phối) được thiết kế để giải quyết.

Bạn hãy triển khai một **State Machine** (máy trạng thái) cho `CheckoutSaga` (có thể sử dụng các framework như Temporal, AWS Step Functions, Camunda hoặc tự xây dựng logic thủ công). Bộ điều phối này sẽ gọi tuần tự từng service theo luồng: **OrderService → PaymentService → InventoryService → ShippingService.**

Với mỗi bước, bạn sẽ đăng ký một hàm bù trừ (**Compensation logic**) tương ứng: `CancelOrder`, `RefundPayment`, `ReleaseInventory`. Khi `InventoryService` gặp lỗi, Orchestrator sẽ tự động chạy ngược lại quy trình (rollback) để thực hiện các hàm bù trừ đã định nghĩa.

**Ưu điểm:**
* **Durable State (Trạng thái bền vững):** Trạng thái của tiến trình được lưu trữ an toàn, không bị mất khi hệ thống gặp sự cố.
* **Observable (Khả năng quan sát):** Bạn có thể dễ dàng theo dõi toàn bộ luồng xử lý.
* **Replayable (Khả năng chạy lại):** Có thể chạy lại các bước bị lỗi một cách dễ dàng.

Vào lúc 3 giờ sáng, khi có sự cố, bạn chỉ cần mở **UI của Orchestrator** là có thể xác định chính xác bước nào đã thất bại, đồng thời xem được toàn bộ `input/output` của request đó để debug.


Để dịch đoạn văn này một cách chuyên nghiệp và sát với ngữ cảnh kiến trúc phần mềm (Software Architecture), chúng ta cần sử dụng các thuật ngữ như *Distributed Systems*, *Event-driven Architecture*, *Compensating Transactions*, và *Observability*.

2. **Tại sao mô hình Choreography lại là một "cái bẫy"?**

Trên lý thuyết thì rất thanh thoát (elegant). Nhưng khi quy trình vượt quá 4 bước và bắt đầu có các nhánh xử lý lỗi (branching compensations) thì hệ thống bắt đầu vỡ vụn.

Hãy thử tưởng tượng logic nghiệp vụ cho trường hợp: *'Điều gì xảy ra khi tồn kho không đủ sau khi đã trừ tiền thành công?'*. Logic này sẽ bị phân tán (smeared) trên 3 microservices, và mỗi service đều phải 'biết' về trạng thái lỗi của các service còn lại. 

Vấn đề là: **Không ai thực sự làm chủ (own) luồng đi của dữ liệu.** Không có một điểm tập trung nào để bạn truy vấn: *"Đơn hàng #4471 đang ở trạng thái nào?"*. Vào lúc 3 giờ sáng, bạn sẽ phải chật vật chắp vá thông tin từ các sự kiện rải rác trên 4 Kafka topics khác nhau.

**Kết luận:** Mô hình *Choreography* chỉ phù hợp với các tác vụ *fire-and-forget* (gửi đi và quên nó luôn) mang tính chất side-effects lỏng lẻo. Nó **không** phải là lựa chọn tối ưu cho các luồng tuần tự như thanh toán (checkout) cần các cơ chế xử lý hoàn tác (compensation) chặt chẽ.

3. **Tại sao phương án C (2PC) là sai lầm?**
Stripe không hỗ trợ **2PC (Two-Phase Commit)**, và thực tế là chẳng có **API** của đơn vị vận chuyển nào hỗ trợ nó cả. 
Hơn nữa, 2PC duy trì **lock (khóa)** trong suốt giai đoạn **PREPARE**. Chỉ cần một **service** bị **latency** (độ trễ cao) là toàn bộ **transaction** sẽ bị **block** (chặn). Với lưu lượng truy cập (checkout volume) lớn, hiện tượng **lock contention** (tranh chấp khóa) sẽ khiến hệ thống của bạn bị "sập" ngay lập tức. Đây là một giải pháp lý thuyết trong sách giáo khoa nhưng lại hoàn toàn không khả thi khi triển khai thực tế.

4. **Tại sao phương án D (Outbox pattern) là chưa đủ?**
**Transactional Outbox** là một giải pháp về **infrastructure** (hạ tầng), chứ không phải là một **Saga**. 
Mục tiêu của nó chỉ là giải quyết bài toán: làm thế nào để **publish event** một cách đáng tin cậy sau khi **local DB commit**. Nó không định nghĩa **step ordering** (thứ tự các bước), không có cơ chế **compensations** (xử lý bù trừ/rollback), và cũng không giải quyết được vấn đề khi **Inventory service** bị lỗi. Nếu dùng Outbox, bạn vẫn phải xây dựng thêm một **Saga orchestration/choreography** bên trên nó.

