

![[Pasted image 20261103135033.png]]


  

Nếu bạn đã sử dụng Claude Code, Codex hay Cursor một thời gian, chắc hẳn bạn đã từng gặp những tình huống như thế này:
  
Bạn yêu cầu một **coding agent** (AI tác tử lập trình) triển khai một tính năng mới. Nó viết code. Mọi thứ trông có vẻ ổn. Nhưng rồi bạn nhận ra nó chẳng chạy dù chỉ một **unit test** nào. Hoặc nó đi **refactor** (tái cấu trúc) một vài file không liên quan, mặc dù bạn đã yêu cầu giữ cho các thay đổi ở mức tối thiểu.

Đôi khi, nó bị kẹt trong việc sửa đi sửa lại một lỗi duy nhất. Bạn phải ngắt quãng nó, giải thích điều gì đang sai và yêu cầu nó thử một cách khác.

Cách đó sửa được vấn đề hiện tại. Tuy nhiên, khi bạn bắt đầu một **session** (phiên làm việc) mới, lỗi tương tự lại có thể tái diễn.

Bạn có thể tiếp tục bổ sung các hướng dẫn vào file `CLAUDE.md` hoặc `AGENTS.md`. Điều đó có giúp ích, nhưng chỉ đến một giới hạn nhất định.

Điều gì sẽ xảy ra nếu bạn có thể kiểm soát cách agent thực thi các **command** (lệnh)? Điều gì sẽ xảy ra nếu bạn có thể kiểm tra công việc của nó, phát hiện các vòng lặp vô hạn (**loops**) và tự động phục hồi sau sự cố mà không cần phải nhúng tay vào mọi lúc?
  
Đó chính là bản chất của **harness engineering** (kỹ thuật xây dựng bộ khung điều phối/harness).

Chúng ta sẽ bắt đầu từ những điều cơ bản, phân tích các thành phần cấu thành một **harness**, sau đó xây dựng một số cơ chế giúp các coding agent hoạt động đáng tin cậy hơn.


## 1. Harness engineering là gì và tại sao nó lại quan trọng?

### Hiểu về Agent Harness (Khung điều phối tác tử)

Khi mọi người so sánh các coding agent, mô hình AI (**model**) thường nhận được tất cả sự chú ý. Liệu Claude lập trình có giỏi hơn GPT không? Chúng ta có nên chuyển sang một model mới hơn không? Model nào chạy nhanh hơn?
Đây đều là những câu hỏi hợp lý, nhưng model chỉ là một phần của bức tranh.
Một coding agent cũng cần một **environment** (môi trường) nơi nó có thể kiểm tra các file, chạy lệnh, sửa đổi code, duy trì tiến độ và xác minh công việc của mình. Hệ thống giúp hiện thực hóa điều này thường được gọi là **agent harness**.

- **Model** có nhiệm vụ diễn giải hướng dẫn và quyết định việc cần làm.
- **Coding agent** sử dụng model đó cùng với các **tools** (công cụ) để thực hiện tác vụ.
- **Harness** cung cấp **context** (ngữ cảnh), quản lý việc thực thi công cụ và **state** (trạng thái), thiết lập các **boundaries** (ranh giới, giới hạn) và kiểm tra kết quả.

Điều này rất dễ bị bỏ qua vì các công cụ như Claude Code vốn đã được tích hợp sẵn một harness bên trong. Các **hooks**, **permissions** (quyền hạn) và **custom workflows** (quy trình tùy chỉnh) giúp mở rộng những gì vốn có sẵn đó.

  
Nói một cách đơn giản: **Model quyết định việc phải làm. Harness định hình những gì model có thể làm, cách nó làm và cách kiểm tra kết quả.**

### Đây có phải chỉ là Context Engineering (Kỹ thuật tối ưu ngữ cảnh)?
- **Context engineering** giống như việc đưa cho tài xế một tấm bản đồ tốt hơn.
- **Harness engineering** ngoài bản đồ ra còn xử lý cả phanh xe, giới hạn tốc độ và hệ thống ghi lại những gì đã xảy ra trong suốt chuyến đi.

