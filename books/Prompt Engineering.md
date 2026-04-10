
Author: Lee Boonstra 


"You don’t need to be a data scientist or a machine learning engineer – everyone can write  a prompt."

Node: [[books]]
Tags: #book , #ai

## Introduction

Khi xem xét **input** và **output** của một _large language model (LLM)_, **prompt** (chuỗi văn bản đầu vào, đôi khi kết hợp thêm các _modalities_ khác như _image prompt_) chính là dữ liệu mà mô hình sử dụng để **suy luận (inference)** và dự đoán ra kết quả đầu ra mong muốn.

Bạn không cần phải là _data scientist_ hay _machine learning engineer_ để viết prompt — bất kỳ ai cũng có thể làm điều đó. Tuy nhiên, việc **thiết kế prompt tối ưu (prompt engineering)** lại không hề đơn giản.

Hiệu quả của một prompt phụ thuộc vào nhiều yếu tố, bao gồm:

- **Model** bạn sử dụng (kiến trúc, khả năng xử lý)
- **Training data** (dữ liệu huấn luyện của mô hình)
- **Model configurations** (các tham số cấu hình như temperature, max tokens, v.v.)
- **Word choice** (lựa chọn từ ngữ)
- **Style & tone** (phong cách và giọng điệu)
- **Structure** (cấu trúc prompt)
- **Context** (ngữ cảnh cung cấp cho mô hình)

Do đó, _prompt engineering_ là một quá trình **lặp (iterative process)** — bạn cần thử nghiệm, đánh giá và tinh chỉnh nhiều lần để đạt được kết quả tốt nhất.

Một prompt không được thiết kế tốt có thể dẫn đến:
- Kết quả **mơ hồ (ambiguous output)**
- Thông tin **không chính xác (inaccurate response)**
- Và làm giảm khả năng của mô hình trong việc tạo ra **output có ý nghĩa (meaningful output)**

Khi bạn tương tác với chatbot Gemini, về cơ bản bạn đang **viết các prompt (câu lệnh đầu vào)**. Tuy nhiên, tài liệu này tập trung vào việc xây dựng prompt cho mô hình Gemini khi triển khai trong **Vertex AI** hoặc thông qua **API**, bởi vì khi gọi trực tiếp đến model, bạn có thể truy cập và tùy chỉnh các **tham số cấu hình (configuration parameters)** như _temperature_, _top-p_, v.v.

Tài liệu này sẽ đi sâu vào **prompt engineering (kỹ thuật thiết kế prompt)**. Chúng ta sẽ cùng phân tích các **kỹ thuật prompting khác nhau** nhằm giúp bạn nhanh chóng bắt đầu, đồng thời chia sẻ các **best practices (thực tiễn tốt nhất)** để nâng cao kỹ năng và trở thành một “prompt engineer” hiệu quả.

Ngoài ra, tài liệu cũng đề cập đến một số **thách thức (challenges)** mà bạn có thể gặp phải trong quá trình thiết kế prompt, chẳng hạn như kiểm soát đầu ra của mô hình, tránh sai lệch ngữ nghĩa, hoặc tối ưu hiệu suất phản hồi.

## Prompt engineering

Hãy nhớ cách một mô hình ngôn ngữ lớn (LLM) hoạt động; nó là một **công cụ dự đoán**. Mô hình nhận **văn bản tuần tự** làm đầu vào, rồi **dự đoán token (đơn vị ngôn ngữ) tiếp theo** sẽ là gì, dựa trên dữ liệu mà nó đã được huấn luyện.

LLM được vận hành để lặp lại quá trình này nhiều lần — mỗi lần, nó **thêm token vừa được dự đoán** vào cuối chuỗi văn bản hiện có để tiếp tục **dự đoán token kế tiếp**.

Việc dự đoán token tiếp theo **dựa trên mối quan hệ** giữa các token trước đó và **những gì LLM đã học được trong quá trình huấn luyện**.

Khi bạn viết một **prompt** , bạn đang cố gắng thiết lập cho **LLM** (mô hình ngôn ngữ lớn) dự đoán đúng chuỗi **token** (đơn vị ngôn ngữ) tiếp theo. **Kỹ thuật thiết kế prompt** (prompt engineering) là quá trình tạo ra những prompt chất lượng cao nhằm hướng dẫn LLM tạo ra các kết quả chính xác.

Quá trình này bao gồm việc thử nghiệm để tìm ra prompt hiệu quả nhất, tối ưu độ dài của prompt, và đánh giá phong cách viết cũng như cấu trúc của prompt trong mối liên hệ với nhiệm vụ được giao.

Trong bối cảnh **xử lý ngôn ngữ tự nhiên (NLP)** và **LLM**, một _prompt_ là phần đầu vào được cung cấp cho mô hình để nó tạo ra phản hồi hoặc dự đoán.

Các lời nhắc (prompts) này có thể được sử dụng để thực hiện nhiều loại nhiệm vụ hiểu và tạo nội dung khác nhau, chẳng hạn như **tóm tắt văn bản, trích xuất thông tin, hỏi đáp, phân loại văn bản, dịch ngôn ngữ hoặc mã, tạo mã, và viết tài liệu hoặc suy luận về mã**.

Bạn có thể tham khảo **các hướng dẫn về cách tạo prompt của Google** với những ví dụ đơn giản và hiệu quả.

Khi thực hiện **kỹ thuật thiết kế prompt (prompt engineering)**, bạn sẽ bắt đầu bằng việc chọn một mô hình. Các prompt có thể cần được **tối ưu hóa cho mô hình cụ thể** mà bạn sử dụng, dù đó là **mô hình ngôn ngữ Gemini trong Vertex AI, GPT, Claude**, hay **một mô hình mã nguồn mở như Gemma hoặc LLaMA**.

Ngoài phần prompt, bạn cũng sẽ cần **điều chỉnh nhiều cấu hình khác nhau của mô hình ngôn ngữ lớn (LLM)**.

## LLM output configuration

Khi bạn đã chọn được mô hình của mình, bạn sẽ cần xác định cấu hình của mô hình đó. Hầu hết các mô hình ngôn ngữ lớn (LLM) đều có nhiều tùy chọn cấu hình khác nhau để kiểm soát đầu ra của chúng. Việc thiết kế prompt (prompt engineering) hiệu quả đòi hỏi phải thiết lập các cấu hình này một cách tối ưu cho nhiệm vụ của bạn.

### Output length

Một thiết lập cấu hình quan trọng là số lượng **token** được tạo ra trong một phản hồi. Việc tạo ra nhiều **token** hơn đòi hỏi mô hình ngôn ngữ lớn (LLM) phải thực hiện nhiều phép tính hơn, dẫn đến **mức tiêu thụ năng lượng cao hơn**, **thời gian phản hồi có thể chậm hơn**, và **chi phí cao hơn**.

Việc giảm độ dài đầu ra của mô hình ngôn ngữ lớn (LLM) **không khiến LLM trở nên ngắn gọn hơn về mặt phong cách hay nội dung** trong văn bản mà nó tạo ra — điều đó chỉ khiến LLM **ngừng sinh thêm token** khi đạt đến giới hạn được đặt ra.

Nếu bạn cần một đầu ra ngắn, bạn có thể sẽ phải **thiết kế lại prompt** của mình để phù hợp với yêu cầu đó.

Giới hạn độ dài đầu ra đặc biệt quan trọng trong một số kỹ thuật gợi ý (prompting) của LLM, như **ReAct**, nơi mà mô hình có thể tiếp tục sinh ra các token không cần thiết sau khi đã tạo xong phản hồi mong muốn.

Hãy lưu ý rằng, **việc tạo ra nhiều token hơn** sẽ **đòi hỏi nhiều tài nguyên tính toán hơn** từ LLM, dẫn đến **tiêu thụ năng lượng cao hơn** và **thời gian phản hồi chậm hơn**, từ đó **làm tăng chi phí**.

### Sampling controls

Các mô hình ngôn ngữ lớn (LLM) không thực sự “dự đoán” một token duy nhất. Thay vào đó, LLM dự đoán **xác suất** cho từng khả năng về token tiếp theo — mỗi token trong **từ vựng** của mô hình sẽ được gán một xác suất. Sau đó, các xác suất này được **lấy mẫu (sampling)** để xác định token nào sẽ được tạo ra tiếp theo.

Ba tham số cấu hình phổ biến nhất — **temperature**, **top-K**, và **top-P** — quyết định cách các xác suất dự đoán được xử lý để chọn ra **một token đầu ra duy nhất**.

### Temperature

Nhiệt độ kiểm soát mức độ ngẫu nhiên trong việc chọn token. Nhiệt độ thấp phù hợp cho các yêu cầu (prompt) cần phản hồi có tính xác định cao, trong khi nhiệt độ cao có thể dẫn đến kết quả đa dạng hoặc bất ngờ hơn.

Nhiệt độ bằng 0 (giải mã tham lam — _greedy decoding_) là xác định: token có xác suất cao nhất luôn được chọn (tuy nhiên, nếu có hai token có cùng xác suất cao nhất, tùy vào cách hệ thống xử lý tình huống “hòa”, bạn có thể không nhận được cùng một đầu ra ngay cả khi nhiệt độ là 0).

Khi nhiệt độ tiến gần giá trị tối đa, đầu ra có xu hướng ngẫu nhiên hơn. Và khi nhiệt độ càng tăng cao, mọi token đều có khả năng như nhau để trở thành token được dự đoán tiếp theo.

Cơ chế điều khiển nhiệt độ của Gemini có thể được hiểu tương tự như hàm _softmax_ được sử dụng trong học máy. Cài đặt nhiệt độ thấp tương ứng với nhiệt độ _softmax_ thấp (T), nhấn mạnh một lựa chọn đơn lẻ, ưu tiên với độ chắc chắn cao. Ngược lại, cài đặt nhiệt độ Gemini cao giống với nhiệt độ _softmax_ cao, khiến một phạm vi rộng hơn của các giá trị nhiệt độ xung quanh mức đã chọn trở nên chấp nhận được hơn.

