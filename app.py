import streamlit as st
import pandas as pd
import random

# ====== Google Fonts ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'Playfair Display', serif;
    }
    .word {
        font-size: 36px; /* 單字大小 */
        font-weight: bold;
    }
    .phonetic {
        font-size: 20px; /* 拼音大小 */
        color: gray;
    }
    .example {
        font-size: 28px; /* 例句大小 */
        color: #444;
    }
    </style>
""", unsafe_allow_html=True)

# ====== Google Sheet 設定 ======
SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"
SHEET_NAME = "工作表1"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

data = load_data()

# ====== 初始化 session state ======
if "question" not in st.session_state:
    st.session_state.question = None
    st.session_state.correct = None
    st.session_state.options = []
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.phonetic = ""
    st.session_state.example = ""

# ====== 產生新題目 ======
def new_question():
    row = data.sample(1).iloc[0]
    word = row["english"]
    phonetic = row.get("phonetic", "")
    example = row.get("example", "")
    correct = row["chinese"]
    wrong = data[data["chinese"] != correct]["chinese"].sample(3).tolist()
    options = wrong + [correct]
    random.shuffle(options)

    st.session_state.question = word
    st.session_state.phonetic = phonetic
    st.session_state.example = example
    st.session_state.correct = correct
    st.session_state.options = options

# ====== 檢查答案 ======
def check_answer(ans):
    st.session_state.total += 1
    if ans == st.session_state.correct:
        st.session_state.score += 1
        st.success("答對了！")
    else:
        st.error(f"答錯了！正確答案是：{st.session_state.correct}")
    new_question()  # 答錯也直接換下一題

# ====== 首次題目 ======
if st.session_state.question is None:
    new_question()

# ====== UI 顯示 ======
st.title("📚 英文單字測驗")

st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

for opt in st.session_state.options:
    st.button(opt, on_click=check_answer, args=(opt,))

st.write(f"得分：{st.session_state.score} / {st.session_state.total}")