Lấy một **API endpoint** làm ví dụ:
- Context engineering cung cấp các ví dụ, **conventions** (quy ước lập trình), tài liệu và test.
- Harness engineering có thể hạn chế việc thực thi công cụ, yêu cầu **validation** (kiểm định), phát hiện các lỗi lặp đi lặp lại và ngăn chặn việc báo cáo một tác vụ thất bại thành đã hoàn thành.
Context engineering thực chất chỉ là một phần của harness engineering, nó không bao phủ toàn bộ hệ thống thực thi.

### Tại sao các lập trình viên nên quan tâm?

Vào tháng 2 năm 2026, LangChain đã mô tả một thí nghiệm trong đó coding agent của họ cải thiện độ chính xác từ 52.8% lên 66.5% trên bộ benchmark Terminal-Bench 2.0, trong khi vẫn giữ nguyên model GPT-5.2-Codex.
  
Nhóm nghiên cứu đã thay đổi các **prompts** (câu lệnh), công cụ, **middleware** (lớp trung gian) và cơ chế xác minh xung quanh mô hình thay vì thay thế chính mô hình đó. Đây là kết quả benchmark, không đảm bảo mọi **repository** (kho mã nguồn) đều cải thiện cùng một mức độ. Tuy nhiên, nó củng cố một luận điểm lớn hơn: **cùng một model có thể có hành vi rất khác biệt tùy thuộc vào harness của nó.**

Và không giống như việc huấn luyện một **foundation model** (mô hình nền tảng), đây là thứ mà các lập trình viên hoàn toàn có thể chủ động can thiệp và cải thiện trực tiếp.

## 2. Các khối xây dựng nên một Agent Harness

Không có một kiến trúc cố định nào mà mọi agent đều tuân theo. Một số harness rất gọn nhẹ (**lightweight**), trong khi số khác bao gồm các **isolated execution services** (dịch vụ thực thi cô lập), **persistent stores** (kho lưu trữ bền vững) và **evaluation pipelines** (đường ống đánh giá).

Chúng ta có thể chia các thành phần này thành ba nhóm chính:

### Kiến thức và năng lực (Knowledge and Capabilities)

Các thành phần này quyết định agent biết những gì và nó được phép sử dụng những gì.


- **Instructions** (Hướng dẫn), thường được lưu trong `CLAUDE.md` hoặc `AGENTS.md`, mô tả các quy ước và ranh giới của dự án.    
- **Skills** (Kỹ năng) đóng gói các quy trình có thể tái sử dụng cho các tác vụ lặp đi lặp lại.
- **Tools và MCP servers** cung cấp quyền truy cập vào file, terminal, API và các hệ thống bên ngoài.
- **Codebase search** giúp agent tìm kiếm các cài đặt (**implementations**), **dependencies** (thư viện phụ thuộc) và test.
- **Context và memory management** quyết định thông tin nào khả dụng tại thời điểm hiện tại và kiến thức hữu ích nào được duy trì qua các session.
### Thực thi và điều khiển (Execution and Control)

- **Agent loop** điều phối các lượt gọi model (**model calls**), thao tác công cụ và **observations** (quan sát).
- **Hooks và middleware** can thiệp vào các thời điểm xác định, ví dụ: sau một thao tác chỉnh sửa code hoặc trước khi gọi công cụ.
- **Sandboxing và permissions** hạn chế việc thực thi và quyền truy cập.
- **Human approvals** (Sự phê duyệt của con người) kiểm soát các thao tác nhạy cảm.
- **Subagents** có thể xử lý các tác vụ được ủy quyền và giới hạn phạm vi.
- **Recovery mechanisms** bao gồm thời gian chờ (**timeouts**), thử lại (**retries**), **checkpoints** và **termination conditions** (điều kiện kết thúc).

