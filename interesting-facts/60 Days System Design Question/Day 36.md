Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your API response went from 320ms to 95ms after a CDN switch.

![[Pasted image 20260907140310.png]]


**API Response time của bạn đột ngột giảm từ 320ms xuống còn 95ms chỉ sau một cú đổi CDN.**

Server không hề thay đổi gì cả. Cùng một origin server. Cùng một payload (dung lượng gói tin).

Điểm khác biệt duy nhất: CDN đã bắt đầu nói chuyện với client bằng **HTTP/3**.

Sơ đồ kiến trúc hiện tại:
Mobile App → Load Balancer → Origin (NestJS) → Database

Mọi request đều đi qua CDN đầu tiên. Độ trễ (latency) hoàn toàn chấp nhận được — cho đến khi gặp môi trường có tỷ lệ mất gói tin cao (packet loss), chẳng hạn như chuyển đổi mạng 4G sang 5G trên di động, Wi-Fi chập chờn, hoặc các tuyến cáp khu vực Châu Á - Thái Bình Dương. Bạn đang thấy độ trễ đuôi (tail latency) ở mức p99 vọt lên tận 800ms+. CDN hiện hỗ trợ cả HTTP/2 và HTTP/3. Bạn sẽ bật cấu hình nào?

**A) Chỉ bật HTTP/2** — Kỹ thuật multiplexing (đa kênh) trên một kết nối TCP duy nhất giúp giải quyết triệt để lỗi head-of-line blocking ( nghẽn đầu hàng đợi) kinh điển của HTTP/1.1. Giải pháp này đã được kiểm chứng và hỗ trợ rộng rãi.

**B) Chỉ bật HTTP/3** — Xây dựng dựa trên nền tảng QUIC (giao thức UDP), loại bỏ hoàn toàn hiện tượng nghẽn head-of-line ở tầng giao vận, hỗ trợ khôi phục kết nối 0-RTT. Các client hiện đại đều xử lý rất mượt mà.

**C) HTTP/2 từ CDN về Origin, HTTP/2 từ Client đến CDN** — Tối ưu hóa multiplexing end-to-end (đầu cuối), tránh rủi ro không ổn định của QUIC qua các firewall (tường lửa) của doanh nghiệp.

**D) HTTP/3 từ Client đến CDN, HTTP/2 từ CDN về Origin** — QUIC xử lý tốt chặng cuối (last mile) dễ rớt gói, trong khi HTTP/2 đảm nhận ổn định chặng kết nối trong data center ( trung tâm dữ liệu).

Một trong các phương án trên chính là cách mà Netflix, Cloudflare và phần lớn các CDN lớn đang triển khai thực tế trên môi trường **production**.

Hãy chọn một đáp án — A, B, C, hoặc D — và nêu lý do của bạn. Phân tích chi tiết sẽ có ở phần bình luận.

Nếu team của bạn đang tranh luận về cấu hình CDN hay việc nâng cấp giao thức mạng, hãy share bài này nhé — bài toán đánh đổi (tradeoff) này thực tế phức tạp hơn nhiều người tưởng đấy.


**Đáp án: D — Dùng HTTP/3 cho client, dùng HTTP/2 cho origin server**

![[Pasted image 20260907143533.png]]

Bài toán cốt lõi nằm ở **"chặng cuối" (last mile)**. Các thiết bị di động (mobile client) hoạt động trên các kết nối mạng hay bị rớt gói tin (lossy connection) chính là nơi giao thức TCP bộc lộ điểm yếu chết người.

HTTP/2 đã khắc phục được lỗi **head-of-line blocking** (chẹn đầu hàng đợi) ở tầng ứng dụng (application-layer) của HTTP/1.1 bằng kỹ thuật **multiplexing** (đa kênh hóa) nhiều stream trên cùng một kết conexión TCP. Tuy nhiên, bản thân TCP vẫn dính lỗi head-of-line blocking ở **tầng giao vận (transport layer)**. Chỉ cần một gói tin (packet) bị mất, nó sẽ làm **đình trệ TOÀN BỘ các stream** cho đến khi gói tin đó được truyền lại (retransmit). Trên một kết nối 4G có tỷ lệ rớt gói tin là 2%, kết nối HTTP/2 gồm 20 stream của bạn sẽ gần như bị bóp nghẹt.

