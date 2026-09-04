
### You’re building the “find nearby drivers” feature for a ride-hailing app.


![[Pasted image 20260827170957.png]]



Bạn đang xây dựng tính năng "tìm tài xế ở gần" cho một ứng dụng gọi xe (như Grab hay Uber).

Vào giờ cao điểm, hệ thống có 500.000 tài xế hoạt động liên tục cập nhật tọa độ GPS mỗi 5 giây. Khách hàng liên tục gửi request tìm tài xế trong bán kính 2km. Tính ở quy mô lớn, hệ thống phải gánh khoảng **100.000 truy vấn tìm kiếm không gian (proximity queries) mỗi giây**.

Cách code ngây thơ (naive implementation) mà bạn hay làm sẽ thế này:

```sql
SELECT * FROM drivers 
WHERE lat BETWEEN ? AND ? 
AND lng BETWEEN ? AND ?
```

Cách này chạy ổn với 1.000 tài xế. Nhưng với 500.000 tài xế, mỗi request sẽ kích hoạt một lệnh **Full Table Scan (quét toàn bộ bảng)**. **Latency (độ trễ)** vọt lên 800ms. Khách hàng chỉ thấy màn hình loading quay đều. Tài xế thì bỏ lỡ cuốc xe.

Team của bạn đề xuất 4 hướng giải quyết:

*   **A) Phân vùng Geohash (Geohash partitioning):** Encode tọa độ của tài xế thành một chuỗi string Geohash. Tạo index trên tiền tố (prefix) của chuỗi đó. Các truy vấn không gian lúc này biến thành việc tra cứu string (string lookup) trên index.
*   **B) PostGIS với Spatial Index:** Cài thêm extension PostGIS vào Postgres. Dùng index không gian chuẩn **R-tree/GiST** để xử lý các truy vấn bounding-box (hình hộp bao) và radius (bán kính).
*   **C) Quadtree lưu trên RAM (In-memory Quadtree):** Lưu toàn bộ tọa độ tài xế đang online vào cấu trúc dữ liệu **Quadtree** trong một service chuyên chạy In-Memory (ví dụ dùng Redis hỗ trợ). Không gian sẽ được phân rã đệ quy cho đến khi mỗi cell có $\le$ N tài xế.
*   **D) Lưới lục giác H3 (H3 hexagonal grid - Hệ thống của Uber):** Chia bề mặt trái đất thành các ô hình lục giác (hexagonal cells) với nhiều độ phân giải khác nhau. Gán mỗi tài xế vào một cell. Khi query, hệ thống chỉ cần check cell mục tiêu + 6 cell lân cận ở độ phân giải phù hợp.

Yêu cầu bài toán: **p99 latency dưới 50ms**, **real-time updates** (cập nhật thời gian thực), và **phải đảm bảo độ chính xác ở các đường biên giới hạn của cell (cell boundaries)**.

Bạn sẽ chọn phương án nào — **A, B, C, hay D** — và tại sao? Xem phân tích chi tiết dưới phần bình luận nhé!



**Tại sao Lưới Lục Giác (H3) lại thắng thế?**

![[Pasted image 20260828152251.png]]

Uber đã mã nguồn mở (open-source) thuật toán **H3** chính để giải quyết bài toán này. 

Lý do là các ô lục giác có **6 ô láng giềng (neighbors)**, và tất cả đều **cách đều tâm một khoảng cách bằng nhau** (equidistant). Trong khi đó, các ô vuông (ví dụ như hệ thống **Geohash**) lại có các ô láng giềng ở góc xa hơn khoảng 40% — điều này làm sai lệch nghiêm trọng các truy vấn dạng *"tìm tài xế trong bán kính 2km"*.

H3 còn hỗ trợ sẵn **16 cấp độ phân giải (resolution levels)**, giúp hệ thống không cần phải **đánh chỉ mục lại (reindexing)** mỗi khi người dùng phóng to/thu nhỏ bản đồ (zoom in/out). 

