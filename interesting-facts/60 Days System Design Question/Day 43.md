


### Your CDN saved you from explaining a 400ms load time to your VP.


![[Pasted image 20261026114553.png]]



CDN (Mạng phân phối nội dung) vừa cứu bạn một bàn thua trông thấy khi không phải giải thích với Sếp tổng (VP) lý do tại sao trang web mất tới 400ms để load.

Nhưng rồi bạn đẩy một bản **deploy** (triển khai code mới) lên. Và chẳng ai nhận được bản vá lỗi đó cả.

Đây là những gì đã xảy ra:

Các **edge node** (nút biên) vẫn đang phục vụ file JS bundle cũ — do **TTL** (Time-to-Live - thời gian sống của cache) vẫn chưa hết hạn. Bạn bèn vào thủ công để **purge cache** (xóa bộ nhớ đệm). Nhưng xui xẻo là bạn lại bấm nhầm môi trường. Thế là môi trường **Prod** (Production) tiếp tục trả về bản **stale** (dữ liệu cũ/ôi) suốt 6 tiếng đồng hồ nữa.

Bạn cần một cấu hình CDN có thể xử lý việc **invalidation** (vô hiệu hóa cache) một cách mượt mà ngay cả dưới áp lực của việc deploy liên tục. Bạn sẽ chọn phương án nào?

A) **Anycast routing** + **stale-while-revalidate** (vừa trả về dữ liệu cũ vừa ngầm fetch dữ liệu mới) + **event-driven purge** (xóa cache theo sự kiện) thông qua API khi deploy.

B) **Unicast routing** + **aggressive TTLs** (TTL ngắn/gắt gao) + **manual cache purge** (xóa cache thủ công) qua trang quản trị (dashboard).

C) **Anycast routing** + **long TTLs** (TTL dài) + **tag-based invalidation** (vô hiệu hóa cache theo thẻ/tag) thông qua API.

D) **Anycast routing** + **short TTLs** (TTL ngắn) + **không có chiến lược invalidation** nào cả (phó mặc cho cache tự hết hạn tự nhiên).

Hãy chọn A, B, C, hoặc D — và chia sẻ luôn câu chuyện "cười ra nước mắt" về việc xử lý cache CDN thực tế của bạn ở dưới phần bình luận nhé. Phân tích chi tiết sẽ có ở bên dưới!



**A — Anycast kết hợp stale-while-revalidate và event-driven purge — Giải pháp tối ưu**\
![[Pasted image 20261026135332.png]]
*   **Anycast:** Định tuyến cùng một địa chỉ IP từ nhiều điểm hiện diện (PoP - Point of Presence). Giao thức BGP sẽ tự động điều hướng từng user (người dùng) đến edge server (máy chủ biên) gần họ nhất. User ở Tokyo sẽ kết nối thẳng đến Tokyo — chứ không phải Virginia.
*   **Stale-while-revalidate (SWR):** Phục vụ ngay lập tức phiên bản đang được cache (lưu trữ tạm thời), đồng thời fetch (tải) bản mới về ở background (chạy ngầm). Người dùng sẽ không bao giờ phải chịu độ trễ chờ đợi khi xảy ra cache miss.
*   **Event-driven purge (Xóa cache dựa trên sự kiện):** Pipeline CI/CD của bạn sẽ gọi API của Cloudflare hoặc CloudFront tại mỗi lần deploy (triển khai), chỉ định chính xác các static asset (tài nguyên tĩnh) vừa thay đổi. Không cần thao tác thủ công, không bấm nhầm môi trường, không còn những cú "lỡ tay" lúc 2 giờ sáng.


**C — Anycast kết hợp TTL dài và tag-based invalidation — Khá tốt, nhưng có "cạm bẫy"**
*   **Tag-based invalidation (Xóa cache theo thẻ):** Tính năng này (như Cloudflare Cache-Tag, Fastly surrogate keys) cho phép bạn gom nhóm các đối tượng (object) lại và purge (xóa) toàn bộ một nhóm logic chỉ với một lần gọi API. Ảnh sản phẩm mới lên? Chỉ cần invalidate (vô hiệu hóa) `tag:product-images`. Rất sạch sẽ và chính xác (surgical).
*   **Cạm bẫy:** TTL (Time-To-Live) dài hoạt động cực kỳ hoàn hảo khi pipeline deploy của bạn trơn tru. Nhưng nếu lệnh gọi API invalidation của bạn bị lỗi ngầm (silent fail) ngay giữa lúc sự cố — thời điểm bạn đang phải thao tác gấp — hệ thống sẽ tiếp tục serve phiên bản cũ sai lệch trong nhiều giờ mà không có TTL ngắn làm "lưới an toàn" cứu nguy.
*   Ngược lại, cơ chế `stale-while-revalidate` của **Phương án A** có khả năng graceful degradation (suy giảm hiệu năng một cách có kiểm soát) tốt hơn nhiều khi pipeline của bạn gặp sự cố.


**B — Unicast kết hợp TTL ngắn (aggressive) và manual purge**
*   **Unicast:** Chỉ sử dụng một region (vùng) duy nhất ở edge. User ở Tokyo của bạn vẫn phải route vòng qua tận Virginia. Bạn vừa tốn tiền mua CDN nhưng lại đang tự tay route vòng qua nó.
*   **Manual dashboard purge (Xóa cache thủ công trên giao diện):** Sớm muộn gì cũng có lúc ai đó quên, bấm nhầm môi trường (env), hoặc bỏ quên luôn bước này vào lúc 2 giờ sáng. Việc cấu hình TTL ngắn chỉ giúp thu nhỏ khoảng thời gian thiệt hại (damage window) — chứ nó không làm cho quy trình invalidation trở nên đáng tin cậy hơn.

**D — TTL ngắn và việc không hỗ trợ Invalidation (Xóa cache chủ động)**

Lầm tưởng đắt giá nhất trong cấu hình CDN chính là tư duy: _"TTL ngắn = dữ liệu lúc nào cũng tươi mới (fresh)"_.

Mỗi khi một bản ghi TTL hết hạn (expiry), nó là một quả bom hẹn giờ cho hiện tượng **Cache Stampede** (Bão cache / Dồn tải cache). Giả sử hệ thống đang gánh 200k RPS (Request Per Second - Yêu cầu mỗi giây) vào giờ cao điểm, TTL của một `hot endpoint` (điểm cuối có lượng truy cập cực lớn) đột ngột hết hạn, lập tức mọi PoP (Point of Presence - Điểm hiện diện của CDN) sẽ đồng loạt bắn request về origin server (máy chủ gốc). Kết quả là bạn chứng kiến hệ thống vọt từ 0 lên 200k RPS chỉ trong vòng 2 giây.

Chưa hết, bạn sẽ hoàn toàn mất quyền kiểm soát khi cần **hotfix** (vá lỗi nhanh). Lúc này, bạn chẳng làm được gì ngoài việc... ngồi đợi TTL tự động hết hạn (drain).