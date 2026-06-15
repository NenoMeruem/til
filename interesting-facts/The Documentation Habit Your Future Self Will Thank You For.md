# The Documentation Habit Your Future Self Will Thank You For

Node: [[article]]
Tags:  #productivity

Bộ nhớ con người giống như một cơ chế cache – nó có thể điền vào các phần thiếu, nhưng không phải lúc nào cũng chính xác.

Bạn từng chắc chắn về một thông tin nào đó, nhưng sau đó phát hiện ra mình đã sai chưa? Ví dụ, bạn có thể “nhớ” rằng nhân vật Monopoly Man đeo kính một mắt (monocle). Hoặc bạn nghĩ tên của loạt truyện thiếu nhi là *Berenstein Bears* thay vì *Berenstain Bears*. Nhưng cả hai ký ức này đều sai.

Hiện tượng này được gọi là Hiệu ứng Mandela (Mandela Effect) – khi nhiều người cùng “truy xuất dữ liệu” từ bộ nhớ và cùng nhớ sai theo một cách giống nhau. Đây không đơn giản là quên, mà là bộ nhớ giả (false memory) – thông tin không đúng được não bộ tạo ra như thể nó là thật.

Tại sao vậy? Giống như một thuật toán auto-complete, não bộ có xu hướng điền vào các chi tiết bị thiếu dựa trên mẫu đã học, hoặc tái sử dụng lại dữ liệu lỗi đã từng gặp. Đôi khi, nó thậm chí còn tạo ra các “giá trị mặc định” (default values) cho các chi tiết chưa từng tồn tại. Và thế là, chúng ta có cảm giác chắc chắn rằng ký ức đó là chính xác — trong khi thực tế thì không.


Trong kỹ thuật phần mềm, chúng ta cũng làm điều tương tự với:

* Mã nguồn (Code)
* Hệ thống (Systems)
* Quy trình (Processes)
* Các quyết định thiết kế (Decisions)

Chúng ta nghĩ rằng mình nhớ rõ cách một thứ gì đó hoạt động.
Cho đến khi... không còn nhớ nữa.


## Tại sao tài liệu kỹ thuật quan trọng hơn bạn nghĩ

Hãy thử hỏi một lập trình viên về một đoạn mã cũ, họ sẽ trả lời: *“À, tôi nhớ cách đoạn này hoạt động.”*
Nhưng khi quay lại xem thực sự, khả năng cao là họ sẽ không nhớ chi tiết. Điều này là hoàn toàn bình thường — con người không thể ghi nhớ chính xác mọi thứ, đặc biệt khi hằng ngày phải tiếp nhận một lượng lớn thông tin kỹ thuật.

Khó có chuyện một nhóm kỹ sư phần mềm "tưởng tượng ra" một hàm không hề tồn tại. Tuy nhiên, các chi tiết nhỏ dễ bị quên lãng, và những giả định trước đó không phải lúc nào cũng đúng. Điều này không chỉ đơn giản là một vấn đề về trí nhớ — mà là một vấn đề kỹ thuật.

Dự án mở rộng, đội ngũ thay đổi, và những gì từng rõ ràng bỗng trở thành một trò chơi đoán mò. Trong trường hợp đó, tài liệu kỹ thuật (code documentation) đóng vai trò như nguồn tham chiếu giúp đội ngũ hiểu cách hệ thống hoạt động. Nhưng trong thực tế, tài liệu thường bị thiếu, không cập nhật, hoặc thậm chí không tồn tại.

Là một quản lý kỹ thuật (Engineering Manager - EM), bạn không phải là người trực tiếp viết toàn bộ mã nguồn. Nhưng bạn chịu trách nhiệm đảm bảo đội ngũ của mình có thể hiểu, bảo trì, và phát triển trên nền tảng đó. Vì vậy, tài liệu kỹ thuật không phải là một tuỳ chọn hay thứ “có thì tốt” — mà là một yếu tố chiến lược và nhu cầu mang tính con người sâu sắc.

## Tài liệu kỹ thuật là cẩm nang sinh tồn của lập trình viên

Đôi khi, bạn sẽ rơi vào tình huống không biết phải dựa vào đâu để giải mã một quy trình phức tạp, một biến không rõ ý nghĩa, hoặc một dịch vụ bị rối như tơ vò. Và chính lúc đó, tài liệu kỹ thuật (documentation) là chiếc phao cứu sinh:

* Giúp làm rõ các khái niệm mơ hồ
* Tiết kiệm thời gian tra cứu
* Giữ cho tiến độ dự án không bị đình trệ

