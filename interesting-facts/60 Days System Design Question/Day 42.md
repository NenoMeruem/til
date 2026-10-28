
Nodes: [[60 Days System Design Question]]
Tags: #system-design 



### Your AI agent remembered the user’s name.


![[Pasted image 20261026113928.png]]




**AI Agent của bạn vừa nhớ được tên người dùng.** **Nhưng ngay sau đó, nó quên béng mất mình đang phải làm gì.**

Tình huống giả định như sau:

Người dùng yêu cầu Agent: *Đặt chuyến bay rẻ nhất đi New York, tìm khách sạn dưới 150 USD/đêm, sau đó so sánh tổng chi phí chuyến đi.*

Đến bước 3, Agent gọi LLM (Large Language Model) với 8.000 token lịch sử hội thoại thô (raw conversation history) — nhưng nó vẫn trả lời cứ như thể đây mới là lượt tương tác (turn) đầu tiên.

Bạn bắt buộc phải thiết kế một **kiến trúc bộ nhớ (memory architecture)** trước khi đưa ứng dụng lên môi trường Production. Bạn sẽ chọn phương án nào?

*   **A) Chỉ dùng In-context Window (Cửa sổ ngữ cảnh) —** Toàn bộ lịch sử hội thoại nằm trong system prompt. Rất đơn giản. Nhưng sẽ bị "tràn" hoặc ngú ngơ sau khoảng 15 lượt chat hoặc 8.000 token (tùy điều kiện nào đến trước).
*   **B) Vector memory store (Kho lưu trữ vector) —** Embedding các lượt chat cũ, truy xuất top-k kết quả dựa trên độ tương đồng ngữ nghĩa (semantic similarity) tại thời điểm query. Hoạt động rất mượt... cho đến khi từ khóa "chuyến bay đi NYC" kéo nhầm một ký ức về chuyến đi New York từ... kiếp trước lên, thay vì phục vụ tác vụ hiện tại.
*   **C) Episodic memory kết hợp Summarization (Bộ nhớ sự kiện kèm tóm tắt) —** Nén các lượt hội thoại cũ thành các bản tóm tắt sự kiện có cấu trúc (structured event summaries), sau đó nạp (inject) các phần liên quan vào mỗi request. Phức tạp hơn để xây dựng. Nhưng cực kỳ khó bị nhầm lẫn ngữ cảnh.
*   **D) Redis session state —** Lưu trữ dạng Key-Value có cấu trúc, Agent chủ động đọc/ghi một cách tường minh (explicit reads/writes). Rất deterministic (tính tất định cao). Đổi lại, bắt buộc Agent phải tự biết mình cần lưu cái gì và lưu vào thời điểm nào.

Một trong số các cách trên sẽ sập nguồn sau 15 lượt chat. Một cách sẽ retrieve (truy xuất) nhầm context vào đúng cái thời điểm trớ trêu nhất. Và chỉ có một cách là **đáp án đúng** dành cho các task-oriented agent (Agent chuyên xử lý tác vụ).

Bạn chọn **A, B, C hay D** — và bạn đã từng "cắn" (gặp lỗi này) ở dự án Production nào chưa? Phân tích chi tiết ở phần bình luận!



Dưới đây là bản dịch sang tiếng Việt, sử dụng các thuật ngữ chuyên ngành lập trình và kiến trúc AI, được trau chuốt để lập trình viên dễ đọc, dễ hiểu và dễ ứng dụng:


**C — Bộ nhớ theo ngữ cảnh (Episodic Memory) kết hợp tóm tắt (Summarization)**


![[Pasted image 20261026114510.png]]


**Giải pháp tối ưu cho các tác vụ Agent (Task-oriented Agents).** Luồng hoạt động (pattern):

→ Giữ lại $N$ lượt hội thoại (turns) gần nhất trực tiếp trong **Context Window** (Bộ nhớ ngắn hạn - Short-term memory).

→ Nén các lượt hội thoại cũ hơn thành các bản tóm tắt sự kiện có cấu trúc (Bộ nhớ dài hạn/Episodic memory).

→ Chỉ **inject** (tiêm/nạp) các bản tóm tắt thực sự liên quan vào mỗi request mới.

Đây là kiến trúc chuẩn mà các production agent tại Anthropic, LangChain Memory v2 và OpenAI Assistants API đều hướng tới. Đòi hỏi nhiều công sức thiết kế và engineering ở giai đoạn đầu — nhưng là pattern duy nhất suy giảm hiệu năng một cách mượt mà (degrades gracefully) khi hệ thống scale lớn.


**A — Chỉ dùng Context Window**

Sụp đổ rất nhanh (Collapses fast). Khoảng 15 lượt hội thoại hoặc 8K tokens là bạn bắt đầu phải **truncate** (cắt bớt) ngữ cảnh cũ hoặc chạm **token limit** của mô hình. Chỉ phù hợp để làm demo. Sẽ thất bại với các production agent thực hiện tác vụ đa bước (multi-step tasks). 

Lập luận kiểu *"cứ tăng độ dài context lên là được"* đã bỏ qua bài toán về **cost** (chi phí API) và hiện tượng **lost-in-the-middle** (mất tập trung ở giữa ngữ cảnh) — LLM thường xuyên bỏ sót các thông tin nằm ở chính giữa các prompt quá dài.

 **B — Vector Memory Store (Lưu trữ bộ nhớ qua Vector DB)**

Bài toán **retrieval** (truy xuất) khoai hơn vẻ bề ngoài của nó rất nhiều. **Semantic similarity** (độ tương đồng ngữ nghĩa) không đồng nghĩa với **task relevance** (tính liên quan đến tác vụ). 

Trong một tác vụ đặt phòng đa bước, việc **embedding** câu *"tìm khách sạn dưới $150"* có thể kéo nhầm một memory từ một user session khác — hoặc từ một cuộc hội thoại cũ ở một thành phố hoàn toàn khác. Rất tối ưu để **knowledge retrieval** (truy xuất tri thức), nhưng cực kỳ kém ổn định khi dùng để lưu **procedural task state** (trạng thái tiến trình của tác vụ).


**D — Redis Session State**

Rất ổn định và **deterministic** (mang tính tất định). Điểm đánh đổi (catch): Agent phải chủ động quyết định thời điểm nào cần ghi dữ liệu gì vào **state**, và khi nào cần đọc ra. 

Đây là một bài toán thiết kế không hề tầm thường — bản chất là bạn đang tự xây dựng một **working memory protocol** (giao thức bộ nhớ làm việc) chồng lên trên các **tool calls** (lời gọi công cụ) của agent. Đa phần các dev team đều đánh giá thấp độ phức tạp của việc thiết kế **schema** (lược đồ dữ liệu) cho phương pháp này.