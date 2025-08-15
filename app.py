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

    .title-box {
        border: 2px solid #444;
        padding: 10px;
        font-size: 24px;  /* 標題小三級 */
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }

    .word {
        font-size: 36px;
        font-weight: bold;
        font-family: "Times New Roman", serif;
        margin-bottom: 5px;
    }
    .phonetic {
        font-size: 20px;
        color: gray;
        font-family: "Times New Roman", serif;
        margin-bottom: 10px;
    }
    .example {
        font-size: 28px;
        color: #444;
        font-family: "宋体", "SimSun", serif;
        margin-bottom: 15px;
    }
    .option {
        margin-bottom: 5px;
    }
    .user-btn {
        font-size: 36px;
        font-family: "Times New Roman", serif;
        border: 2px solid #444;
        padding: 20px;
        width: 200px;
        text-align: center;
        display: block;
        margin: 10px auto;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# ====== 使用者選擇頁 ======
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<h2 style='font-family: Times New Roman; text-align:center;'>請選擇使用者</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Alex", key="alex_btn"):
        st.session_state.user = "Alex"
        st.experimental_rerun()  # 點擊後立即進入題目頁
    if st.button("Eveline", key="eve_btn"):
        st.session_state.user = "Eveline"
        st.experimental_rerun()  # 點擊後立即進入題目頁

# ====== Google Sheet 設定 ======
if st.session_state.user:
    SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"
    SHEET_NAME = st.session_state.user  # 根據使用者選擇工作表
    CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

    @st.cache_data
    def load_data():
        r = requests.get(CSV_URL)
        r.encoding = 'utf-8-sig'
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
        current_word = st.session_state.question
        if ans == st.session_state.correct:
            st.session_state.score += 1
            st.success("Correct!")
        else:
            st.error(f"Wrong, The word, {current_word}, means {st.session_state.correct}")
        new_question()

    # ====== 首次題目 ======
    if st.session_state.question is None:
        new_question()

    # ====== UI 顯示 ======
    st.markdown(f"<div class='title-box'>IELTS Vocabulary Test</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)  # 選項前空行
    for opt in st.session_state.options:
        st.button(opt, on_click=check_answer, args=(opt,))

    st.write(f"Score：{st.session_state.score} / {st.session_state.total}")
