# Đại Học Lạc Hồng — Bài Cuối Môn Xử Lý Ngôn Ngữ Tự Nhiên (NLP)

**Thông tin sinh viên:**

| STT | Mã Số Sinh Viên |         Họ và Tên             |
|-----|-----------------|------------------------------ |
| 1   | 123000733       |    Vũ Minh Anh                |
| 2   | 123000415       |    Phạm Thùy Yến Phương       |

**Đề tài đã chọn:** 
| 2 | Tóm tắt văn bản tự động (Text Summarization) | sumy, BART, VietAI/vit5 |
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

- [ ] Nhiệm vụ 1: Cải thiện chất lượng tóm tắt tiếng Việt (xử lý dấu, stopwords tốt hơn)
- [ ] Nhiệm vụ 2: Tích hợp underthesea cho tiếng Việt
- [ ] Nhiệm vụ 3: Đọc file PDF, DOCX, TXT
- [ ] Nhiệm vụ 4: Tích hợp tóm tắt TF-IDF & TextRank
- [ ] Nhiệm vụ 5: Hỗ trợ tóm tắt qua URL
- [ ] Nhiệm vụ 6: Thêm chức năng tóm tắt theo tỷ lệ % hoặc số câu chỉ định
- [ ] Nhiệm vụ 7: Thêm nút **Download** kết quả tóm tắt
- [ ] Nhiệm vụ 8: Triển khai tính năng **tóm tắt nhiều tài liệu cùng lúc** (Multi-document)
- [ ] NHiệm vụ 9: Hiển thị thống kê và từ khóa
  

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
