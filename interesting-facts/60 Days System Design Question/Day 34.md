
### Your AI feature works in the demo.

![[Pasted image 20260827163504.png]]



Tính năng AI của bạn chạy mượt mà trong môi trường **demo**.

Nhưng lại **toang** ở môi trường **production** sau 3 tuần. Không ai chạm vào **model**. Không ai thay đổi **source code**.

Thứ duy nhất thay đổi: **Dữ liệu đầu vào (inputs) ngày càng nhiễu và bẩn hơn.**

Bối cảnh bài toán như sau:

Bạn đang làm việc tại một công ty SaaS, xử lý 50.000 **support ticket (yêu cầu hỗ trợ)** mỗi tuần. Team của bạn xây dựng một hệ thống **AI triage (phân loại tự động)** — sử dụng GPT-4o để phân loại từng ticket vào 6 category (billing, bug, feature request, account access, security, other) nhằm chuyển đến đúng team phụ trách ngay lập tức.

Ở môi trường **dev**, độ chính xác (**accuracy**) đạt 71%. Bạn cần từ 90% trở lên để loại bỏ hoàn toàn việc review thủ công.

**Model** đã được **lock (đóng băng)**. Ngân sách cho **inference (suy luận)** không phải là vô hạn. Bạn buộc phải san lấp khoảng cách 19% độ chính xác này.

Dưới đây là 4 phương án dành cho bạn:

*   **A) Zero-shot với system prompt tốt hơn:** Viết lại **prompt**, bổ sung định nghĩa rõ ràng cho từng category, và quy định cụ thể các **edge case (trường hợp biên)**. Không dùng **example (ví dụ)**.
*   **B) Few-shot prompting:** Thêm 3–5 **labeled example (dữ liệu mẫu đã gán nhãn)** thực tế trực tiếp vào **prompt**. Mỗi ví dụ tương ứng với một **edge case** của category.
*   **C) Chain-of-Thought (Chuỗi suy luận):** Thêm câu lệnh *"think step-by-step before answering"* (hãy suy nghĩ từng bước trước khi trả lời) vào **prompt**. Ép **model** phải **reasoning (lập luận)** qua nội dung ticket trước khi trả về output là category.
*   **D) Self-Consistency (Tính tự nhất quán):** Chạy mỗi ticket qua **model** 5 lần với **temperature = 0.7**, sau đó lấy kết quả **majority vote (bầu cử đa số)** từ các output trả về.

Cùng một **model**. Cùng một ticket. Nhưng mang lại 4 **profile** về **accuracy** và **cost (chi phí)** khác nhau.

Bạn sẽ chọn phương án nào — A, B, C, hay D — và tại sao? Xem phân tích chi tiết ở phần bình luận.


**B — Kỹ thuật Few-shot: Lời giải tối ưu nhất ở đây**
* **Độ chính xác (Accuracy):** 88–93%
* **Chi phí phát sinh:** Gần như bằng 0 (near-zero)
Kỹ thuật **Few-shot prompting** chuyển dịch mô hình từ việc "đọc các rule (quy tắc)" sang **"pattern-matching (khớp mẫu)"** dựa trên các **example (ví dụ thực tế)**. Đây là một **signal (tín hiệu)** mang lại hiệu quả nền tảng mạnh mẽ hơn hẳn.

Sai lầm phổ biến nhất của các team (đội ngũ phát triển) là: Họ chọn những **example** quá hiển nhiên. Một ticket hỗ trợ thanh toán rõ mười mươi. Một bug report chuẩn không cần chỉnh từ sách giáo khoa. Những thứ đó không dạy cho mô hình bất kỳ kiến thức nào mà nó chưa biết.

Điều bạn thực sự cần là **những trường hợp mơ hồ (ambiguous cases)**. Một cái ticket thoạt nhìn tưởng là vấn đề thanh toán, nhưng thực chất lại là quyền truy cập tài khoản. Một yêu cầu tính năng (feature request) nhưng lại đọc ra giống một con bug. Đó chính là những điểm mà mô hình đang fail (xử lý sai) ở thời điểm hiện tại — và đó mới là những **example** giúp san lấp khoảng cách hiệu năng.

Chọn đúng tập dữ liệu mẫu (selection), bạn sẽ giải quyết được phần lớn trong số 19 điểm chênh lệch hiệu năng mà không cần phải can thiệp vào bất cứ thứ gì khác.



**A — Zero-shot với System Prompt được tối ưu tốt hơn**
*Accuracy ceiling (Trần độ chính xác): ~78–82%.*

