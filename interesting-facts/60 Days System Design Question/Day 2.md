

### Khi "N+1" trở thành bài toán cân não

![[Pasted image 20260622172547.png]]

Endpoint `/orders` của bạn đang tải 50 đơn hàng mỗi trang.

Chỉ số **P95** là 2.4s. **Database (DB)** ổn, **App server** ổn, không có "cháy nhà" nào cả. Nhưng khi bạn mở **query log** ra thì thấy:

Có đến 51 câu truy vấn cho mỗi **request**. Một câu `SELECT` để lấy danh sách đơn hàng, và 50 câu truy vấn tiếp theo — mỗi đơn hàng một câu — chỉ để lấy thông tin khách hàng. **ORM** của bạn đang thực hiện **lazy-loading** cho thuộc tính `order.customer` bên trong vòng lặp `.map()`.

Đây chính là lỗi **N+1** kinh điển. Bạn đã gặp nó nhiều lần. Cách sửa nghe chừng rất "hiển nhiên" — cho đến khi bạn vào buổi họp team, nơi 3 kỹ sư đề xuất 3 giải pháp khác nhau và ai cũng khăng khăng mình đúng.

Dưới đây là các phương án trên bàn cân:

- **A) Eager-loading:** Dùng `include: { customer: true }` trong câu lệnh Prisma. Kết quả là một câu `JOIN` duy nhất, xong.
- **B) Sử dụng DataLoader:** Đặt một **DataLoader** phía trước bước truy vấn khách hàng — nó sẽ gom 50 ID thành một câu lệnh `WHERE id IN (...)` ở dưới nền (backend).
- **C) Caching:** Lưu thông tin khách hàng vào **Redis** theo ID — mọi truy vấn sẽ kiểm tra cache trước, chỉ khi nào **cache miss** mới truy vấn DB.
- **D) Denormalize:** Lưu đè `customer_name` trực tiếp vào bảng `orders` — đọc thẳng từ hàng đó, không `JOIN`, không truy vấn phụ.

Cả 4 cách đều giúp giảm số lượng query xuống. Cả 4 cách đều có thể đẩy lên **production** trong các hệ thống thực tế. Nhưng lựa chọn của bạn không chỉ là giải quyết vấn đề hiện tại, mà là một "canh bạc" về việc endpoint này sẽ phát triển như thế nào trong 6 tháng tới.

Bạn sẽ chọn cái nào — A, B, C, hay D? Tại sao?


1. **Tại sao giải pháp A lại thắng?**

Việc sử dụng một câu lệnh **`LEFT JOIN`** để kết nối bảng `orders` với bảng `customers` (thông qua `customer_id` và `id`) giúp bạn lấy được toàn bộ tập dữ liệu cần thiết chỉ trong **một lượt truy vấn (single round trip)** duy nhất. Kết quả là chỉ số **P95 (độ trễ tại phân vị 95)** giảm từ **2.4s xuống còn khoảng 80ms**. Bạn không cần phải tốn thêm chi phí cho **cơ sở hạ tầng (infrastructure)**mới, cũng như không phát sinh thêm các **điểm lỗi tiềm tàng (failure modes)**nào khác.

Vấn đề **N+1** trong **ORM (Object-Relational Mapping)** thường xuất phát từ cùng một nguyên nhân: các **Lazy Relation** (quan hệ lười) mà chính lập trình viên cũng không nhận ra là nó đang được thực thi theo kiểu "lazy". Dù là **`include`** trong Prisma, Sequelize hay **`relations`** trong TypeORM, mọi công cụ ORM đều tồn tại cơ chế này.

**Lời khuyên:** Chỉ nên tìm đến các **design pattern** phức tạp hơn khi và chỉ khi câu lệnh **`JOIN`** thực sự không thể giải quyết được bài toán của bạn.

![[Pasted image 20260622173111.png]]


2. **Tại sao DataLoader lại là một "cái bẫy"?**

**Vấn đề:** DataLoader là một pattern rất đẹp, nhưng nó thực sự chỉ phát huy giá trị trong GraphQL — nơi mà các `resolver` tạo ra một cây truy vấn phân nhánh (fan-out) phức tạp, vượt quá khả năng xử lý của một câu lệnh `JOIN` đơn thuần.

Trong trường hợp của bạn, chúng ta chỉ có một endpoint trả về danh sách (list endpoint) với duy nhất một quan hệ (relation). Ở ngữ cảnh này, sử dụng `JOIN`trong SQL vừa đơn giản hơn, vừa tối ưu hiệu năng hơn rất nhiều. Bạn đang cố gắng giải quyết một bài toán không hề tồn tại, để rồi phải gánh chịu "thuế phức tạp" (complexity tax) cho toàn bộ vòng đời của hệ thống.

3. **Tại sao việc lạm dụng Redis là sai lầm?**  
"Cache-first" (ưu tiên dùng bộ nhớ đệm) chỉ là cách chữa phần ngọn, không giải quyết được gốc rễ của vấn đề nằm ở **Query Pattern** (cấu trúc truy vấn). 

Việc bạn thực hiện tới 50 lệnh `GET` từ cache cho mỗi request là đang lạm dụng tài nguyên. Chưa kể, bạn sẽ phải đối mặt với **Cache Invalidation** (bài toán xóa/làm mới cache) mỗi khi khách hàng cập nhật dữ liệu, và tình trạng **Cold-hit**(cache bị rỗng/miss liên tục) sẽ xảy ra với mọi ID ngay sau khi bạn deploy bản cập nhật mới.

Hãy nhớ: **Cache là công cụ để tối ưu hóa quy mô (Scaling), không phải là công cụ để sửa lỗi N+1.**


4. **Tại sao Denormalization (phi chuẩn hóa) là cuộc tranh luận kéo dài cả sự nghiệp: Hợp lý ở quy mô Instagram, nhưng đầy cạm bẫy.**

"Denormalization (phi chuẩn hóa) chính là nguyên nhân dẫn đến tình trạng: 3 năm sau khi khách hàng kết hôn, hệ thống vẫn hiển thị tên thời con gái của họ, chỉ vì không ai thiết kế `update path` (luồng cập nhật dữ liệu) cho trường đó.

Về bản chất, **Denormalization là một quyết định đánh đổi bằng Write-amplification (khuếch đại ghi)**, núp bóng dưới danh nghĩa **Read-optimization (tối ưu hóa đọc)**.

Lời khuyên: Chỉ thực hiện nó khi các câu lệnh `JOIN` thực sự không thể đáp ứng được **Latency SLO (mục tiêu độ trễ)** ở quy mô hệ thống hiện tại của bạn — đừng làm điều đó sớm hơn."