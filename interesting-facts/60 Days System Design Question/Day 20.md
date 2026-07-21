Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your checkout service calls a 3rd-party fraud-check API on every order.


![[Pasted image 20260721140541.png]]

### Khi một Dependency "ốm yếu" kéo sập cả hệ thống của bạn

Dịch vụ Checkout của bạn đang gọi một API bên thứ ba để kiểm tra gian lận (fraud-check) cho mỗi đơn hàng.

Đột nhiên, API đó bắt đầu gặp tình trạng **timeout** sau 30 giây thay vì mức **latency** thông thường là 200ms.

Các **pod** Node.js xử lý Checkout của bạn chỉ có **connection pool** giới hạn 50 kết nối. Chỉ trong vòng 90 giây, toàn bộ các kết nối này đều bị "treo" (parked) vì phải chờ phản hồi từ API kiểm tra gian lận. Các request Checkout mới bắt đầu ùn ứ trong hàng đợi. **P99 latency** của endpoint `/checkout` vọt từ 300ms lên 28 giây. Khách hàng bắt đầu thực hiện **retry**. Các pod cạn kiệt bộ nhớ và dẫn đến **OOM (Out of Memory)**. API kiểm tra gian lận bị suy giảm hiệu năng — và toàn bộ dịch vụ Checkout của bạn bị "sập".

**Cấu trúc hệ thống:**
*   Checkout (NestJS) → Fraud API (3rd party) — Timeout lên tới 30s.
*   Các pod này cũng đồng thời xử lý `/cart`, `/orders`, `/health` — tất cả các dependency này vẫn hoạt động bình thường.
*   Dashboard của Fraud API thông báo sẽ khôi phục sau khoảng 10 phút.
*   **SLO (Service Level Objective)** của quý này đang đứng trước nguy cơ "bốc hơi".

Bạn cần ngăn chặn sự cố này ngay lập tức mà không làm mất hoàn toàn chức năng Checkout. Bạn sẽ làm gì?

**A)** Giảm timeout xuống 2 giây và thêm 3 lần **retry** với cơ chế **exponential backoff**.

**B)** Thêm một **Circuit Breaker**: mở mạch sau N lần thất bại, sau đó chuyển sang trạng thái **half-open** (thử nghiệm với một request thăm dò) trước khi đóng mạch hoàn toàn.

**C)** Áp dụng **Bulkhead**: tách các cuộc gọi đến Fraud API vào một **connection pool** hoặc **thread pool** riêng biệt để chúng không làm cạn kiệt tài nguyên của các dịch vụ khác trong Checkout.

**D)** Kết hợp cả **B và C** — dùng Circuit Breaker cho dependency bị lỗi, dùng Bulkhead để cô lập **blast radius** (phạm vi ảnh hưởng).

Trong số này, có 3 phương án thường được các Senior Engineer tranh luận trong các buổi **postmortem**. Một trong số đó là phương án mà các Staff Engineer thực sự triển khai. Và có một phương án sẽ khiến sự cố trở nên tồi tệ hơn.

Hãy chọn một — A, B, C, hoặc D — và giải thích lý do tại sao.

Nếu team của bạn đã từng gặp trường hợp một **downstream service** chậm chạp kéo sập cả một dịch vụ đang khỏe mạnh, hãy chia sẻ bài viết này. Những cuộc thảo luận như thế này cần phải diễn ra *trước* khi sự cố xảy ra, chứ không phải sau đó.

**Hãy đưa ra lựa chọn của bạn bên dưới 👇**




![[Pasted image 20260721140531.png]]
### Tại sao D lại thắng (Circuit Breaker + Bulkhead)?

Hai pattern này giải quyết hai cơ chế lỗi khác nhau, và bạn cần cả hai để đảm bảo tính **resilience** (khả năng chịu lỗi) cho hệ thống.

**1. Circuit Breaker (Ngắt mạch):**
Pattern này ngăn chặn việc bạn tiếp tục gửi request đến một **dependency** (phụ thuộc) đã "chết". Sau khi đạt đến ngưỡng N lỗi liên tiếp (hoặc tỷ lệ lỗi vượt quá ngưỡng trong một khoảng thời gian), trạng thái sẽ chuyển sang **OPEN** — mọi request tiếp theo đến Fraud API sẽ bị từ chối ngay lập tức (fail-fast) và trả về **fallback**. Nhờ đó, hệ thống không phải chờ timeout 30 giây, cũng không để các **connection** bị treo.

Sau một khoảng thời gian **cooldown**, nó sẽ chuyển sang trạng thái **HALF-OPEN**: cho phép đúng một request "thăm dò" đi qua. Nếu thành công, mạch sẽ đóng (**CLOSED**) và traffic được khôi phục. Nếu thất bại, nó lại quay về trạng thái **OPEN**. Trạng thái *Half-open* là điểm quan trọng mà nhiều tài liệu bỏ qua; nó giúp ngăn chặn **thundering herd** (hiệu ứng đám đông) đánh sập một service vừa mới khởi động lại.

**2. Bulkhead (Vách ngăn):**
Đây là pattern mà các kỹ sư thường quên cho đến khi hệ thống thực sự gặp sự cố. Nó giúp **isolate** (cô lập) các **resource pool** (tài nguyên). Giả sử bạn cấp cho Fraud API một pool riêng biệt gồm 10 connections — tách biệt hoàn toàn với 40 connections dành cho các service khác như `/cart`, `/orders`, `/health`. Khi Fraud API bị treo, nó chỉ có thể làm cạn kiệt 10 connections đó, còn 40 connections kia vẫn hoạt động bình thường. Cart vẫn chạy, Health check vẫn ổn. **Blast radius** (phạm vi ảnh hưởng) được giới hạn ngay tại tính năng lỗi. Con tàu sẽ không bị chìm chỉ vì một khoang tàu bị ngập nước — đó chính là lý do cái tên "Bulkhead" ra đời.

