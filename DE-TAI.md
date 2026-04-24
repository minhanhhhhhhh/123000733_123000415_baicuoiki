# Đề Tài Cuối Khoá — Môn Xử Lý Ngôn Ngữ Tự Nhiên (NLP)

---

## CÁC ĐỀ TÀI GỢI Ý

Các đề tài dưới đây phù hợp với sinh viên cuối khoá môn NLP, có thể deploy lên **Streamlit Cloud** để nộp bài và thuyết trình trực tiếp trước giáo viên.

---

### 1. Phân tích cảm xúc (Sentiment Analysis)

**Mô tả:** Xây dựng hệ thống nhận đầu vào là đoạn văn bản (review sản phẩm, bình luận mạng xã hội, đánh giá phim...) và phân loại cảm xúc: tích cực / tiêu cực / trung lập.

**Công nghệ gợi ý:**
- `PhoBERT` hoặc `BERT` cho tiếng Việt
- `scikit-learn` + `TF-IDF` cho baseline
- `underthesea` để tiền xử lý tiếng Việt

**Dữ liệu gợi ý:**
- UIT-VSFC (Vietnamese Students' Feedback Corpus)
- VLSP 2016 Sentiment Dataset

**Lĩnh vực & Ứng dụng liên quan:**
- **Thương mại điện tử:** Theo dõi đánh giá sản phẩm trên Shopee, Tiki, Lazada để cải thiện chất lượng dịch vụ
- **Marketing & truyền thông xã hội:** Đo lường phản ứng dư luận về thương hiệu trên Facebook, TikTok
- **Tài chính — chứng khoán:** Phân tích tâm lý thị trường (market sentiment) hỗ trợ quyết định đầu tư
- **Giáo dục & nhân sự:** Khảo sát mức độ hài lòng của sinh viên hoặc nhân viên

**Demo Streamlit:** Nhập văn bản → hiển thị nhãn cảm xúc + biểu đồ confidence score + word cloud theo cảm xúc.

---

### 2. Tóm tắt văn bản tự động (Text Summarization)

**Mô tả:** Xây dựng công cụ tóm tắt bài báo hoặc tài liệu dài thành đoạn ngắn gọn.

**Công nghệ gợi ý:**
- Extractive: `sumy`, `gensim`, `RAKE`
- Abstractive: `facebook/bart-large-cnn`, `VietAI/vit5-base-vietnews-summarization`

**Dữ liệu gợi ý:**
- VnDS (Vietnamese Document Summarization)
- VietNews dataset

**Lĩnh vực & Ứng dụng liên quan:**
- **Báo chí & truyền thông:** Tóm tắt tin tức hàng ngày cho app đọc báo (VnExpress, Tuổi Trẻ)
- **Giáo dục:** Tóm tắt bài giảng, tài liệu học tập cho sinh viên
- **Pháp lý:** Tóm tắt hợp đồng, văn bản pháp luật cho luật sư
- **Y tế:** Tạo bản tóm tắt hồ sơ bệnh án, báo cáo lâm sàng

**Demo Streamlit:** Dán đoạn báo → hiển thị tóm tắt + tỷ lệ nén + so sánh song song văn bản gốc và tóm tắt.

---

### 3. Nhận dạng thực thể tên (Named Entity Recognition — NER)

**Mô tả:** Hệ thống nhận dạng và gán nhãn các thực thể trong văn bản như NGƯỜI, TỔ CHỨC, ĐỊA ĐIỂM, NGÀY GIỜ.

**Công nghệ gợi ý:**
- `spaCy` với mô hình NER tiếng Anh
- `underthesea` cho NER tiếng Việt
- `PhoBERT` fine-tuned trên VLSP NER dataset

**Dữ liệu gợi ý:**
- VLSP 2016/2018 NER Dataset
- CoNLL-2003 (tiếng Anh)

**Lĩnh vực & Ứng dụng liên quan:**
- **An ninh — tình báo:** Trích xuất tên người, tổ chức, địa điểm từ tin tức để xây dựng đồ thị tri thức (knowledge graph)
- **Y tế:** Nhận dạng tên thuốc, bệnh, triệu chứng từ hồ sơ y tế
- **Tài chính — ngân hàng:** Tự động trích xuất thông tin từ hóa đơn, hợp đồng (tên công ty, ngày, số tiền)
- **Tìm kiếm thông tin:** Hỗ trợ hệ thống tìm kiếm thông minh, lập chỉ mục tự động

**Demo Streamlit:** Nhập đoạn văn → highlight màu sắc từng loại thực thể (dùng `spacy.displacy` hoặc `st.markdown` với HTML).

---

### 4. Chatbot hỏi đáp theo tài liệu (Document QA Chatbot)

**Mô tả:** Cho phép người dùng upload tài liệu (PDF/TXT), sau đó đặt câu hỏi và nhận câu trả lời dựa trên nội dung tài liệu.

**Công nghệ gợi ý:**
- `LangChain` + `FAISS` (vector store)
- `sentence-transformers` (tạo embedding)
- OpenAI API hoặc mô hình local (Ollama, Mistral)

**Lĩnh vực & Ứng dụng liên quan:**
- **Giáo dục (EdTech):** Chatbot tư vấn tuyển sinh dựa trên đề cương, quy chế của trường
- **Doanh nghiệp — chăm sóc khách hàng:** Trợ lý ảo nội bộ hỏi đáp về chính sách HR, quy trình công ty
- **Hành chính công:** Chatbot hỗ trợ tra cứu văn bản pháp luật, thủ tục hành chính
- **Kỹ thuật:** Hệ thống hỏi đáp tài liệu kỹ thuật (technical documentation)

**Demo Streamlit:** Upload file → nhập câu hỏi → hiển thị câu trả lời + đoạn văn bản nguồn được trích dẫn.

---

### 5. Phân loại văn bản (Text Classification)

**Mô tả:** Phân loại tin tức theo chủ đề (thể thao, kinh tế, giải trí, pháp luật...) hoặc phát hiện spam/tin giả.

**Công nghệ gợi ý:**
- `TF-IDF` + `Logistic Regression` / `SVM` (baseline)
- `fastText`, `BERT`, `PhoBERT` (mô hình nâng cao)

**Dữ liệu gợi ý:**
- VNTC (Vietnamese Text Categorization)
- 20 Newsgroups (tiếng Anh)

**Lĩnh vực & Ứng dụng liên quan:**
- **Truyền thông & báo chí:** Tự động phân loại tin tức theo chuyên mục (thể thao, kinh tế, giải trí...)
- **An toàn thông tin:** Phát hiện tin giả (fake news detection), lọc spam email
- **Thương mại điện tử:** Phân loại phản hồi khách hàng theo mức độ ưu tiên (khẩn cấp, bình thường)
- **Mạng xã hội:** Lọc nội dung độc hại, bình luận vi phạm (content moderation)

**Demo Streamlit:** Nhập đoạn văn bản → hiển thị nhãn phân loại + biểu đồ xác suất từng chủ đề.

---

### 6. So sánh độ tương đồng ngữ nghĩa (Semantic Similarity)

**Mô tả:** Đo lường mức độ tương đồng về nghĩa giữa hai câu hoặc đoạn văn.

**Công nghệ gợi ý:**
- `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`)
- `PhoBERT` fine-tuned STS
- Cosine similarity + SBERT

