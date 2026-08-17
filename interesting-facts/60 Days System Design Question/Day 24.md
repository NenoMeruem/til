
Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Your API returns 10 million orders.


![[Pasted image 20260817134652.png]]


### API của bạn trả về 10 triệu đơn hàng.

Frontend gọi API yêu cầu: “Trang 5”.

`Offset 40, limit 10`. Nghe có vẻ đơn giản — cho đến khi DBA nhắn tin cho bạn lúc 2 giờ sáng.

Thời gian thực hiện query: 4.2 giây. Table scan (quét toàn bộ bảng) tăng vọt. Môi trường Production đang bị lag.

Tech stack hiện tại: PostgreSQL, bảng `orders` có 50 triệu rows, được sắp xếp theo `created_at DESC`. Người dùng có thể lọc theo `status`. Bạn đang xây dựng tính năng phân trang cho một trang dashboard quản trị được sử dụng đồng thời bởi 200 support agent.

Offset pagination (phân trang dùng OFFSET) chạy rất mượt khi dữ liệu có 10.000 rows. Nhưng ở mốc 50 triệu rows, database đang phải **đọc và vứt đi 40 triệu rows** chỉ để trả về đúng 10 rows.

Bạn bắt buộc phải fix lỗi này trước khi sprint tiếp theo release phiên bản dành cho khách hàng — dự kiến lượng traffic sẽ tăng gấp 10 lần.

**Cấu hình hệ thống của bạn:**
• **Bảng:** `orders` — 50 triệu rows, đã được đánh index (indexed) trên các cột `created_at`, `user_id`, `status`.
• **Query:** Sắp xếp theo `created_at DESC`, lọc theo `status`.
• **Client:** Cần tính năng điều hướng “Trang trước/Trang sau” + “Nhảy đến trang số X”.
• **SLA:** p99 latency < 200ms.

**Bốn kỹ sư trong team đề xuất 4 giải pháp khác nhau:**

*   **A) Cursor pagination:** Mã hóa `created_at + id` của dòng cuối cùng thành một token, dùng token đó làm mốc cho mệnh đề `WHERE`.
*   **B) Keyset pagination:** Phân trang trực tiếp bằng mệnh đề `WHERE (created_at, id) < (last_created_at, last_id)`.
*   **C) Deferred join:** Query lấy danh sách `id` trước bằng `OFFSET`, sau đó `JOIN` ngược lại để lấy full row.
*   **D) Giữ nguyên offset pagination nhưng tạo một covering index** trên tổ hợp `(status, created_at, id)`.

Cả 4 cách trên đều giúp cải thiện hiệu năng query. Nhưng **chỉ có duy nhất một cách** giải quyết được triệt để bài toán ở quy mô lớn mà không làm hỏng UX (trải nghiệm người dùng) mà dashboard của bạn đang cần.

Hãy chọn một đáp án — **A, B, C, hoặc D** — và giải thích tại sao. Mình sẽ đăng phân tích chi tiết ở phần bình luận (bao gồm cả lý do tại sao một trong các phương án trên thực chất là một "cái bẫy dành cho Senior" — trông thì có vẻ đúng nhưng sẽ sập nguồn ngay khi gặp một ràng buộc ẩn ngay trước mắt).

Nếu team của bạn đang tranh cãi về chiến lược phân trang, đây chính là bài toán bạn cần đưa lên bàn họp. Hãy chia sẻ nó với mọi người nhé!

 **Phương án A — Phân trang bằng Con trỏ (Cursor Pagination) ✅ ĐÁP ÁN ĐÚNG**

![[Pasted image 20260817140250.png]]


Mã hóa cặp giá trị định danh cuối cùng đã thấy `(created_at, id)` thành một **opaque token** (token ẩn/mã hóa mờ). Ở request tiếp theo, giải mã token đó và sử dụng mệnh đề `WHERE created_at < :last_ts OR (created_at = :last_ts AND id < :last_id)` làm điểm mốc (**anchor**) cho truy vấn.

**Lý do phương án này tối ưu:**

• **Query luôn tận dụng được index** tại điểm mốc anchor — không có chuyện quét toàn bảng (**full table scan**), cũng không cần loại bỏ các bản ghi thừa (**discard**).
• **Độ trễ p99** luôn ổn định (flat), cho dù bạn đang ở trang 1 hay trang số 50.000.
• **Hoạt động hoàn hảo với các bộ lọc trạng thái (status filter):** `WHERE status = ‘pending’ AND (created_at, id) < (anchor)`.
• **Con trỏ có tính ổn định về vị trí (position-stable):** Các row mới được insert vào trước vị trí con trỏ của bạn sẽ không làm xê dịch hay lệch trang hiện tại.
**Đánh đổi về mặt UX:** Không hỗ trợ tính năng nhảy đến trang bất kỳ (**jump-to-page**). Chỉ có nút tiến/lùi (previous/next). Tuy nhiên, đây là sự đánh đổi hoàn hảo cho trang dashboard này. Các nhân viên hỗ trợ (support agents) chỉ duyệt dữ liệu tuần tự. Chẳng ai cần phải "nhảy đến trang 3.847" cả.
Với tập dữ liệu **50 triệu rows** đi kèm các bộ lọc đồng thời (**concurrent filters**), phân trang bằng con trỏ là cách tiếp cận duy nhất đảm bảo duy trì độ trễ **p99 < 200ms** một cách đáng tin cậy.

