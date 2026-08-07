#### Your feed service was reading at 20ms.

![[Pasted image 20260807142454.png]]



Dịch vụ News Feed của bạn đang có độ trễ (latency) đọc là 20ms.
Rồi một KOL (người nổi tiếng) với 2 triệu follower đăng bài.
Bây giờ độ trễ vọt lên 4 giây. Chỉ số P99 (percentile 99) đang "gánh còng lưng" (bị quá tải nặng).

**Bài toán:**

10 triệu user. Khoảng 50 nghìn post/ngày. Có một tài khoản sở hữu 2 triệu follower.

Mỗi khi tài khoản đó đăng bài, câu lệnh query feed của bạn phải thực hiện cơ chế **fan-out** (phân rã/nhân bản tác vụ) tới 2 triệu dòng của follower, sort theo timestamp, và làm sập các **read replica** (bản sao đọc) của database.

Team của bạn đang tranh luận xem nên sửa **delivery model** (mô hình phân phối) như thế nào — không phải tối ưu câu query, mà là giải quyết ở cấp độ **architecture** (kiến trúc).

*   **A) Fan-out on Write (Đẩy khi ghi):** Push dữ liệu thẳng vào cache của từng follower ngay khi có post mới. Đọc siêu tốc. Nhưng 1 bài đăng của KOL = 2 triệu lượt ghi cache.
*   **B) Fan-out on Read (Kéo khi đọc):** Không tính toán trước (no precomputation). Fetch và merge dữ liệu trực tiếp tại thời điểm đọc. Ghi thì đơn giản, nhưng chết khi hệ thống scale lớn.
*   **C) Hybrid fanout (Fan-out lai):** Fan-out on write cho user thường, và dùng fan-out on read cho KOL. Chỉ thực hiện merge dữ liệu (tại thời điểm đọc) cho riêng phần của KOL.
*   **D) Materialized feed table (Bảng feed phi chuẩn hóa):** Dùng một bảng denormalized lưu sẵn feed cho từng user, được update bất đồng bộ (async) thông qua **event stream** (luồng sự kiện). Chỉ cần 1 câu lệnh đọc bảng, chấp nhận độ trễ nhất quán (**eventual consistency**).

Bạn chọn phương án nào — A, B, C, hay D — và tại sao? Xem phân tích chi tiết dưới phần bình luận nhé.


**Đáp án: C — Hybrid Fanout (Mô hình Fanout lai)**
**Tại sao C là đáp án chính xác:**

![[Pasted image 20260807143322.png]]

Đây chính là cách mà Twitter (X) đã giải quyết bài toán thực tế — họ đã công bố kiến trúc này. Mấu chốt của vấn đề là: 
* Mô hình **Fanout-on-write** (Đẩy dữ liệu khi ghi) giúp quá trình đọc của user diễn ra cực nhanh, nhưng lại là thảm họa đối với các tài khoản có lượng follower khổng lồ (celebrity/KOL). 
* Ngược lại, mô hình **Fanout-on-read** (Kéo dữ liệu khi đọc) rất đơn giản, nhưng lại làm sập độ trễ (latency) ở quy mô lớn. 
* Mô hình **Hybrid** (Lai) giải quyết triệt để điểm yếu của cả hai cách trên.

**Cách hoạt động:**
Khi một bài viết (post) được tạo ra $\rightarrow$ hệ thống sẽ check (kiểm tra) số lượng follower. 
* **Dưới 10k follower?** Thực hiện fanout ngay lập tức vào Redis feed cache của tất cả follower.
* **Trên 10k follower (tài khoản nổi tiếng)?** Bỏ qua bước fanout. Vào thời điểm đọc feed (read time), hệ thống sẽ fetch (lấy) dữ liệu từ 2 nguồn: precomputed cache (cache đã tính toán sẵn của các tài khoản thường) + real-time query (truy vấn thời gian thực) các bài viết từ tài khoản celebrity. Sau đó, tiến hành **merge** (gộp) và **deduplicate** (lọc bỏ các bản ghi trùng lặp).

