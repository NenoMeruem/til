

### Bài toán Rate Limiting: Tại sao hệ thống của bạn đang "thở oxy"?

![[Pasted image 20260623111723.png]]

Bạn đang vận hành một hệ thống SaaS API. Endpoint `POST /v1/messages`chính là "cần câu cơm" của bạn.

**Cấu hình hiện tại:** Giới hạn 100 requests/phút cho mỗi API key. Tuy nhiên, khách hàng liên tục gặp lỗi **429 Too Many Requests** ngay tại thời điểm giao phút, mặc dù tính trung bình RPS (Requests Per Second) của họ vẫn thấp hơn nhiều so với hạn mức (cap).

**Thực trạng tại Production:**

- **12:59:58:** Khách hàng gửi 90 requests (do job được kích hoạt theo batch).
- **13:00:02:** Vẫn khách hàng đó gửi tiếp 90 requests (tick tiếp theo).
- **Vấn đề:** Vì bộ đếm (counter) của bạn reset vào đúng 13:00:00, cả hai đợt bùng nổ (burst) này đều được thông qua. Tổng cộng **180 requests chỉ trong 4 giây**. Kết quả là database downstream của bạn bắt đầu quá tải (CPU/IOPS spike).

Hiện tại, team Support đang "ép" bạn xử lý lỗi 429, còn team SRE đang "réo" vì traffic spikes. Bạn cần thay thế thuật toán Rate Limiter ngay trong tuần này.

**BỐN PHƯƠNG ÁN ĐƯỢC ĐƯA RA:**

- **A) Fixed Window:** Mỗi `api_key` gắn với một bucket theo từng phút. Cứ request đến thì Increment, check limit, rồi Reject nếu quá. Đơn giản, hiệu năng cao, chỉ cần 1 Redis key cho mỗi user.
- **B) Sliding Window Log:** Lưu lại timestamp của mọi request vào Redis. Mỗi khi có call mới, đếm số request trong 60 giây gần nhất. Độ chính xác lên đến từng millisecond.
- **C) Token Bucket:** Mỗi key có 100 tokens, refill với tốc độ 100/60 per second. Mỗi request tiêu tốn 1 token. Cho phép burst tối đa 100, sau đó traffic sẽ được định hình (shape) theo đúng tốc độ refill.
- **D) Leaky Bucket:** Đưa các request vào một queue, dispatch ra với tốc độ cố định 1.66 requests/giây. Request dư thừa sẽ phải đợi hoặc bị drop.

Cả 4 thuật toán trên đều đang được sử dụng rộng rãi trong production. Tuy nhiên, 3 cái trong số đó là lựa chọn sai cho trường hợp này. Chỉ có 1 phương án là "chuẩn bài" mà các ông lớn như AWS, Stripe và GitHub đang tin dùng.

**Bạn sẽ chọn A, B, C hay D? Hãy giải thích tại sao.** (Phân tích chi tiết sẽ được giải đáp bên dưới, bao gồm cả "cái bẫy" dành cho các Senior Engineer).


**Đáp án: C — Token Bucket ✅**

Dưới đây là lý do tại sao thuật toán này giành chiến thắng và tại sao ba phương án còn lại thường là "cái bẫy" đối với các kỹ sư:

![[Pasted image 20260623112001.png]]


1. **Tại sao C (Token Bucket) lại tối ưu?**

Token Bucket là thuật toán mà AWS API Gateway, Stripe, GitHub và hầu hết các public API trưởng thành hiện nay đang sử dụng. Cơ chế hoạt động: Mỗi API key được cấp một "cái xô" (bucket) chứa 100 tokens, với tốc độ refill (làm đầy) khoảng 1.66 tokens/giây. Mỗi request sẽ tiêu tốn một token. Nếu xô rỗng, hệ thống sẽ trả về lỗi **429 (Too Many Requests)**.

