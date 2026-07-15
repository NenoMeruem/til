
Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your Redis cache just expired on a key that 8,000 users hit every second.



![[Pasted image 20260715143720.png]]


### Khi Redis Cache bị "Thundering Herd" (Hiệu ứng đàn gia súc): Database của bạn đang gặp nguy!

Redis cache của bạn vừa hết hạn (expire) một key mà mỗi giây có tới 8.000 user truy vấn vào.

Kết quả là: Tất cả 8.000 request đó đồng loạt "đâm thẳng" vào database (DB).

Đây chính là hiện tượng **Thundering Herd** (hiệu ứng đàn gia súc). Ban đầu bạn không hề bị quá tải traffic, bạn chỉ gặp vấn đề về cache. Nhưng bây giờ, bạn "dính" cả hai.

**Setup hệ thống hiện tại:**
*   **Service:** Node.js API, xử lý 8.000 req/sec tại endpoint `/feed`.
*   **Cache:** Redis, TTL = 60s cho key feed.
*   **DB:** Postgres, ngưỡng chịu tải ổn định ở mức ~200 req/sec.

**Sự cố:** TTL hết hạn đúng lúc traffic đạt đỉnh (peak), toàn bộ 8.000 req/sec đổ dồn vào Postgres cùng một lúc.

DB của bạn đang "quỳ gối" và chỉ còn vài phút trước khi sập hoàn toàn. Đáng sợ hơn, 60 giây nữa TTL lại hết hạn lần tiếp theo. 

**Bạn sẽ xử lý thế nào?**

*   **A) Mutex Lock:** Chỉ cho phép 1 request duy nhất truy vấn DB để rebuild cache, các request còn lại phải chờ (wait) phía sau.
*   **B) Probabilistic Early Expiry:** Tính toán xác suất để chủ động rebuild cache ngẫu nhiên trước khi TTL thực sự về 0.
*   **C) Request Coalescing:** Gộp tất cả các request đang "in-flight" cho cùng một key thành một query duy nhất, sau đó trả kết quả giống nhau cho tất cả.
*   **D) Cache Pre-warming:** Dùng background job để rebuild key theo lịch trình, đảm bảo TTL không bao giờ thực sự về 0 trên production.

Cả 4 phương án trên đều được áp dụng trong các hệ thống thực tế. Tuy nhiên, **chỉ có duy nhất 1 phương án** ngăn chặn được *thundering herd* mà không gây ra lỗi mới khi hệ thống chịu tải cao.

**Hãy chọn một phương án A, B, C, hoặc D và giải thích lý do.** (Tôi sẽ có phân tích chi tiết bên dưới, bao gồm cả việc đâu là "cái bẫy" dành cho Senior Engineer: phương án nghe thì lý thuyết rất hay nhưng thực tế lại "vỡ trận" khi 8.000 request đang xếp hàng chờ).

Nếu team của bạn từng để cache expiry làm sập database, hãy share bài viết này cho họ. Sự tranh luận về vấn đề này còn giá trị hơn cả nội dung bài viết.

**Bạn chọn phương án nào? Hãy comment xuống dưới 👇**


**Đáp án: D — Cache pre-warming (Làm nóng bộ nhớ đệm trước) ✅**


![[Pasted image 20260715143913.png]]

Dưới đây là lý do tại sao phương án này thắng thế, và tại sao ba phương án còn lại dễ gây nhầm lẫn cho các kỹ sư:

### Tại sao D là phương án tối ưu (Cache pre-warming)?

**Cache pre-warming** triệt tiêu hiện tượng **"thundering herd"** (hiệu ứng đám đông gây sập hệ thống) ngay từ gốc. Thay vì để cache tự hết hạn, một background job (có thể là cron job, một hàm Lambda được lập lịch, hoặc Sidekiq worker) sẽ thực hiện việc tái thiết lập (rebuild) cache key theo một chu kỳ cố định, với khoảng thời gian ngắn hơn thời gian **TTL** (Time To Live). Nhờ đó, cache key sẽ không bao giờ rơi vào trạng thái "lạnh" (cold). Bạn sẽ không bao giờ gặp phải "vách đá hết hạn" (expiry cliff), nơi hàng nghìn request đổ dồn vào database cùng lúc.

Bạn đã nắm rõ dữ liệu nào là "hot data", bạn biết khi nào nó hết hạn, và bạn có đủ tài nguyên tính toán để chủ động tái tạo nó. Chi phí chỉ là một background job chạy mỗi ~45 giây; đổi lại, database của bạn sẽ không bao giờ phải chịu các đợt spike (tăng đột biến) về tải. Netflix sử dụng kỹ thuật này để làm nóng metadata nội dung; Twitter làm nóng timeline cho các tài khoản có lượng follower lớn. Đây là một pattern cực kỳ phổ biến — chỉ là nó không đủ "bóng bẩy" để xuất hiện trên các bài viết về kiến trúc hệ thống hiện nay.

