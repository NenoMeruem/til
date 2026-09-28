Nodes: [[60 Days System Design Question]]
Tags: #system-design 


# Your LLM has 128K tokens.



![[Pasted image 20260928141730.png]]


**LLM của bạn có context window là 128K tokens.**

**Tài liệu của bạn dài 150K từ.**

Chắc chắn hệ thống sẽ bị quá tải (overflow). Bạn sẽ xử lý thế nào?

*   **A) Chunking tài liệu thành các fixed-size chunks (khối có kích thước cố định) và tạo embedding cho từng khối** — sau đó dùng thuật toán Retrieval để lấy top-k kết quả phù hợp nhất tại thời điểm query.
*   **B) Dùng sliding window (cửa sổ trượt)** — xử lý tài liệu bằng các chunk có chồng lấp (overlap) lên nhau, sau đó stitch (ghép nối) các output lại.
*   **C) Summarize (tóm tắt) tuần tự từng phần** — truyền dồn (feed-forward) bản tóm tắt tích lũy (running summary) làm context cho bước tiếp theo.
*   **D) Truncate (cắt bớt)** dữ liệu, chỉ giữ lại các token gần nhất và cầu nguyện rằng câu trả lời nằm ở cuối văn bản.

Có 3 phương pháp trong số này là chiến lược thực tế mà các engineering team vẫn đưa vào môi trường **production**. Và có đúng 1 phương pháp sẽ âm thầm trả về **kết quả sai** đối với một tập hợp các câu hỏi mang tính đặc thù.

Hãy chọn một phương án — và cho tôi biết bạn thực sự sẽ áp dụng phương án nào cho một **hợp đồng pháp lý dài 200 trang** mà câu trả lời có thể nằm ở bất cứ đâu trong đó?


**Tại sao Phương án A thắng thế (RAG với cơ chế chia nhỏ Embedding - Chunked Embeddings)**

![[Pasted image 20260928152214.png]]

Bạn tiến hành cắt nhỏ (split) tài liệu thành các đoạn chồng lấp lên nhau (overlap chunks, khoảng ~500 token, với độ chồng lấp ~10–20%), chuyển đổi từng đoạn thành vector (embed), lưu trữ chúng trong một Vector Database (như Pinecone, pgvector, Qdrant), và thực hiện truy vấn (retrieve) top-k kết quả phù hợp nhất khi có câu hỏi (query time).

Phương án này có khả năng scale (mở rộng quy mô) cho mọi kích thước tài liệu. Tại thời điểm suy luận (inference), ngữ cảnh (context) của LLM chỉ phải xử lý các chunk đã được truy xuất — nhờ đó luôn nằm trong giới hạn của cửa sổ ngữ cảnh (context window). Độ trễ (latency) được duy trì ở mức thấp vì quá trình retrieval thực chất là một thuật toán tìm kiếm lân cận gần đúng (ANN lookup - Approximate Nearest Neighbor) cực nhanh thay vì phải quét tuần tự (sequential scan).

**Điểm mù (The catch):** 
Việc phân chia ranh giới các chunk (chunking boundaries) làm phá vỡ tính mạch lạc ngữ cảnh (semantic coherence). Lấy ví dụ, nếu một mệnh đề bắt đầu từ trang 12 và kết thúc (hoặc được giải quyết) ở trang 13, thì việc cắt cứng (hard chunk boundary) giữa hai trang này sẽ khiến không có chunk nào cung cấp đủ ngữ nghĩa để hệ thống retrieval tìm ra câu trả lời chính xác cho câu hỏi đó. 

Đây là lý do tại sao việc tinh chỉnh kích thước chunk (chunk size) và độ chồng lấp (overlap) lại đóng vai trò tối quan trọng. Hầu hết các team lập trình đều đánh giá thấp vấn đề này.

**Giải pháp cho môi trường Production:** 
Hãy thực hiện chia chunk dựa trên ranh giới của câu (sentence) hoặc đoạn văn (paragraph), thay vì đếm số lượng ký tự (character counts). Ngoài ra, hãy áp dụng phương pháp truy vấn lai (Hybrid retrieval - kết hợp giữa tìm kiếm theo từ khóa keyword và tìm kiếm theo ngữ nghĩa semantic) để xử lý các trường hợp biên (edge cases).


