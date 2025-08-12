import streamlit as st
import pandas as pd
import random

# 讀取雲端 CSV
CSV_URL = "https://drive.google.com/uc?export=download&id=1VKyOWt2D09Qq7QkV4xr5bet4GuCZ7vxl"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

data = load_data()

st.title("📚 英文單字測驗")

# 題目生成
if "question" not in st.session_state:
    st.session_state.question = None
    st.session_state.correct = None
    st.session_state.options = []
    st.session_state.score = 0
    st.session_state.total = 0

def new_question():
    row = data.sample(1).iloc[0]
    word = row["english"]
    correct = row["chinese"]
    wrong = data[data["chinese"] != correct]["chinese"].sample(3).tolist()
    options = wrong + [correct]
    random.shuffle(options)
    st.session_state.question = word
    st.session_state.correct = correct
    st.session_state.options = options

# 按鈕回饋
def check_answer(ans):
    st.session_state.total += 1
    if ans == st.session_state.correct:
        st.success("✅ 答對了！")
        st.session_state.score += 1
    else:
        st.error(f"❌ 答錯了！正確答案是：{st.session_state.correct}")
    new_question()

if st.session_state.question is None:
    new_question()

# 顯示題目
st.subheader(f"請選出 {st.session_state.question} 的中文意思")

# 顯示選項按鈕
for opt in st.session_state.options:
    st.button(opt, on_click=check_answer, args=(opt,))

st.write(f"得分：{st.session_state.score} / {st.session_state.total}")