Sự không chắc chắn tăng lên này phù hợp cho các tình huống mà độ chính xác cứng nhắc không quá cần thiết — chẳng hạn như khi thử nghiệm với các đầu ra mang tính sáng tạo.


### Top-K and top-P

Top-K và top-P (còn được gọi là **lấy mẫu hạt nhân**) là hai thiết lập lấy mẫu được sử dụng trong các mô hình ngôn ngữ lớn (LLM) nhằm giới hạn việc chọn **token** tiếp theo trong số những token có **xác suất dự đoán cao nhất**. Giống như **nhiệt độ (temperature)**, các thiết lập lấy mẫu này điều chỉnh **mức độ ngẫu nhiên và đa dạng** của văn bản được tạo ra.

- Phép lấy mẫu Top-K chọn ra **K token có xác suất cao nhất** từ phân phối dự đoán của mô hình. Giá trị **K càng cao**, đầu ra của mô hình càng **sáng tạo và đa dạng**;  giá trị **K càng thấp**, đầu ra càng **ổn định và mang tính chính xác thực tế** hơn. Khi **top-K = 1**, quá trình này tương đương với **giải mã tham lam (greedy decoding)**.
- Lấy mẫu Top-P (Top-P sampling) chọn ra các token hàng đầu sao cho tổng xác suất tích lũy của chúng không vượt quá một giá trị nhất định (P). Giá trị của P dao động từ 0 (giải mã tham lam — greedy decoding) đến 1 (bao gồm tất cả các token trong vốn từ vựng của mô hình ngôn ngữ lớn).

Cách tốt nhất để lựa chọn giữa **top-K** và **top-P** là **thử nghiệm với cả hai phương pháp** (hoặc kết hợp cả hai) và **xem phương pháp nào tạo ra kết quả mà bạn mong muốn**.


### Putting it all together 


Việc lựa chọn giữa **top-K**, **top-P**, **temperature** và **số lượng token cần sinh (max tokens)** phụ thuộc vào **bài toán cụ thể** và **kết quả mong muốn**. Các tham số này **không hoạt động độc lập** mà **ảnh hưởng lẫn nhau**, vì vậy cần hiểu rõ cách chúng tương tác. Ngoài ra, bạn cũng cần nắm được **cách mô hình kết hợp các tham số sampling** này với nhau.  

Nếu **temperature**, **top-K** và **top-P** đều khả dụng (ví dụ như trong **Vertex AI Studio**), thì quá trình dự đoán token tiếp theo diễn ra như sau:

1. Mô hình trước hết lọc các token thỏa mãn **đồng thời cả hai điều kiện top-K và top-P**.
2. Những token vượt qua bước lọc này sẽ trở thành **ứng viên (candidate tokens)** cho token tiếp theo.
3. Sau đó, **temperature** được áp dụng để **lấy mẫu (sampling)** từ tập token ứng viên này, nhằm điều chỉnh mức độ ngẫu nhiên của kết quả.

Trong trường hợp **chỉ có top-K hoặc chỉ có top-P**, thì cơ chế hoạt động vẫn tương tự, nhưng **chỉ sử dụng một tham số tương ứng** để lọc token trước khi sampling.

Nếu **temperature** không được cung cấp, hệ thống sẽ **lấy mẫu ngẫu nhiên (random sampling)** từ các **token** thỏa mãn tiêu chí **top-K** và/hoặc **top-P** để sinh ra **token dự đoán tiếp theo**.

Ở các **giá trị cực hạn (extreme values)** của một tham số trong cấu hình lấy mẫu (**sampling configuration**), tham số đó có thể **vô hiệu hóa (cancel out)** các tham số cấu hình khác, hoặc trở nên **không còn ảnh hưởng (irrelevant)** đến quá trình sinh token.

```
- Token: đơn vị nhỏ nhất của văn bản mà mô hình xử lý (có thể là từ, một phần của từ, hoặc ký hiệu).
- Top-K sampling: chỉ chọn trong _K token có xác suất cao nhất_.
- Top-P (nucleus sampling): chỉ chọn trong tập token sao cho _tổng xác suất cộng dồn ≥ P_.
- Temperature: điều chỉnh mức độ ngẫu nhiên; càng cao → kết quả càng đa dạng, càng thấp → càng “an toàn” và dễ đoán.    
```

- **Khi bạn đặt `temperature = 0`**. Lúc này, **top-K** và **top-P gần như không còn tác dụng**. Mô hình sẽ **luôn chọn token có xác suất cao nhất** làm token tiếp theo (greedy decoding), không có yếu tố ngẫu nhiên. Ngược lại, **khi `temperature` được đặt rất cao** (lớn hơn 1, thường lên đến hàng chục): `temperature` lúc này **mất tác dụng kiểm soát**. Các token vượt qua bộ lọc **top-K và/hoặc top-P** sẽ được **lấy mẫu ngẫu nhiên (random sampling)** để chọn token tiếp theo
- **Khi bạn đặt `top-K = 1`** `temperature` và `top-P` trở nên **không còn ý nghĩa**. Chỉ **một token duy nhất** (token có xác suất cao nhất) vượt qua bộ lọc top-K. Token đó sẽ **luôn được chọn** làm token tiếp theo. Ngược lại, **khi `top-K` được đặt rất lớn** (ví dụ bằng kích thước vocabulary của LLM): Bất kỳ token nào có **xác suất khác 0** đều thỏa điều kiện top-K. **Không có token nào bị loại bỏ** bởi top-K.
- **Khi bạn đặt `top-P = 0`** (hoặc một giá trị rất nhỏ): Hầu hết các cơ chế sampling sẽ **chỉ giữ lại token có xác suất cao nhất**. Điều này khiến `temperature` và `top-K` trở nên **không còn tác dụng**. Ngược lại, **khi `top-P = 1`**: Mọi token có **xác suất khác 0** đều thỏa điều kiện top-P. **Không có token nào bị loại bỏ** trong bước lọc top-P.

Như một **thiết lập khởi điểm (baseline)**, bạn có thể dùng **temperature = 0.2**, **top-P = 0.95** và **top-K = 30**. Bộ tham số này thường cho ra kết quả **khá mạch lạc (coherent)**, vẫn có **tính sáng tạo**, nhưng **không quá ngẫu nhiên hay khó kiểm soát**.

Nếu bạn muốn mô hình tạo ra kết quả **đặc biệt sáng tạo**, hãy thử bắt đầu với **temperature = 0.9**, **top-P = 0.99** và **top-K = 40**. Cấu hình này cho phép mô hình **khám phá nhiều khả năng hơn trong không gian xác suất**, dẫn đến đầu ra đa dạng hơn.

Ngược lại, nếu bạn cần kết quả **ít sáng tạo hơn**, mang tính **ổn định và dự đoán được**, hãy thử **temperature = 0.1**, **top-P = 0.9** và **top-K = 20**.

Cuối cùng, nếu tác vụ của bạn **luôn chỉ có một đáp án đúng duy nhất** (ví dụ: **giải bài toán toán học** hoặc các bài toán logic xác định), hãy đặt **temperature = 0** để mô hình **loại bỏ yếu tố ngẫu nhiên** và luôn chọn phương án có xác suất cao nhất.

**Lưu ý:** Khi tăng mức độ tự do của mô hình (ví dụ: **temperature** cao hơn, **top-K**, **top-P** lớn hơn và **số lượng output tokens** nhiều hơn), **LLM (Large Language Model)** có xu hướng sinh ra nội dung **kém liên quan hơn** so với yêu cầu ban đầu.

Dưới đây là bản dịch sang **tiếng Việt**, có dùng **thuật ngữ chuyên ngành lập trình/AI** nhưng vẫn cố gắng diễn đạt **dễ hiểu và dễ tiếp cận**:

**Cảnh báo:**  Bạn đã bao giờ thấy một câu trả lời kết thúc bằng **rất nhiều từ ngữ thừa lặp đi lặp lại** chưa? Hiện tượng này còn được gọi là **“repetition loop bug”** (lỗi vòng lặp lặp lại). Đây là một vấn đề khá phổ biến trong **Large Language Models (LLMs)**, khi mô hình bị **kẹt trong một chu kỳ**, liên tục sinh ra cùng một từ, cụm từ hoặc cấu trúc câu (thường là các từ “filler” – từ đệm không mang nhiều ý nghĩa).

Lỗi này thường bị **khuếch đại** khi cấu hình các tham số sinh văn bản như **temperature** và **top-k / top-p** không phù hợp.
Hiện tượng này có thể xảy ra ở **cả temperature thấp lẫn temperature cao**, nhưng vì **những nguyên nhân khác nhau**:
- **Ở temperature thấp**:  
    Mô hình trở nên **quá quyết định (overly deterministic)**, luôn chọn những token có **xác suất cao nhất**. Nếu luồng sinh văn bản này quay lại một trạng thái đã xuất hiện trước đó, mô hình có thể rơi vào **vòng lặp vô hạn**, lặp lại cùng một nội dung.
- **Ở temperature cao**:  
    Đầu ra của mô hình trở nên **quá ngẫu nhiên**. Với không gian lựa chọn rất lớn, khả năng một từ hoặc cụm từ được chọn **tình cờ dẫn ngược lại trạng thái trước đó** sẽ tăng lên, từ đó cũng tạo ra vòng lặp.

Trong cả hai trường hợp, **quy trình sampling** của mô hình bị “kẹt”, dẫn đến đầu ra **đơn điệu, kém hữu ích**, và tiếp tục lặp cho đến khi **hết cửa sổ output (context/output window)**.

**Cách khắc phục**:  
Thông thường cần **tinh chỉnh cẩn thận** các tham số **temperature** và **top-k / top-p** để tìm được **điểm cân bằng tối ưu** giữa:
- **Tính quyết định (determinism)** – giúp câu trả lời nhất quán
- **Tính ngẫu nhiên (randomness)** – giúp nội dung đa dạng và tự nhiên

Sự cân bằng này giúp mô hình tránh bị lặp, đồng thời vẫn tạo ra nội dung chất lượng và hữu ích.

## Prompting techniques

