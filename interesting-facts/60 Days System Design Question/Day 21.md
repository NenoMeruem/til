Nodes: [[60 Days System Design Question]]
Tags: #system-design


### You’re shipping an AI chat product. The LLM streams ~40 tokens/sec per user.


![[Pasted image 20260721140831.png]]


**Tiêu đề: Bạn đang build một sản phẩm AI Chat. LLM stream khoảng 40 tokens/giây cho mỗi user. Bạn sẽ chọn Transport Layer nào?**

Hệ thống của bạn phải gánh 50.000 concurrent users (người dùng đồng thời) ngay ngày launch. Client chỉ chạy trên trình duyệt. Dữ liệu luân chuyển một chiều (uni-directional): Server → Client.

Team bạn đang họp để chốt phương án vận chuyển dữ liệu (transport). Ai cũng có quan điểm riêng.

**Setup hiện tại:**
*   **Frontend:** React (Browser).
*   **Backend:** Python (FastAPI) nằm sau ALB (Application Load Balancer).
*   **Payload:** Text tokens định dạng UTF-8, kích thước ~5–20 bytes/token.
*   **Direction:** Server push dữ liệu, Client chỉ thực hiện render.
*   **Yêu cầu:** Reconnect phải diễn ra mượt mà, không gián đoạn (do mobile network thường xuyên bị drop).

Team lead chốt: "WebSockets chứ còn gì nữa". Platform engineer phản đối. Vậy bạn sẽ chọn phương án nào để release?

**Các option:**
*   **A) WebSockets:** Mặc định cho các ứng dụng "real-time", full-duplex, hầu hết ứng dụng chat đều dùng.
*   **B) Server-Sent Events (SSE):** HTTP stream một chiều, dùng native `EventSource` của trình duyệt, hỗ trợ auto-reconnect sẵn.
*   **C) gRPC server streaming:** HTTP/2, binary frames, hỗ trợ backpressure sẵn.
*   **D) Long polling:** Công nghệ cũ, đã qua kiểm chứng (battle-tested), hoạt động ổn định qua mọi loại proxy trên thế giới.

Ba trong số bốn phương án trên là các pattern production thực thụ. Một phương án còn lại là "cái bẫy" mà hầu hết các team thường đâm đầu vào, để rồi 6 tháng sau mới hối hận.

**Bạn chọn A, B, C hay D?** Hãy đưa ra lựa chọn và giải thích tại sao. Tôi sẽ phân tích chi tiết ở phần bình luận (bao gồm cả lý do tại sao phương án phổ biến nhất lại là "cái bẫy" dành cho các senior).

Nếu team bạn sắp có buổi họp tranh luận về vấn đề này, hãy gửi bài viết này cho họ trước. Tiết kiệm thời gian họp hành vô ích.

**Đáp án của bạn là gì?** 👇



### Tại sao SSE (Server-Sent Events) lại thắng thế?

![[Pasted image 20260721141148.png]]

Luồng dữ liệu ở đây là **đơn hướng (one-way)**. Server thực hiện đẩy (push) các token xuống, và client chỉ việc render. Chỉ đơn giản vậy thôi. Client không bao giờ gửi ngược lại token trong khi luồng đang chạy — nếu người dùng có input, chúng ta sẽ xử lý qua một request POST riêng biệt. Vì vậy, việc dùng WebSocket (vốn hỗ trợ **full-duplex**) cho một bài toán **half-duplex** là sự lãng phí tài nguyên không cần thiết.

SSE được thiết kế chính xác cho mô hình này: một kết nối HTTP **tồn tại lâu dài (long-lived)**, với định dạng `text/event-stream`. Server ghi dữ liệu, và API `EventSource` có sẵn trên trình duyệt sẽ đọc. Không cần **protocol upgrade** (nâng cấp giao thức phức tạp như từ HTTP sang WS), không cần cơ chế **framing** mới, cũng chẳng cần thiết lập luồng **auth** riêng biệt.

**Tính năng "đắt giá" nhất:** Cơ chế **tự động kết nối lại (automatic reconnect)** tích hợp sẵn với `Last-Event-ID`. Khi trình duyệt bị rớt kết nối hoặc thiết bị di động chuyển từ WiFi sang 4G/LTE, `EventSource` sẽ tự động thực hiện reconnect và gửi kèm ID của event cuối cùng mà nó nhận được cho server. Từ đó, server sẽ **replay** (phát lại) dữ liệu tiếp nối từ điểm đó. Nếu dùng WebSocket, bạn sẽ phải tự viết logic này từ đầu, và chắc chắn bạn sẽ viết sai trong vài lần thử nghiệm đầu tiên.

Đó là lý do tại sao các API streaming lớn hiện nay như OpenAI hay Anthropic đều lựa chọn SSE.

### Tại sao phương án A (WebSockets) là một cái bẫy?

Từ khóa "chat" thường gây hiểu lầm. Chat giữa người với người (như Slack, WhatsApp) là **bidirectional** (truyền tải hai chiều). Trong khi đó, một ứng dụng AI Chat thực chất là một **unidirectional token stream** (luồng token một chiều), với phần prompt được gửi đi qua một **POST request** riêng biệt. Hình thái dữ liệu khác nhau, cơ chế truyền tải (transport) cũng phải khác nhau.

**Cái giá phải trả khi duy trì 50.000 kết nối đồng thời:**
*   **Sticky sessions trên ALB (Application Load Balancer):** Gây khó khăn cho việc cân bằng tải.
*   **Tự viết logic reconnect và replay:** Phải xử lý thủ công khi kết nối bị ngắt.
*   **Heartbeats (ping/pong):** Phải duy trì cơ chế kiểm tra kết nối "sống/chết" liên tục.
*   **Lãng phí tài nguyên:** Tốn nhiều bộ nhớ hơn trên mỗi kết nối cho các bộ đệm (buffers) mà bạn gần như không bao giờ dùng đến.

Mỗi điểm trên đều là một "quả bom nổ chậm" khiến bạn phải trực đêm (on-call) để fix lỗi.

### Tại sao phương án C (gRPC streaming) là sai lầm?

Trình duyệt không hỗ trợ trực tiếp gRPC. Bạn sẽ cần **Envoy + gRPC-Web**, điều này vô tình làm giảm hiệu năng của mô hình streaming và thêm một bước trung gian (proxy hop). Bạn sẽ phải tốn công vận hành Envoy và debug các **Protobuf frames** trong tab Network chỉ để gửi các chuỗi ký tự UTF-8. gRPC rất tuyệt cho giao tiếp service-to-service, nhưng là công cụ sai lầm khi dùng cho trình duyệt.

### Tại sao phương án D (Long polling) không khả thi?

Với tốc độ 40 token/giây, mỗi chu kỳ polling sẽ tiêu tốn một **HTTP request** hoàn chỉnh. Với 50.000 người dùng, bạn sẽ phải gánh **2 triệu RPS (Request Per Second) chỉ để render văn bản**. Đây là phương án dự phòng (fallback) hợp lý khi SSE/WS bị chặn, nhưng không bao giờ là lựa chọn ưu tiên cho kiến trúc truyền tải dữ liệu vào năm 2026.