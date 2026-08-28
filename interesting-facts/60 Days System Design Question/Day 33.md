Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your order service takes 200 writes/sec at peak.


![[Pasted image 20260827161524.png]]



Dịch vụ Đặt hàng (Order Service) của bạn đạt tải 200 lượt ghi/giây (writes/sec) vào giờ cao điểm.

Bạn tiến hành audit (kiểm toán) dữ liệu trong 6 tháng. Có gì đó sai sai — hai đơn hàng có cùng ID nhưng tổng tiền (total) lại khác nhau.

Bạn chỉ có **current state** (trạng thái hiện tại). Bạn hoàn toàn mù tịt về việc dữ liệu đã tiến hóa (evolve) như thế nào để đến được trạng thái đó.

Cơ sở dữ liệu (DB) của bạn giờ chẳng khác nào một bãi tha ma của các **overwritten rows** (dòng dữ liệu bị ghi đè).

Kiến trúc hệ thống hiện tại đây:

• `OrderService` → `Postgres` (chỉ lưu current state)
• Các **events** (sự kiện): `placed` (đã đặt), `updated` (đã cập nhật), `cancelled` (đã hủy), `refunded` (đã hoàn tiền)
• Mỗi câu lệnh `UPDATE` đều ghi đè lên row trước đó.
• Không có **audit log** (nhật ký kiểm toán). Không có **event history** (lịch sử sự kiện). Không thể **replay** (phát lại trạng thái).

Một tranh chấp thanh toán (billing dispute) vừa ập đến. Bạn cần **reconstruct** (tái dựng) chính xác chuyện gì đã xảy ra với Đơn hàng #8471. Bạn lực bất tòng tâm.

Thay vì chỉ lưu trữ current state, hãy lưu lại chuỗi các sự kiện đã tạo ra trạng thái đó.

Cách tiếp cận của bạn là gì khi **redesign** (thiết kế lại) dịch vụ này?

**A) Event Sourcing** — Sử dụng **append-only event log** (nhật ký sự kiện chỉ để ghi nối đuôi) làm **source of truth** (nguồn chân lý duy nhất), current state sẽ được **derive** (suy luận/tạo ra) bằng cách **replay** (phát lại) các sự kiện.

**B) Change Data Capture (CDC)** — Giữ nguyên Postgres hiện tại, nhưng **stream** (truyền tải dòng dữ liệu) mọi thay đổi row vào Kafka để làm **audit trail** (dấu vết kiểm toán).

**C) Thêm bảng `audit_log`** — Dùng **database triggers** để thực hiện **shadow writes** (ghi ngầm) trên mọi thao tác `INSERT/UPDATE/DELETE`.

**D) Dual-write** (Ghi kép) — Ghi đồng thời vào cả bảng current state và một bảng events riêng biệt trong mọi thao tác.

Một trong các phương án trên sẽ mang lại khả năng **full replay** (phát lại toàn bộ), **projection flexibility** (sự linh hoạt trong việc tạo góc nhìn dữ liệu), và một **source of truth** thực thụ. Những phương án còn lại chỉ là các miếng vá tạm bợ (patches).

Hãy chọn một — **A, B, C, hoặc D** — và giải thích tại sao. Mình sẽ thả phân tích chi tiết ở phần bình luận.

Nếu team của bạn đang tranh cãi về **audit trails** hay việc **redesign theo hướng event-driven**, hãy tag ngay đồng nghiệp cần đọc bài này vào nhé!



**Đáp án: A — Event Sourcing **

Dưới đây là lý do tại sao, và tại sao 3 phương án còn lại nghe có vẻ hợp lý nhưng lại đi chệch trọng tâm:
![[Pasted image 20260827161909.png]]


**Tại sao A là lựa chọn chính xác (Event Sourcing):**

Event Sourcing đảo ngược hoàn toàn mô hình dữ liệu truyền thống. Thay vì chỉ lưu trữ **state** (trạng thái) mới nhất và làm mất đi lịch sử hình thành nên nó, mô hình này lưu lại toàn bộ mọi **event** (sự kiện) đã từng xảy ra. **Current state** (trạng thái hiện tại) thực chất chỉ là một **projection** (phép chiếu/bản hiển thị) — được tính toán bằng cách **replay** (phát lại/chạy lại) toàn bộ các event từ điểm khởi đầu (hoặc từ một **snapshot** - bản chụp trạng thái).