Các **LLM (Large Language Models – mô hình ngôn ngữ lớn)** được **tinh chỉnh (fine-tuned)** để **tuân theo chỉ dẫn (follow instructions)** và được **huấn luyện (trained)** trên **khối lượng dữ liệu rất lớn**, nhờ đó chúng có khả năng **hiểu prompt (câu lệnh đầu vào)** và **sinh ra câu trả lời (generate output)**.

Tuy nhiên, **LLM không hoàn hảo**. **Prompt càng rõ ràng, cụ thể**, thì **khả năng dự đoán chuỗi văn bản tiếp theo (next-token prediction)** của LLM càng chính xác. Nói cách khác, **chất lượng đầu ra phụ thuộc rất nhiều vào chất lượng đầu vào**.

Ngoài ra, việc áp dụng **các kỹ thuật chuyên biệt** — tận dụng **cách LLM được huấn luyện** và **cách chúng vận hành nội bộ** — sẽ giúp bạn **khai thác mô hình hiệu quả hơn** và **thu được kết quả đúng trọng tâm (relevant results)**.

Bây giờ, khi chúng ta đã hiểu **prompt engineering là gì** và **những yếu tố cần có để viết prompt tốt**, hãy cùng đi sâu vào **các ví dụ minh họa cho những kỹ thuật prompting quan trọng nhất**.


### General prompting / zero shot

**Zero-shot prompt** là loại prompt (lời nhắc) đơn giản nhất. Nó **chỉ cung cấp mô tả của tác vụ** và **một đoạn văn bản đầu vào** để mô hình ngôn ngữ lớn (LLM) bắt đầu xử lý. Đầu vào này có thể là bất cứ thứ gì: **một câu hỏi**, **phần mở đầu của một câu chuyện**, hoặc **các chỉ dẫn/instructions**.  
Tên gọi **zero-shot** có nghĩa là **không có ví dụ mẫu (no examples)** được cung cấp cho mô hình trước khi thực hiện tác vụ.

Hiểu ngắn gọn: zero-shot = mô tả yêu cầu → đưa input → LLM tự suy luận và trả lời, **không cần dữ liệu huấn luyện bổ sung hay ví dụ minh họa trong prompt**.

Hãy sử dụng **Vertex AI Studio (cho Language)** trong **Vertex AI**, một công cụ cung cấp **playground** để thử nghiệm và tinh chỉnh **prompt**. Trong **Bảng 1**, bạn sẽ thấy một ví dụ về **zero-shot prompt** dùng để **phân loại (classify) đánh giá phim**.


<table>
  <tr>
	<th>Name</th>  
    <td colspan="3">1_1_movie_classification </td>
  </tr>
  <tr>
    <th>Goal</th>
    <td colspan="3">Classify movie reviews as positive, neutral or negative.</td>
  </tr>
  <tr>
	<th>Model</th>
	 <td colspan="3">gemini-pro</td>
  </tr>
  <tr>
     <th>Temperature</th>
    <td >0.1</td>
    <th >Token Limit</th>
    <td >5</td>
  </tr>
  <tr>
	  <th>Top K</th>
     <td>N/A</td>
      <th>Top P</th>
     <td>1</td>
  </tr>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">Classify movie reviews as POSITIVE, NEUTRAL or NEGATIVE.  Review: "Her" is a disturbing study revealing the direction  humanity is headed if AI is allowed to keep evolving,  unchecked. I wish there were more movies like this masterpiece.  Sentiment: </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">POSITIVE</td>
  </tr>
</table>


Định dạng bảng như bên dưới là một cách rất hiệu quả để **tài liệu hóa (document)** các prompt. Trên thực tế, prompt của bạn thường sẽ phải trải qua **nhiều vòng lặp (iterations)** trước khi được đưa vào **codebase**, vì vậy việc **theo dõi quá trình prompt engineering** một cách **có kỷ luật và có cấu trúc** là vô cùng quan trọng.

Chi tiết hơn về **định dạng bảng này**, tầm quan trọng của việc theo dõi prompt engineering, cũng như **quy trình phát triển prompt**, sẽ được trình bày trong phần **Best Practices** ở cuối chương này (mục _“Document the various prompt attempts”_).

Thông số **model temperature** nên được đặt ở **mức thấp**, vì bài toán này **không yêu cầu tính sáng tạo**. Đồng thời, chúng ta sử dụng các giá trị mặc định **top-K** và **top-P** của **gemini-pro**, vốn **gần như vô hiệu hóa** cả hai tham số này (xem phần _“LLM Output Configuration”_ ở trên).

Hãy chú ý kỹ đến **output do mô hình sinh ra**. Các từ _“disturbing”_ và _“masterpiece”_ xuất hiện trong cùng một câu sẽ khiến việc **dự đoán (prediction)** trở nên **phức tạp hơn**, vì cả hai từ đều mang sắc thái cảm xúc trái ngược nhau.

Khi **zero-shot prompting** (nhắc lệnh không kèm ví dụ) **không mang lại kết quả như mong muốn**, bạn có thể **cung cấp các bản minh họa (demonstrations) hoặc ví dụ trực tiếp trong prompt**. Cách làm này dẫn đến hai kỹ thuật nâng cao hơn:
- **One-shot prompting**: cung cấp **1 ví dụ mẫu**
- **Few-shot prompting**: cung cấp **một vài ví dụ mẫu**
Trong đó:
- **General prompting / Zero-shot**: Mô hình AI được yêu cầu thực hiện một tác vụ **mà không có bất kỳ ví dụ nào**, chỉ dựa vào kiến thức đã được huấn luyện sẵn.
Nói cách khác:
- Zero-shot giống như gọi một hàm mà **không truyền dữ liệu mẫu**
- One-shot và Few-shot giống như **truyền thêm test case** để mô hình hiểu rõ yêu cầu và xử lý chính xác hơn

### One-shot & few-shot

Khi thiết kế **prompt** (câu lệnh đầu vào) cho các **mô hình AI**, việc cung cấp **ví dụ minh họa** là rất quan trọng. Các ví dụ này giúp mô hình hiểu rõ hơn **yêu cầu** của bạn và **kỳ vọng đầu ra** là gì. Đặc biệt, ví dụ sẽ rất hữu ích khi bạn muốn **định hướng mô hình** tạo ra kết quả theo một **cấu trúc (output structure)** hoặc **mẫu (pattern)** nhất định.

**One-shot prompting** là kỹ thuật cung cấp **một ví dụ duy nhất** cho mô hình — đúng như tên gọi của nó. Ý tưởng ở đây là mô hình sẽ **học theo (imitate)** ví dụ đó để hoàn thành tác vụ một cách chính xác nhất.

**Few-shot prompting** thì mở rộng hơn, bằng cách cung cấp **nhiều ví dụ** cho mô hình. Cách tiếp cận này giúp mô hình nhận diện rõ **pattern cần tuân theo**. Về bản chất, few-shot tương tự one-shot, nhưng việc có **nhiều ví dụ hơn** sẽ **tăng xác suất** mô hình hiểu đúng yêu cầu và tạo ra đầu ra đúng theo mẫu mong muốn.

Số lượng ví dụ cần dùng cho **few-shot prompting** phụ thuộc vào một số yếu tố, bao gồm **độ phức tạp của tác vụ**, **chất lượng của các ví dụ**, và **năng lực của mô hình AI sinh (Generative AI – GenAI)** mà bạn đang sử dụng. Theo **nguyên tắc kinh nghiệm (rule of thumb)**, bạn nên sử dụng **ít nhất từ 3 đến 5 ví dụ** khi áp dụng few-shot prompting. Tuy nhiên, với những tác vụ **phức tạp hơn**, bạn có thể cần **nhiều ví dụ hơn** để mô hình hiểu đúng ngữ cảnh và yêu cầu. Ngược lại, trong một số trường hợp, bạn có thể phải **giảm số lượng ví dụ** do **giới hạn độ dài đầu vào (input length / token limit)** của mô hình.

**Bảng 2** minh họa một ví dụ về few-shot prompt. Trong ví dụ này, chúng ta sẽ sử dụng **cùng cấu hình mô hình Gemini-Pro** như trước, **ngoại trừ việc tăng giới hạn token** để đáp ứng nhu cầu tạo ra **phản hồi dài hơn**.


<table>
  <tr>
	<th>Name</th>  
    <td colspan="3">Parse pizza orders to JSON </td>
  </tr>
  <tr>
    <th>Goal</th>
    <td colspan="3">Classify movie reviews as positive, neutral or negative.</td>
  </tr>
  <tr>
	<th>Model</th>
	 <td colspan="3">gemini-pro</td>
  </tr>
  <tr>
     <th>Temperature</th>
    <td >0.1</td>
    <th >Token Limit</th>
    <td >250</td>
  </tr>
  <tr>
	  <th>Top K</th>
     <td>N/A</td>
      <th>Top P</th>
     <td>1</td>
  </tr>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">
      Parse a customer's pizza order into valid JSON:  
      
      EXAMPLE:  I want a small pizza with cheese, tomato sauce, and pepperoni.  JSON Response:  
      
      ```  
      {  
	      "size": "small",  
	      "type": "normal",  
	      "ingredients": [["cheese", "tomato sauce", "peperoni"]]  
      } 
      ```
	   
	   EXAMPLE:
	   Can I get a large pizza with tomato sauce, basil and mozzarella  
	   ```
	   {  
		   "size": "large",  
		   "type": "normal",  
		   "ingredients": [["tomato sauce", "bazel", "mozzarella"]]  
	   }  
	   ```
	   Now, I would like a large pizza, with the first half cheese and  mozzarella. And the other tomato sauce, ham and pineapple.  JSON Response: ...	   
	   </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">
    ```
    {  
	    "size": "large",  
	    "type": "half-half",  
	    "ingredients": [["cheese", "mozzarella"], ["tomato sauce",  "ham", "pineapple"]]  
    }  
    ``` 
	</td>
</tr>
</table>



