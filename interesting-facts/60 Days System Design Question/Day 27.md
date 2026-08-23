Nodes: [[60 Days System Design Question]]
Tags: #system-design 

### Your LLM answers are wrong. Not hallucination-wrong — outdated-wrong.


![[Pasted image 20260818115647.png]]




**Câu trả lời từ LLM của bạn đang bị sai. Không phải sai do "ảo giác" (hallucination), mà sai vì... lỗi thời (outdated).**

Bạn vừa triển khai một chatbot chăm sóc khách hàng chạy trên nền tảng GPT-4. Model này được train với dữ liệu截止 (cutoff data) đến đầu năm 2024. Sản phẩm của bạn đã thay đổi 14 lần kể từ đó đến nay. Mỗi tuần, người dùng vẫn nhận được những câu trả lời từng rất chuẩn xác vào 8 tháng trước, nhưng lại hoàn toàn sai bét ở thời điểm hiện tại.

Team đang tranh cãi nảy lửa về giải pháp fix lỗi này.

**Dưới đây là sơ đồ kiến trúc hiện tại:**
*   **NestJS API** $\rightarrow$ **OpenAI GPT-4** + **PostgreSQL** (chứa Knowledge Base về sản phẩm)
*   Khoảng **2.000 lượt support query/ngày**, trong đó **15% trả về kết quả sai** do dính dữ liệu cũ (stale knowledge).
*   **Knowledge base cập nhật hàng tuần** — gồm bảng giá mới, tính năng mới, và các user flow đã bị deprecated (khai tử).
*   **Ngân sách:** Startup quy mô trung bình, không đủ tiềm lực để train custom model từ đầu (from scratch).

**Yêu cầu:** Bạn cần câu trả lời chuẩn xác, luôn cập nhật (up-to-date) mà không cần phải re-train lại model mỗi khi sản phẩm có update.

**Bạn sẽ chọn phương án nào?**

*   **A) RAG (Retrieval-Augmented Generation):** Vector hóa (embed) knowledge base, query và retrieve các chunk dữ liệu liên quan tại thời điểm runtime, sau đó inject vào context window. Model giữ nguyên, nhưng knowledge base thì luôn "fresh".
*   **B) Fine-tune base model:** Fine-tune GPT-4 (hoặc một open-source model tương đương) bằng tài liệu sản phẩm của bạn. Model sẽ internalize (nội tâm hóa/ghi nhớ sâu) domain kiến thức này.
*   **C) Fine-tune + RAG Hybrid:** Fine-tune để chuẩn hóa style/tone/domain fluency (độ trôi chảy trong ngành), kết hợp RAG để đảm bảo tính xác thực về mặt fact (factual grounding). Lợi cả đôi đường.
*   **D) Chỉ dùng Prompt Engineering:** Viết system prompt chi tiết + vài ví dụ dạng few-shot. Không cần dựng thêm infra, không cần training, chỉ tối ưu câu lệnh.

Cả 4 phương án trên đều đang được áp dụng trong môi trường Production ở đâu đó ngoài kia. Nhưng chỉ có **một** phương án thực sự giải quyết được bài toán trước mắt của bạn.

Hãy chọn một — **A, B, C, hoặc D** — và giải thích lý do. Mình sẽ thả bản phân tích chi tiết (full breakdown) ở phần comment (bao gồm cả phương án nghe có vẻ xịn xò nhất, nhưng thực chất lại làm cho bài toán "dữ liệu cũ" trở nên trầm trọng hơn chứ không hề khá hơn).

Nếu team của bạn đang tranh luận nảy lửa về RAG và Fine-tuning, hãy share bài này ngay. Việc mapping lại các đánh đổi (tradeoff) là cực kỳ cần thiết trước khi bạn quyết định "đốt" resource vào một architecture nào đó.


**Đáp án: A — RAG (Retrieval-Augmented Generation)**

![[Pasted image 20260818142840.png]]

Vấn đề nằm ở tính **freshness** (độ mới của dữ liệu) — mô hình không biết những gì đã thay đổi, chứ không phải nó không hiểu domain (lĩnh vực/ngành hàng) của bạn.

