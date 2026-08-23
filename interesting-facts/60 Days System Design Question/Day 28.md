### You’re building a semantic search feature for a B2B SaaS product.

![[Pasted image 20260819102250.png]]

Bạn đang xây dựng một tính năng **semantic search (tìm kiếm ngữ nghĩa)** cho một sản phẩm B2B SaaS.

**Tập dữ liệu (corpus):** 4 triệu bài viết hỗ trợ (support articles), tài liệu (docs), và các ticket do người dùng tạo. Người dùng nhập các câu truy vấn bằng ngôn ngữ tự nhiên. Họ kỳ vọng kết quả trả về phải đạt chất lượng như Google — chứ không phải kiểu match từ khóa (keyword matching) truyền thống.

**Tech stack hiện tại:** PostgreSQL 15, Redis và Node.js backend. Team search báo cáo rằng các hàm `ILIKE` và extension `pg_trgm` đã "gánh không nổi". Giải pháp duy nhất lúc này là dùng **embeddings**. Vấn đề là bạn cần một nơi để lưu trữ và truy vấn các vector **1536 chiều** (từ mô hình `OpenAI ada-002`) với độ trễ **p99 dưới 100ms**.

* 4 triệu bản ghi (rows).
* Khoảng 24GB dữ liệu embedding thô (raw embeddings).
* Lưu lượng truy vấn (query volume): 300 req/s, và có thể tăng vọt (spike) lên tới 900 req/s vào cuối tuần.

**Bạn sẽ lưu trữ và truy vấn các vector này ở đâu?**

* **A) pgvector extension trên chính cơ sở dữ liệu PostgreSQL hiện tại** — lưu các vector vào một cột mới, truy vấn bằng toán tử độ tương đồng cosin `<->` (cosine similarity).
* **B) Pinecone** — vector database được quản lý hoàn toàn (fully managed), gói serverless, không cần tự vận hành hạ tầng (no infra).
* **C) Weaviate** — mã nguồn mở vector DB, tự host trên Kubernetes (self-hosted), kiểm soát toàn bộ quá trình lập chỉ mục (indexing).
* **D) Qdrant** — mã nguồn mở vector DB, viết bằng ngôn ngữ Rust, có bản self-hosted hoặc cloud, tối ưu hóa cho việc lọc dữ liệu (filtering) với **throughput** (thông lượng) cao.

Cả 4 giải pháp này đều đang được sử dụng rộng rãi trong môi trường production ở quy mô lớn. Nhưng chỉ có **một** giải pháp thực sự phù hợp với kịch bản này mà không vướng phải các chi phí ẩn (hidden costs) có thể "cắn" bạn đau đớn khi đạt ngưỡng 300 req/s.

Hãy chọn một — **A, B, C hay D** — và giải thích lý do tại sao. Toàn bộ phân tích chi tiết sẽ có ở phần bình luận.

Nếu đây là chủ đề tranh luận mà team bạn đang chuẩn bị đối mặt, hãy share ngay nhé. Những quyết định kiến trúc kiểu này rất khó để "quay xe" về sau.

**Lý do Qdrant là lựa chọn chiến thắng (Why D wins):**

![[Pasted image 20260819104409.png]]

Qdrant được thiết kế chuyên biệt (purpose-built) cho đúng loại workload này. Với phần lõi (core) viết bằng **Rust**, nó mang lại **latency (độ trễ) thấp** và **quản lý memory (bộ nhớ) ổn định** ngay cả dưới tải cao. Ở mức 300 request/giây (req/s), bạn cần một **index** có khả năng xử lý đồng thời các truy vấn **ANN (Approximate Nearest Neighbor - Tìm kiếm gần đúng nhất)** mà không bị suy giảm hiệu năng — và thuật toán **HNSW (Hierarchical Navigable Small World)** của Qdrant đã được tối ưu cực tốt cho việc này.

