"""
Công cụ Tóm Tắt Văn Bản - Không cần API
==========================================
Hỗ trợ: Dán văn bản | Tải file (PDF, DOCX, TXT) | Link URL / Google Docs

Cài đặt:
    pip install -r requirements.txt
    streamlit run app.py
"""

import re
import math
import io
import urllib.request
import urllib.parse
from collections import Counter

import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# CẤU HÌNH TRANG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Tóm Tắt Văn Bản",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .main .block-container { padding-top: 2rem; max-width: 1100px; }
  .stTextArea textarea   { font-size: 14px; line-height: 1.75; }

  /* Tabs nguồn nhập */
  div[data-baseweb="tab-list"] { gap: 4px; }
  div[data-baseweb="tab"]      { border-radius: 8px 8px 0 0; font-size: 14px; }

  /* Thẻ thống kê */
  .metric-row { display:flex; gap:10px; margin:1rem 0; flex-wrap:wrap; }
  .metric-card {
      background:#f5f5f3; border-radius:10px;
      padding:14px 18px; text-align:center; flex:1; min-width:90px;
  }
  .metric-val   { font-size:22px; font-weight:600; color:#1D9E75; }
  .metric-label { font-size:11px; color:#888; text-transform:uppercase;
                  letter-spacing:.05em; margin-top:2px; }

  /* Thanh nén */
  .bar-wrap { background:#e8e8e4; border-radius:4px; height:8px;
              margin:4px 0 14px; overflow:hidden; }
  .bar-fill { background:#1D9E75; height:100%; border-radius:4px; }

  /* Hộp kết quả */
  .result-box {
      background:#f0faf6; border:1px solid #9FE1CB; border-radius:10px;
      padding:1.2rem 1.5rem; font-size:14px; line-height:1.85;
      white-space:pre-wrap; color:#1a1a18;
  }
  .original-box {
      background:#fafaf8; border:1px solid #e0e0dc; border-radius:10px;
      padding:1.2rem 1.5rem; font-size:13px; line-height:1.75;
      max-height:300px; overflow-y:auto; color:#444;
  }

  /* Từ khoá */
  .kw-tag {
      display:inline-block; background:#1D9E75; color:#fff;
      border-radius:20px; padding:3px 11px; font-size:12px;
      font-weight:500; margin:3px 4px 3px 0;
  }

  /* Badge nguồn */
  .source-badge {
      display:inline-block; background:#e8f5f0; color:#0F6E56;
      border:1px solid #9FE1CB; border-radius:6px;
      padding:4px 10px; font-size:12px; font-weight:500; margin-bottom:10px;
  }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TIỆN ÍCH VĂN BẢN
# ══════════════════════════════════════════════════════════════════════════════

def count_words(text: str) -> int:
    return len(text.strip().split()) if text.strip() else 0


def split_sentences(text: str) -> list[str]:
    raw = re.split(r'(?<=[.!?…])\s+', text.strip())
    return [s.strip() for s in raw if len(s.strip()) > 10]


def tokenize(text: str) -> list[str]:
    try:
        from underthesea import word_tokenize
        return word_tokenize(text, format="text").lower().split()
    except ImportError:
        pass
    return re.sub(r'[^\w\s]', ' ', text.lower()).split()


VI_STOPWORDS = {
    "và","là","của","có","được","trong","này","cho","với","các","một","những",
    "đã","sẽ","không","đến","về","tại","từ","theo","ra","vào","thì","hay",
    "cũng","như","bởi","vì","nên","nếu","khi","mà","để","đó","lại","lên",
    "xuống","trên","dưới","sau","trước","qua","đây","ở","đang","hơn","rất",
}
EN_STOPWORDS = {
    "the","a","an","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "must","to","of","in","on","at","by","for","with","about","into",
    "through","during","before","after","from","up","down","out","and",
    "but","or","nor","not","only","same","than","too","very","just","as",
    "until","while","i","me","my","we","our","you","your","he","she","it",
    "they","them","their","this","that","these","those","which","who",
}
ALL_STOPWORDS = VI_STOPWORDS | EN_STOPWORDS


def clean_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in ALL_STOPWORDS and len(t) > 1]


# ══════════════════════════════════════════════════════════════════════════════
# ĐỌC NỘI DUNG TỪ NHIỀU NGUỒN
# ══════════════════════════════════════════════════════════════════════════════

def read_txt(file_bytes: bytes) -> str:
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="replace")


