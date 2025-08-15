import streamlit as st
import pandas as pd
import random
import requests
import io
from gtts import gTTS
import base64

# ====== Google Fonts & CSS ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');

    html, body, [class*="css"] {
        font-family: "宋体", "SimSun", "Times New Roman", serif;
    }

    .user-btn {
        font-size: 36px;
        font-family: "Times New Roman", serif;
        border: 2px solid #444;
        padding: 15px;
        text-align: center;
        width: 200px;
        margin: 10px auto;
        display: block;
        cursor: pointer;
    }

    .title-box {
        border: 2px solid #444;
        padding: 10px;
        font-size: 24px;
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
    </style>
""", unsafe_allow_html=True)

# ====== Google Sheet 設定 ======
SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"

def get_csv_url(sheet_name):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data
def load_data(sheet_name):
    CSV_URL = get_csv_url(sheet_name)
    r = requests.get(CSV_URL)
    r.encoding = 'utf-8-sig'
    df = pd.read_csv(io.StringIO(r.text))
    return df

# ====== 初始化 session state ======
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
    st.session_state.used_words = []

# ====== 選擇使用者 ======
def select_user(user_name):
    st.session_state.user = user_name
    st.session_state.data = load_data(user_name)
    new_question()

# ====== 產生新題目 ======
def new_question():
    available = st.session_state.data[~st.session_state.data["english"].isin(st.session_state.used_words)]
    if available.empty:
        st.info("已答完全部題目！")
        return
    row = available.sample(1).iloc[0]
    word = row["english"]
    phonetic = row.get("phonetic", "")
    example = row.get("example", "")
    correct = row["chinese"]
    wrong = st.session_state.data[st.session_state.data["chinese"] != correct]["chinese"].sample(3).tolist()
    options = wrong + [correct]
    random.shuffle(options)

    st.session_state.question = word
    st.session_state.phonetic = phonetic
    st.session_state.example = example
    st.session_state.correct = correct
    st.session_state.options = options
    st.session_state.used_words.append(word)

# ====== 播放語音 ======
def play_audio(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp.mp3")
    audio_file = open("temp.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

# ====== 檢查答案 ======
def check_answer(ans):
    st.session_state.total += 1
    current_word = st.session_state.question
    if ans == st.session_state.correct:
        st.session_state.score += 1
        st.success("Correct!")
    else:
        st.error(f"答錯了！正確答案是：{current_word} {st.session_state.correct}")
    new_question()

# ====== 首頁：選擇使用者 ======
if st.session_state.user is None:
    st.markdown("<h2 style='font-family: Times New Roman; text-align:center;'>Select User</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Alex", key="alex_btn", on_click=lambda: select_user("Alex"))
    st.button("Eveline", key="eve_btn", on_click=lambda: select_user("Eveline"))
else:
    # ====== 題目頁 ======
    st.markdown(f"<div class='title-box'>IELTS Vocabulary Test ({st.session_state.user})</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

    # 播放單字發音
    play_audio(st.session_state.question)

    st.markdown("<br>", unsafe_allow_html=True)
    for opt in st.session_state.options:
        st.button(opt, on_click=check_answer, args=(opt,))

    st.write(f"Score：{st.session_state.score} / {st.session_state.total}")
