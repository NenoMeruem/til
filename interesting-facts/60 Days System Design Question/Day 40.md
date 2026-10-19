Nodes: [[60 Days System Design Question]]
Tags: #system-design 
# Your React dashboard freezes for 4 seconds every time a user uploads a CSV.


![[Pasted image 20261015170910.png]]



**Dashboard React của bạn bị đơ cứng mất 4 giây mỗi khi người dùng upload một file CSV.**

Không phải lỗi mạng. Mà là trình duyệt bị đóng băng (freezing). Tab không phản hồi (unresponsive). Animation bị kẹt cứng. Hộp thoại “Page Unresponsive” (Trang web không phản hồi) của Chrome bật lên.

Dưới đây là thực trạng đang diễn ra trên môi trường Production:

• Người dùng kéo thả một file CSV nặng 80MB (200.000 dòng, 40 cột) vào vùng upload.

• Code của bạn: Gọi hàm `Papa.parse(file, { complete: … })` chạy trực tiếp trên **Main Thread** (Luồng chính).

• Quá trình Parsing (Phân tích cú pháp) + Validation (Kiểm tra dữ liệu) + Schema Mapping (Ánh xạ lược đồ) = 3.8 giây thực thi **synchronous JS** (JavaScript đồng bộ).

• Trong suốt 3.8 giây đó: Thao tác scroll (cuộn trang) bị chết, loading spinner dừng quay, input lag (độ trễ nhập liệu) tăng lên vô cực.

• Điểm số **INP (Interaction to Next Paint)** trên dashboard hiệu năng của bạn chuyển sang màu đỏ. Lighthouse đang "gào thét".

Product Team yêu cầu phải fix dứt điểm vấn đề này trước buổi demo cho khách hàng doanh nghiệp vào thứ Sáu tới. Có 4 phương án đang được cân nhắc:

**A) requestIdleCallback + time-slicing** — Cắt nhỏ quá trình parse thành các "lát cắt" 5ms, nhường quyền (yield) giữa các dòng, để trình duyệt có khoảng thở.

**B) Web Worker** — Đẩy toàn bộ pipeline parse + validation sang `worker.js`, giao tiếp qua `postMessage`, giữ cho Main Thread luôn rảnh rỗi.

**C) SharedArrayBuffer + Atomics** — Chia sẻ bộ đệm file (file buffer) giữa Main Thread và 4 Web Worker, chạy song song quá trình parse đa luồng trên nhiều core CPU, đạt cơ chế zero-copy.

**D) Compile parser sang WebAssembly (WASM)** — Loại bỏ JS parser, chạy một CSV parser viết bằng ngôn ngữ Rust thông qua WASM để đạt tốc độ gần như native (mã máy).

Cả 4 phương án này đều được áp dụng trong các codebase frontend thực tế. Nhưng có 3 phương án là **lựa chọn sai** cho bài toán cụ thể này. Chỉ có **một đáp án đúng** mà các sản phẩm như Figma, Google Sheets và Excalidraw đang thực tế sử dụng.

Một phương án chính là **cái bẫy dành cho Senior Engineer** (Senior-engineer trap). Nghe có vẻ rất "over-engineered" (thiết kế đao to búa lớn) trong các buổi Design Review. Làm tăng gấp đôi độ phức tạp của hạ tầng. Buộc bạn phải cấu hình lại các HTTP header `COOP`/`COEP` và làm hỏng một nửa các bên thứ ba (third-party embeds) đang tích hợp trên trang. Nó đi giải quyết một vấn đề mà thực tế bạn không hề gặp phải.

Hãy chọn một — **A, B, C, hay D** — và giải thích lý do tại sao. Phân tích chi tiết sẽ có trong phần bình luận (bao gồm cả việc đâu là phương án "cái bẫy", và tại sao câu trả lời "dùng parser nhanh hơn" lại không giải quyết được vấn đề gì trong trường hợp này).


 **Vì sao phương án B giành chiến thắng:**

![[Pasted image 20261015171329.png]]

Vấn đề thực tế không nằm ở tốc độ, mà là **nó được thực thi ở đâu**. 

*Main thread* (luồng chính) chính là nơi xử lý mọi thứ: từ sự kiện cuộn trang (*scroll*), nhận input từ người dùng, tính toán *layout*, *paint* (vẽ giao diện) cho đến các hiệu ứng *animation*. Bất kỳ tác vụ nào chạy đồng bộ (*synchronous*) trên luồng này đều sẽ dẫn đến hiện tượng giật lag (*jank*). Chấm hết.