Đây là lúc chúng ta ngừng việc chỉ đơn thuần "yêu cầu" model cư xử theo ý mình và chuyển sang **ép buộc** cách công việc phải được thực hiện.

  

### Độ tin cậy và cải tiến (Reliability and Improvement)

- **Validation** kiểm tra code được sinh ra thông qua test, **linting**, **type checking** (kiểm tra kiểu dữ liệu) hoặc các tiêu chí chấp nhận tường minh.
- **Observability** ghi lại các hành động, lỗi và mức độ sử dụng tài nguyên.
- **Evaluations** đánh giá agent trên các tác vụ đại diện, và **feedback loops** chuyển các lỗi quan sát được thành các thay đổi nhắm đúng mục tiêu (**targeted changes**) cho harness.

Nếu không có các cơ chế này, chúng ta rất khó phân biệt đâu là cải tiến thực sự và đâu chỉ là một bản **demo** hào nhoáng bề ngoài.

  

## 3. Xây dựng Coding Agent Harness đầu tiên của bạn

Chúng ta sẽ sử dụng một Python repository thông thường và Claude Code làm agent tham chiếu. Không cần phải tạo một ứng dụng hoàn toàn mới chỉ cho bài viết này.

  
Một số cải tiến dưới đây đã có sẵn trong Claude Code. Số khác đòi hỏi một đoạn script nhỏ hoặc một **external controller** (bộ điều khiển bên ngoài). Tôi sẽ chỉ rõ sự khác biệt khi chúng ta đi qua từng phần.

### 1. Cung cấp ngữ cảnh phù hợp cho agent tại thời điểm chạy (Runtime Context)

Giả sử bạn yêu cầu agent sửa đổi một module hiện có. Nó cần phải hiểu rõ **branch** (nhánh Git) hiện tại, các test lân cận và các file liên quan trước khi chỉnh sửa bất cứ thứ gì.

  Một harness có thể chuẩn bị sẵn một phần ngữ cảnh đó một cách tự động thay vì phó mặc vào việc liệu model có tự khám phá ra chúng hay không.

  

Python

```
import subprocess
from pathlib import Path

def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

def build_context(repo: Path) -> dict:
    return {
        "branch": git(repo, "branch", "--show-current"),
        "status": git(repo, "status", "--short"),
        "tests": [
            str(p.relative_to(repo))
            for p in list((repo / "tests").rglob("test_*.py"))[:20]
        ],
    }
```

Cách này cung cấp cho chúng ta một bản tóm tắt ngữ cảnh nhỏ. Chúng ta có thể lưu nó vào một file và truyền cho agent khi một tác vụ bắt đầu. Nó được thiết kế có chủ ý để nhỏ gọn, không phải là một hệ thống **RAG** (Retrieval-Augmented Generation) cồng kềnh.

Mục đích là làm cho việc chuẩn bị ngữ cảnh trở nên có chủ đích và lặp lại được, chứ không phải biến file `CLAUDE.md` thành một cuốn bách khoa toàn thư.


### 2. Kiểm soát việc thực thi công cụ và cô lập môi trường

Cấp quyền truy cập terminal cho agent rất hữu ích. Nó có thể chạy test, kiểm tra log và cài đặt dependency. Nhưng đó cũng là một nguồn rủi ro.

Hãy xem xét quy tắc: _"Không bao giờ chạy lệnh `rm -rf`."_ Điều đó không ngăn được agent xóa một thư mục thông qua hàm `shutil.rmtree()` bên trong một script Python. Một danh sách đen các chuỗi câu lệnh (**blacklist**) không thể đóng vai trò là một biên giới bảo mật.
  
Đối với các thao tác hẹp như chạy kiểm tra, chúng ta có thể phơi bày một **controlled interface** (giao diện được kiểm soát) thay vì các lệnh shell tùy ý:


Python