Khi lựa chọn **ví dụ (examples)** cho **prompt**, hãy sử dụng những ví dụ **liên quan trực tiếp đến tác vụ (task)** mà bạn muốn mô hình thực hiện.  
Các ví dụ này cần **đa dạng**, **chất lượng cao** và được **viết rõ ràng, chính xác**.
Chỉ **một lỗi nhỏ** trong ví dụ cũng có thể khiến mô hình **hiểu sai ngữ cảnh**, từ đó tạo ra **output không mong muốn**.

Nếu mục tiêu của bạn là tạo ra kết quả **ổn định (robust)** trước nhiều loại **đầu vào (inputs)** khác nhau, thì việc **bao gồm các edge case** trong ví dụ là rất quan trọng.
**Edge case** là những đầu vào **bất thường hoặc ít gặp**, nhưng mô hình **vẫn phải xử lý đúng**. Việc đưa edge case vào prompt giúp mô hình:
- Tổng quát hóa tốt hơn
- Giảm lỗi trong các tình huống thực tế
- Hoạt động đáng tin cậy hơn khi gặp dữ liệu không chuẩn

### System, contextual and role prompting 

**System prompting, contextual prompting và role prompting** đều là các kỹ thuật được sử dụng để định hướng cách mà các mô hình ngôn ngữ lớn (LLM) sinh văn bản, nhưng mỗi kỹ thuật tập trung vào các khía cạnh khác nhau:

- **System prompting**: Thiết lập bối cảnh tổng thể và mục đích hoạt động cho mô hình ngôn ngữ. Nó định nghĩa “bức tranh lớn” về nhiệm vụ mà mô hình cần thực hiện, ví dụ như dịch ngôn ngữ, phân loại đánh giá (review), v.v. Trong lập trình, đây giống như việc cấu hình môi trường (environment setup) hoặc khởi tạo một pipeline xử lý dữ liệu.
- **Contextual prompting**: Cung cấp các chi tiết cụ thể hoặc thông tin nền liên quan đến cuộc trò chuyện hay nhiệm vụ hiện tại. Nó giúp mô hình nắm bắt các sắc thái (nuance) của yêu cầu và tạo ra phản hồi phù hợp hơn. Trong lập trình, bạn có thể hình dung đây như việc truyền tham số (parameters) hoặc dữ liệu đầu vào (input data) để một hàm hay module hoạt động chính xác.
- **Role prompting**: Gán một nhân vật hoặc vai trò cụ thể cho mô hình ngôn ngữ. Kỹ thuật này giúp mô hình tạo ra phản hồi nhất quán với vai trò được giao, bao gồm kiến thức và hành vi liên quan. Trong lập trình, nó tương tự việc triển khai một class hoặc object với các phương thức và thuộc tính xác định sẵn để thực hiện một chức năng cụ thể.

Có thể có sự chồng chéo đáng kể giữa **system prompt**, **contextual prompt**, và **role prompt**. Ví dụ: một prompt gán **role** cho hệ thống cũng có thể kèm theo một **context**. Tuy nhiên, mỗi loại prompt lại có **mục đích chính hơi khác nhau**:
- **System prompt**: Xác định **năng lực cốt lõi** của mô hình và **mục đích tổng thể** của nó.
- **Contextual prompt**: Cung cấp **thông tin cụ thể theo nhiệm vụ** để hướng dẫn mô hình trả lời. Nó rất **đặc thù cho nhiệm vụ hoặc dữ liệu hiện tại**, và có tính **động**.
- **Role prompt**: Xác định **phong cách và giọng điệu** của đầu ra mô hình. Nó **thêm một lớp đặc thù và cá tính** cho phản hồi.

**Phân biệt giữa system prompt, contextual prompt và role prompt** cung cấp một khuôn khổ (framework) để thiết kế prompt với mục đích rõ ràng, cho phép kết hợp linh hoạt và dễ dàng phân tích cách mỗi loại prompt ảnh hưởng đến đầu ra của mô hình ngôn ngữ. Hãy cùng tìm hiểu ba loại prompt khác nhau này

### System prompting

**Bảng 3** chứa một _system prompt_, trong đó tôi chỉ định thêm các thông tin về cách mô hình phải trả về _output_. Tôi đã tăng **temperature** để đạt mức độ sáng tạo cao hơn và đồng thời thiết lập **token limit** cao hơn. Tuy nhiên, nhờ các chỉ dẫn rõ ràng về định dạng và nội dung đầu ra, mô hình không sinh thêm văn bản dư thừa ngoài yêu cầu.


<table>
  <tr>
    <th>Goal</th>
    <td colspan="3">Classify movie reviews as positive, neutral or negative.</td>
  </tr>
  <tr>
	<th>Model</th>
	 <td colspan="3">gemini-pro</td>
  </tr>
  <tr>
     <th>Temperature</th>
    <td >1</td>
    <th >Token Limit</th>
    <td >5</td>
  </tr>
  <tr>
	  <th>Top K</th>
     <td>40</td>
      <th>Top P</th>
     <td>0.8</td>
  </tr>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">Classify movie reviews as positive, neutral or negative. Only  return the label in uppercase.  Review: "Her" is a disturbing study revealing the direction  humanity is headed if AI is allowed to keep evolving,  unchecked. It's so disturbing I couldn't watch it.  Sentiment:    </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">NEGATIVE</td>
</tr>
</table>


**System prompt** có thể được sử dụng để tạo ra đầu ra đáp ứng các yêu cầu cụ thể. Thuật ngữ _“system prompt”_ thực chất mang ý nghĩa là _“cung cấp một nhiệm vụ bổ sung cho hệ thống”_. Ví dụ, bạn có thể sử dụng system prompt để:
- Sinh ra một **đoạn mã (code snippet)** tương thích với một **ngôn ngữ lập trình cụ thể**.
- Yêu cầu hệ thống **trả về kết quả theo một cấu trúc nhất định** (ví dụ: JSON, XML, hoặc schema tùy chỉnh).

Hãy xem Bảng 4, nơi tôi trả về kết quả dưới định dạng JSON.