Trong khi đó, **Web Worker** là một OS-level thread (luồng cấp hệ điều hành) độc lập với *event loop* (vòng lặp sự kiện) riêng của nó. Bạn chỉ cần đẩy file sang đó (có thể truyền tải dữ liệu siêu tốc bằng `postMessage` kết hợp với *Transferable objects* để đạt cơ chế *zero-copy* - không tốn phí copy bộ nhớ), tiến hành *parse* (phân tích cú pháp) dữ liệu ở bên đó, rồi gửi các dòng dữ liệu đã xử lý ngược lại. 

Kết quả là *Main thread* vẫn duy trì mượt mà mức **60fps** trong suốt quá trình. Chỉ số **INP** (Interaction to Next Paint) lao dốc từ **3800ms xuống còn khoảng ~80ms**. Hoàn tất.

Đây chính là cách mà Figma áp dụng cho pipeline render của họ, cách Google Sheets tính toán lại công thức (*formula recalc*), cách Excalidraw xử lý scene, và cách VS Code Web thực hiện tô sáng cú pháp (*syntax highlighting*). Mọi sản phẩm nền tảng web nghiêm túc đều đẩy các tác vụ tính toán nặng nhọc vào một Worker riêng biệt. Đó là một giải pháp kinh điển, chuẩn xác và đã được kiểm chứng suốt một thập kỷ qua.


**Tại sao phương án A lại sai (cạm bẫy của sự “khôn vặt”):**

Việc kết hợp `requestIdleCallback` và `time-slicing` (cắt lát thời gian) giúp UI _về mặt lý thuyết_ vẫn phản hồi (responsive), nhưng nó lại kéo dài thời gian parse (phân tích cú pháp) từ 3.8 giây lên tới khoảng 6 giây (wall-clock time — tổng thời gian thực thi thực tế), lý do là vì cứ liên tục phải `yield` (nhường luồng/thread). Tệ hơn nữa là: các idle callback có độ ưu tiên thấp — nên khi hệ thống chịu tải cao (under load), chúng thậm chí còn không thèm chạy. Cơ chế render bất đồng bộ (concurrent rendering) của React 18 dùng time-slicing cho việc _render_, chứ không phải cho các tác vụ mang tính chất I/O (I/O-shaped work) gây block luồng. Dùng sai công cụ rồi.

**Tại sao phương án C lại sai (Cạm bẫy của SENIOR KINH NGHIỆM):**

Dùng `SharedArrayBuffer` kết hợp với `Atomics` là câu trả lời nghe có vẻ rất "nguy hiểm" và thông minh trong các buổi design review (đánh giá thiết kế kiến trúc). *"Chúng ta sẽ chạy đa luồng tận dụng mọi core CPU! Không tốn chi phí copy dữ liệu (Zero-copy)! Lập trình phi khóa (Lock-free)!"* Rồi bạn sẽ nhận ra thực tế phũ phàng:

• Nó bắt buộc phải cấu hình header COOP và COEP trên toàn trang (site-wide), điều này sẽ làm sập/lỗi Stripe Elements, các khung nhúng YouTube, Intercom, và khoảng một nửa số script đo lường analytics của bạn.

• Việc parse một file CSV 80MB là một bài toán _tuần tính một cách hiển nhiên_ (embarrassingly serializable) — việc chia nhỏ các dòng ra 4 core xử lý chỉ giúp bạn tiết kiệm được khoảng 2 giây, nhưng đổi lại là hàng tuần chìm trong "địa ngục" cấu hình cách ly nguồn gốc chéo (cross-origin isolation).

• Giờ đây, bạn đang tự "ôm" một thread pool (nhóm luồng) tự chế viết bằng JavaScript. Vào năm 2026.

`SharedArrayBuffer` chỉ thực sự là đáp án đúng cho _đúng hai_ bài toán: xử lý audio/video thời gian thực (nơi bạn cần các bộ đệm vòng phi khóa - lock-free ring buffers giữa các thread ở tần số 48kHz), và chia sẻ trạng thái giả lập (như các engine game multiplayer chạy trên trình duyệt). Một pha upload file CSV một lần rồi thôi không nằm trong hai trường hợp đó.

**Tại sao phương án D lại sai:**

WebAssembly (WASM) giúp cho trình parser chạy _nhanh hơn_. Nhưng nó không hề bứng (move) tiến trình đó ra khỏi **Main Thread** (luồng chính). Một parser viết bằng WASM mà chạy đồng bộ (synchronously) trên Main Thread thì vẫn cứ làm đơ UI như thường — chỉ là đơ 1.2 giây thay vì 3.8 giây mà thôi. Bạn vẫn phải nhét nó vào trong một **Web Worker**. Thế nên D không phải là một giải pháp hoàn chỉnh; nó chỉ là một kiểu tối ưu tiềm năng nằm _bên trong_ phương án B mà thôi. Và thành thật mà nói, dùng thư viện Papa Parse chạy bên trong một Web Worker là đã đủ nhanh rồi, chẳng cần đến WASM đâu.

