
Author: Lee Boonstra 


"You don’t need to be a data scientist or a machine learning engineer – everyone can write  a prompt."

Node: [[books]]
Tags: #book , #ai

## Introduction




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

**Phân biệt giữa system prompt, contextual prompt và role prompt** cung cấp một khuôn khổ (framework) để thiết kế prompt với mục đích rõ ràng, cho phép kết hợp linh hoạt và dễ dàng phân tích cách mỗi loại prompt ảnh hưởng đến đầu ra của mô hình ngôn ngữ. Hãy cùng tìm hiểu ba loại prompt khác nhau này:

### System prompting