Thuật toán này giải quyết triệt để vấn đề "boundary-burst" (tình trạng dồn ứ tại ranh giới thời gian) vì nó không hề có cơ chế **window reset** (đặt lại hạn ngạch định kỳ). Ví dụ: Nếu người dùng thực hiện một đợt burst (bùng nổ request) lúc 12:59:58, xô sẽ bị rút cạn. Đến 13:00:02, lượng token trong xô vẫn ở mức gần như bằng 0 — chứ không phải được "reset" đầy ắp 100 tokens như các cơ chế Fixed Window cũ.

**Ưu điểm kỹ thuật:**
* **Độ phức tạp:** $O(1)$ về bộ nhớ cho mỗi key và $O(1)$ cho thao tác kiểm tra (check).
* **Khả năng mở rộng:** Dễ dàng triển khai theo cơ chế **distributed** (phân tán) trong hệ thống lớn.

Dưới đây là bản dịch bài viết sang tiếng Việt, sử dụng các thuật ngữ chuyên ngành lập trình/kiến trúc hệ thống để đảm bảo sự chính xác và dễ hiểu đối với các kỹ sư:

2. **Tại sao phương pháp B (Sliding Window Log) lại là một cái bẫy:**
Mặc dù xét về mặt toán học, đây là giải pháp "hoàn hảo", nhưng nó yêu cầu lưu trữ **một bản ghi (entry) trên mỗi request cho mỗi key** trong Redis. Với quy mô 100k active keys, bạn sẽ đối mặt với áp lực cực lớn lên bộ nhớ (memory pressure) và hiện tượng giật lag (latency spikes) ở ngưỡng p99. Những kỹ sư "tưởng là thông minh" thường chọn giải pháp này mà không cân nhắc chi phí bộ nhớ. Đây chính là dấu hiệu của việc thiếu kinh nghiệm thực chiến.

3. **Tại sao phương pháp A (Fixed Window) lại sai:**
Đây chính là lỗi (bug) kinh điển được nhắc đến trong bài viết. Bộ đếm (counter) sẽ reset tại mốc thời gian cố định (ví dụ: đầu phút). Điều này dẫn đến việc người dùng có thể tận dụng kẽ hở để thực hiện số lượng request gấp đôi hạn mức (burst 2x) trong một khoảng thời gian ngắn (chỉ 2 giây). Đây vẫn là sai lầm phổ biến nhất trong các hệ thống production hiện nay.

4. **Tại sao phương pháp D (Leaky Bucket) không phù hợp trong trường hợp này:**
Giải pháp này giải quyết một bài toán khác — nó dùng để định hình **luồng ra (output traffic)** bằng cách đưa các request vào hàng đợi (queue) và xử lý với tốc độ ổn định (constant dispatch rate). Nó rất tốt để bảo vệ các service hạ nguồn (downstream) yếu. Tuy nhiên, nó lại là sai lầm đối với Public API vì nó làm tăng độ trễ (latency) đối với các request hợp lệ nhưng đến cùng lúc (legitimate bursts). 
*   **Token Bucket:** Từ chối (reject) các request vượt quá hạn mức.
*   **Leaky Bucket:** Làm trễ (delay) các request đó.
Đối với Public API, việc **từ chối (reject)** luôn tốt hơn là **làm trễ (delay)**.

### **Giải thích thuật ngữ cho người mới:**
*   **p99 latency:** Độ trễ của 1% các request chậm nhất. Nếu p99 tăng vọt, trải nghiệm người dùng sẽ rất tệ.
*   **Fixed Window:** Cơ chế đếm số lượng request trong một khung giờ cố định (ví dụ 00:00 - 01:00).
*   **Sliding Window Log:** Cơ chế lưu lại dấu thời gian (timestamp) của từng request để tính toán chính xác hơn.
*   **Downstream:** Các dịch vụ phía sau (ví dụ: database hoặc microservice) mà API của bạn cần gọi tới.
*   **Burst:** Hiện tượng lưu lượng truy cập tăng đột biến trong thời gian ngắn.