Không có tài liệu, bạn sẽ phải mò mẫm, đọc ngược code, và dựa vào trí nhớ — những thứ dễ dẫn đến sai sót và làm chậm tiến độ phát triển.

Tài liệu giúp các team phát triển giữ đúng hướng. Nó lưu lại những gì đã được xây dựng, vì sao các quyết định kỹ thuật được đưa ra, và cách các hệ thống phức tạp được cấu trúc. Những thông tin này là nền tảng để việc bảo trì, mở rộng hoặc chuyển giao dự án sau này trở nên dễ dàng và hiệu quả hơn.

## Người hùng thầm lặng trong quy trình onboarding

Hãy tưởng tượng bạn bắt đầu một công việc lập trình mới mà không có bất kỳ sự hướng dẫn nào. Có thể bạn đã từng trải qua rồi: không được giới thiệu, không có tài liệu giải thích — chỉ là một đống mã nguồn (codebase), thời gian hạn hẹp và kỳ vọng rằng bạn sẽ *tự mò mẫm* mọi thứ.

Đó chính là trải nghiệm onboarding (quy trình làm quen công việc) khi thiếu tài liệu kỹ thuật (technical documentation) đầy đủ.

Sự thật là các lập trình viên mới không nhất thiết phải cảm thấy hoang mang hay quá tải. Tài liệu tốt chính là bản đồ dẫn đường cho họ. Thay vì phải liên tục hỏi đồng nghiệp, người mới có thể:

* Nhìn thấy kiến trúc hệ thống và cách các thành phần kết nối với nhau
* Hiểu được lý do đằng sau các quyết định thiết kế trước đó
* Nhanh chóng làm quen và bắt nhịp công việc mà không cần phụ thuộc quá nhiều vào người khác

Tuy nhiên, onboarding chỉ là một phần nhỏ trong bức tranh lớn hơn. Documentation (tài liệu) là tài sản chung của cả team:

* Giúp bảo tồn tri thức (knowledge preservation), tránh để kiến thức quan trọng bị thất lạc khi ai đó nghỉ việc
* Hỗ trợ việc handoff (chuyển giao công việc) trở nên trơn tru hơn
* Tăng cường hiệu quả collaboration (làm việc nhóm) giữa các thành viên

Việc viết tài liệu không chỉ là chuyện tiện lợi. Nó là cách để đảm bảo kiến thức nằm trong hệ thống của team, không bị “giam giữ” trong đầu của một cá nhân nào đó.

## "Chất keo gắn kết xã hội" trong kỹ thuật phần mềm

Nếu bạn may mắn, đội ngũ của bạn sẽ có một người đóng vai trò là “chất keo gắn kết xã hội” — người hay tổ chức các buổi liên hoan, hỏi thăm đồng nghiệp, và giữ cho tinh thần đồng đội luôn tích cực. Họ giúp xây dựng và duy trì các mối quan hệ trong nhóm.

Trong kỹ thuật phần mềm, tài liệu kỹ thuật chính là phiên bản “kỹ thuật” của chất keo này.

Giống như chất keo xã hội giúp kết nối con người, tài liệu kỹ thuật giúp kết nối và duy trì tri thức chung của cả nhóm. Và không chỉ gói gọn trong một nhóm kỹ thuật cụ thể, tài liệu còn là cầu nối giữa các vai trò khác nhau trong quá trình phát triển phần mềm, bao gồm:

* Frontend
* Backend
* UI/UX Designers
* QA
* Và nhiều bộ phận khác

Mỗi vai trò đều đóng góp vào việc xây dựng và duy trì một hệ thống phần mềm phức tạp. Khi tài liệu được viết đầy đủ, rõ ràng và dễ truy cập, nó giúp toàn bộ team vận hành hiệu quả và nhất quán. Ngược lại, khi thiếu tài liệu, quy trình phát triển dễ bị rối loạn, hiểu nhầm hoặc gián đoạn.

Tài liệu không chỉ là thứ để “ghi lại”, mà là nền tảng giúp gắn kết các nhóm kỹ thuật với nhau.


Vì sao tài liệu kỹ thuật (documentation) lại quan trọng:

### 1 — Tài liệu là nguồn chân lý duy nhất (single source of truth)

Tài liệu đóng vai trò là nguồn thông tin trung tâm, giúp mọi thành viên trong team hiểu rõ cách các thành phần trong hệ thống kết nối với nhau. Thay vì phải phụ thuộc vào:

* Tin nhắn rời rạc
* Các buổi họp
* Truyền đạt miệng

Các team có thể sử dụng tài liệu rõ ràng để định nghĩa quy trình (processes), cách hoạt động của API, và các quyết định về kiến trúc hệ thống (architecture decisions).

