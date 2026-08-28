Nodes: [[60 Days System Design Question]]
Tags: #system-design 

### Your startup just got its first SOC 2 audit.

![[Pasted image 20260827105920.png]]


Startup của bạn vừa trải qua đợt kiểm toán SOC 2 đầu tiên.

Kiểm toán viên đặt câu hỏi: *"Database password, API key và service token của các bạn đang được lưu ở đâu?"*

Senior Engineer của bạn chìm vào im lặng.

Hóa ra là một nửa số đó nằm trong các file `.env` đã được `commit` lên git từ 18 tháng trước. Ba cái khác thì bị hardcode thẳng vào biến môi trường của AWS Lambda. Còn một cái thì nằm trong một tin nhắn Slack từ tận năm 2023.

Hệ thống của bạn đang có 6 service chạy trên production, 4 môi trường (environments), và chính sách xoay vòng (rotation policy) bằng không.

Bức tranh hiện tại đây:

• NestJS API → Postgres (password nằm trong biến môi trường)

• NestJS API → Stripe (API key nằm trong biến môi trường)

• Background workers → SQS, S3 (AWS credentials nằm trong biến môi trường)

• Webhook của bên thứ ba → HMAC secret nằm trong biến môi trường)

• Không xoay vòng secret. Không có audit trail (dấu vết kiểm toán). Không có kiểm soát truy cập tập trung (centralized access control).

Bạn bắt buộc phải fix vấn đề này. Và tuyệt đối không được downtime.

**Giải pháp:**

**A) Chuyển toàn bộ sang AWS Secrets Manager** — Gọi SDK lúc runtime, phân quyền truy cập bằng IAM, có sẵn tính năng tự động xoay vòng secret (auto-rotation).

**B) Dùng HashiCorp Vault** — Dynamic secret (secret tạo động), phân quyền chi tiết (fine-grained policies), chạy tốt trên mọi nền tảng cloud hoặc on-premise.

**C) Dùng biến môi trường được inject vào lúc deploy qua CI/CD** — Secret được lưu trong kho lưu trữ của GitHub Actions / GitLab CI, tuyệt đối không lưu cứng xuống ổ đĩa.

**D) Mã hóa secret bằng KMS và lưu bản mã (ciphertext) trực tiếp vào database nhà trồng** — Giải mã lúc runtime, toàn quyền kiểm soát.

Cả 4 phương án này đều đang được dùng trên production tại các tech company thực tế.

Chọn một phương án — A, B, C hay D — và cho tôi biết lý do tại sao. Tôi sẽ thả bài mổ xẻ chi tiết ở phần bình luận.

Nếu team của bạn đang tranh cãi nảy lửa về vấn đề này ngay lúc này, hãy share bài viết này nhé. Kiểu gì cũng có người cần đọc nó đấy.



**A — AWS Secrets Manager (Giải pháp tối ưu)**

![[Pasted image 20260827160637.png]]

Hệ thống của bạn vốn đã chạy hoàn toàn trên nền tảng AWS (Cloud-native với Lambda, SQS, S3). Vì vậy, Secrets Manager mang lại cho bạn những lợi ích sau:

• **Lưu trữ mã hóa tập trung:** Được bảo mật bởi dịch vụ quản lý khóa KMS.
• **Kiểm soát truy cập dựa trên IAM:** Phân quyền chi tiết (granular) cho từng secret đối với từng dịch vụ cụ thể.
• **Tự động xoay vòng credential (Auto-rotation):** Hỗ trợ sẵn cho RDS và cho phép viết custom Lambda function để xoay vòng cho mọi loại tài nguyên khác.
• **Audit log đầy đủ qua CloudTrail:** Mọi thao tác đọc/ghi đều được ghi log lại — đúng chuẩn những gì mà kiểm toán viên SOC 2 yêu cầu.
**Quy trình migration không gián đoạn (Zero-downtime):** 
Chỉ cần thay thế các biến môi trường (`env vars`) bằng các lời gọi hàm `getSecretValue()`, deploy code lên, và tiến hành rotate (đổi mới) credential cũ sau khi đã xác nhận credential mới hoạt động ổn định. 
**Chi phí:** ~0.40 USD/secret/tháng. Với 20 secrets, tổng chi phí chỉ khoảng 8 USD/tháng.

**B — HashiCorp Vault (Cái bẫy của Senior Engineer)**

Vault sở hữu tính năng cực kỳ mạnh mẽ — **Dynamic secrets** (tạo mới thông tin xác thực Postgres cho từng request và tự hủy sau 1 giờ) là một trong những design pattern thanh lịch nhất trong hạ tầng production.
Nhưng hãy nhớ: Vault là hạ tầng tự thân vận động (self-hosted). Bạn sẽ phải quản lý một cụm Raft (từ 3 node trở lên), một storage backend, quy trình unseal (mở khóa), lập kế hoạch Disaster Recovery (phục hồi thảm họa), và cần một team ops hiểu sâu về Vault. Nếu Vault sập, các dịch vụ không lấy được secret và sẽ đồng loạt tạch.
**Khi nào nên dùng Vault:** Khi chạy hệ thống multi-cloud (đa mây), có yêu cầu on-premise, cần dùng dynamic secrets ở quy mô lớn, hoặc công ty bạn có sẵn một infra team chuyên trách. Còn nếu bạn đang thuần dùng AWS và quy mô dưới 50 kỹ sư — hãy ưu tiên dùng AWS Secrets Manager trước, không phải bàn cãi.


 **C — Inject Biến môi trường qua CI/CD (Đúng một phần, nhưng dùng sai ngữ cảnh)**

Các secret trên GitHub Actions hay GitLab CI là nơi hoàn hảo cho các secret dùng trong **build-time** và **deploy-time** — ví dụ như Docker Hub credentials, Terraform token, hoặc deploy key.
Nhưng chúng lại cực kỳ sai lầm nếu dùng cho **runtime secrets** — chẳng hạn như mật khẩu DB mà ứng dụng cần gọi lúc 3 giờ sáng, hay Stripe API key cho webhook đang chạy thật. Nếu nhét chúng vào biến môi trường (env vars) của ECS task definition hay Lambda config, bạn sẽ cực khó rotate (đổi mới) một cách atomic (đồng bộ tức thời), và hoàn toàn không có audit trail (dấu vết kiểm toán) xem ai đã truy cập secret lúc runtime.
Phương án C chỉ nên dùng để bổ trợ cho A hoặc B, chứ không thể thay thế chúng.

 **D — Tự dựng KMS + Tự làm Database riêng (Sai lầm)**

Cách này chẳng khác nào đi "tái phát minh cái bánh xe" nhưng làm tệ hơn AWS Secrets Manager. Giờ đây bạn phải tự gánh toàn bộ đống này: quản lý encryption key (khóa mã hóa), logic rotate, access control (kiểm soát truy cập), audit logging, và quan trọng là phải tự quản lý cái database vốn dĩ... cũng cần có secret để kết nối tới.
Vấn đề cốt lõi ở đây là: *Lấy cái gì để bảo vệ cái kho chứa secret?* Bạn sẽ rơi vào cái bẫy "bootstrapping" (gà có trước hay trứng có trước) mà các dịch vụ managed secret (quản lý sẵn) sinh ra là để giải quyết triệt để vấn đề này. Đây là kiểu kiến trúc mà các team công nghệ hay tự dựng từ năm 2012, thời mà các giải pháp managed service chưa xuất hiện.