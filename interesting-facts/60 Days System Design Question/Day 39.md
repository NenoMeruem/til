Nodes: [[60 Days System Design Question]]
Tags: #system-design 


# You have a payment system. Two users try to spend from the same wallet balance at the same time.

![[Pasted image 20260928152431.png]]


Bạn đang vận hành một hệ thống thanh toán. Hai user (người dùng) cùng lúc cố gắng thực hiện giao dịch trừ tiền từ một `wallet balance` (số dư ví).

Cả hai cùng `read` (đọc) được số dư là $200. Cả hai đều muốn `spend` (tiêu) $150. Cả hai đều thấy số dư hợp lệ. Cả hai cùng `write` (ghi) câu lệnh trừ tiền xuống CSDL.

Kết quả là số dư ví giờ đây âm -$100. Làm sao để chặn lỗi này?

A) **Pessimistic locking (Khóa bi quan):** Dùng câu lệnh `SELECT FOR UPDATE` trên dòng dữ liệu (row) của ví. Một transaction (giao dịch) sẽ bị block (chặn) cho đến khi transaction kia `commit` (hoàn tất).

B) **Optimistic locking (Khóa lạc quan):** Đọc dòng dữ liệu kèm theo một `version number` (số phiên bản). Chỉ cho phép `write` nếu `version` không thay đổi kể từ lúc đọc. `Retry` (thử lại) khi xảy ra conflict (xung đột).

C) **MVCC (Multi-Version Concurrency Control - Kiểm soát tương tranh đa phiên bản):** Cho phép cả hai tiến trình đọc cùng thấy một `consistent snapshot` (ảnh chụp dữ liệu nhất quán), và dựa vào CSDL để phát hiện xung đột ghi tại thời điểm `commit`.

D) **Serializable isolation (Cô lập tuần tự):** Cài đặt `isolation level` (mức độ cô lập giao dịch) của CSDL thành `SERIALIZABLE` và để CSDL tự xử lý.

Cả 4 phương án trên đều là chiến lược thực tế trong môi trường `production` (chạy thật). Nhưng:
* Sẽ có **một phương án âm thầm cho phép double-spend** (chi tiêu trùng lặp) dưới tải trọng `concurrent` (đồng thời).
* Sẽ có **một phương án bóp nát throughput** (thông lượng) trên một bảng có tần suất ghi cao.
* Và **một phương án hầu như luôn là lựa chọn mặc định sai lầm**, dù nó hay được coi là phương án "an toàn".

Hãy chọn một phương án — và cho tôi biết bạn sẽ thực sự đưa phương án nào vào `ship` (triển khai) cho một hệ thống thanh toán xử lý tới 10.000 transaction/giây (10K TPS)?

Chi tiết đầy đủ sẽ có ở phần bình luận.

Nếu bạn đang xây dựng bất kỳ hệ thống nào có xử lý `concurrent writes` (ghi đồng thời) — hãy chia sẻ bài viết này. Đây chính là kiểu bug "đốt tiền" trước khi bạn kịp phát hiện ra nó.




**Tại sao B thắng (Optimistic Locking - Khóa lạc quan):**
![[Pasted image 20260928153051.png]]

Bạn đọc một bản ghi (row) trong bảng ví tiền và lấy ra số hiệu phiên bản (`version number`). Khi thực hiện ghi (write), bạn đính kèm thêm một điều kiện `WHERE version = :read_version`. Nếu một transaction (giao dịch) khác đã cập nhật bản ghi đó trước rồi, câu lệnh `WHERE` của bạn sẽ không khớp với dòng nào cả — xung đột được phát hiện, tiến hành retry (thử lại).

```sql
UPDATE wallets
SET balance = balance - 150, version = version + 1
WHERE id = :wallet_id AND version = :read_version;
```

Nếu `rows_affected = 0` (không có dòng nào bị ảnh hưởng) $\rightarrow$ xung đột $\rightarrow$ retry. 

Không có lock (khóa) nào bị giữ lại trong suốt quá trình đọc (read). Ở mức **10K TPS** (Transactions Per Second - Giao dịch trên giây) với tỷ lệ xung đột thấp, phương pháp này **nhanh hơn đáng kể** so với Pessimistic Locking (Khóa bi quan) — bạn chỉ phải trả "chi phí retry" khi thực sự có xung đột xảy ra, thay vì phải tốn chi phí acquire lock (xin cấp phát khóa) cho mọiao tác đọc.

