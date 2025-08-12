import streamlit as st
import pandas as pd
import random

# Google Fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Playfair Display', serif;
    }
    </style>
""", unsafe_allow_html=True)

# 讀取雲端 CSV
CSV_URL = "https://drive.google.com/uc?export=download&id=13uFgMOeJUGgnd6GS9xBYUAfulSkRLtID"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

data = load_data()

st.title("📚 英文單字測驗")

# 初始化 session state
if "question" not in st.session_state:
    st.session_state.question = None
    st.session_state.correct = None
    st.session_state.options = []
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.show_next_button = False
    st.session_state.phonetic = ""   # 加上這兩行初始化
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
    st.session_state.show_next_button = False

def check_answer(ans):
    st.session_state.total += 1
    if ans == st.session_state.correct:
        st.success("答對了！")
        st.session_state.score += 1
        new_question()
    else:
        st.error(f"答錯了！正確答案是：{st.session_state.correct}")
        st.session_state.show_next_button = True

if st.session_state.question is None:
    new_question()

# 顯示題目
st.subheader(f"{st.session_state.question} {st.session_state.phonetic}")
st.caption(st.session_state.example)

# 顯示選項按鈕
if not st.session_state.show_next_button:
    for opt in st.session_state.options:
        st.button(opt, on_click=check_answer, args=(opt,))
else:
    if st.button("下一頁"):
        new_question()

st.write(f"得分：{st.session_state.score} / {st.session_state.total}")