Ví dụ, một lập trình viên frontend không nên phải đoán xem một API hoạt động ra sao — họ cần tài liệu chi tiết để tích hợp chính xác. Tương tự, kỹ sư kiểm thử phần mềm (QA engineer) cũng cần tài liệu hướng dẫn hành vi mong đợi của hệ thống và các trường hợp kiểm thử (test cases).


### 2 — Hỗ trợ làm việc từ xa và không đồng bộ (remote & async)

Tài liệu không chỉ cần thiết cho các team làm việc tại văn phòng. Với các team remote, việc giao tiếp bằng văn bản là chủ yếu, thay vì các cuộc trao đổi nhanh trực tiếp.

Thiếu tài liệu sẽ khiến việc chia sẻ kiến thức trở nên khó khăn và mất thời gian. Nếu thông tin quan trọng bị thiếu, nhân sự mới sẽ lúng túng khi onboard, dễ xảy ra lỗi và tiến độ công việc bị chậm lại.

Một hệ thống được ghi chép đầy đủ sẽ cho phép các thành viên trong team:

* Hiểu quy trình mà không cần chờ phản hồi từ người khác
* Làm việc không đồng bộ nhưng vẫn bám sát mục tiêu
* Onboard nhanh chóng và đóng góp sớm hơn vào dự án

### 3 — Giúp duy trì sự nhất quán

Mỗi team kỹ thuật đều có workflow, best practices và coding standards riêng. Việc có tài liệu chung giúp các team tuân thủ các tiêu chuẩn này một cách nhất quán trong toàn công ty. Ví dụ:

* Review code theo cùng một nguyên tắc
* Thiết lập môi trường phát triển giống nhau
* Triển khai tính năng theo quy trình chuẩn

Nếu không có tài liệu dùng chung, mỗi team có thể sẽ làm theo cách riêng — điều này dẫn đến sự không đồng nhất, thiếu hiệu quả và dễ xảy ra hiểu lầm trong giao tiếp.


Tóm lại, tài liệu kỹ thuật không chỉ đơn thuần là ghi chép để khỏi quên. Nó là công cụ:

* Kết nối các team
* Giảm ma sát khi phối hợp
* Đảm bảo sự hợp tác trơn tru giữa các vai trò, vị trí địa lý và dự án khác nhau


## Trí tuệ nhân tạo (AI) đang tái định hình cách viết tài liệu kỹ thuật như thế nào?

Hãy thẳng thắn mà nói: việc viết tài liệu (documentation) là một công việc tốn thời gian, và đó là lý do khiến nó thường bị bỏ qua trong quy trình phát triển phần mềm. Tuy nhiên, các công cụ AI đang thay đổi điều đó.

Hiện nay, AI có thể tự động tạo và cập nhật tài liệu dựa trên code – cụ thể là thông qua các comment trong mã nguồn, tên hàm, tham số, và cấu trúc chương trình. Ví dụ, các công cụ như Cursor có khả năng quét mã nguồn và sinh ra tài liệu một cách tự động dựa trên thông tin hiện có trong codebase. Điều này giúp tài liệu luôn đồng bộ với mã nguồn, mà không cần lập trình viên phải tốn thêm công sức cập nhật thủ công.

Ngay cả khi code được refactor (tái cấu trúc), tài liệu vẫn sẽ được cập nhật chính xác theo thay đổi mới. Và không chỉ dừng lại ở tài liệu kỹ thuật truyền thống, AI còn có thể xử lý nhiều định dạng khác như biên bản họp (meeting transcripts), trao đổi trên Slack, hoặc comment trên Jira, và chuyển đổi các thông tin đó thành nội dung tài liệu có hệ thống.

Ví dụ: khi bạn muốn triển khai một service mới trong hệ thống, với tài liệu chuẩn và các quy ước rõ ràng, AI có thể generate (tự động sinh) phần code cho service đó — và đồng thời viết luôn phần tài liệu kỹ thuật cho chức năng mới này.

### Những cải tiến mà AI mang lại cho tài liệu kỹ thuật:

* Lấp đầy khoảng trống tri thức: AI giúp tài liệu luôn có cấu trúc logic, dễ tìm kiếm và đầy đủ nội dung.
* Đảm bảo tính nhất quán giữa các nhóm phát triển: AI thường tuân theo một format chuẩn, giúp toàn bộ nhóm phát triển làm việc với tài liệu đồng nhất và rõ ràng.
* Giảm lỗi và thông tin lỗi thời: AI phát hiện các chi tiết còn thiếu hoặc không nhất quán, từ đó giúp tài liệu chính xác hơn.
* Tự động cập nhật tài liệu: Khi có thay đổi trong mã nguồn, tài liệu cũng sẽ được cập nhật theo mà không cần thao tác thủ công.