def read_pdf(file_bytes: bytes) -> str:
    """Đọc PDF dùng pypdf (ưu tiên) hoặc pdfminer."""
    # Thử pypdf trước
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages  = [p.extract_text() or "" for p in reader.pages]
        text   = "\n".join(pages).strip()
        if text:
            return text
    except ImportError:
        pass

    # Fallback: pdfminer
    try:
        from pdfminer.high_level import extract_text as pm_extract
        text = pm_extract(io.BytesIO(file_bytes))
        if text and text.strip():
            return text.strip()
    except ImportError:
        pass

    return "⚠️ Không thể đọc PDF. Cài: pip install pypdf   hoặc   pip install pdfminer.six"


def read_docx(file_bytes: bytes) -> str:
    """Đọc DOCX dùng python-docx."""
    try:
        import docx
        doc  = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        return "⚠️ Không thể đọc DOCX. Cài: pip install python-docx"


def gdoc_export_url(url: str) -> str | None:
    """
    Chuyển link Google Docs sang URL export plain-text.
    Ví dụ:
      https://docs.google.com/document/d/<ID>/edit
      → https://docs.google.com/document/d/<ID>/export?format=txt
    """
    m = re.search(r'docs\.google\.com/document/d/([^/?#]+)', url)
    if m:
        doc_id = m.group(1)
        return f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    return None


