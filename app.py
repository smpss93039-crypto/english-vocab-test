import gspread
import pandas as pd
import streamlit as st
import random
from oauth2client.service_account import ServiceAccountCredentials

# ====== Google Fonts ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');
html, body, [class*="css"] {
    font-family: 'Playfair Display', serif;
}
.word { font-size: 36px; font-weight: bold; }
.phonetic { font-size: 20px; color: gray; }
.example { font-size: 28px; color: #444; }
</style>
""", unsafe_allow_html=True)

# ====== Google Sheet 讀取 ======
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA").worksheet("工作表1")
data = pd.DataFrame(sheet.get_all_records())

# ====== session state 初始化 ======
if "question" not in st.session_state:
    st.session_state.question = None
    st.session_state.correct = None
    st.session_state.options = []
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.phonetic = ""
    st.session_state.example = ""

# ====== 新題目 ======
def new_question():
    row = data.sample(1).iloc[0]
    st.session_state.question = row["english"]
    st.session_state.phonetic = row.get("phonetic", "")
    st.session_state.example = row.get("example", "")
    st.session_state.correct = row["chinese"]
    wrong = data[data["chinese"] != row["chinese"]]["chinese"].sample(3).tolist()
    st.session_state.options = random.sample(wrong + [row["chinese"]], 4)

# ====== 檢查答案 ======
def check_answer(ans):
    st.session_state.total += 1
    if ans == st.session_state.correct:
        st.session_state.score += 1
        st.success("Correct!")
    else:
        st.error(f"Wrong! Correct answer: {st.session_state.correct}")
    new_question()

if st.session_state.question is None:
    new_question()

# ====== UI ======
st.title("IELTS Vocabulary Test")
st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

for opt in st.session_state.options:
    st.button(opt, on_click=check_answer, args=(opt,))

st.write(f"Score: {st.session_state.score} / {st.session_state.total}")