RAG tách rời phần **knowledge** (tri thức) ra khỏi phần **reasoning** (khả năng suy luận). Mô hình AI được giữ nguyên trạng (frozen) — không tốn chi phí **retraining** (huấn luyện lại), không mất chu kỳ **deployment** (triển khai). Knowledge base (cơ sở tri thức) của bạn được lưu trong một **vector store** (kho lưu trữ vector) — khi cần, chỉ cần cập nhật tài liệu, tiến hành **re-embed** (nhúng lại vector) là xong. Ví dụ, thứ Hai tới có bảng giá mới, thì ngay thứ Hai chatbot của bạn đã nắm được thông tin đó.

Tại **runtime** (thời gian chạy): người dùng đặt câu hỏi $\rightarrow$ **embed query** (chuyển câu hỏi thành vector) $\rightarrow$ **retrieve** (truy xuất) các **top-K relevant chunks** (các đoạn văn bản liên quan nhất) $\rightarrow$ **inject** (tiêm/đưa) vào **context** ( ngữ cảnh) $\rightarrow$ mô hình sẽ **reason** (suy luận) dựa trên nội dung mới nhất và chính xác đó.

Bạn đã chuyển một bài toán về mô hình AI phức tạp thành một bài toán về **data pipeline** (luồng xử lý dữ liệu). Mà đây lại là bài toán mà bất kỳ **engineering team** (đội ngũ kỹ thuật) nào cũng đã biết cách giải quyết.

**B — Fine-tuning (Đáp án bẫy)**

Nghe có vẻ là một bản nâng cấp hiển nhiên, nhưng lại làm vấn đề trở nên tồi tệ hơn.
Fine-tuning (Tinh chỉnh) "nướng" (bake) kiến thức trực tiếp vào các trọng số (**weights**) của mô hình. Các trọng số này là tĩnh (static) cho đến khi bạn tiến hành huấn luyện lại (**retrain**). Cứ mỗi tuần sản phẩm có update đồng nghĩa với việc bạn phải retrain hàng tuần, tốn kém cả chi phí lẫn thời gian, kèm theo rủi ro hiện tượng "quên thảm khốc" (**catastrophic forgetting** — dữ liệu huấn luyện mới có thể làm giảm khả năng truy xuất nội dung cũ nếu không được quản lý kỹ lưỡng).
Fine-tuning là giải pháp đúng đắn cho các thay đổi về *hành vi* (**behavioral changes**) — như giọng điệu, định dạng, độ thông thạo miền dữ liệu, hoặc biệt ngữ nội bộ. Nó dạy mô hình *cách hành xử*, chứ không phải *kiến thức là gì*. Đây là một công cụ sai lầm cho bài toán dữ liệu mới (**freshness problem**).

**C — Kết hợp Fine-tune + RAG (Dùng dao mổ trâu giết gà / Overkill)**
Đây thực sự là một kiến trúc mạnh mẽ — nhưng nó là bước 3, không phải bước 1.
Bạn không thể fine-tune để tạo phong cách một cách hiệu quả nếu nền tảng sự thật (**factual grounding**) của bạn chưa vững chắc. Mô hình lai (**hybrid**) này là thứ bạn hướng tới *sau khi* đã triển khai RAG một cách mượt mà và chạm trần giới hạn của việc chỉ dùng retrieval (truy xuất) đơn thuần.
Đối với một startup đang gặp tỷ lệ trả lời sai 15% do dữ liệu lỗi thời, việc triển khai một hệ thống hybrid là dự án kéo dài 3 tháng, trong khi một giải pháp RAG làm trong 2 tuần đã có thể giải quyết dứt điểm vấn đề thực tế.

**D — Chỉ dùng Prompt Engineering (Nhanh đụng trần)**
Triển khai nhanh nhất, nhưng cũng là thứ dễ gãy đổ đầu tiên.
Một system prompt chi tiết có thể thiết lập giọng điệu và định dạng, nhưng nó không thể "nhồi nhét" 400 trang tài liệu sản phẩm mới cập nhật mà không chạm trán giới hạn **token limit**. Hơn nữa, việc thủ công lựa chọn tài liệu nào để đưa vào chẳng khác nào làm RAG nhưng lại thiếu đi hạ tầng retrieval (truy xuất dữ liệu).

Prompt engineering chỉ phát huy hiệu quả khi bản thân mô hình đã biết những gì nó cần biết. Nó hoàn toàn bất lực trong việc lấp đầy lỗ hổng kiến thức (**knowledge gap**).