Tập dữ liệu từ các tài khoản celebrity này rất nhỏ và có giới hạn. 
**Kết quả:** Chỉ số **P99 latency** luôn được giữ ở mức thấp (fast), tránh được tình trạng phải thực hiện 2 triệu câu lệnh ghi đồng bộ (synchronous writes) cho một bài đăng của người nổi tiếng.


**Tại sao phương án A là một "cái bẫy" (Cơ chế Fanout khi Ghi - Fanout on Write):**

Trông có vẻ hoàn hảo. Tốc độ `read` (đọc) cực kỳ tức thì. Cho đến khi Cristiano Ronaldo đăng bài và hệ thống phải `write` (ghi) song song vào 500 triệu `cache` (bộ nhớ đệm). 

Ngay cả khi bạn chỉ có 2 triệu người theo dõi, tính ra cứ 1ms cho một lần ghi thì tổng cộng mất tới 2.000 giây công sức xử lý ghi. Lúc này, `cache cluster` (cụm cache) sẽ bị bão hòa (saturate). `Write queue` (hàng đợi ghi) bị nghẽn (back up). Hiện tượng `thundering herd` (bầy đàn chớp nhoáng - hàng loạt request cùng đổ dồn) xảy ra ở mọi bài đăng của người nổi tiếng.

Nhiều đội ngũ kỹ thuật áp dụng cách này, thấy chạy rất mượt ở mốc 1 triệu user, nhưng rồi vấp phải "bài toán người nổi tiếng" khi hệ thống đã ở môi trường `production` (chạy thực tế). Đó chính là cái bẫy.

**Tại sao phương án B lại sai (Cơ chế Fanout khi Đọc - Fanout on Read):**

Theo dõi 500 tài khoản đồng nghĩa với việc bạn phải thực hiện 500 `query` (câu lệnh truy vấn), hoặc một câu lệnh `JOIN` khổng lồ, sau đó `sort` (sắp xếp) trên RAM rồi mới trả về kết quả cho client. 

Bạn có thể `cache` (lưu đệm) kết quả này — nhưng lúc này bạn lại đang tốn tài nguyên cho các phép tính toán đắt đỏ chỉ để làm đầy một cái cache có `TTL` (thời gian sống) chỉ vỏn vẹn 30 giây. Bản chất nó chẳng khác gì một cơ chế `fanout-on-write` chậm chạp nhưng lại gánh thêm độ trễ (`latency`). Chắc chắn mô hình này không thể sống sót nổi ở mốc 10 triệu user.

**Tại sao phương án D lại sai (Bảng News Feed được Materialized - tính toán sẵn):**

Nghe thì có vẻ rất sạch sẽ và gọn gàng — mỗi user ứng với một dòng dữ liệu `denormalized` (phi chuẩn hóa), được cập nhật bất đồng bộ (`async`) thông qua `CDC` (Change Data Capture) hoặc `event stream` (luồng sự kiện). 

Nhưng một bài đăng của người nổi tiếng vẫn kích hoạt tới 2 triệu câu lệnh cập nhật dòng (row update), chỉ là nó được làm một cách bất đồng bộ mà thôi. Bạn không hề giải quyết được bài toán `write amplification` (khuếch đại ghi), bạn chỉ đang trì hoãn nó mà thôi. 

Chưa kể đến: độ phức tạp vận hành (`operational complexity`) của một `event stream` + các `idempotent consumer` (bên tiêu thụ dữ liệu có tính lũy đẳng - xử lý nhiều lần kết quả vẫn như một) + logic `reconciliation` (đối soát/đồng bộ dữ liệu). Quá nhiều `moving parts` (các thành phần chuyển động/phụ thuộc) cho cùng một bài toán.