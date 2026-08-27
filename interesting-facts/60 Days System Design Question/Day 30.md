Nodes: [[60 Days System Design Question]]
Tags: #system-design

### You’re building a file upload service. 10TB of user files today. 100TB in 12 months.

![[Pasted image 20260819172453.png]]



Bạn đang xây dựng một **file upload service (dịch vụ tải lên tệp tin)**. Hôm nay là 10TB dữ liệu người dùng. 12 tháng nữa sẽ là 100TB.

Team của bạn đang tranh cãi nảy lửa.
Backend Lead (Trưởng nhóm Backend) nói: *"Cứ xài **S3** đi. Khỏe!"*
DevOps Engineer (Kỹ sư DevOps) nói: *"Mount một cái **EBS volume** vào. Đơn giản, nhanh gọn."*
Platform Architect (Kiến trúc sư nền tảng) nói: *"Mình phải dùng **EFS** — nhiều service khác nhau cần đọc chung đống file đó."*
Startup CTO (Giám đốc Công nghệ) nói: *"Chơi cloud storage kiểu này sạt nghiệp khi scale lớn đấy. Tự host bằng **MinIO** đi cho rẻ."*

Cả 4 người đều đã từng đưa mấy cái này lên **production**. Và cả 4 đều đưa ra quan điểm dựa trên những "vết sẹo" chiến trận của họ.

Bài toán cụ thể thế này:

— **Upload service (NestJS)** nhận file từ mobile và web clients.
— **ML pipeline (Hệ thống Machine Learning)** cần đọc các ảnh đã upload để xử lý.
— **Audit service (Dịch vụ kiểm toán)** cần quyền đọc chính các file đó.
— **Kích thước file:** Đa dạng, từ ảnh đại diện 5KB cho đến video xuất ra nặng tới 2GB.
— **Infrastucture:** Bạn đang chạy trên **AWS**.

Bạn sẽ chọn gì?

A) **S3** — Object storage (lưu trữ đối tượng), scale vô hạn, trả tiền theo GB thực dùng, không phải quản lý server.
B) **EBS** — Block storage (lưu trữ khối), chạy trên nền SSD, gắn trực tiếp vào EC2, độ trễ đọc cực thấp.
C) **EFS** — Managed NFS (hệ thống tệp mạng được quản lý), chia sẻ đồng thời cho nhiều instance EC2.
D) **MinIO trên EC2** — Object storage tự host tương thích với S3, bạn tự quản lý hạ tầng (self-hosted).

Một trong số này là đáp án **chính xác hiển nhiên** cho kịch bản này.
Một phương án sẽ **âm thầm bóp nát kiến trúc hệ thống của bạn** trong vòng 6 tháng tới.
Một phương án rất hay — nhưng **không dành cho bài toán này**.
Một phương án là cái **bẫy ngọt ngào** trá hình dưới dạng "tiết kiệm chi phí".
Hãy chọn một đáp án — **A, B, C, hoặc D** — và nêu lý do. Phân tích chi tiết sẽ có ở phần bình luận.
Nếu team của bạn cũng từng cãi nhau ló đom đóm vì bài toán này, hãy share ngay đi. Đã đến lúc dùng số liệu để chốt hạ thay vì cãi nhau bằng cảm tính!



**Tại sao A lại thắng (S3):**

![[Pasted image 20260819172529.png]]

Một Storage Layer duy nhất. Không cần Capacity Planning. Mọi Service đều đọc dữ liệu từ cùng một Bucket thông qua S3 Key được lưu trực tiếp trong Database của bạn.

Ở quy mô 100TB → chi phí chỉ khoảng $2,300/tháng. Các Lifecycle Policy sẽ tự động chuyển Cold Data sang Glacier. Các S3 Event sẽ kích hoạt trực tiếp ML Pipeline ngay khi file được Upload lên. Versioning, Encryption, Audit Log — tất cả đều là Native Feature, không tốn một dòng code cấu hình thừa.

Với các dự án Green-field Cloud Service, đây là lựa chọn mặc định (Default Choice). Bạn chỉ nên cân nhắc kiến trúc khác khi có một Use Case đặc thù không thể thỏa mãn.


