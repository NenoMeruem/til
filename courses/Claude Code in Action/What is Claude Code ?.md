# Introduction

## Giới thiệu khóa học

Khóa học này cung cấp chương trình đào tạo toàn diện về cách sử dụng **Claude Code** trong các tác vụ phát triển phần mềm. Nội dung bao gồm:
- Kiến trúc nền tảng (underlying architecture) của AI coding assistant
- Kỹ thuật triển khai (implementation techniques) trong môi trường thực tế
- Chiến lược tích hợp nâng cao (advanced integration strategies)

Bạn sẽ tìm hiểu cách **Claude Code** quản lý _context_ (ngữ cảnh làm việc), cũng như cách mở rộng chức năng thông qua **MCP server** và tích hợp với GitHub để tối ưu hóa workflow phát triển phần mềm.

## Bạn sẽ học được gì

### 1. Hiểu về kiến trúc của Coding Assistant

- Nắm được cách AI assistant tương tác với **codebase** thông qua cơ chế _tool integration_.
- Hiểu nền tảng kỹ thuật cho phép hệ thống phân tích (code analysis), sinh mã (code generation) và chỉnh sửa mã (code modification).
- Làm rõ vai trò của các thành phần như parser, abstract syntax tree (AST), và execution environment trong việc xử lý mã nguồn.
### 2. Khai thác hệ thống Tool của Claude Code
- Tìm hiểu cách Claude Code điều phối và kết hợp nhiều tool để xử lý các tác vụ lập trình nhiều bước (multi-step tasks).
- Ứng dụng trong các tình huống như refactor, debugging, test generation và feature implementation.
- Hiểu cách orchestration giữa các tool giúp tự động hóa quy trình phát triển.

### 3. Làm chủ kỹ thuật Context Management
- Học cách duy trì _relevant context_ xuyên suốt hội thoại với AI.
- Biết cách tham chiếu đúng tài nguyên trong project (source files, config files, documentation).
- Tối ưu hóa prompt để giảm nhiễu (noise) và tăng độ chính xác của phản hồi.
### 4. Triển khai quy trình giao tiếp trực quan (Visual Communication Workflow)
- Sử dụng input dạng hình ảnh (UI mockups, screenshot, wireframe) để mô tả thay đổi giao diện.
- Tận dụng các tính năng planning nâng cao để xử lý thay đổi trên codebase lớn.
- Kết hợp giữa phân tích cấu trúc UI và cập nhật logic backend khi cần.

### 5. Xây dựng Custom Automation
- Tạo các custom command có thể tái sử dụng.
- Thiết lập automation pipeline để xử lý các tác vụ lặp lại như linting, formatting, migration script.
- Chuẩn hóa workflow nhằm tăng năng suất và giảm lỗi thủ công (human error).

### 6. Mở rộng chức năng với MCP Server
- Tích hợp các công cụ và dịch vụ bên ngoài thông qua MCP server.
- Kích hoạt các khả năng nâng cao như browser automation, API orchestration và các workflow chuyên biệt.    
- Thiết kế kiến trúc mở rộng (extensible architecture) để Claude Code hoạt động như một thành phần trong hệ sinh thái DevOps.

### 7. Tích hợp với GitHub Workflow
- Thiết lập quy trình automated code review.
- Tích hợp AI vào pipeline quản lý mã nguồn sử dụng Git.
- Áp dụng trong pull request review, CI/CD, và branch management.
### 8. Áp dụng Thinking & Planning Modes
- Hiểu khi nào nên sử dụng các chế độ suy luận khác nhau tùy theo độ phức tạp của bài toán.    
- Phân biệt giữa tác vụ đơn giản (quick patch, minor fix) và bài toán kiến trúc phức tạp (system redesign, large-scale refactor).
- Tối ưu chiến lược giải quyết vấn đề dựa trên complexity level và scope của project.
## Yêu cầu trước khi tham gia
- Thành thạo sử dụng command-line interface (CLI) và thao tác trên terminal.
- Có kiến thức cơ bản về version control với Git (commit, branch, merge, pull request).
## Khóa học này dành cho ai?
- Lập trình viên muốn tích hợp AI assistant vào workflow phát triển phần mềm.
- Các team phát triển phần mềm muốn triển khai tích hợp GitHub có hỗ trợ AI cho nhiều quy trình khác nhau.

# What is a coding assistant?
Một **coding assistant** (trợ lý lập trình) không chỉ đơn thuần là một công cụ sinh ra các đoạn mã nguồn. Thực chất, nó là một **hệ thống phần mềm phức tạp** được xây dựng dựa trên **mô hình ngôn ngữ (Language Model)**, có khả năng phân tích, suy luận và xử lý các bài toán lập trình ở mức độ cao.

Dưới đây là bản dịch sử dụng các thuật ngữ chuyên ngành trong lập trình, nhưng được diễn đạt theo cách dễ hiểu và dễ tiếp cận:

## How Coding Assistant Work

Khi bạn giao cho một coding assistant (trợ lý lập trình) một nhiệm vụ — ví dụ như **debug một bug dựa trên error message** — nó sẽ thực hiện một quy trình tương tự như cách một developer xử lý vấn đề trong thực tế.

![[Pasted image 20260224110710.png]]


 1. Thu thập ngữ cảnh (Gather Context): Phân tích **error message** để hiểu lỗi đang nói đến vấn đề gì, xác định phần nào trong **codebase** bị ảnh hưởng, tìm các **file liên quan** đến lỗi.
