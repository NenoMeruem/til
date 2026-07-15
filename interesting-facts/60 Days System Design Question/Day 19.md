Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your checkout endpoint has a 400ms P95. Profiling shows 70% of that is DB reads.


![[Pasted image 20260715145814.png]]



Endpoint thanh toán của bạn có chỉ số P95 là 400ms. Kết quả profiling (phân tích hiệu năng) cho thấy 70% thời gian đó nằm ở các tác vụ đọc từ cơ sở dữ liệu (DB).

Bạn quyết định thêm một bản sao đọc (read replica) và chuyển hướng tất cả các truy vấn SELECT vào đó. Chỉ số P95 giảm xuống còn 90ms. Cả đội ăn mừng.

Hai giờ sau, hàng loạt ticket báo lỗi từ bộ phận hỗ trợ đổ về. Khách hàng cập nhật địa chỉ giao hàng nhưng vẫn thấy địa chỉ cũ trên màn hình xác nhận. Một khách hàng bị trừ tiền hai lần vì bước kiểm tra "đơn hàng đã tồn tại" đọc phải dữ liệu cũ (stale data) nên không phát hiện ra bản ghi trùng lặp.

**Cấu trúc hệ thống hiện tại:**
*   **Primary (DB chính):** xử lý tất cả các lệnh ghi, độ trễ sao chép (replication lag) khoảng 200ms.
*   **Replica (DB phụ):** xử lý 100% các lệnh đọc.
*   **Các luồng bị ảnh hưởng:** cập nhật hồ sơ, khử trùng lặp đơn hàng, kiểm tra tính lũy đẳng (idempotency) của thanh toán.

Replica đang hoạt động hoàn toàn đúng như thiết kế. Đó chính là vấn đề.

**Bạn sẽ làm gì?**

**A)** Sử dụng tính nhất quán "Read-your-writes" (Đọc dữ liệu chính mình vừa ghi): chuyển hướng các yêu cầu đọc của người dùng về Primary trong một khoảng thời gian ngắn ngay sau khi họ thực hiện lệnh ghi.

**B)** Sao chép đồng bộ (Synchronous replication): bắt Primary phải chờ Replica xác nhận đã cập nhật xong mới phản hồi (ACK) cho người dùng.

**C)** Theo dõi độ trễ Replica + thử lại: phát hiện khi độ trễ vượt ngưỡng thì chuyển hướng tạm thời về Primary.

**D)** Chỉ chuyển các lệnh đọc quan trọng về Primary: Replica chỉ phục vụ các lệnh đọc không quan trọng như phân tích dữ liệu (analytics).

Cả 4 phương án trên đều là những mô hình thực tế đang chạy trên môi trường production. Chỉ có một phương án giải quyết được vấn đề "dữ liệu cũ" mà không làm mất đi hiệu năng mà bạn vừa cải thiện được.

**Hãy chọn một đáp án (A, B, C, hoặc D) và giải thích tại sao.** Phân tích chi tiết sẽ có ở phần bình luận, bao gồm cả việc đâu là cái bẫy dành cho các kỹ sư cấp cao (senior engineer).

Nếu đội ngũ của bạn từng thêm read replica và mất cả tuần để debug lỗi dữ liệu cũ, hãy chia sẻ bài viết này cho họ.

**Hãy để lại câu trả lời của bạn bên dưới 👇**



### Why A wins:

![[Pasted image 20260715150701.png]]

Sau khi user thực hiện một thao tác ghi (write), các thao tác đọc (read) ngay sau đó sẽ được định tuyến (route) trực tiếp về **Primary node** trong một khoảng thời gian ngắn — thường là vài giây hoặc cho đến khi **replica lag** (độ trễ đồng bộ) được xử lý xong. Tất cả các request đọc khác vẫn sẽ truy xuất từ **Replica node**. Nhờ cơ chế này, hiệu năng hệ thống được tối ưu hóa cho đại đa số lưu lượng truy cập (traffic).

### Tại sao phương án D là một cái bẫy?

Định nghĩa về mức độ **“Critical” (nghiêm trọng)** không hề ổn định. Khi danh sách các tác vụ đọc ưu tiên (primary read list) dần thu hẹp, các lỗi **stale read** (đọc dữ liệu cũ) sẽ quay trở lại, và bạn sẽ phải dành cả quý tiếp theo để "đập chuột" (whack-a-mole) với những lỗi **consistency** (nhất quán dữ liệu). Bạn đã đánh đổi một giải pháp mang tính hệ thống (systematic) để lấy những quyết định mang tính cảm tính theo từng tính năng riêng lẻ (per-feature judgment).

### Tại sao phương án B sai?

**Synchronous replication (sao chép đồng bộ)** đồng nghĩa với việc Primary phải chờ Replica xác nhận (ACK) cho mỗi thao tác ghi. Mặc dù **replica lag** (độ trễ sao chép) giảm về bằng 0, nhưng **P95 write latency** (độ trễ ghi ở phân vị 95) của bạn sẽ tăng vọt từ 20ms lên 80–120ms. Tệ hơn nữa, bạn đã vô tình tạo ra sự phụ thuộc chặt chẽ (**coupling**) giữa tính sẵn sàng (**availability**) của Primary và tình trạng sức khỏe của Replica.

### Tại sao phương án C sai?

Vấn đề của bạn không nằm ở **Average lag** (độ trễ trung bình). Vấn đề thực sự là **Read-your-writes consistency**: người dùng thực hiện thao tác ghi nhưng không thấy thay đổi đó khi đọc lại trong vòng 200ms. Dù chỉ số lag trông có vẻ ổn (200ms vẫn được coi là “bình thường”), nhưng thực tế dữ liệu mà người dùng cần truy xuất vẫn đang trong quá trình **in-transit** (truyền tải/chưa được commit xuống replica).

