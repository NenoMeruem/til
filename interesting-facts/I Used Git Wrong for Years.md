

Node: [[article]]
Tags:  #software-engineering 


Tôi từng nghĩ Git chỉ gồm ba lệnh.

```bash
git add .
git commit -m "update"
git push
```

Đó là quy trình làm việc của tôi trong suốt nhiều năm.

Một ngày nọ, tôi quan sát một lập trình viên cấp cao khôi phục các commit đã xóa, dọn dẹp lịch sử lộn xộn suốt 6 tháng trời và hoàn tác một lần merge lỗi mà không cần tra Google, cũng chẳng hề tỏ ra hoảng loạn.

Trong khi đó, tôi thì vẫn đang phải Google: 'làm thế nào để hoàn tác commit gần nhất nhưng vẫn giữ lại các thay đổi'.

Đó là khoảnh khắc tôi nhận ra một điều: "Hầu hết các lập trình viên chỉ biết Git vừa đủ để tồn tại. Những người tiến bộ nhanh là những người hiểu rõ Git thực sự vận hành như thế nào."

Dưới đây là những thủ thuật và thói quen với Git mà tôi đã ước mình biết sớm hơn – những thứ đã thực sự thay đổi cách tôi làm việc mỗi ngày.

Câu trả lời ngắn gọn là: Các lập trình viên cấp cao (Senior) không thao tác Git nhanh hơn nhờ việc ghi nhớ nhiều câu lệnh hơn.

Họ làm nhanh hơn vì họ hiểu Git là một dòng thời gian – một bản ghi chép lại mọi trạng thái mà dự án của bạn từng trải qua. Khi đã nắm bắt được tư duy đó, mọi câu lệnh sẽ trở nên dễ hiểu một cách trực giác.


**Git không chỉ là công cụ kiểm soát phiên bản**

Trong một thời gian dài, tôi từng coi Git như một hệ thống sao lưu.
Thay đổi → commit → push.
Nhưng Git giống như một dòng thời gian ghi lại toàn bộ "cuộc đời" dự án của bạn hơn.
Một khi đã hiểu được điều đó, các lệnh (commands) không còn làm tôi thấy sợ hãi nữa.
Và việc sửa lỗi cũng trở nên dễ dàng hơn rất nhiều.


![Image](images/I%20Used%20Git%20Wrong%20for%20Years/Pasted%20image%2020260615163315.png)

### Mẹo #1: `git status` là lệnh quan trọng nhất
Điều này nghe có vẻ hiển nhiên, nhưng tôi đã từng phớt lờ nó trong nhiều năm.

Giờ đây, tôi chạy lệnh này liên tục trước mỗi lần commit, trước khi chuyển nhánh và trước khi rebase.

```bash
git status
```

Hầu hết các lỗi Git xảy ra khi bạn không nắm rõ trạng thái hiện tại của mình. Tôi từng vô tình commit các tệp `.env`, nhật ký debug, mã nguồn chưa hoàn thiện và cả ảnh chụp màn hình linh tinh chỉ vì bỏ qua bước này.

Chỉ một lệnh. Tốn hai giây. Tiết kiệm hàng giờ đồng hồ.

### Mẹo #2: `git diff` giúp tôi tránh những pha "muối mặt" khi commit
Lệnh này đã thay đổi hoàn toàn cách tôi thực hiện commit.

Trước khi commit:

```bash
git diff
```

Lệnh này hiển thị chính xác những gì đã thay đổi. Tôi đã từng phát hiện ra các khóa API, các đoạn import bị lỗi và những câu lệnh `console.log` còn sót lại ngay trước khi đẩy code lên môi trường sản xuất.

Thậm chí còn tốt hơn:

```bash
git diff --staged
```

Lệnh này chỉ hiển thị những tệp mà bạn đã thêm vào (stage). Bây giờ, tôi sử dụng lệnh này trước hầu hết mọi lần commit.

### Mẹo #3: Đừng dùng `git add .` một cách mù quáng
`git add .` sẽ đưa mọi thứ vào trạng thái stage.

Đôi khi điều đó cũng ổn, nhưng thường thì bạn chỉ muốn commit một thay đổi cụ thể chứ không phải 4 thứ khác mà bạn đã đụng vào trong quá trình làm việc.

Thay vào đó, hãy dùng:

```bash
git add -p
```

Lệnh này cho phép bạn thêm các thay đổi theo từng phần (từng đoạn nhỏ). Bạn sẽ xem xét từng khối mã và quyết định: đưa nó vào stage hay bỏ qua.

Ví dụ thực tế: Tôi đã thực hiện sửa lỗi đăng nhập, thiết kế lại giao diện và dọn dẹp code ngẫu nhiên trên cùng một tệp. `git add -p` cho phép tôi chỉ commit phần sửa lỗi đăng nhập một cách sạch sẽ.