Để dịch bài viết này sang tiếng Việt sao cho vừa chuẩn xác về thuật ngữ chuyên ngành (DevOps/Infrastructure), vừa tự nhiên và dễ tiếp cận với lập trình viên, chúng ta có thể chuyển ngữ như sau:


 **Tại sao dùng MinIO lại là một "cái bẫy tiết kiệm chi phí"?**

MinIO là một sản phẩm thực tế được sử dụng ở quy mô cực lớn (hyperscale). Nó cung cấp API tương thích với S3, có thông lượng (throughput) cao và chạy trực tiếp trên phần cứng của riêng bạn.

Nhưng tự host (self-hosted) đồng nghĩa với việc bạn phải gánh toàn bộ trách nhiệm về **độ khả dụng (availability)**, xử lý **ổ cứng hỏng (disk failures)**, **sao lưu (backups)**, **hoạch định dung lượng (capacity planning)** và cả những **sự cố lúc 3 giờ sáng**. 

Ở quy mô từ 10–100TB, chi phí nhân sự kỹ thuật để vận hành MinIO một cách ổn định thực tế vượt xa rất nhiều so với tiền thuê dịch vụ S3. Bạn không hề tiết kiệm được đồng nào cả — bạn chỉ đang đổi tiền mua cloud (cloud spend) lấy **giờ công kỹ thuật (engineering hours)**, thứ vốn dĩ có giá đắt đỏ hơn nhiều.

MinIO chỉ thực sự hợp lý khi đạt **quy mô petabyte**, nơi có các **infra team (đội ngũ hạ tầng)** chuyên trách và phải đối mặt với hóa đơn cước băng thông (egress bills) đau đớn mà thôi. Còn ở quy mô nhỏ hơn, thì không phải.


**Lý do phương án B (EBS) âm thầm bóp chết kiến trúc hệ thống của bạn:**

EBS thực chất là một ổ cứng (disk). Một ổ cứng chạy nhanh, độ bền cao — nhưng chỉ **gắn được vào một EC2 instance tại một thời điểm**.

Ngay khoảnh khắc Machine Learning (ML) pipeline của bạn chạy trên một instance khác với service chuyên nhận dữ liệu upload, nó sẽ không thể đọc được các file đó. Bạn thêm tính năng Auto-scaling ư? Mỗi instance mới mọc lên sẽ nhận được một ổ đĩa trắng trơn. Deploy hệ thống dàn trải qua hai Availability Zones (AZs) khác nhau? Lại dính nguyên bài toán cũ.

Mọi thứ chạy mượt mà ở môi trường `dev`. Nhưng nó lại **âm thầm "gãy"** ngay lúc bạn scale-out (mở rộng quy mô theo chiều ngang). Đội ngũ kỹ thuật nào chọn EBS trong trường hợp này thường sẽ nhận ra sai lầm sau 6 tháng, lúc mà họ buộc phải làm một đợt migration (chuyển đổi dữ liệu) cực kỳ đau đớn trong lúc áp lực đè nặng.

**Lý do phương án C (EFS) rất xịn — nhưng lại dùng sai chỗ:**

EFS thực sự là một "quái vật" về sức mạnh. Nó là một hệ thống chia sẻ NFS, cho phép nhiều EC2 instance mount (gắn kết) vào cùng một lúc và hỗ trợ đầy đủ các POSIX semantics (chuẩn giao tiếp hệ thống tập tin POSIX).

Nhưng vấn đề nằm ở đây: **$0.30/GB/tháng**. Với dung lượng 100TB, bạn sẽ mất tới **$30.000/tháng**, trong khi dùng S3 chỉ tốn khoảng **$2.300/tháng**. Chênh lệch chi phí tới 13 lần.

EFS chỉ là câu trả lời đúng khi bạn đang vận hành một hệ thống legacy (ứng dụng cũ) mà source code đã bị hardcode các lệnh gọi hệ thống tập tin như `open()`, `read()`, `write()`, và không thể refactor (tái cấu trúc) lại được. Còn đối với một dự án greenfield (xây mới hoàn toàn) như service viết bằng NestJS và tích hợp sẵn S3 SDK? Bạn đang phải trả gấp 13 lần tiền chỉ để đổi lấy các tính năng của hệ thống tập tin mà vốn dĩ bạn chẳng hề cần tới.