Kết quả là lập trình viên có thể tin tưởng vào tài liệu, không còn phải "đoán già đoán non", và tiết kiệm được thời gian để tập trung vào những công việc quan trọng hơn.

AI đang giải phóng lập trình viên khỏi những tác vụ lặp đi lặp lại và tốn công sức, giúp họ dành nhiều thời gian hơn cho việc phát triển sản phẩm chất lượng.


## Vậy bao nhiêu tài liệu là đủ?

Đây là một câu hỏi khó, nhưng vẫn có một số nguyên tắc bạn có thể áp dụng. 

Tài liệu quá nhiều có thể gây quá tải. Những tài liệu dài dòng và phức tạp dễ khiến người đọc lướt qua, bỏ sót chi tiết hoặc thậm chí bỏ qua hoàn toàn.

Ngược lại, thiếu tài liệu cũng gây ra nhiều vấn đề. Khi không có đủ hướng dẫn, lập trình viên dễ đưa ra giả định – mà giả định thì thường dẫn đến lỗi.

Cách tiếp cận tốt nhất là giữ cho tài liệu kỹ thuật đơn giản, rõ ràng và dễ tra cứu.
Thay vì tạo ra những tài liệu đồ sộ, hãy tập trung vào những gì team thực sự cần. Cố gắng đảm bảo tài liệu của bạn có các đặc điểm sau:

* Ngắn gọn: Chỉ ghi lại những thông tin quan trọng nhất.
* Có cấu trúc rõ ràng: Sử dụng tiêu đề, bullet point và chia nhỏ nội dung thành các phần ngắn.
* Dễ truy cập: Lưu trữ ở những nơi quen thuộc như file Markdown, Google Docs hoặc wiki nội bộ.

Hãy nhớ, tài liệu tốt là tài liệu trả lời được câu hỏi trước khi nó được đặt ra. Nó nên hỗ trợ developer, giúp họ nhanh chóng hiểu và thực hiện công việc mà không cần phải “đào bới” qua hàng trăm trang giấy. Kiến thức chia sẻ cần là công cụ hỗ trợ, không phải gánh nặng.

## Tóm tắt ngắn gọn: Viết lại tài liệu, tương lai bạn sẽ cảm ơn chính mình

Bộ nhớ con người không hoàn hảo. Kỹ thuật phần mềm rất phức tạp. Documentation (tài liệu kỹ thuật) chính là cầu nối kết nối các mảnh thông tin rời rạc. Nếu không có nó, team sẽ phải dựa vào trí nhớ, các tin nhắn rải rác và những cuộc họp dài lê thê. Điều này dẫn đến sự nhầm lẫn, trì hoãn và lỗi phát sinh.

Tài liệu tốt chính là source of truth (nguồn thông tin chính xác và duy nhất). Nó giúp các team giữ được sự kết nối và làm việc hiệu quả, đồng thời hỗ trợ:

* Onboarding: giúp các kỹ sư mới nhanh chóng hiểu hệ thống mà không phải phụ thuộc vào ai khác.
* Collaboration: các vai trò khác nhau như frontend, backend, QA, designer làm việc phối hợp trơn tru.
* Remote & distributed work: kiến thức được ghi chép giúp team làm việc không đồng bộ một cách hiệu quả.
* Consistency: tài liệu chung giúp duy trì các best practices xuyên suốt team.

Với vai trò là một Engineering Manager (EM), bạn sẽ định hướng văn hóa làm việc. Nếu team thấy bạn liên tục ghi chép các quyết định và best practice, và giữ cho kiến thức luôn minh bạch — họ sẽ làm theo. Ngược lại, nếu bạn xem việc viết tài liệu là gánh nặng, team cũng vậy.

AI đang thay đổi cách chúng ta làm documentation: nó tự động cập nhật, sinh tài liệu từ code, và đảm bảo tính nhất quán, giúp giảm tải gánh nặng này.

Hãy sử dụng các công cụ đơn giản để làm cho việc viết tài liệu trở nên dễ dàng hơn. Thể hiện giá trị của nó bằng cách nhấn mạnh cách nó tiết kiệm thời gian và tránh lỗi. Biến việc viết tài liệu thành một thói quen, chứ không phải là một nhiệm vụ bắt buộc.

Bài viết được dịch tại:
- https://medium.com/engineering-managers-journal/the-documentation-habit-your-future-self-will-thank-you-for-7bf1234497cb