Tuy nhiên, "vũ khí tối thượng" của H3 chính là **truy vấn k-ring** (bao gồm ô mục tiêu cộng với 6 ô láng giềng xung quanh), giúp **đảm bảo không bỏ sót bất kỳ tài xế nào ở khu vực giáp ranh giữa các ô**. 

Nhờ đó, Uber đạt được tốc độ **truy vấn dưới 10 mili-giây (sub-10ms lookup)** với quy mô hàng triệu tài xế bằng cách kết hợp: *lấy danh sách các cell trong vùng k-ring $\rightarrow$ truy vấn ID tài xế từ Redis Set (với key là ID của cell)*. 

Đó cũng là lý do vì sao các ông lớn như Lyft, Airbnb và DoorDash đều đang sử dụng các biến thể của mô hình này.

**Tại sao phương án A là một "cái bẫy" (Geohash):**

Geohash là một thuật toán đạt chuẩn production (môi trường thực tế) và được sử dụng cực kỳ rộng rãi — nhưng lại sai lầm trong bài toán này. Geohash sử dụng đường cong Z-order (xen kẽ các bit), thứ **không đảm bảo tính lân cận về mặt địa lý** cho các chuỗi tiền tố (prefix) liền kề. Hai tài xế chỉ cách nhau 1 mét có thể sở hữu hai chuỗi prefix hoàn toàn khác nhau nếu họ đứng ở hai bên đường biên của ô lưới (cell boundary). 

Điều này dẫn đến tỷ lệ miss-rate (truy vấn trượt) mang tính hệ thống khi chịu tải 100.000 queries/giây. Tóm lại: Geohash phù hợp với việc phân vùng thô (coarse partitioning, ví dụ như sharding theo khu vực), nhưng hoàn toàn sai lầm đối với bài toán tìm khoảng cách gần thời gian thực (real-time) có độ chính xác dưới 1 km.

**Tại sao phương án B "gục ngã" ở quy mô lớn (PostGIS):**

Về mặt logic, PostGIS hoàn toàn chính xác — đây là lựa chọn tối ưu cho một dashboard quản lý 5.000 chiếc xe tải. Nhưng nó bất khả thi với 500.000 tài xế gửi cập nhật vị trí mỗi 5 giây. 

Hãy nhìn vào bài toán tính toán: $500.000 \times 12$ lần cập nhật/phút = **100.000 thao tác ghi (writes)/giây** đổ vào cấu trúc GiST index. Các loại cây chỉ mục như GiST index rất "tốn kém" về mặt chi phí ghi (write-expensive). Cơ sở dữ liệu của bạn sẽ ngốn một nửa tài nguyên chỉ để duy trì và cập nhật index. Hơn nữa, việc scale ngang (scale horizontally) các thao tác ghi trên Postgres là một bài toán cực kỳ đau đầu. PostGIS chỉ là điểm khởi đầu — còn tổ hợp **H3 + Redis** mới là đích đến khi hệ thống của bạn sập vì quá tải.

**Tại sao phương án C suýt thành công (Quadtree - Cây tứ phân):**

Độ phức tạp thuật toán là $O(\log n)$ cho cả thao tác insert (thêm) và query (truy vấn), nghe rất lý tưởng trên lý thuyết. Nhưng nó sẽ vỡ trận ở mật độ của các ứng dụng gọi xe (ride-hailing): Cứ mỗi lần một tài xế di chuyển qua ranh giới ô lưới, hệ thống sẽ phải thực hiện một chuỗi thao tác *delete (xóa) + reinsert (thêm lại) + potential rebalancing (cân bằng lại cây)* — lặp lại **100.000 lần mỗi giây**. 

Nó cũng vướng phải lỗi về ranh giới hình chữ nhật y hệt như Geohash. Chưa kể, các thành phố đông đúc sẽ tạo ra những nhánh cây quá sâu và mất cân bằng. Quadtree chỉ là một khối xây dựng cơ bản (building block) — chứ không phải là một giải pháp hoàn chỉnh ở quy mô này.