Các commit gọn gàng hơn. Việc debug sau này sẽ dễ dàng hơn nhiều. Rất xứng đáng với 30 giây bỏ ra thêm.

### Mẹo #4: `git bisect` khiến bạn cảm thấy như một "phù thủy"
Tôi đã bỏ qua lệnh này trong nhiều năm vì nghĩ rằng nó quá cao siêu.

Tình huống là: bạn biết có cái gì đó bị hỏng trên môi trường sản xuất. Bạn biết là ba tuần trước nó vẫn chạy tốt. Bạn không có manh mối nào về việc trong 80 commit ở giữa, cái nào đã gây ra lỗi.

```bash
git bisect start
git bisect bad          # trạng thái hiện tại đang bị lỗi
git bisect good v2.3.1  # phiên bản này vẫn ổn
```

Sau đó, Git sẽ kiểm tra (checkout) commit nằm chính giữa trạng thái "tốt" và "xấu".

Bạn kiểm tra nó, rồi báo cho Git biết nó "tốt" hay "xấu".

Nó sẽ tiếp tục chia đôi không gian tìm kiếm một lần nữa. Lặp lại khoảng 7 lần và bạn đã thu hẹp được 80 commit xuống còn đúng 1 commit duy nhất.

Tôi đã dùng cách này cho một lỗi tồn đọng suốt cả tháng. Tôi tìm ra chính xác commit gây lỗi chỉ trong 11 phút. Nội dung commit đó ghi là "dọn dẹp nhỏ". Thật sự thì nó chẳng "nhỏ" chút nào.
### Mẹo #5: git stash – "Cứu tinh" thực thụ
Lệnh này đã cứu tôi không biết bao nhiêu lần.

**Tình huống:** Bạn đang làm dở một tính năng thì xuất hiện một lỗi khẩn cấp. Bạn cần đổi nhánh ngay lập tức.

*   **Trước đây:** Tôi sẽ hoảng loạn.
*   **Bây giờ:**
```bash
git stash
```

Công việc của bạn được cất vào một "chiếc tủ an toàn". Sau đó, bạn cứ việc đổi nhánh, sửa lỗi, rồi quay trở lại:
```bash
git stash pop
```

Mọi thứ trở lại chính xác như lúc bạn rời đi. Các nhánh thực chất là các môi trường thử nghiệm (sandbox), còn `git stash` chính là nút "tạm dừng" khẩn cấp giữa chúng.

### Mẹo #6: git log giúp tôi "thông não" về Git
Trong nhiều năm, lịch sử Git đối với tôi chỉ là một mớ hỗn độn. Cho đến khi tôi bắt đầu dùng:
```bash
git log --oneline --graph --decorate
```
Đột nhiên, toàn bộ tiến trình của dự án hiện ra rõ ràng: các nhánh, các lần hợp nhất (merge), luồng commit... mọi thứ đều được hiển thị mạch lạc. Tôi tạo ngay một alias:
```bash
alias gl='git log --oneline --graph --decorate'
```
`gl` hiện là một trong những lệnh tôi dùng nhiều nhất mỗi ngày.

### Mẹo #7: Nhánh rất rẻ — Hãy dùng nó nhiều hơn
Làm việc trực tiếp trên nhánh `main` là một cái bẫy. Tôi từng mắc lỗi này quá lâu. Giờ đây, tôi tạo nhánh cho hầu hết mọi thứ:
```bash
git switch -c fix-login-bug
```

Điều này thay đổi cách tôi thử nghiệm mà không còn sợ hãi. Tôi có thể kiểm tra ý tưởng, tái cấu trúc mã nguồn mạnh tay và thử các bản sửa lỗi rủi ro mà không bao giờ ảnh hưởng đến mã ổn định. Nhánh là miễn phí, nhưng cái giá phải trả khi làm hỏng nhánh `main` thì không. Hãy coi nhánh là các môi trường sandbox.

### Mẹo #8: Học git restore trước khi bạn thực sự cần đến nó
Lệnh này cứu tôi khỏi những cơn "đau tim". Tôi vô tình sửa nhầm file. Thay vì hoàn tác thủ công:
```bash
git restore app.js
```
File được khôi phục về trạng thái commit gần nhất ngay lập tức. Ước gì tôi biết lệnh này từ tháng đầu tiên đi làm.

### Mẹo #9: git worktree bị đánh giá thấp một cách vô lý

Tôi đọc được điều này từ một bài đăng trên Reddit và hóa ra họ nói rất đúng. Thông thường, khi đang làm dở việc mà phải chuyển task, tôi hay làm: *stash -> đổi nhánh -> sửa lỗi -> quay lại -> unstash -> cầu nguyện không bị conflict.*

