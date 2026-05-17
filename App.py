"""
Công cụ Tóm Tắt Văn Bản AI
============================
Chạy: streamlit run app.py

Cài đặt thư viện:
    pip install streamlit anthropic sumy gensim nltk rake-nltk

Yêu cầu:
    - Python >= 3.9
    - Biến môi trường ANTHROPIC_API_KEY hoặc nhập key trực tiếp trong sidebar
"""

import os
import re
import time
import streamlit as st

# ── Cấu hình trang ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tóm Tắt Văn Bản AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS tuỳ chỉnh ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; max-width: 1100px; }
    .stTextArea textarea { font-size: 14px; line-height: 1.75; }
    .metric-row { display: flex; gap: 12px; margin: 1rem 0; flex-wrap: wrap; }
    .metric-card {
        background: #f5f5f3; border-radius: 10px; padding: 14px 20px;
        text-align: center; flex: 1; min-width: 100px;
    }
    .metric-val { font-size: 24px; font-weight: 600; color: #1D9E75; }
    .metric-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: .05em; margin-top: 2px; }
    .summary-box {
        background: #f0faf6; border: 1px solid #9FE1CB; border-radius: 10px;
        padding: 1.2rem 1.5rem; font-size: 14px; line-height: 1.8;
        white-space: pre-wrap; color: #1a1a18;
    }
    .original-box {
        background: #fafaf8; border: 1px solid #e0e0dc; border-radius: 10px;
        padding: 1.2rem 1.5rem; font-size: 13px; line-height: 1.75;
        max-height: 320px; overflow-y: auto; color: #444;
    }
    .tag { display:inline-block; background:#1D9E75; color:#fff; border-radius:20px;
           padding: 3px 12px; font-size: 12px; font-weight: 500; margin-right:6px; }
    .bar-wrap { background:#e8e8e4; border-radius:4px; height:8px; margin:6px 0 12px; overflow:hidden; }
    .bar-fill { background:#1D9E75; height:100%; border-radius:4px; transition: width .5s; }
    h2.section-title { font-size: 16px; font-weight: 600; margin: 1.5rem 0 .5rem; color: #1a1a18; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: đếm từ
# ══════════════════════════════════════════════════════════════════════════════
def count_words(text: str) -> int:
    return len(text.strip().split()) if text.strip() else 0


# ══════════════════════════════════════════════════════════════════════════════
# PHƯƠNG PHÁP 1 — ABSTRACTIVE (Claude API)
# ══════════════════════════════════════════════════════════════════════════════
def summarize_abstractive(
    text: str,
    domain: str,
    length: str,
    style: str,
    language: str,
    api_key: str,
) -> str:
    """Tóm tắt dùng Claude API (Abstractive)."""
    try:
        import anthropic
    except ImportError:
        return "⚠️ Chưa cài thư viện anthropic. Chạy: pip install anthropic"

    domain_prompts = {
        "Tổng quát":   "Tóm tắt văn bản một cách tổng quát, giữ lại các thông tin quan trọng nhất.",
        "Báo chí":     "Đây là bài báo/tin tức. Tóm tắt theo cấu trúc báo chí: sự kiện chính, ai-cái gì-ở đâu-khi nào-tại sao, tác động.",
        "Giáo dục":    "Đây là tài liệu giáo dục. Tóm tắt các khái niệm chính, luận điểm cốt lõi và kết luận quan trọng.",
        "Pháp lý":     "Đây là văn bản pháp lý/hợp đồng. Tóm tắt các điều khoản chính, quyền/nghĩa vụ các bên, thời hạn và điều kiện quan trọng.",
        "Y tế":        "Đây là tài liệu y tế/hồ sơ bệnh án. Tóm tắt chẩn đoán, kết quả xét nghiệm chính, và phương án điều trị.",
    }
    length_guide = {"Ngắn (~50 từ)": "khoảng 50 từ", "Vừa (~150 từ)": "khoảng 150 từ", "Dài (~300 từ)": "khoảng 300 từ"}
    style_guide  = {
        "Đoạn văn":         "Trình bày dưới dạng đoạn văn mạch lạc.",
        "Gạch đầu dòng":    "Trình bày dưới dạng các gạch đầu dòng ngắn gọn, mỗi điểm 1-2 câu.",
        "Có cấu trúc":      "Trình bày có cấu trúc rõ ràng với tiêu đề phụ (Nội dung chính, Kết luận, Điểm nổi bật).",
    }
    lang_guide = {"Tiếng Việt": "Trả lời bằng Tiếng Việt.", "Tiếng Anh": "Respond in English.", "Giữ nguyên": "Respond in the same language as the input text."}

    prompt = f"""{domain_prompts.get(domain, domain_prompts['Tổng quát'])}

Yêu cầu:
- Độ dài: {length_guide.get(length, 'khoảng 150 từ')}
- Định dạng: {style_guide.get(style, style_guide['Đoạn văn'])}
- Ngôn ngữ: {lang_guide.get(language, lang_guide['Tiếng Việt'])}
- Chỉ trả về bản tóm tắt, không thêm giải thích hay lời dẫn.

Văn bản cần tóm tắt:
{text}"""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ══════════════════════════════════════════════════════════════════════════════
# PHƯƠNG PHÁP 2 — EXTRACTIVE (sumy)
# ══════════════════════════════════════════════════════════════════════════════
def summarize_extractive_sumy(text: str, ratio: float = 0.3, algorithm: str = "LSA") -> str:
    """Tóm tắt trích xuất dùng sumy."""
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.summarizers.lex_rank import LexRankSummarizer
        from sumy.summarizers.luhn import LuhnSummarizer
        from sumy.summarizers.text_rank import TextRankSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words
    except ImportError:
        return "⚠️ Chưa cài thư viện sumy. Chạy: pip install sumy"

    SUMMARIZER_MAP = {
        "LSA":      LsaSummarizer,
        "LexRank":  LexRankSummarizer,
        "Luhn":     LuhnSummarizer,
        "TextRank": TextRankSummarizer,
    }

    language = "english"  # sumy dùng stemmer tiếng Anh; với tiếng Việt dùng "english" fallback
    parser    = PlaintextParser.from_string(text, Tokenizer(language))
    stemmer   = Stemmer(language)
    SummarizerClass = SUMMARIZER_MAP.get(algorithm, LsaSummarizer)
    summarizer = SummarizerClass(stemmer)
    summarizer.stop_words = get_stop_words(language)

    sentence_count = max(2, int(len(parser.document.sentences) * ratio))
    sentences = summarizer(parser.document, sentence_count)
    return " ".join(str(s) for s in sentences)


# ══════════════════════════════════════════════════════════════════════════════
# PHƯƠNG PHÁP 3 — EXTRACTIVE (RAKE keyword extraction)
# ══════════════════════════════════════════════════════════════════════════════
def extract_keywords_rake(text: str, top_n: int = 10) -> list[str]:
    """Trích xuất từ khoá dùng RAKE."""
    try:
        from rake_nltk import Rake
        import nltk
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)

        r = Rake()
        r.extract_keywords_from_text(text)
        return r.get_ranked_phrases()[:top_n]
    except ImportError:
        return ["⚠️ Chưa cài rake-nltk. Chạy: pip install rake-nltk nltk"]


# ══════════════════════════════════════════════════════════════════════════════
# PHƯƠNG PHÁP 4 — EXTRACTIVE (gensim TextRank)
# ══════════════════════════════════════════════════════════════════════════════
def summarize_gensim(text: str, ratio: float = 0.3) -> str:
    """Tóm tắt dùng gensim TextRank."""
    try:
        from gensim.summarization import summarize as gensim_summarize
        result = gensim_summarize(text, ratio=ratio)
        return result if result.strip() else "Văn bản quá ngắn để tóm tắt bằng Gensim."
    except ImportError:
        return "⚠️ Chưa cài gensim. Chạy: pip install gensim==3.8.3"
    except Exception as e:
        return f"⚠️ Gensim lỗi: {e}. Văn bản cần đủ dài (>100 từ) và nhiều câu."


# ══════════════════════════════════════════════════════════════════════════════
# VĂN BẢN MẪU
# ══════════════════════════════════════════════════════════════════════════════
EXAMPLES = {
    "📰 Bài báo VnExpress": """Hà Nội, ngày 14 tháng 5 năm 2026 - Chính phủ Việt Nam vừa công bố gói đầu tư 50.000 tỷ đồng nhằm phát triển hạ tầng giao thông tại các tỉnh miền Trung trong giai đoạn 2026-2030. Đây được xem là một trong những gói đầu tư lớn nhất từ trước đến nay dành cho khu vực này, với mục tiêu kết nối các tỉnh từ Thanh Hóa đến Bình Thuận thông qua hệ thống đường cao tốc hiện đại.

Theo Bộ Giao thông Vận tải, dự án sẽ bao gồm mở rộng và nâng cấp tuyến đường cao tốc Bắc-Nam với tổng chiều dài hơn 800 km, xây dựng thêm 12 nút giao thông mới, và cải tạo toàn bộ hệ thống cầu vượt tại các điểm xung yếu. Dự kiến đến năm 2028, các tuyến đường chính sẽ hoàn thành và đưa vào sử dụng.

Nhiều chuyên gia kinh tế cho rằng gói đầu tư này không chỉ giải quyết bài toán ách tắc giao thông vốn là điểm yếu của miền Trung, mà còn tạo ra khoảng 200.000 việc làm trực tiếp và gián tiếp trong suốt thời gian thi công. Bộ trưởng Bộ Giao thông Vận tải cam kết áp dụng cơ chế giám sát chặt chẽ để đảm bảo tính minh bạch và chống thất thoát.""",

    "⚖️ Hợp đồng pháp lý": """ĐIỀU 1. CÁC BÊN THAM GIA HỢP ĐỒNG. Hợp đồng này được ký kết giữa Công ty TNHH Phát Triển Phần Mềm Sao Mai (sau đây gọi là "Bên Cung Cấp Dịch Vụ") và Công ty Cổ phần Thương Mại Bình Minh (sau đây gọi là "Khách Hàng").

ĐIỀU 2. PHẠM VI DỊCH VỤ. Bên Cung Cấp Dịch Vụ cam kết triển khai hệ thống quản lý bán hàng tích hợp bao gồm: (a) Phần mềm ERP tùy chỉnh cho 3 chi nhánh; (b) Module quản lý kho hàng thời gian thực; (c) Ứng dụng di động cho nhân viên kinh doanh; (d) Hệ thống báo cáo tự động. Thời gian triển khai không quá 6 tháng kể từ ngày ký hợp đồng.

ĐIỀU 3. GIÁ TRỊ HỢP ĐỒNG VÀ PHƯƠNG THỨC THANH TOÁN. Tổng giá trị hợp đồng là 1.800.000.000 đồng. Thanh toán theo 3 đợt: 30% khi ký hợp đồng, 40% khi hoàn thành giai đoạn 1, 30% khi nghiệm thu toàn bộ hệ thống.

ĐIỀU 4. BẢO HÀNH VÀ HỖ TRỢ KỸ THUẬT. Bên Cung Cấp Dịch Vụ bảo hành hệ thống trong 24 tháng kể từ ngày nghiệm thu. Cam kết sửa lỗi trong vòng 24 giờ đối với lỗi nghiêm trọng và 72 giờ đối với lỗi thông thường. Hỗ trợ kỹ thuật qua hotline 24/7.

ĐIỀU 5. ĐIỀU KHOẢN BẢO MẬT. Cả hai bên cam kết bảo mật toàn bộ thông tin liên quan đến hợp đồng, dữ liệu kinh doanh trong thời gian 5 năm sau khi hợp đồng kết thúc.""",

    "🏥 Hồ sơ y tế": """BÁO CÁO THĂM KHÁM LÂM SÀNG - Ngày: 14/05/2026 - Bệnh nhân: Nguyễn Văn A, 58 tuổi, nam giới.

Lý do nhập viện: Bệnh nhân được đưa vào khoa Tim mạch vì đau ngực trái dữ dội kèm khó thở, xuất hiện đột ngột khoảng 2 giờ trước khi nhập viện. Tiền sử tăng huyết áp 10 năm, đái tháo đường type 2 được chẩn đoán 5 năm trước, đang điều trị bằng Metformin 500mg x 2 lần/ngày và Amlodipine 5mg/ngày.

Kết quả xét nghiệm: Troponin I: 2.8 ng/mL (tăng cao); CK-MB: 45 U/L (tăng); ECG: ST chênh lên ở các chuyển đạo II, III, aVF gợi ý nhồi máu cơ tim cấp vùng thành sau-dưới; Siêu âm tim: EF 45%; HbA1c: 8.2%; Huyết áp: 165/100 mmHg; Đường huyết: 12.3 mmol/L.

Chẩn đoán: Nhồi máu cơ tim cấp ST chênh lên vùng thành sau-dưới (STEMI inferior). Tăng huyết áp không kiểm soát tốt. Đái tháo đường type 2 kiểm soát kém.

Hướng xử trí: Can thiệp mạch vành qua da (PCI) cấp cứu. Aspirin 300mg tải, Ticagrelor 180mg tải. Heparin 5000 IU tiêm tĩnh mạch. Nitroglycerin truyền tĩnh mạch kiểm soát huyết áp và đau ngực.""",
}


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("⚙️ Cài đặt")

    st.subheader("🔑 API Key")
    api_key = st.text_input(
        "Anthropic API Key",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        type="password",
        placeholder="sk-ant-...",
        help="Lấy key tại: https://console.anthropic.com",
    )

    st.divider()
    st.subheader("📋 Lĩnh vực")
    domain = st.selectbox("Chọn lĩnh vực", ["Tổng quát", "Báo chí", "Giáo dục", "Pháp lý", "Y tế"])

    st.subheader("📏 Tùy chỉnh")
    length   = st.selectbox("Độ dài tóm tắt", ["Ngắn (~50 từ)", "Vừa (~150 từ)", "Dài (~300 từ)"], index=1)
    style    = st.selectbox("Phong cách",      ["Đoạn văn", "Gạch đầu dòng", "Có cấu trúc"])
    language = st.selectbox("Ngôn ngữ đầu ra", ["Tiếng Việt", "Tiếng Anh", "Giữ nguyên"])

    st.divider()
    st.subheader("🔬 So sánh phương pháp")
    compare_mode = st.checkbox("Bật chế độ so sánh", value=False, help="So sánh Abstractive vs Extractive")

    if compare_mode:
        st.caption("Các thuật toán extractive:")
        use_sumy     = st.checkbox("Sumy (LSA / LexRank / Luhn / TextRank)", value=True)
        sumy_algo    = st.selectbox("Thuật toán Sumy", ["LSA", "LexRank", "Luhn", "TextRank"]) if use_sumy else None
        use_gensim   = st.checkbox("Gensim TextRank", value=False)
        use_rake     = st.checkbox("RAKE Keywords",   value=True)
        sumy_ratio   = st.slider("Tỷ lệ trích xuất", 0.1, 0.5, 0.3, 0.05) if (use_sumy or use_gensim) else 0.3


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.title("◈ Tóm Tắt Văn Bản AI")
st.caption("Hỗ trợ Tiếng Việt & Tiếng Anh · Abstractive (Claude) + Extractive (sumy, gensim, RAKE)")

# Văn bản mẫu
col_ex, _ = st.columns([3, 1])
with col_ex:
    example_choice = st.selectbox("Tải văn bản mẫu:", ["— chọn mẫu —"] + list(EXAMPLES.keys()))

# Input
default_text = EXAMPLES.get(example_choice, "") if example_choice != "— chọn mẫu —" else ""
input_text = st.text_area(
    "Văn bản đầu vào",
    value=default_text,
    height=220,
    placeholder="Dán văn bản cần tóm tắt vào đây...",
)

word_count = count_words(input_text)
st.caption(f"📝 {word_count:,} từ · {len(input_text):,} ký tự")

# Nút tóm tắt
run_btn = st.button("✦ Tóm tắt ngay", type="primary", use_container_width=True, disabled=(not input_text.strip()))

# ── Xử lý ────────────────────────────────────────────────────────────────────
if run_btn and input_text.strip():

    if len(input_text.strip()) < 50:
        st.error("Vui lòng nhập văn bản có ít nhất 50 ký tự.")
        st.stop()

    # ── Abstractive (Claude) ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🤖 Kết quả tóm tắt (Abstractive — Claude API)")

    if not api_key:
        st.warning("⚠️ Chưa nhập API Key. Nhập key trong sidebar để dùng Claude.")
        abstract_summary = None
    else:
        with st.spinner("Claude đang tóm tắt..."):
            t0 = time.time()
            try:
                abstract_summary = summarize_abstractive(input_text, domain, length, style, language, api_key)
                elapsed = time.time() - t0
            except Exception as e:
                st.error(f"Lỗi Claude API: {e}")
                abstract_summary = None
                elapsed = 0

        if abstract_summary:
            # Thống kê
            orig_w = count_words(input_text)
            sum_w  = count_words(abstract_summary)
            comp   = max(0, round((1 - sum_w / orig_w) * 100)) if orig_w else 0
            rt     = max(1, round(sum_w / 3))

            st.markdown(f"""
<div class="metric-row">
  <div class="metric-card"><div class="metric-val">{orig_w:,}</div><div class="metric-label">Từ gốc</div></div>
  <div class="metric-card"><div class="metric-val">{sum_w:,}</div><div class="metric-label">Từ tóm tắt</div></div>
  <div class="metric-card"><div class="metric-val">{comp}%</div><div class="metric-label">Tỷ lệ nén</div></div>
  <div class="metric-card"><div class="metric-val">{rt}s</div><div class="metric-label">Thời gian đọc</div></div>
  <div class="metric-card"><div class="metric-val">{elapsed:.1f}s</div><div class="metric-label">Thời gian xử lý</div></div>
</div>
<div class="bar-wrap"><div class="bar-fill" style="width:{min(comp,98)}%"></div></div>
""", unsafe_allow_html=True)

            # So sánh song song
            col_orig, col_sum = st.columns(2)
            with col_orig:
                st.markdown("**📄 Văn bản gốc**")
                preview = input_text[:700] + ("…" if len(input_text) > 700 else "")
                st.markdown(f'<div class="original-box">{preview}</div>', unsafe_allow_html=True)
            with col_sum:
                st.markdown("**✨ Bản tóm tắt AI**")
                st.markdown(f'<div class="summary-box">{abstract_summary}</div>', unsafe_allow_html=True)

            st.download_button(
                "⬇️ Tải bản tóm tắt (.txt)",
                data=abstract_summary,
                file_name="tom_tat.txt",
                mime="text/plain",
            )

    # ── Extractive (nếu bật compare mode) ────────────────────────────────────
    if compare_mode:
        st.markdown("---")
        st.markdown("### 🔬 So sánh phương pháp Extractive")

        tabs_names = []
        if use_sumy:   tabs_names.append(f"Sumy ({sumy_algo})")
        if use_gensim: tabs_names.append("Gensim TextRank")
        if use_rake:   tabs_names.append("RAKE Keywords")

        if tabs_names:
            tabs = st.tabs(tabs_names)
            tab_idx = 0

            if use_sumy:
                with tabs[tab_idx]:
                    with st.spinner(f"Sumy {sumy_algo} đang xử lý..."):
                        result = summarize_extractive_sumy(input_text, ratio=sumy_ratio, algorithm=sumy_algo)
                    st.markdown(f'<div class="summary-box">{result}</div>', unsafe_allow_html=True)
                    w = count_words(result)
                    orig_w = count_words(input_text)
                    st.caption(f"📊 {w} từ · Nén {max(0, round((1 - w/orig_w)*100))}% · Thuật toán: {sumy_algo}")
                tab_idx += 1

            if use_gensim:
                with tabs[tab_idx]:
                    with st.spinner("Gensim đang xử lý..."):
                        result = summarize_gensim(input_text, ratio=sumy_ratio)
                    st.markdown(f'<div class="summary-box">{result}</div>', unsafe_allow_html=True)
                    w = count_words(result)
                    orig_w = count_words(input_text)
                    st.caption(f"📊 {w} từ · Nén {max(0, round((1 - w/orig_w)*100))}% · Thuật toán: TextRank (gensim)")
                tab_idx += 1

            if use_rake:
                with tabs[tab_idx]:
                    with st.spinner("RAKE đang trích xuất từ khoá..."):
                        keywords = extract_keywords_rake(input_text, top_n=12)
                    st.markdown("**Từ khoá quan trọng nhất:**")
                    tags_html = " ".join(f'<span class="tag">{kw}</span>' for kw in keywords)
                    st.markdown(tags_html, unsafe_allow_html=True)
                    st.caption(f"📊 {len(keywords)} cụm từ khoá được trích xuất")
                tab_idx += 1

        # Bảng so sánh tổng hợp
        if abstract_summary:
            st.markdown("---")
            st.markdown("### 📊 Bảng so sánh tổng hợp")
            rows = []
            orig_w = count_words(input_text)

            rows.append({
                "Phương pháp": "🤖 Claude (Abstractive)",
                "Số từ": count_words(abstract_summary),
                "Tỷ lệ nén": f"{max(0, round((1 - count_words(abstract_summary)/orig_w)*100))}%",
                "Ưu điểm": "Hiểu ngữ nghĩa, viết lại mạch lạc",
                "Nhược điểm": "Cần API key, tốn chi phí",
            })
            if use_sumy:
                r = summarize_extractive_sumy(input_text, sumy_ratio, sumy_algo)
                rows.append({
                    "Phương pháp": f"📌 Sumy {sumy_algo} (Extractive)",
                    "Số từ": count_words(r),
                    "Tỷ lệ nén": f"{max(0, round((1 - count_words(r)/orig_w)*100))}%",
                    "Ưu điểm": "Không cần API, giữ câu gốc",
                    "Nhược điểm": "Không viết lại, kém mạch lạc",
                })
            if use_gensim:
                r = summarize_gensim(input_text, sumy_ratio)
                rows.append({
                    "Phương pháp": "🔗 Gensim TextRank (Extractive)",
                    "Số từ": count_words(r),
                    "Tỷ lệ nén": f"{max(0, round((1 - count_words(r)/orig_w)*100))}%",
                    "Ưu điểm": "Offline, nhanh, miễn phí",
                    "Nhược điểm": "Cần văn bản dài, tiếng Anh tốt hơn",
                })

            import pandas as pd
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Powered by **Claude API** (claude-sonnet-4-20250514) · sumy · gensim · RAKE-NLTK · Streamlit")
