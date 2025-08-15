import streamlit as st
import pandas as pd
import random
import requests
import io

# ====== Google Fonts & CSS ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');

    html, body, [class*="css"] {
        font-family: "宋体", "SimSun", "Times New Roman", serif;
    }

    .word {
        font-size: 36px;
        font-weight: bold;
        font-family: "Times New Roman", serif;
    }
    .phonetic {
        font-size: 20px;
        color: gray;
        font-family: "Times New Roman", serif;
    }
    .example {
        font-size: 28px;
        color: #444;
        font-family: "宋体", "SimSun", serif;
    }
    </style>
""", unsafe_allow_html=True)


# ====== Google Sheet 設定 ======
SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"
SHEET_NAME = "工作表1"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_data():
    r = requests.get(CSV_URL)
    r.encoding = 'utf-8-sig'  # 避免 Unicode 問題
    df = pd.read_csv(io.StringIO(r.text))
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
    # 將按鈕對應的單字存在變數
    current_word = st.session_state.question
    if ans == st.session_state.correct:
        st.session_state.score += 1
        st.success("Correct!")
    else:
        st.error(f"Wrong, The word," " {current_word}, means " " {st.session_state.correct}")
    new_question()


# ====== 首次題目 ======
if st.session_state.question is None:
    new_question()

# ====== UI 顯示 ======
st.title("IELTS Vocabulary Test")

st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

for opt in st.session_state.options:
    st.button(opt, on_click=check_answer, args=(opt,))

st.write(f"Score：{st.session_state.score} / {st.session_state.total}")