```
import subprocess

CHECKS = {
    "lint": ["ruff", "check", "."],
    "test": ["pytest", "-q"],
}

def run_check(name: str, cwd: str) -> dict:
    if name not in CHECKS:
        raise ValueError(f"Unknown check: {name}")
    try:
        result = subprocess.run(
            CHECKS[name],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            shell=False,
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": None, "error": "Command timed out"}
```

Bây giờ agent nhận được các thao tác có tên gọi rõ ràng, giới hạn thời gian (**time limits**) và phần log lỗi được cắt gọn (**trimmed error output**). Phần log cắt gọn rất quan trọng: một đoạn test log khổng lồ có thể ngốn một lượng context lớn một cách đáng ngạc nhiên.

Tuy nhiên, **wrapper** (lớp bọc) này chỉ kiểm soát các hành động được định tuyến qua nó. Nếu agent vẫn giữ quyền truy cập terminal không bị giới hạn, nó có thể vòng qua wrapper. Hơn nữa, `pytest` vẫn có thể thực thi các đoạn code repository chưa được kiểm duyệt ngay cả khi lệnh `pytest` đó được phép chạy.

Để cô lập thực sự, hãy sử dụng **sandbox** hoặc **container** bị giới hạn với các biên giới phù hợp về hệ thống file, mạng và **secrets** (thông tin mật). Lưu ý rằng một **Git worktree** chỉ giúp tách biệt các thay đổi code chứ không phải là một sandbox bảo mật.

### 3. Cấu trúc hóa quá trình thực thi theo mô hình Plan–Implement–Validate (PIV)

Các coding agent đôi khi bắt đầu tiến hành chỉnh sửa code trước khi chúng thực sự hiểu rõ **scope** (phạm vi). Cole Medin đã thảo luận về mô hình Plan–Implement–Validate (PIV) như một cách tổ chức các tác vụ lớn hơn.


- Trong giai đoạn **Plan (Lập kế hoạch)**, agent kiểm tra repository và viết ra các file bị ảnh hưởng, các **constraints** (ràng buộc) và **acceptance criteria** (tiêu chí nghiệm thu).
- Trong giai đoạn **Implement (Triển khai)**, nó thực hiện các thay đổi dựa trên kế hoạch đó.
- Trong giai đoạn **Validate (Xác thực)**, nó kiểm tra bản **diff** cuối cùng và chạy các test liên quan.
Một bản kế hoạch ngắn gọn là đủ để làm cho quy trình làm việc trở nên cụ thể:


Markdown

```
# Implementation Plan
## Scope
- Update src/users/service.py
- Add tests in tests/test_users.py
## Constraints
- Keep public interfaces unchanged
- Avoid unrelated refactoring
## Acceptance criteria
- Existing tests pass
- New behavior has test coverage
- Ruff passes
```

Đối với một thay đổi lớn hơn, bạn có thể chạy các giai đoạn này trong các session riêng biệt. Một validation session hoàn toàn mới sẽ hữu ích hơn vì nó không kế thừa mọi giả định mà implementation agent đã đưa ra trước đó.

  

Một bộ điều khiển tùy chỉnh thậm chí có thể ngăn việc thực thi giai đoạn Implement nếu chưa có Plan, hoặc ngăn chặn việc hoàn thành tác vụ nếu chưa vượt qua bước Validate. Claude Code có thể hỗ trợ từng bước đơn lẻ, trong khi việc chuyển đổi các giai đoạn nghiêm ngặt giữa các session có thể đòi hỏi một bộ điều khiển bên ngoài hoặc **Agent SDK**.

Bạn không cần quy trình này cho một bản sửa lỗi chính tả nhỏ. Nó phát huy tác dụng tốt hơn khi có sự tham gia của nhiều module hoặc các quyết định về kiến trúc.

### 4. Thêm cơ chế tự động xác minh, tự sửa lỗi và phát hiện vòng lặp (Self-Repair & Loop Detection)

Bây giờ, hãy tưởng tượng agent thông báo rằng tác vụ đã hoàn thành. Làm sao chúng ta biết chắc chắn điều đó?