2. Xây dựng phương án xử lý (Formulate a Plan): Quyết định cách sửa lỗi (ví dụ: refactor một đoạn code, thay đổi logic xử lý, hoặc cập nhật dependency), lên kế hoạch kiểm chứng kết quả bằng cách chạy test (unit test, integration test, v.v.).
3. Thực thi giải pháp (Take Action):  Chỉnh sửa file (modify source files), thực thi các command cần thiết (ví dụ: build project, chạy test suite, lint code)

Điểm Quan Trọng Cần Lưu Ý:  **Bước 1 (thu thập ngữ cảnh)** và **Bước 3 (thực thi giải pháp)** đều yêu cầu assistant phải **tương tác với môi trường bên ngoài (external environment)** - Đọc file trong hệ thống, truy xuất tài liệu (documentation), thực thi command trong terminal, chỉnh sửa mã nguồn.

## The Tool Use Challenge

Đây là lúc mọi thứ trở nên thú vị. Về bản chất, **language model (LLM – Large Language Model)** chỉ có khả năng **xử lý chuỗi văn bản (text input)** và sinh ra **chuỗi văn bản đầu ra (text output)**. Chúng **không có quyền truy cập trực tiếp vào hệ thống file (file system)**, **không thể thực thi lệnh (execute command)**, cũng không thể tương tác với môi trường runtime. Ví dụ:  Nếu bạn yêu cầu một LLM thuần túy đọc nội dung một file, nó sẽ phản hồi rằng nó **không có capability (khả năng hệ thống)** để thực hiện thao tác đó.

Vậy làm thế nào các **coding assistant** (trợ lý lập trình) giải quyết được bài toán này? Câu trả lời nằm ở một cơ chế thông minh gọi là **Tool Use**.

## How Tool Use Works

Khi bạn gửi một request đến coding assistant, hệ thống **không chỉ chuyển nguyên văn câu hỏi của bạn cho LLM**. Thay vào đó, nó sẽ:

1. **Inject thêm instruction (chỉ thị hệ thống)** vào prompt.
    
2. Dạy LLM cách “yêu cầu hành động” thông qua một format chuẩn.
    
3. Diễn giải output của LLM như một lệnh hệ thống thay vì câu trả lời thông thường.
    

Ví dụ, hệ thống có thể tự động thêm vào prompt một hướng dẫn như sau:

> “Nếu bạn muốn đọc file, hãy phản hồi theo format:  
> `ReadFile: <tên_file>`”

---

## Toàn bộ luồng xử lý (Execution Flow)

Giả sử bạn gửi yêu cầu:

> “Code trong file `main.go` là gì?”

### Bước 1 – Prompt Augmentation

Coding assistant sẽ **augment prompt** bằng cách thêm các tool instruction vào request ban đầu.

### Bước 2 – Tool Invocation Request

LLM phản hồi:

```
ReadFile: main.go
```

Lưu ý:  
LLM không thực sự đọc file. Nó chỉ **sinh ra một chuỗi text có cấu trúc đúng theo giao thức (protocol format)**.

### Bước 3 – Tool Execution Layer

Coding assistant (phần wrapper/backend):

- Parse output của model
    
- Nhận diện đây là một **tool call**
    
- Thực thi hành động thực tế: đọc file `main.go` từ file system
    
- Gửi nội dung file ngược lại cho LLM như một context mới
    

### Bước 4 – Final Response Generation

LLM nhận được nội dung file và sinh ra câu trả lời cuối cùng dựa trên dữ liệu thực tế.

---

## Bản chất kỹ thuật của hệ thống

Điểm quan trọng:

LLM **không thật sự:**

- Đọc file
    
- Ghi file
    
- Chạy chương trình
    
- Thực thi shell command
    

Thay vào đó, nó:

- Sinh ra **structured text output**
    
- Tuân thủ một **tool calling protocol**
    
- Được hệ thống bên ngoài (orchestrator / runtime wrapper) thực thi thay
    

Nói cách khác:

> Tool Use là một cơ chế **orchestration giữa LLM và môi trường thực thi**, trong đó LLM đóng vai trò bộ máy suy luận (reasoning engine), còn hệ thống bên ngoài đảm nhiệm phần tương tác với tài nguyên hệ thống.

---

## Tại sao cơ chế này quan trọng?

Nhờ Tool Use, coding assistant có thể:

- “Đọc file”
    
- “Viết code”
    
- “Refactor project”
    
- “Chạy test”
    
- “Build project”
    
- “Thực thi CLI command”
    

Trong khi thực tế, LLM chỉ đang **generate text theo một contract định dạng nghiêm ngặt**.

---

## Tóm lại

Tool Use là một mô hình:

- **LLM = Brain (Reasoning + Text Generation)**
    
- **Assistant Backend = Executor (Tool Runtime + Environment Access)**
    

Sự kết hợp này tạo ra trải nghiệm như thể AI có quyền truy cập hệ thống, trong khi về bản chất nó chỉ đang thực hiện **text-based function invocation thông qua một giao thức được thiết kế sẵn**.

Nếu bạn muốn, mình có thể vẽ thêm sơ đồ kiến trúc (architecture diagram) để bạn hình dung rõ hơn luồng xử lý nội bộ.