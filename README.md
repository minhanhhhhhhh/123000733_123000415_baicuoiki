# Đại Học Lạc Hồng — Bài Cuối Môn Xử Lý Ngôn Ngữ Tự Nhiên (NLP)

**Thông tin sinh viên:**

| STT | Mã Số Sinh Viên |         Họ và Tên             |
|-----|-----------------|------------------------------ |
| 1   | 123000733       |    Vũ Minh Anh                |
| 2   | 123000415       |    Phạm Thùy Yến Phương       |

**Đề tài đã chọn:** _(ghi tên đề tài ở đây)_

---

## Danh sách đề tài gợi ý

> Chi tiết từng đề tài xem tại [DE-TAI.md](DE-TAI.md)

| # | Đề tài | Công nghệ gợi ý |
|---|--------|-----------------|
| 1 | Phân tích cảm xúc (Sentiment Analysis) | PhoBERT, scikit-learn, underthesea |
| 2 | Tóm tắt văn bản tự động (Text Summarization) | sumy, BART, VietAI/vit5 |
| 3 | Nhận dạng thực thể tên (NER) | spaCy, underthesea, PhoBERT |
| 4 | Chatbot hỏi đáp theo tài liệu (Document QA) | LangChain, FAISS, sentence-transformers |
| 5 | Phân loại văn bản (Text Classification) | TF-IDF, fastText, PhoBERT |
| 6 | So sánh độ tương đồng ngữ nghĩa (Semantic Similarity) | sentence-transformers, SBERT |
| 7 | Phân cụm chủ đề văn bản (Topic Modeling) | BERTopic, LDA, KMeans |
| 8 | Trích xuất từ khoá (Keyword Extraction) | KeyBERT, YAKE, RAKE |

---

## Mô tả dự án

# Công cụ Tóm Tắt Văn Bản Tự Động 

**Ứng dụng Web tóm tắt văn bản tiếng Việt và tiếng Anh không cần API**

---

## Giới thiệu

Đây là **ứng dụng Streamlit** hỗ trợ tóm tắt văn bản một cách nhanh chóng và hiệu quả. Dự án được thực hiện trong khuôn khổ **Bài Cuối Môn Xử Lý Ngôn Ngữ Tự Nhiên (NLP)**

Ứng dụng cho phép người dùng:
- Dán trực tiếp văn bản
- Tải lên file **PDF, DOCX, TXT**
- Nhập **link URL** hoặc **Google Docs**

Ứng dụng sử dụng các phương pháp tóm tắt trích xuất (**Extractive Summarization**) hiện đại, không phụ thuộc vào API bên thứ ba.

---

## Tính năng nổi bật

- **Hỗ trợ đa nguồn đầu vào**: Text, PDF, DOCX, TXT, URL, Google Docs
- **Nhiều thuật toán tóm tắt**:
  - TF-IDF
  - TextRank
  - Sumy (LSA, LexRank, Luhn, TextRank)
  - RAKE (trích xuất từ khóa)
- **Hỗ trợ tiếng Việt và tiếng Anh** (sử dụng underthesea cho tiếng Việt)
- **Giao diện đẹp, thân thiện**, responsive với Streamlit
- **Thống kê**: số từ, số câu, tỷ lệ nén
- **Từ khóa chính** được trích xuất tự động
- **Không cần API key** (hoàn toàn offline/local)

---

## Công nghệ sử dụng

- **Python**
- **Streamlit** (framework giao diện)
- **underthesea** (tokenization tiếng Việt)
- **pypdf / pdfminer** (đọc PDF)
- **python-docx** (đọc DOCX)
- **BeautifulSoup4** (parse web)
- **sumy, rake-nltk** (các thuật toán tóm tắt)
- **scikit-learn / numpy** (hỗ trợ tính toán)

---

---

## Hướng dẫn cài đặt & chạy

> Xem chi tiết tại [SETUP.md](SETUP.md)

```bash
# 1. Tạo môi trường ảo
python3 -m venv venv

# 2. Kích hoạt môi trường ảo
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Chạy ứng dụng
streamlit run app.py
```

---

## Các nhiệm vụ cần hoàn thành trong `app.py`

_(Sinh viên liệt kê các TODO / nhiệm vụ cụ thể theo đề tài đã chọn)_

- [ ] Nhiệm vụ 1: ...
- [ ] Nhiệm vụ 2: ...
- [ ] Nhiệm vụ 3: ...
- [ ] Nhiệm vụ 4: Xử lý lỗi khi input rỗng
- [ ] Nhiệm vụ 5: Export kết quả (CSV / PDF / ...)
- [ ] Nhiệm vụ 6: Trực quan hoá kết quả (biểu đồ, highlight, word cloud...)

---

## Công nghệ sử dụng

- Python
- Streamlit
- _(Thêm các thư viện theo đề tài đã chọn)_

---

## Demo

_(Thêm screenshot hoặc link Streamlit Cloud sau khi deploy)_

---

## Tài liệu tham khảo

_(Liệt kê các nguồn tài liệu, dataset, paper đã sử dụng)_
