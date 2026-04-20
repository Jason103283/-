import streamlit as st
import re
import random

# --- 1. 核心解析邏輯 (加入類型標註) ---
def advanced_parser(text, p_on, r_on, s_on, rate):
    questions = [] # 儲存格式: {"ans": "...", "type": "..."}
    
    def process_inner(inner_text):
        def handle_p(m):
            ans = m.group(1)
            if p_on and random.random() < rate:
                questions.append({"ans": ans, "type": "助詞"})
                return f" **({len(questions)})** "
            return ans
        
        def handle_r(m):
            kanji, reading = m.group(1), m.group(2)
            if r_on and random.random() < rate:
                questions.append({"ans": reading, "type": "讀音"})
                return f"{kanji}**({len(questions)})**"
            return kanji

        temp = re.sub(r"\[\[(.*?)\]\]", handle_p, inner_text)
        temp = re.sub(r"\{\{(.*?)\|(.*?)\}\}", handle_r, temp)
        return temp

    def process_outer(match):
        content = match.group(1)
        if s_on and random.random() < rate:
            # 取得純淨答案
            clean_ans = re.sub(r"\[\[(.*?)\]\]|\{\{(.*?)\|(.*?)\}\}", 
                               lambda m: m.group(1) or m.group(2), content)
            questions.append({"ans": clean_ans, "type": "整句"})
            # 整句挖空在畫面上顯示得更長、更明顯
            return f" 📝__**[整句({len(questions)})]**__ "
        else:
            return process_inner(content)

    display_text = re.sub(r"<<(.*?)>>", process_outer, text)
    display_text = process_inner(display_text)
    
    return display_text, questions

# --- 2. Streamlit 介面 ---
def main():
    st.set_page_config(page_title="日文全方位練習器", layout="centered")
    st.title("🇯🇵 日文巢狀練習工具")

    raw_text = "<<そこで{{友達|ともだち}}[[と]]勉強をします。>> 私は[[每天]]{{圖書館|としょかん}}[[に]]行きます。"

    with st.sidebar:
        st.header("🛠 練習設定")
        p_on = st.checkbox("挖助詞 [[ ]]", value=True)
        r_on = st.checkbox("挖讀音 {{ }}", value=True)
        s_on = st.checkbox("挖整句 << >>", value=True)
        rate = st.slider("挖空機率", 0.0, 1.0, 1.0)
        
        if st.button("🔄 刷新題目"):
            if 'quiz_data' in st.session_state: del st.session_state['quiz_data']
            st.rerun()

    if 'quiz_data' not in st.session_state:
        display, q_list = advanced_parser(raw_text, p_on, r_on, s_on, rate)
        st.session_state.quiz_data = {"display": display, "q_list": q_list}

    data = st.session_state.quiz_data

    # --- 顯示區 ---
    st.info("### 📖 文章題目")
    # 使用 Markdown 渲染，讓整句挖空的樣式跑出來
    st.markdown(data["display"])
    st.divider()

    # --- 互動區 ---
    if data["q_list"]:
        st.subheader("✍️ 填寫答案")
        user_answers = []
        
        for i, q_item in enumerate(data["q_list"]):
            q_type = q_item["type"]
            q_ans = q_item["ans"]
            
            # 根據類型給予不同的標籤顏色或提示
            label = f"第 ({i+1}) 題 【{q_type}】"
            
            if q_type == "整句":
                # 整句填空使用較大的輸入框
                u_in = st.text_area(label, key=f"input_{i}", help="此題為整句填空").strip()
            else:
                # 助詞與讀音使用一般輸入框
                u_in = st.text_input(label, key=f"input_{i}").strip()
            
            user_answers.append(u_in)

        if st.button("✅ 檢查答案", type="primary"):
            correct_count = 0
            for idx, (u, q_obj) in enumerate(zip(user_answers, data["q_list"])):
                correct_ans = q_obj["ans"]
                if u == correct_ans:
                    st.success(f"({idx+1}) 正確！")
                    correct_count += 1
                else:
                    st.error(f"({idx+1}) 錯誤！正確答案：{correct_ans}")
            
            st.metric("總分", f"{correct_count} / {len(data['q_list'])}")
    else:
        st.warning("⚠️ 沒有題目，請調整機率。")

if __name__ == "__main__":
    main()