Chúng ta có thể tin tưởng vào tin nhắn cuối cùng của nó. Nhưng tôi thích việc harness tự chạy các kiểm tra thực tế hơn:


Bash

```
ruff check .
pytest -q
```

Nếu các kiểm tra thất bại, harness có thể trả về một bản tóm tắt lỗi ngắn gọn cho agent để nó thử lại lần nữa. Giả sử `pytest` báo lỗi:


Plaintext

```
FAILED tests/test_users.py::test_invalid_email
AssertionError: expected 422, got 500
```

Agent sẽ tiến hành điều tra, thay đổi code và chạy lại bước xác minh. Đó chính là **self-repair loop** (vòng lặp tự sửa lỗi). Nhưng nó cần phải có **stopping rule** (quy tắc dừng). Nếu không có quy tắc này, agent có thể tiếp tục chỉnh sửa mãi một hàm mà không tiến gần hơn đến đích.

Chúng ta có thể theo dõi cả số lần thử và việc liệu lỗi cũ có lặp lại liên tục hay không:

Python

```
def record_failure(state: dict, fingerprint: str) -> str:
    if fingerprint == state.get("last_failure"):
        state["consecutive_count"] += 1
    else:
        state["last_failure"] = fingerprint
        state["consecutive_count"] = 1
        state["attempts"] += 1
    
    if state["consecutive_count"] >= 3:
        return "stop_repeated_failure"
    if state["attempts"] >= 5:
        return "stop_attempt_limit"
    return "retry"

state = {
    "last_failure": None,
    "consecutive_count": 0,
    "attempts": 0,
}
```

Phần `fingerprint` có thể kết hợp định danh của test và kiểu ngoại lệ đã được chuẩn hóa. Đừng so sánh toàn bộ log theo từng byte: **timestamps** (dấu thời gian) và đường dẫn tạm thời (**temporary paths**) có thể thay đổi ngay cả khi vấn đề cốt lõi không đổi.

  

Một bộ điều khiển sẽ gọi hàm này sau mỗi lần validation thất bại. Nó sẽ quyết định cho phép sửa lỗi tiếp, cung cấp ngữ cảnh chẩn đoán khác, hoặc dừng lại và yêu cầu sự can thiệp của con người. Các ngưỡng giới hạn trên chỉ mang tính chất minh họa, không phải là mặc định phổ biến cho mọi trường hợp.
  
Đôi khi, việc biết **khi nào nên dừng lại** có giá trị tương đương với việc biết cách thử lại thế nào.

### 5. Làm cho trạng thái thực thi mang tính bền vững và có thể khôi phục (Persistent & Resumable State)

Điều gì xảy ra khi session kết thúc ngang chừng một tác vụ, hoặc ngữ cảnh bị nén lại (**compacted**)?
  
Nếu bản ghi duy nhất về tiến độ chỉ nằm trong đoạn hội thoại, session tiếp theo sẽ phải tái tạo lại mọi thứ từ đầu.

Một cách tiếp cận đáng tin cậy hơn là duy trì một file **task-state** mang tính bền vững:

JSON

```
{
  "task_id": "feature-042",
  "stage": "validate",
  "status": "failed",
  "plan": "plan.md",
  "completed_steps": ["plan", "implement"],
  "failed_check": "test_invalid_email",
  "attempts": 2,
  "next_action": "inspect_failure"
}
```

Một session mới sẽ đọc trạng thái này, kiểm tra repository và tiếp tục công việc còn dang dở. Nó không nên mù quáng tin tưởng vào file đó; branch có thể đã thay đổi, các file có thể đã bị chỉnh sửa và kết quả test cũ có thể không còn phù hợp nữa.
  
Anthropic đã nghiên cứu vấn đề này khi phát triển các tác vụ chạy dài (**long-running agents**). Một **progress artifact** (sản phẩm lưu trữ tiến độ) không đồng nghĩa với việc giữ lại mọi tin nhắn từ đoạn hội thoại trước đó. Nó chỉ nắm bắt các dữ kiện vận hành cần thiết để tiếp tục công việc.

