"""
Công cụ Tóm Tắt Văn Bản - Không cần API
==========================================
Tính năng:
  · Dán văn bản | Tải file (PDF, DOCX, TXT) | Link URL / Google Docs
  · Multi-document: tóm tắt nhiều tài liệu cùng lúc
  · Tóm tắt theo số câu hoặc tỷ lệ %
  · Tiếng Việt: xử lý dấu, stopwords mở rộng
  · Thống kê chi tiết + biểu đồ từ khoá
  · Download kết quả (.txt / .json)

Cài đặt:
    pip install -r requirements.txt
    streamlit run app.py
"""

import re
import math
import io
import json
import unicodedata
import urllib.request
import urllib.parse
from collections import Counter
from datetime import datetime

import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Tóm Tắt Văn Bản",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .main .block-container { padding-top: 1.5rem; max-width: 1150px; }
  .stTextArea textarea   { font-size: 14px; line-height: 1.75; }

  .metric-row { display:flex; gap:10px; margin:.8rem 0; flex-wrap:wrap; }
  .metric-card {
      background:#f5f5f3; border-radius:10px;
      padding:12px 16px; text-align:center; flex:1; min-width:85px;
  }
  .metric-val   { font-size:20px; font-weight:600; color:#1D9E75; }
  .metric-label { font-size:10px; color:#888; text-transform:uppercase;
                  letter-spacing:.05em; margin-top:2px; }

  .bar-wrap { background:#e8e8e4; border-radius:4px; height:7px;
              margin:4px 0 12px; overflow:hidden; }
  .bar-fill { background:linear-gradient(90deg,#1D9E75,#5DCAA5);
              height:100%; border-radius:4px; }

  .result-box {
      background:#f0faf6; border:1px solid #9FE1CB; border-radius:10px;
      padding:1.1rem 1.4rem; font-size:14px; line-height:1.85;
      white-space:pre-wrap; color:#1a1a18; min-height:120px;
  }
  .original-box {
      background:#fafaf8; border:1px solid #e0e0dc; border-radius:10px;
      padding:1.1rem 1.4rem; font-size:13px; line-height:1.75;
      max-height:280px; overflow-y:auto; color:#444;
  }
  .kw-tag {
      display:inline-block; background:#1D9E75; color:#fff;
      border-radius:20px; padding:3px 11px; font-size:12px;
      font-weight:500; margin:3px 4px 3px 0;
  }
  .kw-tag-gray {
      display:inline-block; background:#e8e8e4; color:#444;
      border-radius:20px; padding:3px 11px; font-size:12px;
      font-weight:500; margin:3px 4px 3px 0;
  }
  .source-badge {
      display:inline-block; background:#e8f5f0; color:#0F6E56;
      border:1px solid #9FE1CB; border-radius:6px;
      padding:3px 10px; font-size:12px; font-weight:500; margin-bottom:8px;
  }
  .doc-card {
      background:#fafaf8; border:1px solid #e0e0dc; border-radius:10px;
      padding:1rem 1.2rem; margin-bottom:10px;
  }
  .doc-title { font-size:13px; font-weight:600; color:#1a1a18; margin-bottom:4px; }
  .section-title { font-size:15px; font-weight:600; color:#1a1a18;
                   margin:1.2rem 0 .5rem; }
  .stat-detail { background:#f5f5f3; border-radius:8px; padding:10px 14px;
                 font-size:13px; line-height:1.8; color:#444; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# XỬ LÝ TIẾNG VIỆT — cải thiện dấu, chuẩn hoá Unicode
# ══════════════════════════════════════════════════════════════════════════════

# Bảng stopwords Tiếng Việt mở rộng (~200 từ)
VI_STOPWORDS = {
    # Liên từ / giới từ
    "và","hay","hoặc","nhưng","mà","vì","bởi","do","nên","nếu","thì","khi",
    "dù","tuy","dẫu","mặc","vậy","thế","bằng","cùng","với","theo","về",
    "tại","ở","trong","ngoài","trên","dưới","trước","sau","giữa","qua",
    "từ","đến","đối","cho","của","bởi","vì","qua","lên","xuống","vào","ra",
    # Đại từ
    "tôi","tao","mình","ta","chúng","họ","anh","chị","em","ông","bà",
    "cô","chú","bác","nó","hắn","thị","y","người","ai","gì","đâu","nào",
    # Trạng từ / phó từ
    "đã","sẽ","đang","vừa","mới","cũng","còn","lại","vẫn","đều","chỉ",
    "chưa","không","chẳng","chả","hầu","khá","rất","quá","lắm","thật",
    "thực","cực","siêu","hơi","khá","hẳn","cả","suốt","mãi","luôn",
    # Từ chỉ định / số lượng
    "này","kia","đây","đó","đấy","ấy","các","những","mọi","một","hai",
    "ba","nhiều","ít","vài","mấy","toàn","tất","cả","một số","một vài",
    # Động từ phụ trợ thông dụng
    "là","có","được","bị","làm","thành","trở","biết","muốn","cần","phải",
    "nên","được","cho","đưa","đặt","bỏ","bắt","gặp","thấy","nghĩ","nói",
    # Kết từ / chuyển tiếp
    "tuy nhiên","mặc dù","bên cạnh","ngoài ra","hơn nữa","do đó","vì vậy",
    "như vậy","như thế","vì thế","thế nên","cho nên","tức là","ví dụ",
    "chẳng hạn","theo đó","qua đó","để","nhằm","nhờ","dựa","theo",
    # Số đếm & đơn vị thông thường
    "lần","năm","tháng","ngày","giờ","phút","giây","tuần","quý","kỳ",
}

EN_STOPWORDS = {
    "the","a","an","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "must","to","of","in","on","at","by","for","with","about","into",
    "through","during","before","after","from","up","down","out","and",
    "but","or","nor","not","only","same","than","too","very","just","as",
    "until","while","i","me","my","we","our","you","your","he","she","it",
    "they","them","their","this","that","these","those","which","who","also",
    "its","been","each","more","other","than","then","so","such","no","here",
}

ALL_STOPWORDS = VI_STOPWORDS | EN_STOPWORDS


def normalize_vi(text: str) -> str:
    """Chuẩn hoá Unicode NFC cho Tiếng Việt (tránh lỗi dấu tổ hợp)."""
    return unicodedata.normalize("NFC", text)


def count_words(text: str) -> int:
    text = text.strip()
    return len(text.split()) if text else 0


def count_chars_no_space(text: str) -> int:
    return len(text.replace(" ", "").replace("\n", ""))


def split_sentences(text: str) -> list[str]:
    """
    Tách câu cải tiến — xử lý dấu tiếng Việt đúng hơn.
    Xử lý: . ! ? … và các dấu kép.
    """
    text = normalize_vi(text)
    # Bảo vệ số thập phân (3.14, 1.000)
    text = re.sub(r'(\d)\.(\d)', r'\1<DOT>\2', text)
    # Tách theo dấu kết thúc câu
    parts = re.split(r'(?<=[.!?…])\s+(?=[A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ\"\'])', text)
    sentences = []
    for s in parts:
        s = s.replace('<DOT>', '.').strip()
        if len(s) > 8:
            sentences.append(s)
    return sentences


def tokenize_vi(text: str) -> list[str]:
    """Token hoá Tiếng Việt: ưu tiên underthesea, fallback regex."""
    text = normalize_vi(text)
    try:
        from underthesea import word_tokenize
        tokens = word_tokenize(text, format="text").lower().split()
        return tokens
    except ImportError:
        pass
    # Fallback: lowercase + tách theo ký tự không phải chữ/số
    text = text.lower()
    tokens = re.findall(r'[a-záàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ\w]+', text)
    return tokens


def clean_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in ALL_STOPWORDS and len(t) > 1 and not t.isdigit()]


def detect_language(text: str) -> str:
    """Phát hiện ngôn ngữ đơn giản dựa trên ký tự đặc trưng."""
    vi_chars = len(re.findall(r'[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]', text.lower()))
    return "vi" if vi_chars > len(text) * 0.02 else "en"


# ══════════════════════════════════════════════════════════════════════════════
# THỐNG KÊ VĂN BẢN CHI TIẾT
# ══════════════════════════════════════════════════════════════════════════════

def text_stats(text: str) -> dict:
    """Tính toán thống kê đầy đủ cho một văn bản."""
    sentences  = split_sentences(text)
    words      = text.strip().split()
    tokens     = clean_tokens(tokenize_vi(text))
    freq       = Counter(tokens)
    avg_sent_len = round(len(words) / max(len(sentences), 1), 1)
    unique_words = len(set(w.lower() for w in words))
    lexical_density = round(unique_words / max(len(words), 1) * 100, 1)
    return {
        "words":        len(words),
        "chars":        len(text),
        "chars_ns":     count_chars_no_space(text),
        "sentences":    len(sentences),
        "unique_words": unique_words,
        "avg_sent_len": avg_sent_len,
        "lex_density":  lexical_density,
        "read_time_s":  max(1, round(len(words) / 200 * 60)),  # 200 wpm
        "top_words":    freq.most_common(20),
        "lang":         detect_language(text),
    }


# ══════════════════════════════════════════════════════════════════════════════
# ĐỌC FILE
# ══════════════════════════════════════════════════════════════════════════════

def read_txt(file_bytes: bytes) -> str:
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return normalize_vi(file_bytes.decode(enc))
        except UnicodeDecodeError:
            continue
    return normalize_vi(file_bytes.decode("utf-8", errors="replace"))


def read_pdf(file_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages  = [p.extract_text() or "" for p in reader.pages]
        text   = "\n".join(pages).strip()
        if text:
            return normalize_vi(text)
    except ImportError:
        pass
    try:
        from pdfminer.high_level import extract_text as pm_extract
        text = pm_extract(io.BytesIO(file_bytes))
        if text and text.strip():
            return normalize_vi(text.strip())
    except ImportError:
        pass
    return "⚠️ Cài: pip install pypdf"


def read_docx(file_bytes: bytes) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return normalize_vi("\n".join(p.text for p in doc.paragraphs if p.text.strip()))
    except ImportError:
        return "⚠️ Cài: pip install python-docx"


def gdoc_export_url(url: str) -> str | None:
    m = re.search(r'docs\.google\.com/document/d/([^/?#]+)', url)
    if m:
        return f"https://docs.google.com/document/d/{m.group(1)}/export?format=txt"
    return None


def fetch_url_text(url: str) -> tuple[str, str]:
    url = url.strip()
    gdoc = gdoc_export_url(url)
    if gdoc:
        try:
            req  = urllib.request.Request(gdoc, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            return normalize_vi(read_txt(resp.read())), "Google Docs"
        except Exception as e:
            return f"⚠️ Không tải được Google Docs: {e}", "Lỗi"
    try:
        req  = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"⚠️ Không tải được URL: {e}", "Lỗi"
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script","style","nav","footer","header","aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return normalize_vi(text), urllib.parse.urlparse(url).netloc
    except ImportError:
        pass
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s{2,}', '\n', text).strip()
    return normalize_vi(text), urllib.parse.urlparse(url).netloc


# ══════════════════════════════════════════════════════════════════════════════
# THUẬT TOÁN TÓM TẮT
# ══════════════════════════════════════════════════════════════════════════════

def _resolve_num(text: str, mode: str, num_sent: int, pct: int) -> int:
    """Tính số câu cần giữ dựa trên mode (câu / %)."""
    sentences = split_sentences(text)
    n = len(sentences)
    if mode == "Tỷ lệ %":
        return max(1, round(n * pct / 100))
    return min(num_sent, max(1, n - 1))


def tfidf_summarize(text: str, k: int) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= k:
        return text
    tokenized = [clean_tokens(tokenize_vi(s)) for s in sentences]
    N  = len(sentences)
    df: Counter = Counter()
    for toks in tokenized:
        for t in set(toks):
            df[t] += 1
    idf    = {t: math.log((N + 1) / (c + 1)) + 1 for t, c in df.items()}
    scores = []
    for toks in tokenized:
        if not toks:
            scores.append(0.0); continue
        tf    = Counter(toks)
        score = sum((tf[t] / len(toks)) * idf.get(t, 0) for t in tf)
        scores.append(score)
    ranked  = sorted(range(N), key=lambda i: scores[i], reverse=True)
    top_idx = sorted(ranked[:k])
    return " ".join(sentences[i] for i in top_idx)


def _sim(s1: list[str], s2: list[str]) -> float:
    a, b = set(s1), set(s2)
    if not a or not b:
        return 0.0
    return len(a & b) / (math.log(len(a)+1) + math.log(len(b)+1) + 1e-9)


def textrank_summarize(text: str, k: int, damping: float = 0.85, iters: int = 30) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= k:
        return text
    tokenized = [clean_tokens(tokenize_vi(s)) for s in sentences]
    N   = len(sentences)
    mat = [[_sim(tokenized[i], tokenized[j]) if i != j else 0.0
            for j in range(N)] for i in range(N)]
    for i in range(N):
        rs = sum(mat[i])
        if rs:
            mat[i] = [v / rs for v in mat[i]]
    scores = [1.0 / N] * N
    for _ in range(iters):
        scores = [(1-damping)/N + damping*sum(mat[j][i]*scores[j] for j in range(N))
                  for i in range(N)]
    ranked  = sorted(range(N), key=lambda i: scores[i], reverse=True)
    top_idx = sorted(ranked[:k])
    return " ".join(sentences[i] for i in top_idx)


def sumy_summarize(text: str, k: int, algorithm: str = "LSA") -> str:
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
        return "⚠️ Cài: pip install sumy"
    MAP    = {"LSA":LsaSummarizer,"LexRank":LexRankSummarizer,
              "Luhn":LuhnSummarizer,"TextRank":TextRankSummarizer}
    lang   = "english"
    parser = PlaintextParser.from_string(text, Tokenizer(lang))
    sumr   = MAP.get(algorithm, LsaSummarizer)(Stemmer(lang))
    sumr.stop_words = get_stop_words(lang)
    return " ".join(str(s) for s in sumr(parser.document, k))


def rake_keywords(text: str, top_n: int = 15) -> list[tuple[str, float]]:
    """Trả về list (phrase, score)."""
    try:
        from rake_nltk import Rake
        import nltk
        for res in ("corpora/stopwords","tokenizers/punkt_tab"):
            try:    nltk.data.find(res)
            except: nltk.download(res.split("/")[1], quiet=True)
        r = Rake()
        r.extract_keywords_from_text(text)
        ranked = r.get_ranked_phrases_with_scores()[:top_n]
        return [(ph, sc) for sc, ph in ranked]
    except ImportError:
        pass
    # Fallback thuần Python
    words = re.findall(r'\b\w+\b', normalize_vi(text).lower())
    phrases, current = [], []
    for w in words:
        if w in ALL_STOPWORDS or not re.match(r'^[\w]+$', w):
            if current: phrases.append(" ".join(current)); current = []
        else:
            current.append(w)
    if current: phrases.append(" ".join(current))
    freq: Counter = Counter(phrases)
    deg:  Counter = Counter()
    for ph in phrases:
        for w in ph.split(): deg[w] += len(ph.split())
    scores = {ph: sum(deg[w]/(freq[w] or 1) for w in ph.split()) for ph in freq}
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


# ══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD HELPER
# ══════════════════════════════════════════════════════════════════════════════

def build_txt_export(docs: list[dict]) -> str:
    lines = [f"BÁO CÁO TÓM TẮT — {datetime.now().strftime('%d/%m/%Y %H:%M')}\n{'='*60}\n"]
    for i, d in enumerate(docs, 1):
        lines.append(f"\n[{i}] {d['title']}")
        lines.append(f"Thuật toán : {d['algo']}")
        lines.append(f"Số câu gốc : {d['orig_sent']}  |  Số câu TT: {d['sum_sent']}")
        lines.append(f"Số từ gốc  : {d['orig_words']}  |  Số từ TT: {d['sum_words']}  |  Nén: {d['compress']}%")
        lines.append(f"\nBẢN TÓM TẮT:\n{d['summary']}\n")
        lines.append("-"*60)
    return "\n".join(lines)


def build_json_export(docs: list[dict]) -> str:
    return json.dumps(docs, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN HEADERS
# ══════════════════════════════════════════════════════════════════════════════

DOMAIN_HEADERS = {
    "Tổng quát": "",
    "Báo chí":   "📰 Tóm tắt tin tức",
    "Giáo dục":  "🎓 Tóm tắt tài liệu học tập",
    "Pháp lý":   "⚖️ Tóm tắt văn bản pháp lý",
    "Y tế":      "🏥 Tóm tắt hồ sơ y tế",
}


def postprocess(raw: str, domain: str) -> str:
    header = DOMAIN_HEADERS.get(domain, "")
    return f"**{header}**\n\n{raw}" if header else raw


# ══════════════════════════════════════════════════════════════════════════════
# RENDER KẾT QUẢ
# ══════════════════════════════════════════════════════════════════════════════

def render_result(summary: str, method_name: str, source_text: str,
                  show_stats: bool = True) -> dict:
    """Hiển thị kết quả tóm tắt + thống kê. Trả về dict metadata."""
    orig_sentences = split_sentences(source_text)
    sum_sentences  = split_sentences(summary)
    orig_w = count_words(source_text)
    sum_w  = count_words(summary)
    comp   = max(0, round((1 - sum_w / orig_w) * 100)) if orig_w else 0
    rt_orig= max(1, round(orig_w / 200 * 60))   # giây đọc gốc (200wpm)
    rt_sum = max(1, round(sum_w  / 200 * 60))

    fmt_time = lambda s: f"{s//60}p{s%60:02d}s" if s >= 60 else f"{s}s"

    if show_stats:
        st.markdown(f"""
<div class="metric-row">
  <div class="metric-card"><div class="metric-val">{orig_w:,}</div><div class="metric-label">Từ gốc</div></div>
  <div class="metric-card"><div class="metric-val">{sum_w:,}</div><div class="metric-label">Từ tóm tắt</div></div>
  <div class="metric-card"><div class="metric-val">{len(orig_sentences)}</div><div class="metric-label">Câu gốc</div></div>
  <div class="metric-card"><div class="metric-val">{len(sum_sentences)}</div><div class="metric-label">Câu TT</div></div>
  <div class="metric-card"><div class="metric-val">{comp}%</div><div class="metric-label">Tỷ lệ nén</div></div>
  <div class="metric-card"><div class="metric-val">{fmt_time(rt_orig)}</div><div class="metric-label">Đọc gốc</div></div>
  <div class="metric-card"><div class="metric-val">{fmt_time(rt_sum)}</div><div class="metric-label">Đọc TT</div></div>
</div>
<div class="bar-wrap"><div class="bar-fill" style="width:{min(comp,98)}%"></div></div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📄 Văn bản gốc**")
        preview = source_text[:800] + ("…" if len(source_text) > 800 else "")
        st.markdown(f'<div class="original-box">{preview}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"**✨ Tóm tắt — {method_name}**")
        st.markdown(f'<div class="result-box">{summary}</div>', unsafe_allow_html=True)

    return {
        "title":       method_name,
        "algo":        method_name,
        "summary":     summary,
        "orig_words":  orig_w,
        "sum_words":   sum_w,
        "orig_sent":   len(orig_sentences),
        "sum_sent":    len(sum_sentences),
        "compress":    comp,
    }


def render_keywords(text: str, top_n: int = 15):
    """Hiển thị từ khoá với màu sắc theo điểm."""
    keywords = rake_keywords(text, top_n=top_n)
    if not keywords:
        return
    max_score = keywords[0][1] if keywords else 1
    tags = []
    for ph, sc in keywords:
        opacity = max(0.4, sc / max(max_score, 1))
        style   = f"opacity:{opacity:.2f}"
        tags.append(f'<span class="kw-tag" style="{style}" title="Điểm: {sc:.1f}">{ph}</span>')
    st.markdown(" ".join(tags), unsafe_allow_html=True)

    # Top 10 dạng bảng
    with st.expander("📊 Xem bảng từ khoá chi tiết"):
        import pandas as pd
        df = pd.DataFrame(keywords[:10], columns=["Cụm từ khoá", "Điểm RAKE"])
        df["Điểm RAKE"] = df["Điểm RAKE"].round(2)
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_text_stats(text: str):
    """Hiển thị thống kê chi tiết về văn bản."""
    s = text_stats(text)
    rt = s["read_time_s"]
    rt_str = f"{rt//60}p {rt%60:02d}s" if rt >= 60 else f"{rt}s"
    lang_str = "🇻🇳 Tiếng Việt" if s["lang"] == "vi" else "🇺🇸 Tiếng Anh"

    with st.expander("📈 Thống kê chi tiết văn bản gốc"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="stat-detail">
🔤 <b>Số từ:</b> {s['words']:,}<br>
📝 <b>Số ký tự (có dấu cách):</b> {s['chars']:,}<br>
✍️ <b>Số ký tự (không dấu cách):</b> {s['chars_ns']:,}<br>
🔀 <b>Từ không trùng:</b> {s['unique_words']:,}<br>
</div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="stat-detail">
📖 <b>Số câu:</b> {s['sentences']}<br>
📏 <b>Độ dài câu TB:</b> {s['avg_sent_len']} từ/câu<br>
💡 <b>Mật độ từ vựng:</b> {s['lex_density']}%<br>
⏱️ <b>Thời gian đọc:</b> {rt_str}<br>
🌐 <b>Ngôn ngữ phát hiện:</b> {lang_str}
</div>""", unsafe_allow_html=True)

        # Biểu đồ top từ
        if s["top_words"]:
            import pandas as pd
            df = pd.DataFrame(s["top_words"][:12], columns=["Từ","Tần suất"])
            st.bar_chart(df.set_index("Từ"), height=200)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("⚙️ Cài đặt")

    # Lĩnh vực
    st.subheader("📋 Lĩnh vực")
    domain = st.selectbox("Chọn lĩnh vực",
        ["Tổng quát","Báo chí","Giáo dục","Pháp lý","Y tế"])

    st.divider()

    # Chế độ số câu / tỷ lệ %
    st.subheader("📐 Độ dài tóm tắt")
    sum_mode = st.radio("Chế độ", ["Số câu", "Tỷ lệ %"], horizontal=True)
    if sum_mode == "Số câu":
        num_sentences = int(st.number_input("Số câu (1–20)", min_value=1, max_value=20, value=4, step=1))
        pct_sentences = 30
    else:
        pct_sentences = int(st.slider("Tỷ lệ giữ lại (%)", 5, 60, 30, 5,
                                       help="Phần trăm câu giữ lại so với bản gốc"))
        num_sentences = 4

    st.divider()

    # Thuật toán
    st.subheader("🔬 Thuật toán")
    algorithm = st.selectbox("Chọn thuật toán",
        ["TF-IDF (built-in)","TextRank (built-in)",
         "Sumy — LSA","Sumy — LexRank","Sumy — Luhn","Sumy — TextRank"])

    st.divider()

    # So sánh
    st.subheader("📊 So sánh phương pháp")
    compare_all = st.checkbox("Bật chế độ so sánh", value=False)
    if compare_all:
        use_sumy   = st.checkbox("Sumy", value=True)
        sumy_algo  = st.selectbox("Thuật toán Sumy", ["LSA","LexRank","Luhn","TextRank"]) if use_sumy else "LSA"
        use_gensim = st.checkbox("Gensim TextRank", value=False)
    else:
        use_sumy, use_gensim, sumy_algo = False, False, "LSA"

    st.divider()

    # RAKE + Thống kê
    st.subheader("🏷️ Từ khoá & Thống kê")
    show_rake  = st.checkbox("Hiển thị từ khoá RAKE", value=True)
    rake_top   = st.slider("Số từ khoá", 5, 25, 12) if show_rake else 12
    show_stats = st.checkbox("Thống kê chi tiết văn bản", value=True)

    st.divider()
    st.info(
        "🟢 **Không cần API key**\n\n"
        "**Built-in:** TF-IDF · TextRank · RAKE\n\n"
        "**Cài thêm:**\n"
        "`pip install sumy`\n"
        "`pip install pypdf`\n"
        "`pip install python-docx`\n"
        "`pip install beautifulsoup4`\n"
        "`pip install underthesea`"
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI — TIÊU ĐỀ
# ══════════════════════════════════════════════════════════════════════════════

st.title("◈ Tóm Tắt Văn Bản")
st.caption("TF-IDF · TextRank · Sumy · RAKE · PDF / DOCX / TXT · URL · Google Docs · Multi-document")

# ══════════════════════════════════════════════════════════════════════════════
# 4 TAB NGUỒN ĐẦU VÀO
# ══════════════════════════════════════════════════════════════════════════════

tab_text, tab_file, tab_url, tab_multi = st.tabs([
    "✏️  Dán văn bản",
    "📁  Tải file lên",
    "🔗  Link URL / Google Docs",
    "📚  Nhiều tài liệu",
])

documents: list[dict] = []   # [{"title": str, "text": str}]
input_text   = ""
source_label = ""
multi_mode   = False

# ── TAB 1: Dán văn bản ────────────────────────────────────────────────────────
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
        "bao gồm phần mềm ERP tùy chỉnh cho 3 chi nhánh, module quản lý kho hàng thời gian thực. "
        "Thời gian triển khai không quá 6 tháng kể từ ngày ký hợp đồng. "
        "ĐIỀU 3. GIÁ TRỊ HỢP ĐỒNG. Tổng giá trị hợp đồng là 1.800.000.000 đồng. "
        "Thanh toán theo 3 đợt: 30% khi ký hợp đồng, 40% khi hoàn thành giai đoạn 1, 30% khi nghiệm thu. "
        "ĐIỀU 4. BẢO HÀNH. Bên Cung Cấp Dịch Vụ bảo hành hệ thống trong 24 tháng kể từ ngày nghiệm thu. "
        "Cam kết sửa lỗi trong vòng 24 giờ đối với lỗi nghiêm trọng và 72 giờ đối với lỗi thông thường. "
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
        "Hướng xử trí: can thiệp mạch vành qua da cấp cứu, Aspirin và Ticagrelor liều tải, Heparin tiêm tĩnh mạch."
    ),
}

with tab_text:
    ex = st.selectbox("Tải văn bản mẫu:", ["— chọn mẫu —"] + list(EXAMPLES.keys()), key="ex")
    default_text = EXAMPLES.get(ex, "") if ex != "— chọn mẫu —" else ""
    pasted = st.text_area("Văn bản đầu vào", value=default_text, height=240,
                           placeholder="Dán bài báo, tài liệu, hợp đồng... (Tiếng Việt hoặc Tiếng Anh)",
                           key="paste_area")
    if pasted.strip():
        input_text   = normalize_vi(pasted)
        source_label = "Văn bản dán"
        documents    = [{"title": "Văn bản dán", "text": input_text}]

# ── TAB 2: Tải file ───────────────────────────────────────────────────────────
with tab_file:
    uploaded = st.file_uploader("Chọn file", type=["txt","pdf","docx"],
                                 help=".txt · .pdf (cần pypdf) · .docx (cần python-docx)")
    if uploaded:
        fb  = uploaded.read()
        ext = uploaded.name.rsplit(".",1)[-1].lower()
        with st.spinner(f"Đang đọc {uploaded.name}..."):
            extracted = {"txt": read_txt,"pdf": read_pdf,"docx": read_docx}.get(ext, read_txt)(fb)
        if extracted.startswith("⚠️"):
            st.error(extracted)
        elif extracted.strip():
            st.success(f"✅ {uploaded.name} · {count_words(extracted):,} từ")
            st.text_area("Xem trước", extracted[:1500]+("…" if len(extracted)>1500 else ""),
                         height=160, disabled=True, key="fp")
            input_text   = extracted
            source_label = uploaded.name
            documents    = [{"title": uploaded.name, "text": input_text}]

# ── TAB 3: Link URL ───────────────────────────────────────────────────────────
with tab_url:
    st.markdown("🟢 **Google Docs** (chia sẻ *Anyone with link*) · 🌐 **Trang web** (cần beautifulsoup4)")
    url_input = st.text_input("Dán link:", placeholder="https://docs.google.com/... hoặc https://vnexpress.net/...", key="url")
    if st.button("⬇️ Tải nội dung", key="fetch"):
        with st.spinner("Đang tải..."):
            fetched, src = fetch_url_text(url_input.strip())
        if fetched.startswith("⚠️"):
            st.error(fetched)
        elif fetched.strip():
            st.success(f"✅ {src} · {count_words(fetched):,} từ")
            st.text_area("Xem trước", fetched[:1500]+("…" if len(fetched)>1500 else ""),
                         height=160, disabled=True, key="up")
            st.session_state["url_text"]   = fetched
            st.session_state["url_source"] = src
    if not input_text and st.session_state.get("url_text"):
        input_text   = st.session_state["url_text"]
        source_label = st.session_state.get("url_source","URL")
        documents    = [{"title": source_label, "text": input_text}]

# ── TAB 4: Multi-document ────────────────────────────────────────────────────
with tab_multi:
    st.markdown("##### Tải lên nhiều tài liệu để tóm tắt và so sánh cùng lúc")
    multi_files = st.file_uploader("Chọn nhiều file cùng lúc",
                                    type=["txt","pdf","docx"],
                                    accept_multiple_files=True,
                                    key="multi_upload")
    multi_texts: list[dict] = []
    if multi_files:
        for mf in multi_files:
            fb  = mf.read()
            ext = mf.name.rsplit(".",1)[-1].lower()
            extracted = {"txt": read_txt,"pdf": read_pdf,"docx": read_docx}.get(ext, read_txt)(fb)
            if not extracted.startswith("⚠️") and extracted.strip():
                multi_texts.append({"title": mf.name, "text": normalize_vi(extracted)})

    # Thêm văn bản dán thủ công
    st.markdown("**Hoặc dán văn bản thêm vào:**")
    extra_title = st.text_input("Tên tài liệu", placeholder="Tài liệu thêm vào", key="extra_title")
    extra_text  = st.text_area("Nội dung", height=120, placeholder="Dán văn bản...", key="extra_text")
    if extra_text.strip():
        multi_texts.append({"title": extra_title or f"Tài liệu {len(multi_texts)+1}",
                             "text": normalize_vi(extra_text)})

    if multi_texts:
        st.success(f"✅ {len(multi_texts)} tài liệu sẵn sàng")
        for i, d in enumerate(multi_texts):
            st.markdown(f'<div class="doc-card"><div class="doc-title">📄 {d["title"]}</div>'
                        f'{count_words(d["text"]):,} từ · {len(split_sentences(d["text"]))} câu</div>',
                        unsafe_allow_html=True)
        documents  = multi_texts
        multi_mode = True
        # dùng tài liệu đầu tiên làm preview
        input_text   = multi_texts[0]["text"]
        source_label = f"{len(multi_texts)} tài liệu"


# ── Thông tin văn bản hiện tại ────────────────────────────────────────────────
if input_text.strip():
    wc     = count_words(input_text)
    n_sent = len(split_sentences(input_text))
    st.markdown(f'<div class="source-badge">📌 Nguồn: {source_label}</div>', unsafe_allow_html=True)
    st.caption(f"📝 {wc:,} từ · {len(input_text):,} ký tự · {n_sent} câu · "
               f"Chế độ: {'Tỷ lệ '+str(pct_sentences)+'%' if sum_mode=='Tỷ lệ %' else str(num_sentences)+' câu'} · "
               f"Thuật toán: {algorithm}")
else:
    wc = n_sent = 0

st.markdown("---")

# Nút tóm tắt
col_run, col_dl_holder = st.columns([3, 1])
with col_run:
    run = st.button("▶ Tóm tắt" + (" tất cả tài liệu" if multi_mode else ""),
                    type="primary", use_container_width=True,
                    disabled=not input_text.strip())


# ══════════════════════════════════════════════════════════════════════════════
# XỬ LÝ KHI NHẤN NÚT
# ══════════════════════════════════════════════════════════════════════════════

if run and input_text.strip():

    if len(input_text.strip()) < 60:
        st.error("Văn bản quá ngắn (ít nhất 60 ký tự).")
        st.stop()

    all_results: list[dict] = []

    def run_algo(text: str, algo_key: str, k: int) -> str:
        algo_map = {
            "TF-IDF (built-in)":   lambda: tfidf_summarize(text, k),
            "TextRank (built-in)": lambda: textrank_summarize(text, k),
            "Sumy — LSA":          lambda: sumy_summarize(text, k, "LSA"),
            "Sumy — LexRank":      lambda: sumy_summarize(text, k, "LexRank"),
            "Sumy — Luhn":         lambda: sumy_summarize(text, k, "Luhn"),
            "Sumy — TextRank":     lambda: sumy_summarize(text, k, "TextRank"),
        }
        return algo_map.get(algo_key, lambda: tfidf_summarize(text, k))()

    # ── MULTI-DOCUMENT ────────────────────────────────────────────────────────
    if multi_mode and len(documents) > 1:
        st.markdown("---")
        st.markdown(f"### 📚 Kết quả — {len(documents)} tài liệu · {algorithm}")

        for doc in documents:
            k = _resolve_num(doc["text"], sum_mode, num_sentences, pct_sentences)
            st.markdown(f"#### 📄 {doc['title']}")
            with st.spinner(f"Đang xử lý {doc['title']}..."):
                raw     = run_algo(doc["text"], algorithm, k)
                summary = postprocess(raw, domain)
            meta = render_result(summary, algorithm, doc["text"], show_stats=show_stats)
            meta["title"] = doc["title"]
            all_results.append(meta)
            st.markdown("---")

        # Bảng tổng hợp multi-doc
        st.markdown("### 📋 Bảng tổng hợp tất cả tài liệu")
        import pandas as pd
        df_rows = [{
            "Tài liệu":   r["title"],
            "Từ gốc":     r["orig_words"],
            "Từ TT":      r["sum_words"],
            "Câu TT":     r["sum_sent"],
            "Nén":        f"{r['compress']}%",
        } for r in all_results]
        st.dataframe(pd.DataFrame(df_rows), use_container_width=True, hide_index=True)

    # ── SO SÁNH THUẬT TOÁN ────────────────────────────────────────────────────
    elif compare_all:
        st.markdown("---")
        st.markdown("### 📊 So sánh thuật toán")
        k = _resolve_num(input_text, sum_mode, num_sentences, pct_sentences)

        methods: dict = {
            "TF-IDF (built-in)":   lambda: tfidf_summarize(input_text, k),
            "TextRank (built-in)": lambda: textrank_summarize(input_text, k),
        }
        if use_sumy:
            _a = sumy_algo
            methods[f"Sumy {_a}"] = lambda: sumy_summarize(input_text, k, _a)
        if use_gensim:
            def _gensim():
                try:
                    from gensim.summarization import summarize as gs
                    r = gs(input_text, ratio=pct_sentences/100)
                    return r if r.strip() else "Văn bản quá ngắn cho Gensim."
                except ImportError:
                    return "⚠️ Cài: pip install gensim==3.8.3"
                except Exception as e:
                    return f"⚠️ Gensim lỗi: {e}"
            methods["Gensim TextRank"] = _gensim

        tabs = st.tabs(list(methods.keys()))
        results = {}
        for tab, (name, fn) in zip(tabs, methods.items()):
            with tab:
                with st.spinner(f"{name}..."):
                    raw    = fn()
                    result = postprocess(raw, domain)
                results[name] = result
                meta = render_result(result, name, input_text, show_stats=show_stats)
                all_results.append(meta)

        st.markdown("---")
        st.markdown("### 📋 Bảng tổng hợp")
        import pandas as pd
        orig_w = count_words(input_text)
        df_rows = [{
            "Thuật toán":   r["algo"],
            "Số câu TT":    r["sum_sent"],
            "Số từ TT":     r["sum_words"],
            "Tỷ lệ nén":    f"{r['compress']}%",
            "Cần cài":      "Không" if "built-in" in r["algo"] else "sumy/gensim",
        } for r in all_results]
        st.dataframe(pd.DataFrame(df_rows), use_container_width=True, hide_index=True)

    # ── ĐƠN LẺ ────────────────────────────────────────────────────────────────
    else:
        k = _resolve_num(input_text, sum_mode, num_sentences, pct_sentences)
        algo_label = algorithm.replace(" (built-in)","").replace(" — "," ")
        st.markdown("---")
        st.markdown(f"### ✨ Kết quả — {algo_label}  ·  {domain}")
        with st.spinner(f"{algo_label} đang xử lý..."):
            raw     = run_algo(input_text, algorithm, k)
            summary = postprocess(raw, domain)
        meta = render_result(summary, algo_label, input_text, show_stats=show_stats)
        all_results.append(meta)

    # ── THỐNG KÊ VĂN BẢN GỐC ────────────────────────────────────────────────
    if show_stats and input_text:
        render_text_stats(input_text)

    # ── TỪ KHOÁ RAKE ─────────────────────────────────────────────────────────
    if show_rake and input_text:
        st.markdown("---")
        st.markdown("### 🏷️ Từ khoá quan trọng (RAKE)")
        with st.spinner("Trích xuất từ khoá..."):
            render_keywords(input_text, top_n=rake_top)

    # ── DOWNLOAD ──────────────────────────────────────────────────────────────
    if all_results:
        st.markdown("---")
        st.markdown("### ⬇️ Tải xuống kết quả")
        c1, c2 = st.columns(2)
        txt_data  = build_txt_export(all_results)
        json_data = build_json_export(all_results)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        with c1:
            st.download_button("📄 Tải file .txt", data=txt_data,
                               file_name=f"tom_tat_{ts}.txt", mime="text/plain",
                               use_container_width=True)
        with c2:
            st.download_button("🗂️ Tải file .json", data=json_data,
                               file_name=f"tom_tat_{ts}.json", mime="application/json",
                               use_container_width=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("TF-IDF · TextRank · Sumy · RAKE · Multi-document · Tiếng Việt · Không cần API")