<table>
  <tr>
    <th>Goal</th>
    <td colspan="3">Classify movie reviews as positive, neutral or negative, return JSON.</td>
  </tr>
  <tr>
	<th>Model</th>
	 <td colspan="3">gemini-pro</td>
  </tr>
  <tr>
     <th>Temperature</th>
    <td >1</td>
    <th >Token Limit</th>
    <td >1024</td>
  </tr>
  <tr>
	  <th>Top K</th>
     <td>40</td>
      <th>Top P</th>
     <td>0.8</td>
  </tr>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">Classify movie reviews as positive, neutral or negative. Return  valid JSON:  Review: "Her" is a disturbing study revealing the direction  humanity is headed if AI is allowed to keep evolving,  unchecked. It's so disturbing I couldn't watch it.  Schema:  
      ```  
      MOVIE:  {  
			      "sentiment": String "POSITIVE" | "NEGATIVE" | "NEUTRAL",  
			      "name": String 
			}  
      MOVIE REVIEWS:  {  
		      "movie_reviews": [MOVIE]  
		      }  
	```  JSON Response: </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">```  
    {  "movie_reviews": [  
	    {  
		    "sentiment": "NEGATIVE",  
		    "name": "Her"  
	    }  ]  
	}  ``` </td>
</tr>
</table>




Có một số lợi ích khi trả về các đối tượng **JSON** từ một prompt dùng để trích xuất dữ liệu. Trong các ứng dụng thực tế (real-world application), tôi không cần phải tự tay xây dựng định dạng JSON này, vì tôi đã có thể trả về dữ liệu theo thứ tự đã được sắp xếp (điều này đặc biệt hữu ích khi làm việc với các đối tượng **datetime**).

Quan trọng hơn, việc yêu cầu đầu ra ở định dạng JSON giúp “ép” mô hình phải tạo ra một cấu trúc rõ ràng, từ đó giảm thiểu hiện tượng **hallucination** (mô hình tự bịa hoặc suy diễn sai dữ liệu).

Ngoài ra, **system prompt** cũng rất hữu ích trong việc đảm bảo **an toàn (safety)** và kiểm soát nội dung độc hại (**toxicity**). Để kiểm soát đầu ra, bạn chỉ cần thêm một dòng vào prompt, ví dụ:  “You should be respectful in your answer.” (Bạn nên trả lời một cách tôn trọng).

### Role prompting 

**Role prompting** là một kỹ thuật trong **prompt engineering** (kỹ thuật thiết kế prompt) liên quan đến việc gán một _vai trò cụ thể_ cho mô hình **GenAI** (generative AI).

Khi được gán vai trò, mô hình có thể sinh ra output (đầu ra) mang tính **context-aware** (phù hợp ngữ cảnh) và **domain-specific** (đúng chuyên môn) hơn, vì nó “điều chỉnh” cách phản hồi dựa trên role đã được định nghĩa.

Ví dụ, bạn có thể role prompt một mô hình GenAI thành:
- một **book editor** (biên tập viên sách),
- một **kindergarten teacher** (giáo viên mầm non),
- hoặc một **motivational speaker** (diễn giả truyền động lực).

Sau khi thiết lập role, bạn tiếp tục cung cấp các **prompt mang tính đặc thù theo vai trò** (_role-specific prompts_). Điều này giúp mô hình tạo ra nội dung có cấu trúc và mục tiêu rõ ràng hơn.

Ví dụ:

- Nếu mô hình được gán vai trò **teacher**, bạn có thể yêu cầu nó **generate một lesson plan (kế hoạch bài giảng)**, sau đó tiến hành **review hoặc refine** nội dung đó.

Bạn có thể tham khảo thêm ở _Table 5_, nơi mô hình được cấu hình với role là một **travel guide (hướng dẫn viên du lịch)**, nhằm minh họa cách role prompting ảnh hưởng đến cách mô hình xây dựng câu trả lời.



<table>
  <tr>
    <th>Goal</th>
    <td colspan="3">Act as travel guide and provide 3 travel suggestions.</td>
  </tr>
  <tr>
	<th>Model</th>
	 <td colspan="3">gemini-pro</td>
  </tr>
  <tr>
     <th>Temperature</th>
    <td >1</td>
    <th >Token Limit</th>
    <td >1024</td>
  </tr>
  <tr>
	  <th>Top K</th>
     <td>40</td>
      <th>Top P</th>
     <td>0.8</td>
  </tr>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">I want you to act as a travel guide. I will write to you  about my location and you will suggest 3 places to visit near  me. In some cases, I will also give you the type of places I  will visit.  My suggestion: "I am in Amsterdam and I want to visit  only museums."  Travel Suggestions: </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">
    1. Rijksmuseum: World-renowned museum, known for Dutch masterpieces  like Rembrandt’s “The Night Watch.” Don’t miss the incredible collection of  paintings and artifacts showcasing Dutch art and history.  
    2. Van Gogh Museum: Immerse yourself in the captivating works of Vincent  van Gogh. The museum houses the largest collection of his paintings and  drawings, including “The Starry Night” and “Sunflowers.” 
      3. Stedelijk Museum Amsterdam: Discover modern and contemporary art  from around the world. The museum’s collection includes works by Picasso,  Kandinsky, and Rietveld, housed in a striking modern building. </td>
</tr>
</table>


Ví dụ trên minh họa việc gán cho AI một **role (vai trò)** như một _travel agent_ (đại lý du lịch). Khi bạn chuyển **role** sang _teacher of geography_ (giáo viên địa lý), bạn sẽ nhận được một **response (phản hồi)** khác biệt rõ rệt.

Việc định nghĩa **role perspective (góc nhìn vai trò)** cho một mô hình AI giống như cung cấp một **blueprint (bản thiết kế)** về **tone (giọng điệu)**, **style (phong cách)** và **domain expertise (chuyên môn theo lĩnh vực)** mà bạn mong muốn. Điều này giúp cải thiện đáng kể **output quality (chất lượng đầu ra)**, tăng **relevance (độ liên quan)** và nâng cao **effectiveness (hiệu quả)** của nội dung được tạo ra.

Nói cách khác, việc “đóng vai” trong prompt chính là một kỹ thuật **prompt engineering** quan trọng, giúp bạn **control behavior (kiểm soát hành vi)** của mô hình và tối ưu hóa kết quả theo mục tiêu cụ thể.

Dưới đây là một số phong cách mà bạn có thể lựa chọn, và tôi thấy chúng khá hiệu quả: Đối đầu, Mô tả, Trực tiếp, Trang trọng, Hài hước, Có ảnh hưởng, Thân mật, Truyền cảm hứng, Thuyết phục. Hãy thay đổi lời nhắc của chúng ta trong Bảng 6 để bao gồm phong cách hài hước và truyền cảm hứng.


<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">I want you to act as a travel guide. I will write to you about  my location and you will suggest 3 places to visit near me in  a humorous style.  My suggestion: "I am in Manhattan."  Travel Suggestions:  </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">
    1. Behold the Empire State of Mind: Ascend to the dizzying heights of the Empire  State Building and bask in the glory of Manhattan's skyline. Prepare to feel like  King Kong atop the Big Apple, minus the giant ape-sized banana.  2. Get Artsy-Fartsy at MoMA: Unleash your inner art aficionado at the Museum  of Modern Art (MoMA). Gaze upon masterpieces that will boggle your  mind and make you question whether your stick-figure drawings have any  artistic merit.  3. Shop ‘Til You Drop on Fifth Avenue: Indulge in some retail therapy on the  iconic Fifth Avenue. Brace yourself for sticker shock as you window-shop (or  actually shop) at designer boutiques that will make your wallet cry. But hey,  you’re in Manhattan, so you might as well embrace the fabulousness!  </td>
</tr>
</table>



### Contextual prompting 

Bằng cách cung cấp các _prompt_ theo ngữ cảnh (_contextual prompts_), bạn có thể giúp các tương tác với AI trở nên liền mạch (_seamless_) và hiệu quả (_efficient_) hơn. Mô hình (_model_) sẽ nhanh chóng nắm bắt được _request_ của bạn, từ đó sinh ra (_generate_) các _response_ chính xác và phù hợp (_relevant_) hơn — như minh họa trong ví dụ ở Bảng 7.



<table>
  <tr>
    <th>Goal</th>
    <td colspan="3">Act as travel guide and provide 3 travel suggestions.</td>
  </tr>
  <tr>
	<th>Model</th>
	 <td colspan="3">gemini-pro</td>
  </tr>
  <tr>
     <th>Temperature</th>
    <td >1</td>
    <th >Token Limit</th>
    <td >1024</td>
  </tr>
  <tr>
	  <th>Top K</th>
     <td>40</td>
      <th>Top P</th>
     <td>0.8</td>
  </tr>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">I want you to act as a travel guide. I will write to you  about my location and you will suggest 3 places to visit near  me. In some cases, I will also give you the type of places I  will visit.  My suggestion: "I am in Amsterdam and I want to visit  only museums."  Travel Suggestions: </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">
    1. Rijksmuseum: World-renowned museum, known for Dutch masterpieces  like Rembrandt’s “The Night Watch.” Don’t miss the incredible collection of  paintings and artifacts showcasing Dutch art and history.  
    2. Van Gogh Museum: Immerse yourself in the captivating works of Vincent  van Gogh. The museum houses the largest collection of his paintings and  drawings, including “The Starry Night” and “Sunflowers.” 
      3. Stedelijk Museum Amsterdam: Discover modern and contemporary art  from around the world. The museum’s collection includes works by Picasso,  Kandinsky, and Rietveld, housed in a striking modern building. </td>
</tr>
</table>



### Step-back prompting 

**Step-back prompting** là một kỹ thuật giúp cải thiện hiệu năng của mô hình ngôn ngữ lớn (LLM) bằng cách thiết kế prompt theo hai giai đoạn.

Cụ thể, thay vì yêu cầu LLM giải quyết trực tiếp một bài toán cụ thể (**specific task**), ta sẽ:

1. Trước tiên đưa ra một câu hỏi mang tính tổng quát hơn (**generalized prompt**) có liên quan đến bài toán.
2. Sau đó sử dụng câu trả lời từ bước này làm **context / input bổ sung** cho prompt thứ hai để giải quyết bài toán chính.

Cách “lùi lại một bước” (step back) này giúp LLM kích hoạt (**activate**) các **background knowledge** và **reasoning patterns** phù hợp trước khi đi vào xử lý chi tiết bài toán. Nhờ đó, mô hình có thể:

- Hiểu rõ hơn **nguyên lý nền tảng (underlying principles)**
- Suy luận chính xác hơn (**improved reasoning**)
- Tạo ra câu trả lời có chiều sâu và chất lượng cao hơn (**more insightful outputs**)

Ngoài ra, step-back prompting còn:

- Khuyến khích LLM **tư duy phản biện (critical thinking)**
- Tận dụng tốt hơn kiến thức đã được encode trong **model parameters**
- Giảm thiểu **bias** trong phản hồi bằng cách tập trung vào các nguyên tắc tổng quát thay vì các chi tiết cụ thể

Nói cách khác, kỹ thuật này thay đổi cách xây dựng **final prompt** bằng cách “bơm” thêm ngữ cảnh tri thức, giúp mô hình khai thác tối đa năng lực suy luận vốn có, thay vì phản hồi một cách trực tiếp và đôi khi hời hợt.

Tiếp theo, chúng ta sẽ xem các ví dụ minh họa để hiểu rõ hơn cách step-back prompting cải thiện kết quả. Trước tiên, hãy xem một **prompt truyền thống** (Bảng 8), sau đó so sánh với **step-back prompt** (Bảng 9).


<table>
  <tr>
    <th>Goal</th>
    <td colspan="3">Write a storyline for a level of a first-person shooter video game. </td>
  </tr>
  <tr>
	<th>Model</th>
	 <td colspan="3">gemini-pro</td>
  </tr>
  <tr>
     <th>Temperature</th>
    <td >1</td>
    <th >Token Limit</th>
    <td >1024</td>
  </tr>
  <tr>
	  <th>Top K</th>
     <td>40</td>
      <th>Top P</th>
     <td>0.8</td>
  </tr>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">Write a one paragraph storyline for a new level of a firstperson shooter video game that is challenging and engaging. </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">The level begins with the player’s squad being ambushed in a dense urban area  by a relentless enemy faction. Players must fight their way through a maze of  back alleys and dilapidated buildings, utilizing stealth and precision to eliminate  enemy forces and avoid detection. The player must use their environment to their  advantage, setting traps, utilizing cover, and making calculated moves to survive.  Along the way, they uncover intel suggesting the enemy is planning a devastating  attack, and the player must race against time to gather evidence and relay it back  to their headquarters before the enemy can carry out their plans. </td>
</tr>
</table>

Khi bạn đặt (temperature) là 1, bạn có thể nhận được đủ loại nội dung sáng tạo cho một cốt truyện, nhưng nó cũng khá ngẫu nhiên và mang tính chung chung. Vì vậy, hãy lùi lại một bước:



<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">Based on popular first-person shooter action games, what are  5 fictional key settings that contribute to a challenging and  engaging level storyline in a first-person shooter video game?  </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">1. **Abandoned Military Base**: A sprawling, post-apocalyptic military complex  crawling with mutated soldiers and rogue robots, ideal for challenging  firearm combat.  2. **Cyberpunk City**: A neon-lit, futuristic urban environment with towering  skyscrapers and dense alleyways, featuring cybernetically enhanced enemies  and hacking mechanics.  3. **Alien Spaceship**: A vast alien vessel stranded on Earth, with eerie  corridors, zero-gravity sections, and extraterrestrial creatures to encounter.  4. **Zombie-Infested Town**: A desolate town overrun by hordes of aggressive  zombies, featuring intense close-quarters combat and puzzle-solving to find  safe passage.  5. **Underwater Research Facility**: A deep-sea laboratory flooded with water,  filled with mutated aquatic creatures, and requiring stealth and underwater  exploration skills to survive.  </td>
</tr>
</table>

Vâng, những chủ đề đó có vẻ phù hợp cho một trò chơi điện tử góc nhìn thứ nhất. Hãy quay lại yêu cầu ban đầu, nhưng lần này chúng ta đưa câu trả lời của bước lùi lại làm ngữ cảnh và xem nó sẽ trả về điều gì.

<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">Context: 5 engaging themes for a first person shooter video game:  1. **Abandoned Military Base**: A sprawling, post-apocalyptic  military complex crawling with mutated soldiers and rogue  robots, ideal for challenging firearm combat.  2. **Cyberpunk City**: A neon-lit, futuristic urban environment  with towering skyscrapers and dense alleyways, featuring  cybernetically enhanced enemies and hacking mechanics.  3. **Alien Spaceship**: A vast alien vessel stranded on  Earth, with eerie corridors, zero-gravity sections, and  extraterrestrial creatures to encounter.  4. **Zombie-Infested Town**: A desolate town overrun by hordes of  aggressive zombies, featuring intense close-quarters combat and  puzzle-solving to find safe passage.  5. **Underwater Research Facility**: A deep-sea laboratory flooded  with water, filled with mutated aquatic creatures, and requiring  stealth and underwater exploration skills to survive.  Take one of the themes and write a one paragraph storyline  for a new level of a first-person shooter video game that is  challenging and engaging. </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">In the heart of a murky abyss, lies a dilapidated underwater research facility,  standing as a testament to human ambition and its disastrous consequences.  Shrouded in darkness, pulsating with the hum of malfunctioning machinery, and  haunted by the echoes of drowned souls, the facility is now a breeding ground for  a nightmare borne from the deep sea. The player, an elite marine equipped with  advanced diving gear and experimental weaponry, is tasked with venturing into  this aquatic realm of terror. Armed with resilience and resourcefulness, they must  navigate treacherous corridors, solve cryptic puzzles, and confront gruesome sea  monstrosities that lurk in the depths. From grappling with the crushing pressure  of the deep sea to outsmarting cunning aquatic predators, every moment in this  uncharted underworld tests the limits of human endurance and courage. </td>
</tr>
</table>



Đó trông giống như một trò chơi điện tử thú vị! Bằng cách sử dụng các kỹ thuật “step-back prompting” (đặt câu hỏi lùi lại một bước), bạn có thể tăng độ chính xác của các prompt của mình. 

### Chain of Thought (CoT) 


Kỹ thuật **Chain of Thought (CoT) prompting** là một phương pháp trong lĩnh vực **xử lý ngôn ngữ tự nhiên (NLP)**nhằm cải thiện khả năng suy luận của các **mô hình ngôn ngữ lớn (LLMs)** bằng cách tạo ra các bước suy luận trung gian (intermediate reasoning steps). Cách tiếp cận này giúp mô hình đưa ra câu trả lời chính xác hơn thay vì chỉ dự đoán trực tiếp đầu ra.

Bạn cũng có thể kết hợp CoT với **few-shot prompting** (cung cấp một số ví dụ mẫu) để đạt hiệu quả tốt hơn trong các bài toán phức tạp — đặc biệt là những bài toán đòi hỏi suy luận trước khi phản hồi. Điều này rất hữu ích vì **zero-shot chain of thought** (không có ví dụ mẫu) thường gặp khó khăn trong các tác vụ reasoning.

### Ưu điểm của CoT prompting

- **Hiệu quả cao với chi phí thấp**: Không cần **fine-tuning** mô hình, vẫn có thể cải thiện đáng kể chất lượng đầu ra.
- **Tương thích với các LLM có sẵn (off-the-shelf models)**: Có thể áp dụng trực tiếp mà không cần huấn luyện lại.
- **Tính diễn giải (interpretability)**: Bạn có thể quan sát các bước suy luận của mô hình, từ đó hiểu cách nó đi đến kết quả.
- **Dễ debug**: Khi có lỗi (malfunction), bạn có thể xác định chính xác bước suy luận nào gặp vấn đề.
- **Tăng độ ổn định (robustness)**: Khi chuyển giữa các phiên bản LLM khác nhau, prompt sử dụng CoT thường ít bị “trôi hiệu năng” (performance drift) hơn so với prompt không có chuỗi suy luận.
### Nhược điểm của CoT prompting

- **Tăng số lượng token đầu ra**: Vì mô hình phải sinh thêm các bước suy luận, dẫn đến:
    - Chi phí suy luận (inference cost) cao hơn
    - Thời gian phản hồi lâu hơn
	- Điều này có thể ảnh hưởng đến các hệ thống cần tối ưu về latency hoặc chi phí vận hành.

Để minh họa cho ví dụ trong **Bảng 11 (Table 11)**, trước tiên ta sẽ thử xây dựng một prompt **không sử dụng CoT prompting**, nhằm làm rõ những hạn chế (flaws) của mô hình ngôn ngữ lớn khi không có hướng dẫn suy luận từng bước.

<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">When I was 3 years old, my partner was 3 times my age. Now, I  am 20 years old. How old is my partner?. </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">63 years old. </td>
</tr>
</table>

Yikes. Rõ ràng đây là một kết quả sai.
Thực tế, các **LLM (Large Language Models)** thường gặp khó khăn với các tác vụ liên quan đến toán học và có thể đưa ra kết quả không chính xác — ngay cả với những phép toán đơn giản như nhân hai số.
Nguyên nhân là vì chúng được **huấn luyện trên tập dữ liệu văn bản quy mô lớn (large-scale text corpus)**, trong khi các bài toán toán học thường đòi hỏi một **phương pháp xử lý khác**, mang tính suy luận logic và tính toán chính xác hơn, thay vì chỉ dựa trên **pattern recognition**.
Vì vậy, hãy thử kiểm tra xem việc bổ sung các **bước suy luận trung gian (intermediate reasoning steps)** có giúp cải thiện chất lượng đầu ra (**output quality**) hay không.

<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">When I was 3 years old, my partner was 3 times my age. Now,  I am 20 years old. How old is my partner? Let's think step  by step.  </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">1. Let’s assume my current age is “x” years.  2. When I was 3 years old, my age was 3 years.  3. My partner’s age at that time was 3 times my age, which means my partner’s  age was 3 * 3 = 9 years.  4. Now, I am 20 years old, which means my age has increased by 20 - 3 = 17  years since I was 3 years old.  5. Since my partner’s age was 9 years when I was 3 years old, and my age has  increased by 17 years, my partner’s age must have also increased by 17 years.  6. Therefore, my partner’s current age is 9 + 17 = 26 years.  So, my partner is 26 years old. </td>
</tr>
</table>


Được rồi, bây giờ câu trả lời cuối cùng đã chính xác. Điều này là do chúng ta đã **rõ ràng yêu cầu LLM (Large Language Model)** giải thích từng bước thay vì chỉ trả về kết quả.

Điều thú vị là mô hình đã cộng dồn 17 năm tăng thêm. Trong suy nghĩ của tôi, tôi sẽ tính theo cách khác: lấy chênh lệch số tuổi giữa tôi và đối tác, rồi cộng lại, ví dụ: _(20 + (9 - 3))_.

Hãy thử **điều chỉnh prompt / hướng dẫn (instruction tuning)** để giúp mô hình “suy nghĩ” gần giống với cách tư duy của tôi hơn — tức là tối ưu hóa cách nó **phân rã bài toán (problem decomposition)** và **suy luận từng bước (step-by-step reasoning / chain-of-thought)**.

Bảng 12 là một ví dụ về “Chain of Thought” ở chế độ “zero-shot”. Phương pháp gợi ý theo chuỗi suy nghĩ (Chain of Thought prompting) có thể rất mạnh mẽ khi được kết hợp với “single-shot” hoặc “few-shot”, như bạn có thể thấy trong Bảng 13.

<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">Q: When my brother was 2 years old, I was double his age. Now  I am 40 years old. How old is my brother? Let's think step  by step.  A: When my brother was 2 years, I was 2 * 2 = 4 years old.  That's an age difference of 2 years and I am older. Now I am 40  years old, so my brother is 40 - 2 = 38 years old. The answer  is 38.  Q: When I was 3 years old, my partner was 3 times my age. Now,  I am 20 years old. How old is my partner? Let's think step  by step.  A: </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">1. Let’s assume my current age is “x” years.  2. When I was 3 years old, my age was 3 years.  3. My partner’s age at that time was 3 times my age, which means my partner’s  age was 3 * 3 = 9 years.  4. Now, I am 20 years old, which means my age has increased by 20 - 3 = 17  years since I was 3 years old.  5. Since my partner’s age was 9 years when I was 3 years old, and my age has  increased by 17 years, my partner’s age must have also increased by 17 years.  6. Therefore, my partner’s current age is 9 + 17 = 26 years.  So, my partner is 26 years old. </td>
</tr>
</table>


**Chain of Thought (CoT)** có thể hữu ích trong nhiều trường hợp sử dụng khác nhau trong lập trình và AI.
Hãy xem xét một số ví dụ:
- Trong **sinh mã (code generation)**, CoT giúp bạn phân rã yêu cầu (problem decomposition) thành nhiều bước nhỏ, sau đó ánh xạ (mapping) từng bước này thành các dòng lệnh cụ thể trong mã nguồn.
- Khi **tạo dữ liệu tổng hợp (synthetic data generation)**, đặc biệt khi bạn có một “seed” ban đầu (ví dụ: _“Sản phẩm có tên là XYZ”_), CoT cho phép bạn xây dựng mô tả bằng cách hướng dẫn mô hình từng bước suy luận (guided reasoning), dựa trên các giả định hợp lý từ tên sản phẩm.

Nói chung, bất kỳ tác vụ nào có thể được giải quyết bằng cách **diễn giải từng bước (step-by-step reasoning)** đều là ứng viên phù hợp để áp dụng Chain of Thought.
Nếu bạn có thể giải thích quy trình để giải quyết vấn đề một cách rõ ràng và tuần tự, thì hãy cân nhắc sử dụng CoT.

Vui lòng tham khảo notebook10 được lưu trữ trong kho Github của GoogleCloudPlatform, nơi sẽ đi sâu hơn vào kỹ thuật gợi ý CoT (Chain of Thought): Trong phần các phương pháp hay nhất của chương này, chúng ta sẽ tìm hiểu một số thực tiễn tốt nhất dành riêng cho kỹ thuật gợi ý theo chuỗi suy nghĩ.

### Self-consistency 

Mặc dù các mô hình ngôn ngữ lớn (Large Language Models – LLMs) đã đạt được những thành công ấn tượng trong nhiều tác vụ xử lý ngôn ngữ tự nhiên (NLP), khả năng **lập luận (reasoning)** của chúng vẫn thường bị xem là một hạn chế — và hạn chế này không thể chỉ khắc phục bằng cách đơn thuần tăng kích thước mô hình (model scaling).

Như đã đề cập trong phần **Chain of Thought (CoT) prompting**, mô hình có thể được “prompt” để sinh ra các bước suy luận trung gian, tương tự cách con người giải quyết bài toán từng bước. Tuy nhiên, CoT thường sử dụng chiến lược **greedy decoding** (giải mã tham lam) — tức là tại mỗi bước chỉ chọn token có xác suất cao nhất. Cách tiếp cận này làm giảm tính đa dạng của các chuỗi suy luận, từ đó hạn chế hiệu quả tổng thể.

Phương pháp **Self-consistency** cải thiện điểm yếu này bằng cách kết hợp:
- **Sampling (lấy mẫu)**: sinh ra nhiều chuỗi suy luận khác nhau thay vì chỉ một.
- **Majority voting (bỏ phiếu đa số)**: chọn đáp án xuất hiện nhiều nhất trong các kết quả.

Nhờ đó, mô hình có thể khám phá nhiều “reasoning paths” (đường suy luận) khác nhau và chọn ra câu trả lời có tính nhất quán cao nhất. Kết quả là độ chính xác (accuracy) và tính mạch lạc (coherence) của đầu ra được cải thiện đáng kể.

Tuy nhiên, Self-consistency thực chất chỉ cung cấp một dạng **pseudo-probability** (xác suất giả định) về khả năng một câu trả lời là đúng, và đi kèm với chi phí tính toán cao (high computational cost), do phải sinh và xử lý nhiều mẫu đầu ra.


Quy trình thực hiện như sau:
1. **Sinh nhiều đường dẫn suy luận (Generating diverse reasoning paths):**  
    LLM (Large Language Model) được cung cấp cùng một prompt nhiều lần. Việc đặt **temperature cao** sẽ khuyến khích mô hình tạo ra **nhiều đường dẫn suy luận và góc nhìn khác nhau** về cùng một vấn đề.
2. **Trích xuất câu trả lời từ từng phản hồi (Extract the answer from each generated response):**  
    Sau khi mô hình tạo ra các phản hồi khác nhau, từng câu trả lời sẽ được **trích xuất riêng biệt** để đánh giá.
3. **Chọn câu trả lời phổ biến nhất (Choose the most common answer):**  
    Cuối cùng, **câu trả lời xuất hiện nhiều nhất** trong số các phản hồi sẽ được chọn làm kết quả cuối cùng.

Hãy xem ví dụ về **hệ thống phân loại email (email classification system)**, nơi email được phân loại là **IMPORTANT** hoặc **NOT IMPORTANT**. Một **prompt theo chuỗi suy nghĩ zero-shot (zero-shot chain of thought prompt)** sẽ được gửi đến LLM nhiều lần để kiểm tra xem **các phản hồi có khác nhau sau mỗi lần gửi không**.

Lưu ý rằng **giọng văn thân thiện, cách chọn từ và cả sự mỉa mai trong email** đều có thể **gây “bẫy” cho LLM**, khiến mô hình đưa ra các suy luận khác nhau hoặc lỗi trong phân loại.

<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">EMAIL:  ```  Hi,  I have seen you use Wordpress for your website. A great open  source content management system. I have used it in the past  too. It comes with lots of great user plugins. And it's pretty  easy to set up.  I did notice a bug in the contact form, which happens when  you select the name field. See the attached screenshot of me  entering text in the name field. Notice the JavaScript alert  box that I inv0k3d.  But for the rest it's a great website. I enjoy reading it. Feel  free to leave the bug in the website, because it gives me more  interesting things to read.  Cheers,  Harry the Hacker.  ```  Classify the above email as IMPORTANT or NOT IMPORTANT. Let's  think step by step and explain why. </td>
  </tr>
  <tr>
    <th>Output 1</th>
    <td colspan="3">**Step 1: Identify the purpose of the email.**  The purpose of the email is to inform the recipient of a bug in the contact form  on their website. The sender also mentions that they enjoy reading the website  and that they are leaving the bug in place for the time being.  **Step 2: Assess the potential impact of the bug.**  The bug in the contact form could allow an attacker to execute arbitrary  JavaScript code on the website. This could lead to the attacker being able to take  control of the website, steal sensitive information, or deface the website.  **Step 3: Consider the credibility of the sender.**  The sender of the email claims to be a hacker named Harry. However, there is no  way to verify the sender’s identity. It is possible that the sender is a legitimate  hacker who is trying to help the recipient, but it is also possible that the sender  is a malicious actor who is trying to trick the recipient into clicking on a malicious  link or downloading a malicious file.  **Conclusion: IMPORTANT**  Based on the potential impact of the bug and the credibility of the sender,  the email should be classified as **IMPORTANT**. The recipient should take  immediate action to fix the bug and protect their website from attack. </td>
</tr>
<tr>
    <th>Output 2</th>
    <td colspan="3">**Explanation:**  1. **Lack of urgency:** The email does not convey any sense of urgency or  time-sensitivity. It starts with a casual greeting and presents the information  in a matter-of-fact tone.  2. **Non-critical bug report:** The bug reported in the contact form is  described as interesting but not critical. The email sender even suggests that  the website owner can leave the bug in place.  3. **Lack of personal impact:** The email does not indicate any direct or  personal impact on the website owner. It simply mentions that the sender  enjoys reading the website. 4. **Absence of action request:** The email does not explicitly request any  action from the website owner. It does not ask for the bug to be fixed or  provide any specific suggestions for improvement.  5. **Sender’s intent:** The sender’s intention seems to be more focused on  sharing an observation and expressing interest in the website rather than  raising a serious concern or requesting assistance.  **Conclusion: NOT IMPORTANT** </td>
</tr>
<tr>
    <th>Output 3</th>
    <td colspan="3">**Step 1: Identify the purpose of the email.**  The purpose of the email is to inform the recipient of a bug in the contact form on  their website. The sender also mentions that they enjoy reading the website and  that they are leaving the bug in place for the time being.  **Step 2: Assess the potential impact of the bug.**  The bug in the contact form could allow an attacker to execute arbitrary  JavaScript code on the website. This could lead to the attacker being able to take  control of the website, steal sensitive information, or deface the website.  **Step 3: Consider the credibility of the sender.**  The sender of the email claims to be a hacker named Harry. However, there is no  way to verify the sender’s identity. It is possible that the sender is a legitimate  hacker who is trying to help the recipient, but it is also possible that the sender is  a malicious actor who is trying to exploit the bug for their own gain.  **Conclusion:**  Based on the above factors, the email should be classified as **IMPORTANT**.  The bug in the contact form is a serious security risk, and the sender’s credibility  is unknown. The recipient should take immediate action to fix the bug and </td>
</tr>
</table>


Bạn có thể sử dụng đoạn lệnh trên và thử xem nó có trả về một phân loại nhất quán hay không. Tùy thuộc vào mô hình mà bạn đang sử dụng và cấu hình nhiệt độ (temperature), nó có thể trả về “QUAN TRỌNG” hoặc “KHÔNG QUAN TRỌNG”. Không rõ.

Bằng cách tạo ra nhiều chuỗi suy nghĩ (**Chains of Thought**) và chọn câu trả lời xuất hiện phổ biến nhất (**“IMPORTANT”**), chúng ta có thể nhận được kết quả chính xác và nhất quán hơn từ mô hình ngôn ngữ lớn (LLM). Ví dụ này cho thấy phương pháp gợi ý tự nhất quán (**self-consistency prompting**) có thể được sử dụng để cải thiện độ chính xác trong phản hồi của LLM bằng cách xem xét nhiều góc độ khác nhau và lựa chọn câu trả lời có tính thống nhất cao nhất.

### Tree of Thoughts (ToT) 

Sau khi đã làm quen với kỹ thuật chuỗi suy nghĩ (**Chain of Thought**) và gợi ý tự nhất quán (**Self-consistency prompting**), chúng ta hãy cùng xem xét phương pháp Cây suy nghĩ (**Tree of Thoughts - ToT**). Phương pháp này khái quát hóa khái niệm gợi ý CoT vì nó cho phép các mô hình ngôn ngữ lớn (LLM) khám phá đồng thời nhiều lộ trình lập luận khác nhau, thay vì chỉ tuân theo một chuỗi suy nghĩ tuyến tính duy nhất. Điều này được mô tả trong Hình...

![[Pasted image 20260409162343.png]]



Hình 1. Minh họa phương pháp “chain of thought prompting” bên trái so với phương pháp “Tree of Thoughts prompting” bên phải.

Cách tiếp cận này khiến **Tree of Thought (ToT)** đặc biệt phù hợp với các **task** phức tạp đòi hỏi khả năng **exploration**. Nó hoạt động bằng cách duy trì một **cây suy nghĩ (tree of thoughts)**, trong đó mỗi **thought** đại diện cho một **chuỗi ngôn ngữ (language sequence)** mạch lạc, đóng vai trò như một **intermediate step** hướng tới việc giải quyết vấn đề.

Mô hình sau đó có thể **khám phá (explore)** các **reasoning path** khác nhau bằng cách **branch out** từ các **node** khác nhau trong cây. Có một **notebook** rất hay, đi vào chi tiết hơn và minh họa **The Tree of Thought (ToT)**, được phát triển dựa trên bài báo _‘Large Language Model Guided Tree-of-Thought’_.


### ReAct (reason & act) 

**ReAct (Reason and Act) prompting** [10]13 là một _paradigm_ (mô hình phương pháp) giúp các **LLM (Large Language Models)** giải quyết các bài toán phức tạp bằng cách kết hợp **suy luận ngôn ngữ tự nhiên (natural language reasoning)** với việc sử dụng **các công cụ bên ngoài** (ví dụ: _search engine_, _code interpreter_, v.v.).

Cách tiếp cận này cho phép LLM thực hiện các **action (hành động)** cụ thể, chẳng hạn như gọi **external APIs** để truy xuất dữ liệu — đây được xem là bước đầu tiên hướng tới việc xây dựng **AI agents (mô hình tác nhân)**.

ReAct mô phỏng cách con người hoạt động trong thế giới thực: chúng ta thường **suy luận bằng lời nói (verbal reasoning)** và sau đó thực hiện hành động để thu thập thêm thông tin. Nhờ đó, ReAct đạt hiệu suất tốt hơn so với nhiều phương pháp **prompt engineering** khác trong nhiều lĩnh vực khác nhau.

 ReAct prompting vận hành dựa trên một vòng lặp gọi là **thought–action loop**:
1. **Reasoning (Suy luận)**  
    LLM phân tích vấn đề và xây dựng một **kế hoạch hành động (plan of action)**.
2. **Acting (Hành động)**  
    Mô hình thực thi các hành động đã đề ra (ví dụ: gọi API, tìm kiếm dữ liệu, chạy code).
3. **Observation (Quan sát)**  
    LLM thu thập kết quả từ các hành động đó.
4. **Update (Cập nhật suy luận)**  
    Dựa trên dữ liệu quan sát được, mô hình điều chỉnh lại suy luận và tạo kế hoạch mới.

Quá trình này lặp lại liên tục cho đến khi LLM tìm ra **giải pháp cuối cùng (final solution)** cho bài toán.

Triển khai thực tế. Để hiểu rõ cách hoạt động của ReAct, bạn cần triển khai bằng code. Trong _code snippet_ được đề cập, tác giả sử dụng:
- **LangChain framework (Python)**: để xây dựng pipeline cho LLM và agent
- **Vertex AI (google-cloud-aiplatform)**: nền tảng AI của Google
- **google-search-results (pip package)**: để tích hợp khả năng tìm kiếm dữ liệu từ bên ngoài

Sự kết hợp này cho phép xây dựng một hệ thống ReAct hoàn chỉnh, nơi LLM có thể vừa suy luận vừa tương tác với thế giới bên ngoài thông qua các công cụ.

Để chạy ví dụ này, bạn phải tạo một khóa SerpAPI (miễn phí) từ [https://serpapi.com/manageapi-key](https://serpapi.com/manageapi-key) và thiết lập một biến môi trường SERPAPI_API_KEY.

Tiếp theo, hãy viết một số mã Python, với nhiệm vụ để mô hình ngôn ngữ (LLM) tìm ra: Có bao nhiêu đứa trẻ có người cha nổi tiếng biểu diễn trong ban nhạc Metallica.


```python

