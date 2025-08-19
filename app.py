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

    .user-btn {
        font-size: 36px;  /* 比題目大三級 */
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
        font-family: "Times New Roman", serif;  /* 跟 .word 一樣的字體，不加粗 */
        margin-bottom: 15px;
    }
    .option {
        margin-bottom: 5px;
    }
    .review-title {
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0 20px 0;
        font-family: "Times New Roman", serif;
    }
    .review-item {
        margin: 8px 0 16px 0;
    }
    .divider {
        height: 1px;
        background: #ddd;
        margin: 8px 0 12px 0;
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
    st.session_state.used_indices = set()   # 全局已出現題目索引（避免跨 part 重複）
    st.session_state.data = None

# 新增：每 30 題一個 part 的狀態
if "block_count" not in st.session_state:
    st.session_state.block_count = 0        # 目前這個 part 已作答題數
if "wrong_list" not in st.session_state:
    st.session_state.wrong_list = []        # 本 part 答錯清單：[(word, example), ...]
if "in_review" not in st.session_state:
    st.session_state.in_review = False      # 是否在檢討頁面

BLOCK_SIZE = 30  # 每個 part 的題數

# ====== 選擇使用者 ======
def select_user(user_name):
    st.session_state.user = user_name
    st.session_state.data = load_data(user_name)
    st.session_state.used_indices = set()  # 切換使用者時重置已用題目
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.block_count = 0
    st.session_state.wrong_list = []
    st.session_state.in_review = False
    new_question()

# ====== 產生新題目（不重複） ======
def new_question():
    df = st.session_state.data
    available_indices = set(df.index) - st.session_state.used_indices
    if not available_indices:
        st.success("Finish All the Questions")
        st.session_state.question = None
        st.session_state.options = []
        return
    idx = random.choice(list(available_indices))
    st.session_state.used_indices.add(idx)

    row = df.loc[idx]
    word = row["english"]
    phonetic = row.get("phonetic", "")
    example = row.get("example", "")
    correct = row["chinese"]

    # 準備選項
    wrong_pool = df[df["chinese"] != correct]["chinese"]
    if len(wrong_pool) >= 3:
        wrong = wrong_pool.sample(3).tolist()
    else:
        # 若資料不足，隨機補齊（避免當機）
        wrong = wrong_pool.sample(min(3, len(wrong_pool))).tolist()
        while len(wrong) < 3:
            wrong.append(correct)  # 退而求其次，但後面會 shuffle
    options = wrong + [correct]
    random.shuffle(options)

    st.session_state.question = word
    st.session_state.phonetic = phonetic
    st.session_state.example = example
    st.session_state.correct = correct
    st.session_state.options = options

# ====== 檢查答案 ======
def check_answer(ans):
    # 累積全程分數
    st.session_state.total += 1
    current_word = st.session_state.question
    current_example = st.session_state.example

    if ans == st.session_state.correct:
        st.session_state.score += 1
        st.success("Correct!")
    else:
        st.error(f"Wrong！{current_word} means {st.session_state.correct}")
        # 記錄本 part 的錯題（只需要 Word & Example）
        st.session_state.wrong_list.append((current_word, current_example))

    # 累積本 part 題數
    st.session_state.block_count += 1

    # 若達到 BLOCK_SIZE，切到檢討頁面
    if st.session_state.block_count >= BLOCK_SIZE:
        st.session_state.in_review = True
        return  # 不再出新題，交給主畫面改顯示檢討頁
    else:
        new_question()

# ====== 檢討頁 Continue ======
def proceed_next_block():
    # 重置本 part 計數與錯題清單，開始下一個 part
    st.session_state.block_count = 0
    st.session_state.wrong_list = []
    st.session_state.in_review = False
    new_question()

# ====== 首頁：選擇使用者 ======
if st.session_state.user is None:
    st.markdown("<h2 style='font-family: Times New Roman; text-align:center;'>Select User</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Alex", key="alex_btn", on_click=lambda: select_user("Alex"))
    st.button("Eveline", key="eve_btn", on_click=lambda: select_user("Eveline"))

else:
    # 檢討頁（每 30 題出現一次）
    if st.session_state.in_review:
        st.markdown(f"<div class='title-box'>Review (Last {BLOCK_SIZE} Questions)</div>", unsafe_allow_html=True)
        st.markdown("<div class='review-title'>Wrong Answers Lists</div>", unsafe_allow_html=True)

        if len(st.session_state.wrong_list) == 0:
            st.info("All Correct")
        else:
            # 顯示 Word & Example 清單
            for i, (w, ex) in enumerate(st.session_state.wrong_list, start=1):
                st.markdown(f"<div class='review-item'><div class='word'>{w}</div><div class='example'>{ex}</div></div>", unsafe_allow_html=True)
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Continue", on_click=proceed_next_block)

    # 題目頁
    else:
        st.markdown(f"<div class='title-box'>IELTS Vocabulary Test ({st.session_state.user})</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.question is None:
            # 沒題目可出時，顯示完成
            st.success("Finish All the Questions")
        else:
            st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            for opt in st.session_state.options:
                st.button(opt, on_click=check_answer, args=(opt,))

        st.write(f"Score：{st.session_state.score} / {st.session_state.total}  |  Part Progress：{st.session_state.block_count} / {BLOCK_SIZE}")