### 6. Sử dụng execution traces để cải thiện harness của bạn

Chúng ta đã thêm các bộ điều khiển và cơ chế phục hồi. Làm thế nào để biết liệu chúng có thực sự giúp ích hay không?

Hãy bắt đầu bằng việc ghi lại những gì agent thực sự làm (**execution traces**). Ngay cả một event log nhỏ cũng có thể hé lộ một **failure pattern** (mẫu hình lỗi):


Plaintext

```
10:12:01  task_started
10:12:02  context_initialized
10:12:41  file_modified
10:12:45  pytest_failed
10:13:02  file_modified
10:13:07  pytest_failed
10:13:25  file_modified
10:13:31  pytest_failed
10:13:31  repeated_failure_detected
10:13:31  task_stopped
```

Bản trace này cho chúng ta biết agent đã thực hiện một số chỉnh sửa nhưng liên tục vấp phải cùng một lỗi. Chúng ta vẫn cần phải kiểm tra các phần code được sửa và chi tiết lỗi để hiểu nguyên nhân sâu xa: Liệu có thiếu ngữ cảnh quan trọng nào không? Bản tóm tắt lỗi có quá mơ hồ không? Hay agent cứ lặp đi lặp lại việc áp dụng một bản sửa lỗi sai lầm?
  

Một khi xác định được nguyên nhân khả dĩ, chúng ta thực hiện một thay đổi nhắm đúng mục tiêu vào harness và kiểm tra lại.

Hãy xây dựng một tập hợp nhỏ các tác vụ repository mô phỏng chính công việc thực tế hàng ngày của bạn. Chạy chúng với harness ban đầu, sau đó chạy với harness đã chỉnh sửa, đồng thời giữ cho model và điều kiện thực thi ở mức tương đương.

So sánh các chỉ số: **completion rates** (tỷ lệ hoàn thành), lỗi validation, lỗi lặp lại, số lần gọi công cụ, **elapsed time** (thời gian trôi qua) và **token cost** (chi phí token).
  

Có một sự khác biệt rõ rệt giữa việc **validate code** và **đánh giá harness**. Pytest cho chúng ta biết liệu một thay đổi cụ thể có vượt qua các test của nó hay không. Trong khi đó, đánh giá harness cho chúng ta biết liệu agent có hoàn thành ổn định các tác vụ qua các lần chạy và kịch bản khác nhau hay không.
  
Đây là phần mà tôi thấy hữu ích nhất. Thay vì liên tục bổ sung thêm nhiều hướng dẫn, chúng ta có thể kiểm tra các lỗi phát sinh, thay đổi hệ thống và kiểm chứng xem những thay đổi đó có cải thiện kết quả hay không.

## Lời kết

Các coding agent đang ngày càng thông minh hơn, nhưng việc sử dụng chúng một cách đáng tin cậy trên các dự án thực tế vẫn đòi hỏi một lượng công sức kỹ thuật nhất định.
  
Một model tốt rất hữu ích. Các hướng dẫn rõ ràng và ngữ cảnh phù hợp cũng hữu ích không kém. Nhưng không có yếu tố nào trong số đó đảm bảo cho việc thực thi an toàn, phục hồi hiệu quả hay validation chuẩn xác.

Tôi khuyên bạn nên bắt đầu với các cơ chế kiểm tra tự động và execution traces cơ bản, sau đó cải thiện bất cứ thứ gì hay gặp lỗi nhất. Bạn không cần phải áp dụng mọi cơ chế trong bài viết này ngay từ ngày đầu tiên.

Cho đến nay, chúng ta mới chỉ tập trung vào một coding agent duy nhất. Nhưng vẫn còn rất nhiều thứ khác đáng để khám phá: các **long-running workflows** (quy trình chạy dài), **Ralph loops**, và những gì xảy ra khi nhiều session agent cùng làm việc trên một dự án.

  