Đối với Đơn hàng #8471: bạn không truy vấn trực tiếp một dòng dữ liệu (row). Thay vào đó, hệ thống sẽ replay các event: `OrderPlaced` (Đã đặt hàng), `OrderUpdated` (Đã cập nhật), `PaymentCaptured` (Đã thu tiền), `RefundInitiated` (Đã yêu cầu hoàn tiền). Mọi **mutation** (thao tác làm thay đổi dữ liệu) đều được bảo tồn, gắn mốc thời gian (**timestamped**) và **immutable** (bất biến). Bạn có thể tái tạo lại **state** tại bất kỳ mốc thời gian nào trong quá khứ. Bạn cũng có thể xây dựng các **projection** mới (ví dụ: *"tổng doanh thu theo mã SKU trong 90 ngày qua"*) mà không cần phải thay đổi **core model** (mô hình cốt lõi) — chỉ đơn giản là replay và project lại theo cách khác.

Đây chính là cách mà các công cụ như Axon, EventStoreDB và các tầng xử lý hướng sự kiện (event-sourced layer) trong hầu hết các hệ thống fintech/e-commerce lớn đang vận hành. Nó không đơn thuần là một file **log** ghi nhật ký — mà là **primary data model** (mô hình dữ liệu chính) của toàn hệ thống.

**Tại sao phương án B (CDC) là một "cái bẫy":**

CDC (Change Data Capture) rất mạnh mẽ nhưng thường bị đánh giá thấp. Các công cụ như Debezium kết hợp với Kafka cho phép bạn stream (truyền tải) mọi thay đổi trên từng row (dòng dữ liệu) của Postgres về các hệ thống downstream (hạ nguồn) mà không cần chạm vào ứng dụng. Nhìn bên ngoài, nó trông giống như Event Sourcing (Lưu vết sự kiện) — bạn cũng có một chuỗi các thay đổi dữ liệu nối tiếp nhau.

Nhưng cái bẫy nằm ở đây: **CDC chỉ bắt được *state delta* (độ chênh lệch trạng thái), chứ không phải *business event* (sự kiện nghiệp vụ).** Bạn chỉ nhận được thông tin rằng tổng tiền đã thay đổi từ 89.99 xuống 79.99 — chứ không biết đó là do sự kiện `DiscountApplied` (Áp dụng mã giảm giá) từ coupon `SAVE10`. Ý nghĩa ngữ nghĩa (semantic meaning) đã bị mất. Bạn có thể tái tạo lại *cái gì* đã thay đổi, nhưng không thể biết *tại sao* nó lại thay đổi. Sự khác biệt cốt lõi này sẽ "giết chết" bạn trong các tranh chấp giao dịch hoặc khi kiểm toán tuân thủ (compliance audit).

CDC là một công cụ bổ trợ tuyệt vời cho Event Sourcing ở khía cạnh data propagation (lan truyền dữ liệu). Nhưng nó không thể thay thế cho Event Sourcing.

**Tại sao phương án C (Bảng audit_log) là sai lầm:**

Việc dùng trigger (trợ thủ kích hoạt trong DB) để ghi audit log là một giải pháp chắp vá kinh điển (band-aid solution). Vấn đề là: bạn đang coi `row` trong database là source of truth (nguồn chân lý duy nhất) và việc ghi log chỉ là một tác dụng phụ (side effect).

Các tác dụng phụ rất dễ hỏng. Trigger có thể bị vô hiệu hóa trong quá trình migration (chuyển đổi dữ liệu). Các thao tác bulk import (nhập liệu hàng loạt) thường bỏ qua trigger. Thay đổi schema (lược đồ DB) có thể làm trigger bị mồ côi (orphaned). Sáu tháng sau, bảng `audit_log` của bạn sẽ thủng lỗ chỗ — và đó lại là lúc bạn cần nó nhất. Nó chỉ là một cái bóng, không phải là một nền tảng vững chắc.

**Tại sao phương án D (Dual-write - Ghi kép) là sai lầm:**

Dual-write thoạt nghe có vẻ hợp lý. Nhưng thực tế là bạn đang tự tạo ra một bài toán distributed consistency (tính nhất quán phân tán) ngay trong chính service của mình. Nếu việc ghi state (trạng thái DB) thành công nhưng việc ghi event (sự kiện) thất bại — do rớt mạng, sập tiến trình, hay lỗi OOM (Out Of Memory) — bạn sẽ lâm vào cảnh: dữ liệu trạng thái đã đổi nhưng không hề có sự kiện tương ứng nào được sinh ra. Hệ thống audit trail (dấu vết kiểm toán) từ thiết kế đã không còn đáng tin cậy.

Đây chính xác là bài toán mà **Outbox Pattern** được sinh ra để giải quyết. Nhưng nếu bạn đã phải đầu tư đến mức đó, thì coi như bạn đã đi được nửa đường để tiến tới một kiến trúc Event Sourcing chuẩn chỉnh rồi còn gì.

