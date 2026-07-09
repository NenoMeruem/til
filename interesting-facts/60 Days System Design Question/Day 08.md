Nodes: [[60 Days System Design Question]]
Tags: #system-design

### Bài toán: Hệ thống E-commerce Product Catalog. Sử dụng Redis đặt trước Postgres. Đạt ngưỡng 40K RPS (Requests Per Second) vào giờ cao điểm.

![[Pasted image 20260623151612.png]]

Ở môi trường Staging, Cache Hit Ratio (tỷ lệ truy vấn trúng cache) đạt 94%. Response time (thời gian phản hồi) dưới 20ms. Mọi thứ trông có vẻ rất ổn định.

**Ship to production.** Chỉ trong vòng 48 giờ, hàng loạt ticket hỗ trợ đổ về. Khách hàng thấy giá sai. Số lượng tồn kho (stock count) cũ. Sản phẩm hiển thị "còn hàng" dù thực tế đã bán hết từ 3 tiếng trước.

**Kiến trúc hệ thống:**
App (Node.js) → Redis (Cache) → Postgres (Source of Truth - Nguồn dữ liệu gốc)

*   **Writes (Ghi dữ liệu):** Từ Admin Panel (cập nhật giá), Inventory Service (trừ kho), Order Service (sự kiện thanh toán).
*   **Reads (Đọc dữ liệu):** Từ trang sản phẩm, kết quả tìm kiếm, quy trình checkout.

Cache đang bị hiện tượng **Stale Data** (dữ liệu cũ/hết hạn) trên production. Team của bạn đang tranh luận về chiến lược **Invalidation** (vô hiệu hóa/làm mới cache). Bạn sẽ chọn giải pháp nào?

**A) Write-through:** Mỗi thao tác ghi đều đồng thời update vào Cache và Postgres trong cùng một transaction. Đảm bảo Cache không bao giờ bị stale.

**B) Write-behind (Write-back):** Dữ liệu ghi vào Redis trước, sau đó một async worker sẽ đẩy dữ liệu xuống Postgres theo từng batch.

**C) Cache-aside (Lazy loading):** App ghi trực tiếp vào Postgres, sau đó thực hiện lệnh invalidation (xóa key) trên cache, để lần đọc tiếp theo tự động repopulate (nạp lại) dữ liệu mới vào.

**D) Read-through:** Redis đóng vai trò trung gian, tự xử lý các trường hợp Cache Miss bằng cách tự động fetch dữ liệu từ Postgres khi cần.

1. **✅ Đáp án: C — Cache-aside (Cơ chế đệm dữ liệu)**

![[Pasted image 20260623161541.png]]

**Tại sao C là lựa chọn tối ưu:**

Trong hệ thống của bạn, có nhiều luồng ghi dữ liệu đồng thời (**multiple write paths**) đến từ Admin Panel, Inventory Service và Order Service, tất cả đều tác động trực tiếp vào cơ sở dữ liệu Postgres. Chiến lược **Cache-aside** là lựa chọn hoàn hảo trong tình huống này:

1. **Quy trình hoạt động:** Mỗi khi một service thực hiện ghi dữ liệu vào Postgres, nó sẽ đồng thời thực hiện lệnh **invalidate** (xóa bỏ) cache key tương ứng trong Redis (ví dụ: `DEL product:123`).
2. **Cơ chế đọc:** Ở lần truy vấn tiếp theo, hệ thống sẽ gặp tình trạng **cache miss**, từ đó buộc service phải thực hiện truy vấn (**fetch**) dữ liệu mới nhất từ Postgres và tiến hành **repopulate** (nạp lại) vào Redis.
3. **Tính nhất quán:** Postgres luôn được đảm bảo là **Source of Truth** (nguồn dữ liệu gốc duy nhất). Redis lúc này chỉ đóng vai trò là lớp **read accelerator** (tăng tốc độ đọc) có tính chất tạm thời (disposable).

**Điểm mạnh:** Nếu chẳng may Redis gặp sự cố (crash), ứng dụng vẫn hoạt động bình thường, đảm bảo tính đúng đắn của dữ liệu dù hiệu năng có thể giảm nhẹ. Đây chính là kiến trúc chuẩn mà các nền tảng lớn như Shopify, Etsy và hầu hết các **reference architecture** (kiến trúc tham chiếu) của AWS đang triển khai trong môi trường production.

2. **Tại sao phương án A là "cái bẫy" (Write-through)**
*"Chúng ta ghi dữ liệu vào cả hai nơi một cách nguyên tử (atomically)"* — thực tế, không có cơ chế **distributed transaction** (giao dịch phân tán) giữa Redis và Postgres. Bạn ghi vào Postgres trước, sau đó mới ghi tiếp vào Redis. Nếu thao tác ghi vào Redis thất bại (do **network blip**, **timeout**), bạn sẽ rơi vào tình trạng: Postgres có dữ liệu mới, còn Redis chứa dữ liệu cũ (**stale data**). Đây chính xác là bug mà bạn đang cố giải quyết.

Tồi tệ hơn, **Write-through** làm hệ thống của bạn bị **tightly coupled** (ghép nối chặt) với Redis: giờ đây mọi service (ví dụ: Inventory Service và Order Service) đều cần quyền truy cập Redis. Chỉ cần Redis gặp sự cố (**outage**), toàn bộ luồng ghi (write path) của bạn sẽ bị sập. Kiến trúc này chỉ hiệu quả với các hệ thống đơn service/đơn writer, nhưng sẽ đổ vỡ ngay khi có nhiều thành phần cùng ghi dữ liệu.

3. **Tại sao phương án B sai (Write-behind / Write-back)**
Ở đây, Redis trở thành **source of truth** (nguồn dữ liệu chính). Tuy nhiên, Redis có thể mất dữ liệu trong các trường hợp: **failover** (chuyển đổi dự phòng), bị **OOM Killer** (hết bộ nhớ) hoặc độ trễ từ **AOF** (Append Only File). Nếu xảy ra sự cố, việc giải trình rằng "chúng ta có thể đã mất vài cập nhật giá cuối cùng" là không thể chấp nhận được trong một bản **postmortem** (báo cáo phân tích sự cố), đặc biệt khi liên quan đến tiền bạc. **Write-behind** chỉ phù hợp cho các luồng xử lý metrics hoặc đếm số liệu phân tích, tuyệt đối không dùng cho các luồng ghi dữ liệu quan trọng như thương mại điện tử.

4. **Tại sao phương án D sai (Read-through)**
Phương án này chỉ giải quyết được phía đọc (read side). Các thao tác ghi vẫn đi qua 3 service riêng biệt mà không có cơ chế nào cập nhật/đồng bộ với cache. **Read-through** không thể xử lý vấn đề dữ liệu cũ (stale data) khi có nhiều nguồn ghi. Cuối cùng, bạn vẫn phải triển khai thêm cơ chế **invalidation** (vô hiệu hóa cache) thủ công; lúc này nó chẳng khác gì mô hình **Cache-aside** nhưng lại phức tạp và rườm rà hơn.