Nodes: [[60 Days System Design Question]]
Tags: #system-design

### 4 chiến lược Database Sharding. 4 kết quả Scaling hoàn toàn khác biệt. Chỉ cần một nước đi sai lầm, bạn sẽ làm "hot shard" Primary Database ngay đúng dịp Black Friday.

![[Pasted image 20260623143540.png]]

Bảng `orders` trong Postgres của bạn vừa cán mốc 500 triệu bản ghi.

Các câu lệnh truy vấn Range scan (quét theo dải) vốn chỉ mất 40ms giờ đây đã lẹt đẹt lên quá 800ms.

Vertical scaling (nâng cấp phần cứng) đã đến giới hạn. Bạn buộc phải Shard.

**Dưới đây là đặc thù workload của hệ thống:**

*   **Dữ liệu:** 500 triệu rows, tăng trưởng 3 triệu rows/tuần.
*   **80% Read:** Truy vấn "danh sách đơn hàng của khách hàng X trong 30 ngày gần nhất".
*   **15% Read:** Các tác vụ Analytics thực hiện JOIN theo dải thời gian.
*   **5% Write:** Tạo đơn hàng mới (400 RPS ổn định, tăng gấp đôi vào các ngày sale).

**Bạn sẽ chọn chiến lược nào?**

*   **A) Hash sharding trên `order_id`:** Phân bổ dữ liệu đều, không bị hotspot (điểm nóng).
*   **B) Range sharding trên `created_at`:** Tối ưu cho các truy vấn theo chuỗi thời gian (time-series) vì dữ liệu nằm cùng một shard.
*   **C) Directory-based sharding:** Sử dụng một bảng lookup để map khách hàng tới shard cụ thể.
*   **D) Consistent hashing với virtual nodes:** Dễ dàng rebalance khi cần scale-up hệ thống.

Cả 4 phương án trên đều là những chiến lược thực tế thường thấy trong môi trường Production. Nhưng chỉ có duy nhất một phương án phù hợp với workload thương mại điện tử, nơi mà 80% truy vấn tập trung vào dữ liệu khách hàng.

Có một phương án "sai" nhưng lại là cái bẫy dành cho các Senior Engineer. Nó nghe có vẻ cực kỳ cao siêu, xuất hiện trong mọi tutorial trên YouTube, nhưng nó sẽ âm thầm "phá hủy" query latency của bạn ngay trên workload này.

Tôi sẽ đưa ra phân tích chi tiết và câu trả lời đúng ở phần comment.

Nếu team bạn đang cân nhắc việc migration database, hãy share bài này — vì rất có thể một thành viên trong team bạn sắp chọn sai chiến lược rồi đấy.

**Còn bạn, lựa chọn của bạn là gì: A, B, C, hay D? 👇**

1. **Đáp án: C — Directory-based sharding (Phân đoạn dựa trên thư mục) ✅**

Dưới đây là lý do tại sao ba phương án còn lại thường gây nhầm lẫn cho các kỹ sư:

**Tại sao C thắng thế (Directory-based sharding):**

Trong hệ thống này, 80% các truy vấn đọc (reads) đều nhắm đến "đơn hàng của khách hàng X". Bạn sẽ muốn toàn bộ đơn hàng của một khách hàng cụ thể chỉ nằm gọn trên đúng một **shard** (phân đoạn). Khi đó, các truy vấn đọc theo phạm vi khách hàng (customer-scoped) sẽ chỉ cần đánh vào đúng một **node** duy nhất, loại bỏ hoàn toàn hiện tượng **scatter-gather fan-out** (truy vấn dàn trải đến tất cả các node rồi tổng hợp kết quả – điều gây tốn kém tài nguyên).

Bạn duy trì một bảng `customer_shard_map` (ánh xạ khách hàng với shard) và **cache** nó trên Redis để truy xuất tốc độ cao. Nếu một shard (ví dụ shard 3) bị quá tải (**hot shard**), bạn có thể dễ dàng di chuyển dữ liệu của những khách hàng có lưu lượng truy cập lớn (**whales**) sang shard khác mà không cần phải thực hiện **rehash** toàn bộ hệ thống. 

Khả năng **tái cân bằng dữ liệu có mục tiêu (targeted rebalancing)** chính là "vũ khí tối thượng" của phương pháp này. Đây là kỹ thuật đang được các ông lớn như Figma, Notion và Slack áp dụng.


Dưới đây là bản dịch bài viết sang tiếng Việt, sử dụng các thuật ngữ chuyên ngành (terminology) phổ biến trong lĩnh vực kiến trúc hệ thống và phân tán (distributed systems) để bạn dễ dàng nắm bắt:


2. **Tại sao phương án A là một "cái bẫy"? (Hash trên `order_id`)**

Đây là lời khuyên "kinh điển" trong các tutorial: *"Hãy Hash trên khóa chính (Primary Key)!"*. Nhưng cách này sẽ khiến hệ thống của bạn gặp rắc rối lớn. Với phương pháp này, 200 đơn hàng của cùng một khách hàng sẽ bị phân tán (scatter) trên tất cả các shard. 

Hậu quả là mọi thao tác đọc (read) đều trở thành một tác vụ **fan-out** đến 4 shard, và tốc độ truy vấn bị "thắt cổ chai" bởi node chậm nhất trong cụm. Điều này làm tăng độ trễ (latency) của chỉ số **P99** lên đáng kể.

3. **Tại sao phương án B là sai lầm? (Range trên `created_at`)**

Cách này tạo ra **hot shard** (shard bị quá tải cục bộ) ngay từ khâu thiết kế. Mọi đơn hàng mới đều được ghi (write) vào cùng một shard. Kết quả là shard mới nhất này phải gánh 100% lưu lượng ghi và 70% lưu lượng đọc. Đến những đợt cao điểm như Black Friday, shard này sẽ bị "quá nhiệt" (melt) và sập, trong khi các shard khác lại đang nhàn rỗi (idle).

4. **Tại sao phương án D vẫn chưa tối ưu? (Consistent Hashing)**

Mặc dù **Consistent Hashing** rất hiệu quả trong việc phân tán dữ liệu đồng nhất (uniform data), nhưng nó không cho phép bạn di chuyển (migrate) dữ liệu của các **heavy tenants** (các khách hàng có lưu lượng lớn) một cách linh hoạt. Nếu vô tình có 4 "ông lớn" (whales) cùng nằm trên một shard, hệ thống của bạn sẽ bị nghẽn và bạn không có cách nào để tách biệt hay tối ưu riêng cho họ.