**Tại sao đáp án B là một "cái bẫy" (Kỹ thuật Cửa sổ trượt - Sliding Window):**

Cửa sổ trượt (sliding window) thoạt nhìn có vẻ rất thanh thoát: xử lý tài liệu bằng các lượt quét chồng lấp nhau (overlapping passes) rồi gom kết quả lại. Nhưng thực tế, nó không giải quyết được bài toán **giới hạn ngữ cảnh (context window)**. Bạn vẫn phải xử lý tuần tự từng *chunk* (khúc dữ liệu), và nếu câu hỏi nằm rải rác giữa *chunk 1* và *chunk 47*, nó sẽ bị bỏ sót. 

Hơn nữa, bạn đang phải gọi LLM với độ phức tạp thời gian là $O(n)$ cho mỗi *query* (truy vấn). Với một tài liệu dài 150.000 từ và tốc độ 3 giây cho mỗi lần gọi API, bạn sẽ mất tới vài phút chỉ để trả lời một truy vấn. Sẽ chẳng có team nào đưa một giải pháp thế này lên *production* (môi trường vận hành thực tế) để làm hệ thống Hỏi - Đáp (QA) trên tài liệu lớn cả.

Phương pháp này chỉ chạy ổn với các tác vụ **tóm tắt (summarization)** — nơi đầu ra của *chunk N* được feed (truyền) tiếp vào *chunk N+1*. Còn dùng cho việc *retrieval* (truy xuất thông tin)? Sai công cụ hoàn toàn.

**Tại sao đáp án C đôi khi lại hiệu quả (Tóm tắt lũy tiến - Progressive Summarization):**

Để tóm tắt một tài liệu dài 200 trang? Rất chắc tay. Bạn áp dụng mô hình *map-reduce* cho tài liệu: tóm tắt từng phần nhỏ, sau đó tiếp tục tóm tắt các bản tóm tắt đó. GPT-4o làm việc này rất tốt.

Nhưng để trả lời một câu hỏi cụ thể về điều khoản 38(b) ở trang 97 thì sao? Không đời nào. Bản tóm tắt trung gian đã nén và làm mất đi các chi tiết cụ thể mà bạn đang cần. Việc áp dụng *nén mất mát* (lossy compression) vào bài toán truy xuất thông tin là một sự nhầm lẫn về mặt bản chất (*category error*).

Hãy dùng tóm tắt lũy tiến khi bạn muốn có một cái nhìn tổng quan (high-level understanding). Đừng dùng nó khi bạn cần các *fact* (sự thật/chi tiết cụ thể) sống sót được đến cuối *pipeline* (luồng xử lý).

**Tại sao đáp án D sai hoàn toàn (nhưng lại cực kỳ phổ biến đến ngạc nhiên):**

Cắt bớt (truncate) dữ liệu cho đến khi vừa đủ $N$ *token* cuối cùng là hành vi mặc định của hầu hết các *wrapper* API LLM khi bạn vượt quá giới hạn ngữ cảnh mà không xử lý thủ công. Nhiều team đã vô tình đưa code này lên production mà không hay biết.

Vấn đề lớn hơn ngoài việc mất dữ liệu hiển nhiên, đó là LLM gặp lỗi **“lạc trôi ở giữa” (Lost in the Middle failure mode)** (theo Liu et al., 2023). Hiệu suất của các tác vụ truy xuất đạt mức cao nhất khi câu trả lời nằm ở đầu hoặc cuối cửa sổ ngữ cảnh — và sẽ sụt giảm nghiêm trọng nếu thông tin bị chôn vùi ở chính giữa. Thế nên, ngay cả khi bạn cố nhồi nhét mọi thứ vào ngữ cảnh, *thứ tự vị trí (position)* vẫn đóng vai trò quyết định.

Việc cắt bớt dữ liệu (truncation) càng làm trầm trọng thêm vấn đề này — bạn không chỉ bị mất dữ liệu, mà còn mất một cách vô định, không kiểm soát được.