### Các công cụ hỗ trợ
Các thư viện như **Resilience4j**, **Polly** (.NET) hay **Hystrix** (đã cũ) đều hỗ trợ cả hai pattern này. Ở tầng hạ tầng, **AWS App Mesh + Envoy** cũng cung cấp cơ chế Bulkhead ngay tại lớp proxy. Netflix đã phát triển Hystrix sau khi rút ra bài học xương máu: một dependency chậm chạp có thể gây ra **cascading failure** (lỗi dây chuyền) thông qua các **shared thread pool**, dẫn đến việc sập toàn bộ hệ thống gợi ý (recommendations) vào giờ cao điểm.

Dưới đây là bản dịch bài viết sang tiếng Việt, sử dụng các thuật ngữ chuyên ngành lập trình/hệ thống để đảm bảo tính chính xác và gần gũi với dân kỹ thuật:

### Tại sao phương án B lại là "cái bẫy" của các Staff Engineer?

**Tại sao chỉ chọn B lại là chưa đủ:**

Sử dụng **Circuit Breaker** (ngắt mạch) mà không có **Bulkhead** (vách ngăn) là câu trả lời nghe có vẻ "hợp lý" nhất trong các buổi phỏng vấn. Đây là pattern được nhắc đến nhiều nhất trong các bài toán về tính bền vững (**resilience**). Đúng là nó giải quyết được lỗi cụ thể được mô tả: khi breaker mở, các request gọi API gian lận sẽ **fail-fast** (thất bại nhanh) và không chiếm dụng connection pool nữa.

Nhưng thực tế vận hành (**production**) lại khác: Trong khoảng thời gian từ lỗi đầu tiên cho đến khi breaker kịp trip (ngắt mạch), mọi request trong chuỗi N lỗi đó vẫn đang chiếm dụng connection từ **shared pool**. Nếu bạn đặt ngưỡng là 20 lỗi trong 10 giây, bạn hoàn toàn có thể làm cạn kiệt (saturate) pool 50 connection trước khi breaker kịp nhận ra vấn đề. Bạn chỉ đang thu hẹp "cửa sổ sự cố" chứ không hề loại bỏ được hiện tượng **cascading failure** (lỗi dây chuyền).

**Bulkhead** giúp ngưỡng của breaker có khả năng **latency-tolerant** (chịu đựng được độ trễ). Nó tạo ra một khoảng đệm để hệ thống có thời gian phát hiện và xử lý trước khi toàn bộ hệ thống "bốc cháy".

Đây là cái bẫy vì phương án B không sai, nhưng nó **thiếu sót**. Các Senior Engineer thường dừng lại ở B trong các buổi thiết kế vì thấy thế là đủ. Còn các Staff Engineer sẽ chọn phương án D (kết hợp cả hai) vì họ đã từng chứng kiến B thất bại thảm hại lúc 3 giờ sáng trên Production.

### Tại sao chỉ chọn C lại chưa đủ:

Có **Bulkhead** vẫn tốt hơn là không có gì — nó giúp khu trú phạm vi ảnh hưởng (**contain the damage**). Tuy nhiên, 10 connection dành riêng cho API gian lận đó vẫn sẽ tốn 30 giây mỗi request để chờ đợi các gọi gọi "đã nắm chắc phần thất bại". Bạn vẫn phải trả cái giá về độ trễ (latency) trên mỗi lượt checkout, chỉ là trên một cái pool nhỏ hơn. Người dùng vẫn thấy checkout bị chậm; chỉ là bạn không bị mất luôn cả service `/cart` cùng với nó mà thôi.

**Bulkhead mà thiếu Circuit Breaker = "Vết rò rỉ đã được khoanh vùng, nhưng căn phòng vẫn đang ngập nước."**

### Tại sao A lại sai (và nguy hiểm):

Giảm **timeout** kết hợp với **retries with backoff** (thử lại với độ trễ tăng dần) là điều tồi tệ nhất bạn có thể làm đối với một dependency đang bị suy yếu. Đây là **anti-pattern** kinh điển.

API gian lận vốn đã đang quá tải, còn bạn thì quyết định gửi cho nó lượng traffic gấp 3 lần. Mỗi đợt **retry storm** từ mọi pod checkout sẽ dồn dập đổ vào một service đang cần "giảm tải" để phục hồi. Đây chính là cách một sự cố cục bộ biến thành sự cố toàn hệ thống — và là lý do tại sao một incident 10 phút lại kéo dài thành 4 tiếng.

**Retry** chỉ nên dùng cho các lỗi tạm thời (ví dụ: một mã 503 đơn lẻ, hoặc connection reset), không phải cho sự suy giảm hiệu năng hệ thống (**systemic degradation**). Và chúng luôn cần một **Circuit Breaker** đặt ở phía trước để kiểm soát **blast radius** (phạm vi ảnh hưởng).

Nếu bạn từng đọc các bản **postmortem** (báo cáo phân tích sự cố) có cụm từ *"retry storm contributed to extended recovery time"* (bão retry đã góp phần kéo dài thời gian phục hồi) — thì đây chính là thứ mà họ đang ám chỉ.