
### Two users edit the same document at 9:03 AM.


![[Pasted image 20260908134510.png]]



Hai user cùng edit một document vào lúc 9:03 sáng.

Không locking. Không coordination (đồng bộ hóa). Đơn giản là 2 client cùng ghi (write) vào một record.

Cả 2 thay đổi (change) bắn đến server chỉ cách nhau 300ms. Request nào đến trước được ghi trước. Request đến sau sẽ overwrite (ghi đè) cái trước.

Công sức của User A bốc hơi. Họ không hề nhận được một thông báo lỗi (error) nào cả. Họ chỉ đơn giản là… mất sạch data vừa sửa.

Đây chính là **bài toán xung đột đa luồng ghi (multi-writer conflict problem)**. Cuối cùng thì mọi hệ thống cộng tác (collaborative system) đều sẽ dính chưởng này. Bạn có các lựa chọn sau:

*   **A) Last-Write-Wins (LWW)** — Timestamp (dấu thời gian) nào cao hơn thì thắng. Thay đổi của bên thua cuộc sẽ biến mất trong im lặng.
*   **B) Vector Clocks** — Track (theo dõi) tính nhân quả (causality) trên từng replica (bản sao), phát hiện các version bị xung đột (conflict), sau đó đẩy về cho tầng application tự xử lý (resolve).
*   **C) CRDTs (Conflict-free Replicated Data Types)** — Các cấu trúc dữ liệu có khả năng tự động merge các write đồng thời (concurrent write) bằng toán học mà không cần cơ chế coordination.
*   **D) Operational Transformation (OT)** — Biến đổi (transform) từng thao tác (operation) dựa trên các operation chạy đồng thời trước khi apply nó, nhằm giữ nguyên vẹn ý đồ của user (intent).

Google Docs, Figma, Notion và DynamoDB đều đặt cược vào những hướng đi khác nhau cho bài toán này.

Có một giải pháp scale được tới hàng triệu writer đồng thời. Có một giải pháp chạy rất mượt cho đến khi nó âm thầm làm corrupt (hỏng) data của bạn. Và có hai giải pháp đòi hỏi một data model hoàn toàn khác biệt từ gốc.

Chọn đi — A, B, C hay D — và cho tôi biết lý do tại sao. Tôi sẽ thả bài phân tích chi tiết ở phần comment (bao gồm cả việc Google Docs thực sự đang dùng cái nào và tại sao suýt chút nữa họ đã điền vào ô sai).


Để bài viết mang phong cách chuyên nghiệp của lập trình viên Việt Nam nhưng vẫn dễ hiểu, mượt mà và gần gũi, mình xin dịch và tối ưu hóa lại như sau:


**Đáp án: C — CRDTs** *(nhưng câu trả lời thực tế còn phụ thuộc vào conflict model của bạn — xem chi tiết bên dưới).*

![[Pasted image 20260908134638.png]]


C — CRDTs là "vua" ở quy mô lớn (scale)
**CRDTs** (Conflict-free Replicated Data Types) là các cấu trúc dữ liệu được thiết kế để mọi **replica** (bản sao dữ liệu) luôn có thể **merge** (gộp) lại với nhau — tính toán theo toán học mà không cần **coordination** (cơ chế điều phối trung tâm). 

Bí quyết nằm ở chỗ: nếu các **operation** (thao tác) có tính **giao hoán** (commutative), **kết hợp** (associative), và **đẳng lũy** (idempotent), thì các **conflict** (xung đột) sẽ hoàn toàn không thể xảy ra về mặt cấu trúc.

**Ví dụ thực tế:**
*   **G-Counter:** Chỉ tăng giá trị. Thuật toán **merge** = lấy giá trị max của từng replica. Đảm bảo luôn **converge** (hội tụ về một trạng thái chung).
*   **LWW-Element-Set:** Hợp nhất các thao tác thêm (`add`) và xóa (`remove`) dựa trên **timestamp** (dấu thời gian).
*   **RGA / YATA (Sequence CRDTs):** Mỗi ký tự được gán một ID duy nhất, các thao tác **concurrent** (đồng thời) sẽ được sắp xếp theo một thứ tự tất định (deterministic) — đây chính là công nghệ đằng sau các trình soạn thảo văn bản cộng tác (collaborative editing).

Canvas của Figma chạy trên nền tảng CRDTs. Mô hình block của Notion cũng dựa trên CRDTs. Với hàng triệu **concurrent writers** (người ghi dữ liệu đồng thời) phân bố khắp các khu vực địa lý, mọi **node** (nút mạng) vẫn tự **converge** độc lập — hoàn toàn không cần cơ chế điều phối nào.

