import streamlit as st
import pandas as pd
import random

# ====== Google Fonts & CSS ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'Playfair Display', serif;
    }
    .word {
        font-size: 36px; /* 單字最大 */
        font-weight: bold;
        margin-bottom: 5px;
    }
    .phonetic {
        font-size: 20px; /* 拼音小三級 */
        color: gray;
        margin-bottom: 10px;
    }
    .example {
        font-size: 28px; /* 例句小一級 */
        color: #444;
        margin-bottom: 20px;
    }
    .option-btn {
        width: 100%;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ====== Google Sheet 設定 ======
SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"
SHEET_NAME = "工作表1"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL, encoding="utf-8-sig")
    df.fillna("", inplace=True)
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
        st.success("Correct!")
    else:
        st.error(f"Wrong! The correct answer is：{st.session_state.correct}")
    new_question()

# ====== 首次題目 ======
if st.session_state.question is None:
    new_question()

# ====== UI 顯示 ======
st.title("IELTS Vocabulary Test")

st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

# 顯示選項按鈕
for opt in st.session_state.options:
    st.button(opt, on_click=check_answer, args=(opt,), key=opt)

st.write(f"Score：{st.session_state.score} / {st.session_state.total}")
