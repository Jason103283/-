import streamlit as st
import re
import random
import os

# --- 1. 核心解析邏輯 (保留上一版本的完美順序遞迴) ---
def advanced_parser(text, p_on, r_on, s_on, rate):
    questions = []
    pattern = r"<<.*?>>|\[\[.*?\]\]|\{\{.*?\|.*?\}\}"

    def clean_text(t):
        t = re.sub(r"\[\[(.*?)\]\]", r"\1", t)
        t = re.sub(r"\{\{(.*?)\|(.*?)\}\}", r"\1", t)
        t = re.sub(r"<<(.*?)>>", r"\1", t)
        return t

    def handler(match):
        raw = match.group(0)
        if raw.startswith("<<"):
            content = raw[2:-2]
            if s_on and random.random() < rate:
                ans = clean_text(content)
                questions.append({"ans": ans, "type": "整句"})
                return f" 📝__**[整句({len(questions)})]**__ "
            else:
                return re.sub(pattern, handler, content)
        elif raw.startswith("[["):
            ans = raw[2:-2]
            if p_on and random.random() < rate:
                questions.append({"ans": ans, "type": "助詞"})
                return f" **({len(questions)})** "
            return ans
        elif raw.startswith("{{"):
            m = re.match(r"\{\{(.*?)\|(.*?)\}\}", raw)
            kanji, reading = m.group(1), m.group(2)
            if r_on and random.random() < rate:
                questions.append({"ans": reading, "type": "讀音"})
                return f"{kanji}**({len(questions)})**"
            return kanji
        return raw

    display_text = re.sub(pattern, handler, text)
    return display_text, questions

# --- 2. 檔案讀取工具 ---
def get_local_lessons(folder_path="data"):
    """讀取指定資料夾內的所有 .txt 檔案"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    lesson_dict = {}
    for f in files:
        with open(os.path.join(folder_path, f), 'r', encoding='utf-8') as file:
            # 檔名當作標題，內容當作題目
            lesson_dict[f.replace('.txt', '')] = file.read()
    return lesson_dict

# --- 3. Streamlit 介面 ---
def main():
    st.set_page_config(page_title="日文練習器-檔案讀取版", layout="centered")
    st.title("📂 日文自動化題庫練習器")

    # A. 取得本地題庫
    local_lessons = get_local_lessons()

    with st.sidebar:
        st.header("📂 題庫來源")
        
        # 提供上傳檔案功能
        uploaded_file = st.file_uploader("上傳自定義文字檔 (.txt)", type=["txt"])
        
        st.divider()
        st.header("⚙️ 練習設定")
        
        # 決定文章內容
        if uploaded_file is not None:
            # 使用者上傳的內容
            raw_text = uploaded_file.read().decode("utf-8")
            current_title = "上傳的練習"
        elif local_lessons:
            # 下拉選單選擇本地檔案
            selected_lesson = st.selectbox("選擇本地題庫", list(local_lessons.keys()))
            raw_text = local_lessons[selected_lesson]
            current_title = selected_lesson
        else:
            # 預設範例
            raw_text = "[[私]]は{{每天|まいにち}}[[に]]圖書館[[で]]勉強[[を]]します。"
            current_title = "範例練習"

        p_on = st.checkbox("挖助詞", value=True)
        r_on = st.checkbox("挖讀音", value=True)
        s_on = st.checkbox("挖整句", value=True)
        rate = st.slider("挖空機率", 0.0, 1.0, 1.0)
        
        if st.button("🔄 刷新題目"):
            if 'quiz_data' in st.session_state: del st.session_state['quiz_data']
            st.rerun()

    # 初始化數據
        # 找到這一段並修正：
    if 'quiz_data' not in st.session_state:
        # 將原本的 solve_order_issue_parser 改成 advanced_parser
        display, q_list = advanced_parser(raw_text, p_on, r_on, s_on, rate) 
        st.session_state.quiz_data = {"display": display, "q_list": q_list, "title": current_title}

        data = st.session_state.quiz_data

    # 顯示區
    st.info(f"### 📖 當前練習：{data['title']}")
    st.markdown(data["display"])
    st.divider()

    # 互動填空
    if data["q_list"]:
        st.subheader("✍️ 填寫答案")
        user_answers = []
        for i, q in enumerate(data["q_list"]):
            label = f"({i+1}) 【{q['type']}】"
            if q['type'] == "整句":
                u = st.text_area(label, key=f"q_{i}", placeholder="請輸入完整句子...")
            else:
                u = st.text_input(label, key=f"q_{i}")
            user_answers.append(u.strip())

        if st.button("✅ 檢查結果", type="primary"):
            correct = 0
            for idx, (u, q) in enumerate(zip(user_answers, data["q_list"])):
                if u == q['ans']:
                    st.success(f"({idx+1}) 正確")
                    correct += 1
                else:
                    st.error(f"({idx+1}) 錯誤！正確答案：{q['ans']}")
            st.metric("總分", f"{correct} / {len(data['q_list'])}")
            if correct == len(data["q_list"]): st.balloons()
    else:
        st.warning("⚠️ 此文章內沒有找到標記或機率抽籤未選中。")

if __name__ == "__main__":
    main()