from langchain.agents import load_tools  
from langchain.agents import initialize_agent  
from langchain.agents import AgentType  
from langchain.llms import VertexAI  

prompt = "How many kids do the band members of Metallica have?"  

llm = VertexAI(temperature=0.1)  
tools = load_tools(["serpapi"], llm=llm)  

agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run(prompt) 

```

Đoạn Code Snippet 2 minh họa kết quả thu được. Có thể thấy rõ rằng ReAct thực hiện một chuỗi gồm năm truy vấn tìm kiếm liên tiếp (_search chain_). Thực chất, mô hình ngôn ngữ lớn (LLM) đang “scrape” dữ liệu từ kết quả tìm kiếm của Google để suy luận và xác định tên các ban nhạc.

Sau mỗi lần truy vấn, hệ thống ghi nhận các kết quả dưới dạng _observations_ (quan sát), sau đó sử dụng các thông tin này để tiếp tục xây dựng _chain-of-thought_ (chuỗi suy luận) cho truy vấn kế tiếp.

```

> Entering new AgentExecutor chain...   
Metallica has 4 members.  
Action: Search  
Action Input: How many kids does James Hetfield have?  
Observation: three children  
Thought: 1/4 Metallica band members have 3 children  
Action: Search  
Action Input: How many kids does Lars Ulrich have?  
Observation: 3  
Thought: 2/4 Metallica band members have 6 children  
Action: Search  Action Input: How many kids does Kirk Hammett have?  Observation: Hammett has been married to his second wife Lani since 1998.  They have two sons, Angel (b. September 29, 2006) and Vincenzo (b. June  28, 2008).  
Thought: 3/4 Metallica band members have 8 children  
Action: Search  Action Input: How many kids does Robert Trujillo have?  Observation: 2  
Thought: 4/4 Metallica band members have 10 children  
Final Answer: 10 