Đây là điểm xuất phát của mọi team. Bạn liên tục iterate (lặp) lại prompt, bổ sung định nghĩa cho các category (phân loại), và liệt kê các edge case (trường hợp biên/ngoại lệ). Bạn sẽ có cảm giác mọi thứ đang tiến triển tốt. Và đúng là như vậy trong một khoảng thời gian.
Nhưng bạn sẽ đụng phải một bức tường cứng: các instruction (chỉ thị) chỉ có thể *mô tả* category chứ không thể *minh hoạ* cho model thấy các trường hợp ambiguous (mập mờ/nhập nhèm) sẽ rơi vào đâu.
Ví dụ thực tế: Bạn định nghĩa "billing" (thanh toán) là mọi thứ liên quan đến phí hoặc hóa đơn. Sau đó, bạn nhận được ticket này: *"Tôi không đăng nhập được và tháng trước tôi bị trừ tiền hai lần."* Đây là billing? Hay account access (quyền truy cập tài khoản)? Hay cả hai?
Dù bạn có rewrite (viết lại) prompt bao nhiêu lần đi nữa, nó cũng không thể chỉ cho model biết ticket đó phải xếp vào bucket (nhóm/giỏ) nào. Model vẫn sẽ đoán sai từ 20–25% ở các edge case. Mà dataset (tập dữ liệu) của bạn thì ngập tràn edge case. Trần độ chính xác này là có thật và rất khó vượt qua.


**C — Chain-of-Thought (Chuỗi suy luận)**
*Accuracy delta (Biên độ cải thiện độ chính xác): ±2%. Latency (Độ trễ): +200–400ms.*

CoT hiện là kỹ thuật bị áp dụng sai nhiều nhất trong các hệ thống AI production (môi trường vận hành thực tế). Các team thêm câu "hãy suy nghĩ từng bước một" vào mọi thứ. Với một số tác vụ, cách này hiệu quả. Nhưng với bài toán này thì không.
Lý do nó gặp khó ở đây: model sẽ generate (sinh ra) một reasoning chain (chuỗi suy luận), sau đó commit (chốt) một label (nhãn). Với những ticket mập mờ, chuỗi suy luận đó lại trở thành điểm yếu (liability). *"Có nhắc đến khoản phí... nhưng cũng có vấn đề đăng nhập... phí được nhắc đến trước... chắc là billing."* Thế là nó chọn billing. Trong khi đáp án đúng phải là account access.
CoT chỉ phát huy tác dụng khi câu trả lời *được rút ra từ quá trình suy luận* — chẳng hạn như toán học, debugging (gỡ lỗi), hoặc planning (lập kế hoạch). Còn đối với bài toán classification (phân loại), câu trả lời xuất phát từ **calibration (sự hiệu chỉnh/căn chỉnh)**. Suy luận không thể thay thế cho việc hiệu chỉnh.
Bạn chỉ nên layer (chồng) CoT lên trên Few-shot nếu vẫn đang bị sót các edge case. Đừng vội với lấy nó đầu tiên.


**D — Self-Consistency (Tính tự nhất quán)**
*Accuracy (Độ chính xác): 93–96%. Cost (Chi phí): Gấp 5 lần. Latency: Gấp 5 lần.*

Chạy cùng một ticket 5–10 lần với `temperature=0.7`, sau đó lấy majority vote (kết quả đa số). Cách này hiệu quả vì mỗi lần chạy sẽ sample (lấy mẫu) một path (đường đi) hơi khác nhau một chút — noise (nhiễu) sẽ tự triệt tiêu qua các lần chạy.
Về mặt toán học thì rất ổn. Nhưng về mặt chi phí thì cực kỳ tàn khốc (brutal).
50.000 ticket/tuần × $0.002 × 5 lần chạy = **$500/tuần**, so với **$100/tuần** nếu dùng few-shot. Bạn đang phải trả thêm $400 mỗi tuần chỉ để đổi lấy mức tăng trưởng 3–5% cho các case khó nhằn nhất.

Phương án này chỉ đáng giá khi cái giá của việc đoán sai là rất cao: phát hiện gian lận (fraud detection - bỏ sót một cờ cảnh báo có thể tốn hàng trăm đô), phân loại y tế (chọn sai category = tổn hại thực tế). Còn với việc routing (điều hướng) support ticket, một ticket bị misclassify (phân loại sai) chỉ tốn khoảng ~$0.10 thời gian của human (nhân sự con người) để reroute (điều hướng lại). Hãy dùng phương án B.