**Điểm đánh đổi (The catch):** Dưới lượng **High Contention** (tranh chấp tài nguyên cao — ví dụ: một "hot wallet" - ví hot bị truy cập liên tục), **retry storm** (bão retry/bão thử lại) sẽ bóp nghẹt hệ thống của bạn. Các hot wallet đòi hỏi phải dùng `Redis INCRBY` với cơ chế giảm trừ nguyên tử (atomic decrement), hoặc phải đặt một message queue (hàng đợi) ở tầng trước bước update ví.


**Lý do Đáp án A là một "cái bẫy" (Pessimistic Locking - Khóa bi quan):**

`SELECT FOR UPDATE` vẫn hoạt động và hoàn toàn đúng đắn. Nhưng nó giữ một row-level lock (khóa mức dòng) trong suốt cả transaction (giao dịch) — khiến mọi concurrent write (lượng ghi đồng thời) phải xếp hàng chờ.

Ở mức 10K TPS (giao dịch mỗi giây) đối với một ứng dụng ví điện tử phổ biến, bạn đã vô tình serialize (tuần tự hóa) toàn bộ thao tác ghi vào một hàng đợi duy nhất. Throughput (thông lượng) sụp đổ. Các lỗi lock wait timeout (hết thời gian chờ khóa) xuất hiện dây chuyền — các transaction thất bại sẽ retry (thử lại), làm tăng thêm contention (sự tranh chấp tài nguyên). Bạn vừa tự tạo ra một cái bottleneck (nút cổ chai) tự thân.

Hãy chỉ dùng pessimistic locking cho các luồng low-concurrency (độ đồng thời thấp) như tác vụ admin, batch job (tác vụ hàng loạt) — nơi xác suất conflict (xung đột) gần như 100%. Tuyệt đối không dùng cho các thao tác thanh toán có throughput cao.

**Lý do Đáp án C là một lỗi "chìm xuồng" (MVCC + mức cô lập mặc định):**

Đây mới là trường hợp nguy hiểm nhất. PostgreSQL đặt mức default (mặc định) là `READ COMMITTED`. MVCC (Multi-Version Concurrency Control - Kiểm soát đồng thời đa phiên bản) cung cấp cho mỗi transaction một consistent snapshot (ảnh chụp dữ liệu nhất quán) — nhưng ở mức `READ COMMITTED`, snapshot đó được làm mới theo từng statement (câu lệnh), chứ không phải theo toàn bộ transaction.

Hai transaction chạy đồng thời cùng đọc số dư là $200, cả hai đều vượt qua điều kiện kiểm tra “đủ tiền”, và cả hai cùng commit. Không có conflict nào bị phát hiện. **Lỗi Double spend (chi tiêu gấp đôi) xảy ra ngay trên môi trường production.**

MVCC ngăn chặn được dirty read (đọc bẩn). Nhưng nó KHÔNG ngăn được lost update (mất cập nhật) ở mức `READ COMMITTED`. Hầu hết các kỹ sư đều mặc định rằng cứ có MVCC là an toàn trước các thao tác ghi đồng thời. Thực tế không phải vậy.

**Lý do Đáp án D hầu như luôn là lựa chọn mặc định sai lầm (`SERIALIZABLE`):**

Về mặt lý thuyết thì đúng — database đảm bảo các transaction hoạt động giống như thể chúng chạy tuần tự từng cái một. Không có anomaly (dị thường) nào xảy ra.

Vấn đề nằm ở chỗ: Thuật toán SSI (Serializable Snapshot Isolation) của PostgreSQL theo dõi các phụ thuộc đọc-ghi giữa các transaction. Dưới điều kiện high-concurrency (độ đồng thời cao), serialization failure (lỗi tuần tự hóa) tăng vọt — các transaction bị abort (hủy bỏ) và retry ngay cả khi thực tế không có conflict nào xảy ra. Điều này gây suy giảm throughput nghiêm trọng ở quy mô lớn.

Nó phù hợp cho các luồng tài chính phức tạp nơi tính đúng đắn được đặt lên trên throughput (ví dụ: quy cuối ngày - reconciliation). Nhưng lại là một default tồi tệ cho một API xử lý thanh toán có throughput cao.