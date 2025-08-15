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
        user-select: none;
    }

    .title-box {
        border: 2px solid #444;
        padding: 10px;
        font-size: 24px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
    .word { font-size: 36px; font-weight: bold; font-family: "Times New Roman", serif; margin-bottom:5px; }
    .phonetic { font-size: 20px; color: gray; font-family: "Times New Roman", serif; margin-bottom:10px; }
    .example { font-size: 28px; color: #444; font-family: "宋体", "SimSun", serif; margin-bottom:15px; }
</style>
""", unsafe_allow_html=True)

SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"

def load_data(sheet_name):
    CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    r = requests.get(CSV_URL)
    r.encoding = 'utf-8-sig'
    df = pd.read_csv(io.StringIO(r.text))
    return df

# ====== 使用者選擇 ======
if "user" not in st.session_state:
    st.session_state.user = None

# 顯示選擇頁面
if st.session_state.user is None:
    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    alex_html = "<div class='user-select' onclick=\"window.parent.postMessage({funcName:'select_user', user:'Alex'}, '*')\">Alex</div>"
    eveline_html = "<div class='user-select' onclick=\"window.parent.postMessage({funcName:'select_user', user:'Eveline'}, '*')\">Eveline</div>"
    st.markdown(alex_html, unsafe_allow_html=True)
    st.markdown(eveline_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 使用 streamlit 的 message listener 來捕捉按鈕
    st.components.v1.html("""
        <script>
        const sendUser = (user) => {
            window.parent.postMessage({funcName:'select_user', user:user}, '*')
        };
        window.addEventListener('message', (event) => {
            if(event.data.funcName === 'select_user'){
                fetch(`/__stapi__/set_user?user=${event.data.user}`)
            }
        })
        </script>
    """, height=0)

# 如果已經選擇使用者
if st.session_state.user is not None:
    SHEET_NAME = st.session_state.user
    data = load_data(SHEET_NAME)

    if "question" not in st.session_state:
        st.session_state.question = None
        st.session_state.correct = None
        st.session_state.options = []
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.phonetic = ""
        st.session_state.example = ""

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

    def check_answer(ans):
        st.session_state.total += 1
        current_word = st.session_state.question
        if ans == st.session_state.correct:
            st.session_state.score += 1
            st.success("Correct!")
        else:
            st.error(f"Wrong, The word, {current_word}, means {st.session_state.correct}")
        new_question()

    if st.session_state.question is None:
        new_question()

    st.markdown(f"<div class='title-box'>IELTS Vocabulary Test ({st.session_state.user})</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    for opt in st.session_state.options:
        st.button(opt, on_click=check_answer, args=(opt,))
    st.write(f"Score：{st.session_state.score} / {st.session_state.total}")