Tính năng "sát thủ" (killer feature) ở đây chính là **payload filtering (lọc dữ liệu đi kèm)**. Trong một sản phẩm B2B, người dùng chỉ tìm kiếm trong phạm vi workspace, tenant (khách hàng đa thuê bao) hoặc dòng sản phẩm của họ — chứ không phải tìm kiếm toàn cục (global). Qdrant xử lý cả **vector search** lẫn **metadata filter** chỉ trong **một vòng lặp/truy vấn duy nhất (one pass)**. Trong khi đó, mọi giải pháp khác đều ép bạn phải dùng **post-filtering (lọc hậu kỳ)**, làm giảm độ chính xác (**recall**) và cộng thêm các vòng lặp round-trip tốn kém.

Việc chạy dạng **self-hosted (tự host)** cho phép bạn toàn quyền kiểm soát các tham số của HNSW (`m`, `ef_construction`), cơ chế **memory mapping (ánh xạ bộ nhớ)**, và **on-disk indexing (đánh index trên ổ đĩa)** — những yếu tố cực kỳ sống còn khi tập dữ liệu (**corpus**) của bạn lớn hơn dung lượng RAM.

**Tại sao phương án A (pgvector) là một cái bẫy:**

`pgvector` rất tuyệt để khởi động dự án — với dưới ~500k vectors, đây thường là lựa chọn tối ưu vì bạn vốn đã sẵn có hệ thống PostgreSQL. Tuy nhiên, khi đạt mốc 4 triệu rows (bản ghi) và tải 300 req/s (yêu cầu mỗi giây), chỉ mục `HNSW` sẽ chạy trực tiếp trong *buffer pool* (vùng đệm) của Postgres, tranh chấp tài nguyên với các tác vụ OLTP (truy vấn giao dịch) của bạn. Độ trễ (latency) sẽ tăng theo hàm phi tuyến tính khi concurrency (độ đồng thời) cao. Việc chạy `VACUUM` trên một bảng chứa vector dung lượng lớn thực sự là một cơn ác mộng.

*Quy tắc ngón tay cái (Rule of thumb):* Dưới 500k vectors + concurrency thấp = dùng tốt. Vượt quá ngưỡng đó, bạn đang "vay nặng lãi" cho những rắc rối về sau.

**Tại sao phương án B (Pinecone) thất bại:**

Pinecone hoạt động ổn định và giúp team dev release sản phẩm rất nhanh. Nhưng mô hình pricing (chi phí) bắt đầu "cắn" rất đau khi duy trì mức 300 req/s — gói serverless tính tiền theo query unit (đơn vị truy vấn), khiến hóa đơn đội lên tới hàng nghìn đô-la mỗi tháng. Vấn đề lớn nữa là vendor lock-in (bị khóa chặt bởi nhà cung cấp): không hỗ trợ standard wire protocol (giao thức mạng chuẩn), đồng nghĩa với việc nếu muốn migrate (di cư dữ liệu), bạn phải viết lại toàn bộ ingestion pipeline (đường ống nạp dữ liệu) từ con số không.

*Phù hợp khi nào:* Tốc độ đưa sản phẩm ra thị trường (time-to-market) quan trọng hơn chi phí, và lượng query dưới ~50 req/s.

**Tại sao phương án C (Weaviate) thất bại:**

Weaviate là một giải pháp solid (vững chắc) với tính năng hybrid search (tìm kiếm lai: BM25 + vector) rất tốt và hỗ trợ multi-modal (đa phương thức). Dù vậy, Kubernetes footprint (dấu chân tài nguyên K8s) của nó lại nặng nề hơn Qdrant đối với use case này. Với một team chưa sẵn vận hành K8s cho tầng vector, operational overhead (chi phí vận hành/quản trị) phát sinh là rất lớn. Weaviate thực sự tỏa sáng ở các bài toán tìm kiếm đa phương thức hoặc semantic graph relationships (quan hệ đồ thị ngữ nghĩa) — còn đối với pure dense vector search (tìm kiếm thuần túy vector dày đặc) kèm filtering (lọc), Qdrant vẫn là cái tên tinh gọn hơn.