**Một chi tiết quan trọng cần lưu ý:** Hãy kết hợp nó với chiến lược **stale-while-revalidate**. Bạn vẫn phục vụ dữ liệu cũ (stale) trong khi background job đang thực hiện refresh, nhờ đó nếu việc tái tạo dữ liệu có bị chậm trễ một chút, hệ thống vẫn không bị tình trạng cache miss (trượt cache).


Dưới đây là bản dịch đã được tinh chỉnh bằng các thuật ngữ chuyên ngành (jargon) phổ biến trong kỹ thuật phần mềm để giúp bạn dễ dàng tiếp cận vấn đề:


### Tại sao phương án C (Request Coalescing) là cái bẫy:

**Request Coalescing** (Gộp yêu cầu) nghe có vẻ rất "xịn": gom tất cả các concurrent request (yêu cầu đồng thời) cùng truy vấn vào một key thành một query duy nhất gửi xuống Database (DB), sau đó trả kết quả đó cho tất cả các bên. Không lo **Cache Stampede** (hiệu ứng đám đông làm sập cache), không lo **Lock contention** (tranh chấp khóa). Rất thanh thoát.

**Vấn đề nằm ở đây:** Coalescing đòi hỏi cơ chế **in-process coordination** (điều phối nội bộ tiến trình). Nó hoạt động hoàn hảo trên một server đơn lẻ. Nhưng nếu bạn có 50 instance Node.js chạy sau Load Balancer, mỗi instance sẽ thực hiện coalescing độc lập. Thay vì 8,000 query, bạn vẫn có 50 query đồng thời đổ vào DB. Tuy có cải thiện, nhưng mỗi khi **TTL expiry** (hết hạn cache), bạn vẫn gặp tình trạng **spike** (tăng đột biến) gấp 50 lần. Để gộp yêu cầu xuyên suốt các instance, bạn cần một **distributed coordination layer** (tầng điều phối phân tán), và lúc này bạn lại đang xây dựng một thứ phức tạp gần bằng **Mutex** mà lại mất đi sự đơn giản ban đầu.

Đây là giải pháp đúng cho kiến trúc đơn tiến trình (single-process), nhưng ở quy mô hệ thống lớn (scale), nó chỉ là giải pháp chắp vá mà các kỹ sư thường tự huyễn hoặc là "đã xong".

### Tại sao phương án A (Mutex lock) lại sai:

**Mutex lock** (Khóa tương hỗ) nhìn rất gọn: chỉ một request lấy được lock để rebuild cache, các request còn lại phải đợi. Không bao giờ xảy ra duplicate query xuống DB.

Vấn đề là ở chỗ "các request còn lại phải đợi". Với lưu lượng 8,000 req/sec, việc đợi đồng nghĩa với **API threads** bị block, **request queue** bị đầy, và **p99 latency** sẽ vọt lên hàng giây. Bạn vừa đánh đổi việc quá tải DB bằng việc làm nghẽn tầng ứng dụng. Database thì sống, nhưng trải nghiệm người dùng (UX) thì "chết". Thêm nữa, nếu tiến trình giữ lock chạy chậm (do DB đang tải cao, việc rebuild mất 500ms), thì toàn bộ request trong hệ thống sẽ bị treo trong khoảng thời gian đó.

### Tại sao phương án B (Probabilistic early expiry) lại sai:

**XFetch** hay **Jitter-based expiry** (hết hạn dựa trên xác suất) rất thông minh: khi TTL đếm ngược, mỗi lượt đọc cache sẽ có một xác suất ngẫu nhiên để kích hoạt rebuild sớm. Không cần lock, không cần tầng điều phối. Toán học rất thanh thoát.

Vấn đề là nó dựa trên **xác suất** (probabilistic), không phải sự **đảm bảo** (guaranteed). Trong trường hợp xấu nhất (lưu lượng thấp ngay trước khi hết TTL, sau đó tăng đột biến), key vẫn sẽ bị expire trong trạng thái "lạnh" (cold). Bạn đã giảm được xác suất xảy ra **thundering herd** (hiệu ứng đám đông) nhưng không loại bỏ triệt để nó. Với một endpoint chạy 8,000 req/sec liên tục 24/7, bạn cần một sự đảm bảo **deterministic** (có tính xác định), chứ không thể dựa vào vận may.