**Đánh đổi (The catch):** CRDTs ép bạn phải tuân thủ một **data model** (mô hình dữ liệu) nhất định. Không phải bài toán nào cũng map mượt mà vào đây. Một số thao tác (ví dụ: di chuyển một file giữa các thư mục) cực kỳ khó biểu diễn bằng CRDT mà không làm mất đi **intent** (ý định ban đầu của người dùng).

 **D — Biến đổi thao tác (Operational Transformation - OT) ⚠️ Ấn tượng nhưng cực khó**

OT từng là thuật toán cốt lõi của Google Docs ở giai đoạn đầu. Khi có hai `operation` (thao tác) được gửi đến đồng thời, hệ thống sẽ thực hiện `transform` (biến đổi) thao tác này dựa trên ngữ cảnh của thao tác kia trước khi `apply` (áp dụng) lên state (trạng thái). 

Ví dụ: User A thực hiện `insert` (chèn) tại vị trí 5, cùng lúc đó User B thực hiện `delete` (xóa) tại vị trí 3 — thuật toán OT sẽ tự động điều chỉnh lại vị trí `insert` của A để bù trừ cho việc B vừa xóa dữ liệu. Nhờ đó, `intent` (ý định) ban đầu của người dùng được bảo toàn.

Đó là lý do vì sao vào năm 2009, Google Docs mang lại cảm giác vi diệu như phép thuật.

Nhưng về mặt vận hành, OT thực sự là một cơn ác mộng. Các `transformation function` (hàm biến đổi) nổi tiếng là khó viết đúng — ngay cả các tài liệu nghiên cứu gốc về OT cũng từng có bug. Cứ mỗi loại `operation` mới được thêm vào, số lượng cặp hàm biến đổi cần viết sẽ tăng theo hàm số mũ (tăng trưởng bậc hai - quadratically). Ngoài ra, OT bắt buộc phải có một `centralized server` (máy chủ tập trung) để đóng vai trò `sequence` (tuần tự hóa) các thao tác; nó không thể `distribute` (phân tán) một cách trọn vẹn.

Google Docs hiện đại đã chuyển dịch sang một mô hình `hybrid` (lai), kết hợp thêm các tư tưởng tương tự như CRDT. Bản thân OT đơn lẻ không thể scale (mở rộng quy mô) sang kiến trúc phân tán toàn diện.


 **B — Đồng hồ véc-tơ (Vector Clocks) ⚠️ Thành thật nhưng chưa đủ**

Vector clocks giải quyết bài toán theo dõi `causality` (quan hệ nhân quả). Mỗi câu lệnh `write` (ghi dữ liệu) đi kèm với một `version vector` — gồm một bộ đếm cho mỗi `replica` (bản sao). Khi hai thao tác ghi không có mối quan hệ nhân quả với nhau (không có thao tác nào "xảy ra trước" thao tác kia), hệ thống biết rằng một `conflict` (xung đột) đã xảy ra. Cả hai phiên bản dữ liệu sẽ được đẩy lên `application layer` (tầng ứng dụng) để tự xử lý.

Hệ thống Dynamo nội bộ của Amazon từng sử dụng cơ chế này. Nó đúng đắn và minh bạch. Vấn đề nằm ở chỗ: việc `conflict resolution` (giải quyết xung đột) lúc này trở thành trách nhiệm của bạn. Bạn phải tự viết `merge logic` (logic hợp nhất dữ liệu) cho từng kiểu dữ liệu. Với giỏ hàng trên trang thương mại điện tử, việc này còn khả thi (chỉ cần lấy phép hợp - union các mặt hàng lại). Nhưng với các tài liệu phức tạp bất kỳ? Mô hình này sập nguồn rất nhanh.

Vector clocks chỉ cho bạn biết xung đột nằm ở **đâu**, chứ không chỉ cho bạn biết phải **giải quyết chúng như thế nào**.


 **A — Ghi-lần-cuối-thắng (Last-Write-Wins - LWW) ❌ Cực kỳ nguy hiểm**

Rất đơn giản. Đơn giản đến mức tàn nhẫn. `Timestamp` (dấu thời gian) nào cao nhất thì thắng. Thay đổi của kẻ thua cuộc sẽ bốc hơi — không có lỗi, không có thông báo, biến mất hoàn toàn.

Apache Cassandra sử dụng cơ chế này làm mặc định. Đối với các `workload` (tải công việc) chỉ ghi nối đuôi (append-only) như metrics (chỉ số hệ thống), event logs (nhật ký sự kiện) hay telemetry (dữ liệu đo đạc từ xa) thì hoàn toàn vô tư. 

Nhưng còn đối với bất cứ thứ gì do con người chỉnh sửa trực tiếp thì sao? Đó chính là hiện tượng `silent data loss` (mất dữ liệu ngầm) kèm theo một cái mác timestamp. Phần nguy hiểm nhất là: người dùng chẳng bao giờ nhận được một thông báo lỗi nào cả. Công việc của họ đơn giản là "bốc hơi" khỏi hệ thống.