Với `git worktree` thì khác:
```bash
git worktree add ../hotfix-branch hotfix/login-timeout
```
Lệnh này checkout nhánh đó ra một thư mục riêng biệt. Nhánh hiện tại của bạn vẫn nguyên vẹn. Bạn chỉ cần di chuyển sang thư mục kia, sửa lỗi, push, rồi quay lại thư mục làm việc chính. Không cần stash, không cần checkout, không còn cảnh "ôi chết, mình đang làm dở đến đâu rồi nhỉ?".

### Mẹo #10: git reflog tựa như du hành thời gian

Đây là lệnh khiến các lập trình viên senior trông thật "vi diệu". Tôi từng nghĩ mình đã mất vĩnh viễn các commit sau khi rebase lỗi. Thực tế, Git ghi nhớ gần như mọi thứ:
```bash
git reflog
```
Nó hiển thị mọi hành động gần đây, kể cả những commit bạn tưởng đã xóa, nhánh bạn đã hủy, hoặc trạng thái bạn đã reset. Khôi phục chỉ bằng một lệnh:
```bash
git checkout <commit-id>
```
Khoảnh khắc đó thay đổi hoàn toàn cách tôi nhìn nhận sai lầm trong Git. Git reflog là tấm lưới an toàn của bạn, nó lưu giữ thông tin khoảng 90 ngày. Đừng cho rằng bất cứ thứ gì đã mất cho đến khi bạn kiểm tra reflog.

### Mẹo #11: Commit message quan trọng hơn bạn nghĩ
*   **Tôi ngày xưa:** `git commit -m "fix"`
*   **Tôi ngày nay:** `git commit -m "Sửa lỗi làm mới token trong auth middleware"`

Commit message tốt không phải dành cho Git, mà dành cho con người. Thường là cho chính bạn vào 6 tháng sau, khi đang cố hiểu tại sao mình lại thay đổi code vào lúc 11 giờ đêm thứ Năm.

### Mẹo #12: Interactive Rebase giúp lịch sử gọn gàng hơn
Tôi từng tránh `git rebase` vì nghe nó có vẻ nguy hiểm. Nhưng khi học được:
```bash
git rebase -i HEAD~5
```
Nó cho phép bạn gộp (squash), đổi tên, sắp xếp lại các commit trước khi gửi PR. Thay vì một đống commit lộn xộn, bạn sẽ có một commit sạch sẽ, đầy ý nghĩa. Đồng nghiệp của bạn chắc chắn sẽ thấy sự khác biệt.

### Mẹo #13: git blame hữu ích đến bất ngờ

Bất chấp cái tên nghe có vẻ "đổ lỗi" (blame), lệnh này cực kỳ hữu ích:
```bash
git blame app.js
```
Nó hiển thị ai đã sửa dòng nào, sửa khi nào và trong commit nào. Tôi thường dùng nó để truy ngược lỗi production về đúng commit gây ra nó, hoặc hiểu lý do tại sao một đoạn code lạ lùng lại tồn tại. Đây giống như môn khảo cổ học code vậy.

### Mẹo #14: Alias giúp loại bỏ sự ma sát (cản trở)
Tôi chán ngấy việc gõ các lệnh dài dòng, nên tôi tạo alias:
```bash
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
```
Mỗi alias tiết kiệm 3 giây. Nếu dùng 50 lần/ngày, qua nhiều tháng, con số đó rất đáng kể. Quan trọng hơn, khi việc gõ lệnh dễ dàng, bạn sẽ chủ động thực hiện các thao tác đúng đắn thường xuyên hơn.

### Sự thay đổi thực sự
Nhiều năm liền, tôi tưởng giỏi Git là phải thuộc lòng các câu lệnh. Giờ đây tôi hiểu ra, đó chỉ là:
**Giữ bình tĩnh khi mọi thứ đi chệch hướng.**

Những lập trình viên giỏi nhất tôi biết không sợ Git. Bởi vì họ hiểu cách **khôi phục**. Đó mới là sự khác biệt thực sự. Không phải là gõ phím nhanh, không phải là quy trình hoa mỹ, mà là **sự tự tin**.

Sự tự tin trong Git đến từ việc học cách:
1. Kiểm tra các thay đổi (`git diff`)
2. Hoàn tác lỗi (`git restore`)
3. Khôi phục an toàn (`git reflog`)

Một khi nắm vững những điều đó, Git sẽ không còn đáng sợ nữa. Hãy bắt đầu với 3 lệnh trên, chúng sẽ tiết kiệm cho bạn vô số giờ làm việc.


Bài viết được dịch tại:
- https://medium.com/@TusharKanjariya/i-used-git-wrong-for-years-8c8307402640