**Dữ liệu gợi ý:**
- STS Benchmark
- SNLI, MultiNLI

**Lĩnh vực & Ứng dụng liên quan:**
- **Tuyển dụng (HR Tech):** Matching CV ứng viên với mô tả công việc (job matching)
- **Giáo dục:** Phát hiện đạo văn (plagiarism detection) trong bài luận sinh viên
- **Hỗ trợ khách hàng:** Tìm kiếm câu hỏi tương tự trong hệ thống FAQ
- **Gợi ý nội dung:** Gợi ý bài viết, sản phẩm liên quan dựa trên nội dung

**Demo Streamlit:** Nhập 2 câu → hiển thị điểm tương đồng (0-1) + biểu đồ heatmap ma trận similarity cho nhiều câu.

---

### 7. Phân cụm chủ đề văn bản (Topic Modeling / Clustering)

**Mô tả:** Tự động khám phá các chủ đề tiềm ẩn trong tập văn bản lớn mà không cần nhãn.

**Công nghệ gợi ý:**
- `LDA` (Gensim) + `pyLDAvis`
- `BERTopic` (hiện đại, dễ visualize)
- `KMeans` + `TF-IDF`

**Dữ liệu gợi ý:**
- Tập báo tự thu thập hoặc scrape từ VnExpress, Tuổi Trẻ
- 20 Newsgroups (tiếng Anh)

**Lĩnh vực & Ứng dụng liên quan:**
- **Nghiên cứu thị trường:** Phân tích xu hướng dư luận trên mạng xã hội (social listening)
- **Khoa học:** Khám phá chủ đề nghiên cứu nổi bật từ tập hợp bài báo khoa học
- **Chăm sóc khách hàng:** Phân nhóm ticket hỗ trợ để phát hiện vấn đề phổ biến
- **Khảo sát:** Phân tích nội dung khảo sát mở (open-ended survey) không cần gán nhãn trước

**Demo Streamlit:** Upload tập văn bản → hiển thị danh sách chủ đề + scatter plot màu sắc theo cụm + từ khoá đặc trưng mỗi chủ đề.

---

### 8. Trích xuất từ khoá (Keyword Extraction)

**Mô tả:** Trích xuất các từ khoá và cụm từ quan trọng nhất từ một đoạn văn bản.

**Công nghệ gợi ý:**
- `KeyBERT` (BERT-based)
- `YAKE` (unsupervised, đa ngôn ngữ)
- `RAKE` (rule-based, dễ implement)

**Lĩnh vực & Ứng dụng liên quan:**
- **SEO & Digital Marketing:** Tự động gắn tag/từ khoá cho bài viết blog, báo chí để tối ưu SEO
- **Xuất bản & thư viện:** Tạo chỉ mục (index) tự động cho sách, tài liệu thư viện
- **Nghiên cứu khoa học:** Trích xuất từ khoá từ abstract bài báo để phân loại và tìm kiếm
- **Doanh nghiệp:** Hỗ trợ tóm tắt nhanh nội dung cuộc họp từ biên bản

**Demo Streamlit:** Nhập đoạn văn → hiển thị danh sách từ khoá kèm điểm quan trọng + word cloud.

---