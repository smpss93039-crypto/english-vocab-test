import streamlit as st
import pandas as pd
import random
import requests
import io

# ====== Google Fonts & CSS ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
    html, body, [class*="css"] { font-family: "宋体", "SimSun", "Times New Roman", serif; }

    .user-select {
        font-family: "Times New Roman", serif;
        font-size: 32px;
        font-weight: bold;
        border: 3px solid #444;
        width: 150px;
        height: 150px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 20px;
        cursor: pointer;
        text-align: center;
        border-radius: 10px;
    }

    .title-box { border: 2px solid #444; padding: 10px; font-size: 24px; font-weight: bold; display: inline-block; margin-bottom: 15px; }
    .word { font-size: 36px; font-weight: bold; font-family: "Times New Roman", serif; margin-bottom:5px; }
    .phonetic { font-size: 20px; color: gray; font-family: "Times New Roman", serif; margin-bottom:10px; }
    .example { font-size: 28px; color: #444; font-family: "宋体", "SimSun", serif; margin-bottom:15px; }
</style>
""", unsafe_allow_html=True)

# ====== Google Sheet 讀取 ======
SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"
def load_data(sheet_name):
    CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    r = requests.get(CSV_URL)
    r.encoding = 'utf-8-sig'
    return pd.read_csv(io.StringIO(r.text))

# ====== session_state 初始化 ======
if "user" not in st.session_state:
    st.session_state.user = None
if "question" not in st.session_state:
    st.session_state.question = None
    st.session_state.correct = None
    st.session_state.options = []
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.phonetic = ""
    st.session_state.example = ""

# ====== 使用者選擇頁面 ======
if st.session_state.user is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Alex"):
            st.session_state.user = "Alex"
    with col2:
        if st.button("Eveline"):
            st.session_state.user = "Eveline"
    st.stop()  # 停止執行，等使用者選擇

# ====== 題目資料 ======
data = load_data(st.session_state.user)

# ====== 產生題目 ======
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
    current_word = st.session_state.question
    if ans == st.session_state.correct:
        st.session_state.score += 1
        st.success("Correct!")
    else:
        st.error(f"Wrong, The word, {current_word}, means {st.session_state.correct}")
    new_question()

# ====== 初始化題目 ======
if st.session_state.question is None:
    new_question()

# ====== UI 顯示 ======
st.markdown(f"<div class='title-box'>IELTS Vocabulary Test ({st.session_state.user})</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
for opt in st.session_state.options:
    st.button(opt, on_click=check_answer, args=(opt,))
st.write(f"Score：{st.session_state.score} / {st.session_state.total}")