Trong khi đó, HTTP/3 chạy trên nền tảng **QUIC** (sử dụng giao thức UDP). Lúc này, mỗi stream hoàn toàn độc lập với nhau. Một gói tin bị rớt sẽ chỉ làm khựng lại đúng stream đó, còn 19 stream kia vẫn luân chuyển bình thường. Cộng thêm tính năng **0-RTT resumption** (các kết nối tiếp theo sẽ bỏ qua hoàn toàn bước bắt tay 3 bước - handshake), bạn tiết kiệm được 1-2 vòng **round trip** (RTT) cho mỗi lần kết nối lại. Đó chính là bí quyết giúp tối ưu **latency** (độ trễ).

Tuy nhiên, chặng đường truyền dữ liệu trong trung tâm dữ liệu (datacenter leg - từ CDN về đến **origin server**) lại là một câu chuyện hoàn toàn khác. Đây là một mạng nội bộ (private network) ổn định và có tỷ lệ rớt gói cực thấp. Trên những kết nối đáng tin cậy như vậy, ưu thế của QUIC sẽ biến mất. Ngược lại, tính năng multiplexing của HTTP/2 đã rất trưởng thành, được tối ưu cực tốt và không ngốn nhiều **CPU overhead** cho việc mã hóa như QUIC (QUIC mã hóa toàn bộ ngay từ tầng giao vận, tuyệt đối không có dạng cleartext - văn bản thuần).

Đây chính xác là mô hình vận hành của các ông lớn như Cloudflare, Fastly và Akamai: Dùng **HTTP/3 ở phía edge-facing** (hướng về phía người dùng/client) và dùng **HTTP/2** (hoặc thậm chí HTTP/1.1 kèm cơ chế keep-alive) ở **phía origin-facing** (hướng về máy chủ gốc).


**Lý do Phương án A không khả thi (Chỉ dùng HTTP/2):**

Multiplexing (đa hợp kênh) trong HTTP/2 là một cải tiến thực sự so với HTTP/1.1, nhưng nó không giải quyết được bài toán **TCP head-of-line blocking** (chặn đầu hàng đợi TCP). Trên các kết nối di động kém ổn định (lossy), ứng dụng của bạn vẫn phải chịu sự chi phối của **TCP retransmission window** (cửa sổ truyền lại TCP). Đối với chỉ số **p99 tail latency** (độ trễ đuôi ở phân vị 99) trên các mạng kém chất lượng, HTTP/2 hoàn toàn không mang lại sự cải thiện nào đáng kể.

**Lý do Phương án B sai (Chỉ dùng HTTP/3):**

Việc áp dụng HTTP/3 trực tiếp tới **origin server** (máy chủ gốc) tiềm ẩn rủi ro vận hành rất lớn. Các **enterprise firewall** (tường lửa doanh nghiệp) và một số **cloud load balancer** (bộ cân bằng tải trên mây) thường chặn cổng UDP 443 hoặc áp dụng **rate-limit** (giới hạn tốc độ) lên nó. Nền tảng hạ tầng ở origin không phải là **bottleneck** (nút cổ chai), mà chặng **last mile** (dặm cuối - kết nối đến người dùng cuối) mới là vấn đề. Việc tối ưu hóa chặng origin bằng QUIC không giải quyết được gốc rễ bài toán; nó chỉ làm hệ thống thêm phức tạp và dễ phát sinh lỗi (breakage).

**Lý do Phương án C sai (Dùng HTTP/2 end-to-end):**

Gặp lỗi tương tự như Phương án A. Bạn vẫn chưa làm gì để cải thiện chặng **last mile**. Việc duy trì chuẩn HTTP/2 **end-to-end** (đầu cuối) nghe có vẻ đồng bộ và sạch sẽ, nhưng sự "sạch sẽ" đó không làm giảm được chỉ số **p99** của bạn.