```

Đoạn **Code Snippet 2** xác định rằng ban nhạc **Metallica** có bốn thành viên. Sau đó, nó thực hiện việc **truy vấn (query)**từng thành viên để lấy thông tin về tổng số con của họ, rồi tiến hành **tổng hợp (aggregate)** dữ liệu này lại. Cuối cùng, hệ thống trả về **tổng số con** như là kết quả cuối cùng.

Trong thực tế, kỹ thuật **ReAct prompting** yêu cầu bạn hiểu rằng bạn cần liên tục **gửi lại (resend)** các prompt và response trước đó trong mỗi vòng lặp suy luận. Đồng thời, bạn cũng phải thực hiện **cắt tỉa (trimming)** các nội dung được sinh ra không cần thiết để tránh làm nhiễu ngữ cảnh. Bên cạnh đó, việc **thiết lập (configure)** mô hình với các **ví dụ (examples)** và **hướng dẫn (instructions)** phù hợp là rất quan trọng để đảm bảo chất lượng đầu ra.

Bạn có thể tham khảo **notebook14** được lưu trữ trong repository **GoogleCloudPlatform trên GitHub**, nơi cung cấp giải thích chi tiết hơn, bao gồm cả các **input/output thực tế của LLM** với một ví dụ phức tạp hơn.


### Automatic Prompt Engineering 

Tại thời điểm này, bạn có thể nhận ra rằng việc **thiết kế prompt (prompt engineering)** không hề đơn giản. Sẽ thật tiện lợi nếu chúng ta có thể **tự động hóa quá trình này** (tức là viết một prompt để tạo ra các prompt khác). Và đúng vậy — đã có một phương pháp gọi là **Automatic Prompt Engineering (APE)**.

APE là một kỹ thuật giúp **giảm thiểu sự can thiệp thủ công của con người (human input)**, đồng thời **cải thiện hiệu năng của mô hình (model performance)** trên nhiều tác vụ khác nhau.

Cách hoạt động cơ bản của APE như sau:
- Bạn sử dụng một mô hình (LLM) để **generate (sinh) nhiều prompt khác nhau**.
- Sau đó **đánh giá (evaluate)** các prompt này dựa trên chất lượng đầu ra.
- Lựa chọn những prompt tốt, có thể **tinh chỉnh (refine / optimize)** thêm.
- Và **lặp lại vòng lặp (iteration loop)** này để ngày càng tối ưu hơn.

Ví dụ: bạn có thể áp dụng APE để hỗ trợ **huấn luyện chatbot (chatbot training)** cho một **webshop bán áo thun merchandise**. Mục tiêu là xác định tất cả các cách mà khách hàng có thể **diễn đạt ý định mua hàng (user intent expression)** — cụ thể là đặt mua áo thun của một ban nhạc.

Nói cách khác, hệ thống sẽ giúp bạn khám phá các biến thể như:
- “Tôi muốn mua áo band này”
- “Có áo của nhóm X không?”
- “Cho mình đặt một cái áo tour của band Y”
- …

Việc bao phủ đầy đủ các cách diễn đạt này giúp chatbot:

- **hiểu intent chính xác hơn (intent recognition)**
- cải thiện **trải nghiệm người dùng (UX)**
- và tăng **tỷ lệ chuyển đổi (conversion rate)**


1. Viết câu lệnh (prompt) sẽ tạo ra các biến thể đầu ra. Trong ví dụ này, tôi sử dụng gemini-pro để tạo 10 hướng dẫn. Xem Bảng 15:


<table>
  <tr>
	  <th>Prompt</th>
      <td colspan="3">We have a band merchandise t-shirt webshop, and to train a  chatbot we need various ways to order: "One Metallica t-shirt  size S". Generate 10 variants, with the same semantics but keep  the same meaning. </td>
  </tr>
  <tr>
    <th>Output</th>
    <td colspan="3">1. I’d like to purchase a Metallica t-shirt in size small.  2. Can I order a small-sized Metallica t-shirt?  3. I’d like to buy one Metallica t-shirt in small.  4. One Metallica shirt, size small, please.  5. I want one Metallica t-shirt in size small.  6. I’d like to place an order for one Metallica t-shirt in small.  7. Small Metallica t-shirt, one please.  8. I’m looking for one Metallica t-shirt in small.  9. Can you get me one Metallica t-shirt in small?  10.One Metallica small t-shirt, please. </td>
</tr>
</table>


2. Đánh giá (evaluate) tất cả các _instruction candidates_ (các phương án câu lệnh/đề bài) bằng cách chấm điểm dựa trên một _metric_ (thước đo) đã chọn. Ví dụ, bạn có thể sử dụng các chỉ số như **BLEU (Bilingual Evaluation Understudy)** hoặc **ROUGE (Recall-Oriented Understudy for Gisting Evaluation)** để đo mức độ tương đồng và chất lượng giữa các đầu ra.
3. Lựa chọn _instruction candidate_ có _evaluation score_ (điểm đánh giá) cao nhất. Đây sẽ là _final prompt_ (câu lệnh đầu vào cuối cùng) mà bạn có thể sử dụng trong ứng dụng phần mềm hoặc chatbot của mình. Ngoài ra, bạn cũng có thể _fine-tune_ (tinh chỉnh) lại prompt đã chọn và thực hiện đánh giá lại để tối ưu hiệu suất.

### Code prompting 