def fetch_url_text(url: str) -> tuple[str, str]:
    """
    Tải nội dung văn bản từ URL.
    Trả về (text, source_label).
    Hỗ trợ: Google Docs, trang web thông thường.
    """
    url = url.strip()

    # Google Docs → export txt
    gdoc = gdoc_export_url(url)
    if gdoc:
        try:
            req  = urllib.request.Request(gdoc, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            raw  = resp.read()
            return read_txt(raw), "Google Docs"
        except Exception as e:
            return f"⚠️ Không tải được Google Docs: {e}", "Lỗi"

    # Trang web thông thường — dùng BeautifulSoup nếu có, fallback regex
    try:
        req  = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        raw  = resp.read()
        html = raw.decode("utf-8", errors="replace")
    except Exception as e:
        return f"⚠️ Không tải được URL: {e}", "Lỗi"

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Xoá script, style, nav
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text, urllib.parse.urlparse(url).netloc
    except ImportError:
        pass

    # Fallback: strip HTML tags bằng regex
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s{2,}', '\n', text).strip()
    return text, urllib.parse.urlparse(url).netloc


# ══════════════════════════════════════════════════════════════════════════════
# THUẬT TOÁN TÓM TẮT
# ══════════════════════════════════════════════════════════════════════════════

def tfidf_summarize(text: str, num_sentences: int) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return text
    tokenized = [clean_tokens(tokenize(s)) for s in sentences]
    N  = len(sentences)
    df: Counter = Counter()
    for tokens in tokenized:
        for t in set(tokens):
            df[t] += 1
    idf    = {t: math.log((N + 1) / (cnt + 1)) + 1 for t, cnt in df.items()}
    scores = []
    for tokens in tokenized:
        if not tokens:
            scores.append(0.0); continue
        tf    = Counter(tokens)
        score = sum((tf[t] / len(tokens)) * idf.get(t, 0) for t in tf)
        scores.append(score)
    ranked  = sorted(range(N), key=lambda i: scores[i], reverse=True)
    top_idx = sorted(ranked[:num_sentences])
    return " ".join(sentences[i] for i in top_idx)


def _sim(s1: list[str], s2: list[str]) -> float:
    a, b = set(s1), set(s2)
    if not a or not b:
        return 0.0
    return len(a & b) / (math.log(len(a) + 1) + math.log(len(b) + 1) + 1e-9)


def textrank_summarize(text: str, num_sentences: int,
                       damping: float = 0.85, iterations: int = 30) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return text
    tokenized = [clean_tokens(tokenize(s)) for s in sentences]
    N   = len(sentences)
    mat = [[_sim(tokenized[i], tokenized[j]) if i != j else 0.0
            for j in range(N)] for i in range(N)]
    for i in range(N):
        row_sum = sum(mat[i])
        if row_sum:
            mat[i] = [v / row_sum for v in mat[i]]
    scores = [1.0 / N] * N
    for _ in range(iterations):
        scores = [
            (1 - damping) / N + damping * sum(mat[j][i] * scores[j] for j in range(N))
            for i in range(N)
        ]
    ranked  = sorted(range(N), key=lambda i: scores[i], reverse=True)
    top_idx = sorted(ranked[:num_sentences])
    return " ".join(sentences[i] for i in top_idx)


def sumy_summarize(text: str, num_sentences: int, algorithm: str = "LSA") -> str:
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers   import Tokenizer
        from sumy.summarizers.lsa       import LsaSummarizer
        from sumy.summarizers.lex_rank  import LexRankSummarizer
        from sumy.summarizers.luhn      import LuhnSummarizer
        from sumy.summarizers.text_rank import TextRankSummarizer
        from sumy.nlp.stemmers          import Stemmer
        from sumy.utils                 import get_stop_words
    except ImportError:
        return "⚠️ Chưa cài sumy. Chạy: pip install sumy"
    MAP    = {"LSA": LsaSummarizer, "LexRank": LexRankSummarizer,
              "Luhn": LuhnSummarizer, "TextRank": TextRankSummarizer}
    lang   = "english"
    parser = PlaintextParser.from_string(text, Tokenizer(lang))
    stemmer= Stemmer(lang)
    sumr   = MAP.get(algorithm, LsaSummarizer)(stemmer)
    sumr.stop_words = get_stop_words(lang)
    return " ".join(str(s) for s in sumr(parser.document, num_sentences))


def rake_keywords(text: str, top_n: int = 15) -> list[str]:
    try:
        from rake_nltk import Rake
        import nltk
        for res in ("corpora/stopwords", "tokenizers/punkt_tab"):
            try:    nltk.data.find(res)
            except: nltk.download(res.split("/")[1], quiet=True)
        r = Rake()
        r.extract_keywords_from_text(text)
        return r.get_ranked_phrases()[:top_n]
    except ImportError:
        pass
    # Fallback thuần Python
    words = re.findall(r'\b\w+\b', text.lower())
    phrases, current = [], []
    for w in words:
        if w in ALL_STOPWORDS or not w.isalpha():
            if current: phrases.append(" ".join(current)); current = []
        else:
            current.append(w)
    if current: phrases.append(" ".join(current))
    freq: Counter = Counter(phrases)
    deg:  Counter = Counter()
    for ph in phrases:
        for w in ph.split(): deg[w] += len(ph.split())
    scores = {ph: sum(deg[w] / (freq[w] or 1) for w in ph.split()) for ph in freq}
    return sorted(scores, key=scores.get, reverse=True)[:top_n]


# ══════════════════════════════════════════════════════════════════════════════
# VĂN BẢN MẪU
# ══════════════════════════════════════════════════════════════════════════════
EXAMPLES = {
    "📰 Bài báo (Báo chí)": (
        "Hà Nội, ngày 14 tháng 5 năm 2026 - Chính phủ Việt Nam vừa công bố gói đầu tư 50.000 tỷ đồng "
        "nhằm phát triển hạ tầng giao thông tại các tỉnh miền Trung trong giai đoạn 2026-2030. "
        "Đây được xem là một trong những gói đầu tư lớn nhất từ trước đến nay dành cho khu vực này, "
        "với mục tiêu kết nối các tỉnh từ Thanh Hóa đến Bình Thuận qua hệ thống đường cao tốc hiện đại. "
        "Theo Bộ Giao thông Vận tải, dự án sẽ bao gồm mở rộng tuyến đường cao tốc Bắc-Nam dài hơn 800 km, "
        "xây dựng thêm 12 nút giao thông mới, và cải tạo hệ thống cầu vượt tại các điểm xung yếu. "
        "Dự kiến đến năm 2028, các tuyến đường chính sẽ hoàn thành và đưa vào sử dụng. "
        "Nhiều chuyên gia kinh tế cho rằng gói đầu tư này còn tạo ra khoảng 200.000 việc làm trực tiếp "
        "và gián tiếp trong suốt thời gian thi công. "
        "Bộ trưởng Bộ Giao thông Vận tải cam kết áp dụng cơ chế giám sát chặt chẽ để đảm bảo minh bạch."
    ),
    "⚖️ Hợp đồng (Pháp lý)": (
        "ĐIỀU 1. CÁC BÊN THAM GIA HỢP ĐỒNG. Hợp đồng này được ký kết giữa Công ty TNHH Phát Triển "
        "Phần Mềm Sao Mai và Công ty Cổ phần Thương Mại Bình Minh. "
        "ĐIỀU 2. PHẠM VI DỊCH VỤ. Bên Cung Cấp Dịch Vụ cam kết triển khai hệ thống quản lý bán hàng tích hợp "
        "bao gồm phần mềm ERP tùy chỉnh cho 3 chi nhánh, module quản lý kho hàng thời gian thực, "
        "ứng dụng di động cho nhân viên kinh doanh và hệ thống báo cáo tự động. "
        "Thời gian triển khai không quá 6 tháng kể từ ngày ký hợp đồng. "
        "ĐIỀU 3. GIÁ TRỊ HỢP ĐỒNG. Tổng giá trị hợp đồng là 1.800.000.000 đồng. "
        "Thanh toán theo 3 đợt: 30% khi ký hợp đồng, 40% khi hoàn thành giai đoạn 1, "
        "30% khi nghiệm thu toàn bộ hệ thống. "
        "ĐIỀU 4. BẢO HÀNH. Bên Cung Cấp Dịch Vụ bảo hành hệ thống trong 24 tháng kể từ ngày nghiệm thu. "
        "ĐIỀU 5. BẢO MẬT. Cả hai bên cam kết bảo mật toàn bộ thông tin trong thời gian 5 năm."
    ),
    "🏥 Hồ sơ y tế": (
        "BÁO CÁO THĂM KHÁM LÂM SÀNG ngày 14 tháng 5 năm 2026. "
        "Bệnh nhân Nguyễn Văn A, 58 tuổi, nam giới, nhập viện vì đau ngực trái dữ dội kèm khó thở. "
        "Bệnh nhân có tiền sử tăng huyết áp 10 năm và đái tháo đường type 2 được chẩn đoán 5 năm trước. "
        "Kết quả xét nghiệm: Troponin I tăng cao 2.8 ng/mL, CK-MB tăng 45 U/L. "
        "ECG ghi nhận ST chênh lên ở các chuyển đạo II, III, aVF gợi ý nhồi máu cơ tim cấp. "
        "Siêu âm tim cho thấy EF 45%, giảm vận động vùng thành sau-dưới. "
        "Huyết áp 165/100 mmHg, đường huyết 12.3 mmol/L, HbA1c 8.2%. "
        "Chẩn đoán: STEMI vùng thành sau-dưới, tăng huyết áp và đái tháo đường type 2 kiểm soát kém. "
        "Hướng xử trí: can thiệp mạch vành qua da cấp cứu, Aspirin và Ticagrelor liều tải, "
        "Heparin tiêm tĩnh mạch, Nitroglycerin truyền tĩnh mạch kiểm soát huyết áp."
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("⚙️ Cài đặt")

    # ── Lĩnh vực ──────────────────────────────────────────────────────────────
    st.subheader("📋 Lĩnh vực")
    domain = st.selectbox(
        "Chọn lĩnh vực",
        ["Tổng quát", "Báo chí", "Giáo dục", "Pháp lý", "Y tế"],
        index=0,
        help="Thêm tiêu đề lĩnh vực vào đầu bản tóm tắt",
    )

    st.divider()

    # ── Số câu tóm tắt ────────────────────────────────────────────────────────
    st.subheader("📐 Số câu tóm tắt")
    num_sentences = int(st.number_input(
        "Số câu (1 – 20)",
        min_value=1, max_value=20, value=4, step=1,
        help="Số câu được giữ lại trong bản tóm tắt",
    ))
    sent_min, sent_max = 1, 20  # dùng cho caption ở main UI

    st.divider()

    # ── Thuật toán ────────────────────────────────────────────────────────────
    st.subheader("🔬 Thuật toán")
    algorithm = st.selectbox(
        "Chọn thuật toán",
        ["TF-IDF (built-in)", "TextRank (built-in)",
         "Sumy — LSA", "Sumy — LexRank", "Sumy — Luhn", "Sumy — TextRank"],
        index=0,
        help="TF-IDF và TextRank chạy ngay, không cần cài thêm",
    )

    st.divider()

    # ── So sánh phương pháp ───────────────────────────────────────────────────
    st.subheader("🔬 So sánh phương pháp")
    compare_all = st.checkbox("Bật chế độ so sánh", value=False,
                              help="Chạy và so sánh nhiều thuật toán cùng lúc")
    if compare_all:
        st.caption("Các thuật toán extractive:")
        use_sumy   = st.checkbox("Sumy (LSA / LexRank / Luhn / TextRank)", value=True)
        sumy_algo  = st.selectbox("Thuật toán Sumy", ["LSA", "LexRank", "Luhn", "TextRank"]) if use_sumy else "LSA"
        use_gensim = st.checkbox("Gensim TextRank", value=False)
        use_rake   = st.checkbox("RAKE Keywords", value=True)
        extract_ratio = st.slider("Tỷ lệ trích xuất", 0.10, 0.50, 0.30, 0.05,
                                  help="Tỷ lệ câu giữ lại (cho Sumy/Gensim)")
    else:
        use_sumy, use_gensim, use_rake = False, False, True
        sumy_algo, extract_ratio       = "LSA", 0.30

    st.divider()

    # ── RAKE ──────────────────────────────────────────────────────────────────
    st.subheader("🏷️ Từ khoá RAKE")
    show_rake = st.checkbox("Hiển thị từ khoá", value=True)
    rake_top  = st.slider("Số từ khoá", 5, 20, 10) if show_rake else 10
    if compare_all:
        show_rake = use_rake

    st.divider()
    st.info(
        "🟢 **Không cần API key**\n\n"
        "**Built-in** (chạy ngay):\n"
        "- TF-IDF · TextRank · RAKE\n\n"
        "**Tuỳ chọn** (cần cài):\n"
        "`pip install sumy`\n"
        "`pip install pypdf` *(PDF)*\n"
        "`pip install python-docx` *(DOCX)*\n"
        "`pip install beautifulsoup4` *(web)*\n"
        "`pip install underthesea` *(Tiếng Việt)*"
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════
st.title("◈ Tóm Tắt Văn Bản")
st.caption("TF-IDF · TextRank · Sumy · RAKE · Hỗ trợ File PDF / DOCX / TXT · Link URL · Google Docs")

# ── 3 tab nguồn đầu vào ───────────────────────────────────────────────────────
tab_text, tab_file, tab_url = st.tabs([
    "✏️  Dán văn bản",
    "📁  Tải file lên",
    "🔗  Link URL / Google Docs",
])

input_text  = ""
source_label = ""

# ── TAB 1: Dán văn bản ────────────────────────────────────────────────────────
with tab_text:
    example_choice = st.selectbox(
        "Tải văn bản mẫu:",
        ["— chọn mẫu —"] + list(EXAMPLES.keys()),
        key="ex",
    )
    default_text = EXAMPLES.get(example_choice, "") if example_choice != "— chọn mẫu —" else ""
    pasted = st.text_area(
        "Văn bản đầu vào",
        value=default_text,
        height=240,
        placeholder="Dán bài báo, tài liệu, hợp đồng... vào đây (Tiếng Việt hoặc Tiếng Anh)",
        key="paste_area",
    )
    if pasted.strip():
        input_text   = pasted
        source_label = "Văn bản dán"

# ── TAB 2: Tải file ───────────────────────────────────────────────────────────
with tab_file:
    uploaded = st.file_uploader(
        "Chọn file cần tóm tắt",
        type=["txt", "pdf", "docx"],
        help="Hỗ trợ: .txt · .pdf (cần pypdf) · .docx (cần python-docx)",
    )
    if uploaded is not None:
        file_bytes = uploaded.read()
        ext        = uploaded.name.rsplit(".", 1)[-1].lower()

        with st.spinner(f"Đang đọc file {uploaded.name}..."):
            if ext == "txt":
                extracted = read_txt(file_bytes)
            elif ext == "pdf":
                extracted = read_pdf(file_bytes)
            elif ext == "docx":
                extracted = read_docx(file_bytes)
            else:
                extracted = ""

        if extracted.startswith("⚠️"):
            st.error(extracted)
        elif extracted.strip():
            st.success(f"✅ Đọc thành công: **{uploaded.name}** · {count_words(extracted):,} từ")
            st.text_area("Nội dung trích xuất (xem trước)", extracted[:1500] + ("…" if len(extracted) > 1500 else ""),
                         height=180, disabled=True, key="file_preview")
            input_text   = extracted
            source_label = f"File: {uploaded.name}"
        else:
            st.warning("File rỗng hoặc không trích xuất được nội dung.")

# ── TAB 3: Link URL / Google Docs ────────────────────────────────────────────
with tab_url:
    st.markdown("""
**Hỗ trợ các loại link:**
- 🟢 **Google Docs** — link chia sẻ (chế độ *Anyone with the link can view*)
- 🌐 **Trang web** — bài báo, blog, trang tin tức (cần `pip install beautifulsoup4`)
""")
    url_input = st.text_input(
        "Dán link vào đây:",
        placeholder="https://docs.google.com/document/d/...   hoặc   https://vnexpress.net/...",
        key="url_input",
    )
    fetch_btn = st.button("⬇️ Tải nội dung từ link", key="fetch_btn")

    if fetch_btn and url_input.strip():
        with st.spinner("Đang tải nội dung..."):
            fetched, src = fetch_url_text(url_input.strip())

        if fetched.startswith("⚠️"):
            st.error(fetched)
        elif fetched.strip():
            st.success(f"✅ Tải thành công từ **{src}** · {count_words(fetched):,} từ")
            st.text_area("Nội dung trích xuất (xem trước)", fetched[:1500] + ("…" if len(fetched) > 1500 else ""),
                         height=180, disabled=True, key="url_preview")
            input_text   = fetched
            source_label = src
            # Lưu vào session để giữ sau khi re-render
            st.session_state["url_text"]   = fetched
            st.session_state["url_source"] = src
        else:
            st.warning("Không lấy được nội dung từ link này.")

    # Khôi phục từ session nếu đã tải trước đó
    if not input_text and st.session_state.get("url_text"):
        input_text   = st.session_state["url_text"]
        source_label = st.session_state.get("url_source", "URL")


# ── Thông tin văn bản đang dùng ───────────────────────────────────────────────
if input_text.strip():
    wc     = count_words(input_text)
    n_sent = len(split_sentences(input_text))
    st.markdown(f'<div class="source-badge">📌 Nguồn: {source_label}</div>', unsafe_allow_html=True)
    st.caption(f"📝 {wc:,} từ · {len(input_text):,} ký tự · {n_sent} câu")
else:
    wc     = 0
    n_sent = 0

st.markdown("---")

# ── Nút tóm tắt ──────────────────────────────────────────────────────────────
col_info, col_btn = st.columns([4, 1], vertical_alignment="bottom")
with col_info:
    st.caption(
        f"**Thuật toán:** {algorithm}  ·  "
        f"**Lĩnh vực:** {domain}  ·  "
        f"**Số câu:** {num_sentences} (giới hạn {sent_min}–{sent_max})"
    )
with col_btn:
    run = st.button(
        "▶ Tóm tắt",
        type="primary",
        use_container_width=True,
        disabled=not input_text.strip(),
    )


# ══════════════════════════════════════════════════════════════════════════════
# RENDER KẾT QUẢ
# ══════════════════════════════════════════════════════════════════════════════

def render_result(summary: str, method_name: str, source_text: str):
    orig_w = count_words(source_text)
    sum_w  = count_words(summary)
    comp   = max(0, round((1 - sum_w / orig_w) * 100)) if orig_w else 0
    rt     = max(1, round(sum_w / 3))

    st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-val">{orig_w:,}</div>
    <div class="metric-label">Từ gốc</div>
  </div>
  <div class="metric-card">
    <div class="metric-val">{sum_w:,}</div>
    <div class="metric-label">Từ tóm tắt</div>
  </div>
  <div class="metric-card">
    <div class="metric-val">{comp}%</div>
    <div class="metric-label">Tỷ lệ nén</div>
  </div>
  <div class="metric-card">
    <div class="metric-val">{rt}s</div>
    <div class="metric-label">Đọc tóm tắt</div>
  </div>
</div>
<div class="bar-wrap">
  <div class="bar-fill" style="width:{min(comp, 98)}%"></div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📄 Văn bản gốc**")
        preview = source_text[:700] + ("…" if len(source_text) > 700 else "")
        st.markdown(f'<div class="original-box">{preview}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"**✨ Tóm tắt — {method_name}**")
        st.markdown(f'<div class="result-box">{summary}</div>', unsafe_allow_html=True)

    st.download_button(
        "⬇️ Tải tóm tắt (.txt)",
        data=summary,
        file_name=f"tom_tat_{method_name.replace(' ','_').lower()}.txt",
        mime="text/plain",
        key=f"dl_{method_name}_{hash(summary) % 9999}",
    )


# ══════════════════════════════════════════════════════════════════════════════
# HẬU XỬ LÝ: Áp dụng lĩnh vực / độ dài / phong cách / ngôn ngữ
# ══════════════════════════════════════════════════════════════════════════════

DOMAIN_HEADERS = {
    "Tổng quát": "",
    "Báo chí":   "📰 Tóm tắt tin tức",
    "Giáo dục":  "🎓 Tóm tắt tài liệu học tập",
    "Pháp lý":   "⚖️ Tóm tắt văn bản pháp lý",
    "Y tế":      "🏥 Tóm tắt hồ sơ y tế",
}

def postprocess(raw: str, domain: str) -> str:
    """Thêm tiêu đề lĩnh vực vào đầu bản tóm tắt."""
    header = DOMAIN_HEADERS.get(domain, "")
    if header:
        return f"**{header}**\n\n{raw}"
    return raw


# ══════════════════════════════════════════════════════════════════════════════
# XỬ LÝ KHI NHẤN NÚT TÓM TẮT
# ══════════════════════════════════════════════════════════════════════════════

if run and input_text.strip():

    if len(input_text.strip()) < 60:
        st.error("Văn bản quá ngắn. Vui lòng nhập ít nhất 60 ký tự.")
        st.stop()

    num_out = min(num_sentences, max(1, n_sent - 1))

    st.markdown("---")

    # ── So sánh tất cả ────────────────────────────────────────────────────────
    if compare_all:
        st.markdown("### 📊 So sánh tất cả thuật toán")

        # Chọn thuật toán theo lựa chọn trong so sánh
        methods: dict = {
            "TF-IDF (built-in)":   lambda: tfidf_summarize(input_text, num_out),
            "TextRank (built-in)": lambda: textrank_summarize(input_text, num_out),
        }
        if use_sumy:
            methods[f"Sumy {sumy_algo}"] = lambda: sumy_summarize(input_text, num_out, sumy_algo)
        if use_gensim:
            def _gensim():
                try:
                    from gensim.summarization import summarize as gs
                    r = gs(input_text, ratio=extract_ratio)
                    return r if r.strip() else "Văn bản quá ngắn cho Gensim."
                except ImportError:
                    return "⚠️ Chưa cài gensim==3.8.3"
                except Exception as e:
                    return f"⚠️ Gensim lỗi: {e}"
            methods["Gensim TextRank"] = _gensim

        tabs    = st.tabs(list(methods.keys()))
        results = {}
        for tab, (name, fn) in zip(tabs, methods.items()):
            with tab:
                with st.spinner(f"{name} đang xử lý..."):
                    raw    = fn()
                    result = postprocess(raw, domain)
                results[name] = result
                render_result(result, name, input_text)

        st.markdown("---")
        st.markdown("### 📋 Bảng tổng hợp")
        import pandas as pd
        orig_w = count_words(input_text)
        rows = []
        for name, res in results.items():
            w = count_words(res)
            rows.append({
                "Thuật toán":   name,
                "Lĩnh vực":     domain,
                "Số câu":       len(split_sentences(res)),
                "Số từ":        w,
                "Tỷ lệ nén":    f"{max(0, round((1 - w/orig_w)*100))}%",
                "Cần cài thêm": "Không" if "built-in" in name else "pip install sumy/gensim",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Đơn lẻ ────────────────────────────────────────────────────────────────
    else:
        algo_map = {
            "TF-IDF (built-in)":   ("TF-IDF",        lambda: tfidf_summarize(input_text, num_out)),
            "TextRank (built-in)": ("TextRank",       lambda: textrank_summarize(input_text, num_out)),
            "Sumy — LSA":          ("Sumy LSA",       lambda: sumy_summarize(input_text, num_out, "LSA")),
            "Sumy — LexRank":      ("Sumy LexRank",   lambda: sumy_summarize(input_text, num_out, "LexRank")),
            "Sumy — Luhn":         ("Sumy Luhn",      lambda: sumy_summarize(input_text, num_out, "Luhn")),
            "Sumy — TextRank":     ("Sumy TextRank",  lambda: sumy_summarize(input_text, num_out, "TextRank")),
        }
        label, fn = algo_map[algorithm]
        with st.spinner(f"{label} đang xử lý..."):
            raw     = fn()
            summary = postprocess(raw, domain)
        st.markdown(f"### ✨ Kết quả — {label}  ·  {domain}")
        render_result(summary, label, input_text)

    # ── RAKE keywords ──────────────────────────────────────────────────────────
    if show_rake:
        st.markdown("---")
        st.markdown("### 🏷️ Từ khoá quan trọng (RAKE)")
        with st.spinner("Đang trích xuất từ khoá..."):
            keywords = rake_keywords(input_text, top_n=rake_top)
        tags = " ".join(f'<span class="kw-tag">{kw}</span>' for kw in keywords)
        st.markdown(tags, unsafe_allow_html=True)
        st.caption(f"Trích xuất {len(keywords)} cụm từ khoá")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("TF-IDF · TextRank · Sumy · RAKE · Streamlit · Không cần API · Hỗ trợ PDF, DOCX, TXT, URL, Google Docs")