Dưới đây là bản dịch sang tiếng Việt, được tối ưu hóa bằng các thuật ngữ chuyên ngành lập trình và cơ sở dữ liệu để các lập trình viên dễ đọc, dễ tiếp cận và nắm bắt đúng bản chất vấn đề:

**Phương án B — Phân trang theo bộ khóa (Keyset Pagination)** -- ( Cần xem xét )

Nhìn bề ngoài, **Keyset** và **Cursor** trông có vẻ giống hệt nhau. Sự khác biệt ở đây rất tinh tế: Keyset là một *query pattern* (mẫu truy vấn), trong khi Cursor là một *product decision* (quyết định thiết kế sản phẩm).

Keyset sử dụng cấu trúc SQL dạng `WHERE (created_at, id) < (val1, val2)`. Trong khi đó, Cursor đóng gói (wrap) cấu trúc đó thành một *encoded token* (mã thông báo đã mã hóa) mà phía client không thể nhìn thấy hoặc can thiệp (manipulate).

Vấn đề bắt đầu phát sinh ở điểm này: *status filter* (bộ lọc trạng thái) làm hỏng phép so sánh *row-tuple* (bộ giá trị hàng) trong hầu hết các *query planner* (trình tối ưu hóa truy vấn). 

Cụ thể, câu lệnh `WHERE status = 'pending' AND (created_at, id) < (anchor)` sẽ không thể tận dụng hiệu quả một *composite index* (chỉ mục tổng hợp) trong PostgreSQL khi mà cột dùng để so sánh bằng (`status`) không nằm chung trong cụm so sánh tuple. Hệ quả là bạn sẽ gặp hiện tượng quét chỉ mục một phần (*partial index scan*), khiến hiệu năng bị suy giảm nghiêm trọng khi đối mặt với các bộ lọc có *high cardinality* (độ phân giải dữ liệu cao / nhiều giá trị khác biệt).

Ngược lại, **Cursor pagination** xử lý bài toán này bằng cách mã hóa toàn bộ ngữ cảnh của mệnh đề `WHERE`, chứ không chỉ lưu mỗi *positional anchor* (mốc neo vị trí). 

Đó chính là khoảng trống kỹ thuật. Nó rất tinh tế, và chính là cái bẫy sẽ "cắn" bạn ở môi trường *production* (thực tế) chỉ khoảng ba tháng sau khi bạn triển khai code lên hệ thống…



**Giải pháp C — Deferred Join (Join Trì Hoãn)**

```sql
SELECT o.* FROM orders o
JOIN (
  SELECT id FROM orders
  WHERE status = 'pending'
  ORDER BY created_at DESC
  OFFSET 500000 LIMIT 10
) ids ON o.id = ids.id
```

Đây là một kỹ thuật tối ưu hóa hợp pháp (legitimate optimization) cho bài toán phân trang dựa trên `OFFSET` (offset pagination). 

Câu lệnh subquery (truy vấn con) bên trong chỉ fetch (lấy) các trường `id` (vừa vặn với index, do đó tốc độ cực kỳ nhanh). Sau đó, câu lệnh `JOIN` ở bên ngoài mới tiến hành fetch toàn bộ row (dòng dữ liệu) cho đúng 10 record (bản ghi) đó.

Kỹ thuật này là thật. Nó hoạt động tốt. Thậm chí Shopify cũng đang sử dụng một biến thể của phương pháp này.

**Nhưng:** Bạn vẫn phải trả chi phí $O(\text{offset})$ cho câu query bên trong khi người dùng truy cập vào các trang sâu (deep pages). 

Phương pháp này mang tính chất **giảm thiểu** chứ không phải **giải quyết triệt để**. Ở trang số 50.000, database của bạn vẫn phải thực hiện quét (scan) qua 500.000 entry trong index. Nói cách khác, bạn đã cắt giảm được 80% chi phí hiệu năng, nhưng vẫn phải gánh chịu 20% bản chất của vấn đề cũ.

 **Phương án D — Covering Index (Chỉ mục bao phủ)**

Việc bổ sung câu lệnh `CREATE INDEX ON orders(status, created_at DESC, id DESC)` luôn là một giải pháp tối ưu bất kể bạn chọn phương hướng xử lý nào ở trên. Nó giúp loại bỏ hoàn động `heap fetches` (truy vấn trực tiếp vào vùng chứa dữ liệu thô) đối với các câu lệnh truy vấn có lọc theo `status`.

Tuy nhiên, một cái index (chỉ mục) không thể làm thay đổi độ phức tạp thuật toán (algorithmic complexity) của mệnh đề `OFFSET`. Nó chỉ giúp các thao tác `table scan` (quét bảng) diễn ra *nhanh hơn*, chứ không làm *giảm bớt* số lượng bước cần duyệt qua. 

Nói cách khác, đây chỉ là giải pháp "đập tiền mua phần cứng" (throw hardware at it). Nó chỉ mua thêm thời gian cho bạn, chứ không giải quyết tận gốc vấn đề.


