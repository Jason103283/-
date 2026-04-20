import streamlit as st
import re
import random

# --- 1. 核心解析邏輯 (支援巢狀) ---
def advanced_parser(text, p_on, r_on, s_on, rate):
    questions = []
    
    # 內層解析：處理 [[助詞]] 與 {{漢字|讀音}}
    def process_inner(inner_text):
        # 處理助詞
        def handle_p(m):
            ans = m.group(1)
            if p_on and random.random() < rate:
                questions.append(ans)
                return f" **({len(questions)})** "
            return ans
        
        # 處理讀音
        def handle_r(m):
            kanji, reading = m.group(1), m.group(2)
            if r_on and random.random() < rate:
                questions.append(reading)
                return f"{kanji}**({len(questions)})**"
            return kanji

        temp = re.sub(r"\[\[(.*?)\]\]", handle_p, inner_text)
        temp = re.sub(r"\{\{(.*?)\|(.*?)\}\}", handle_r, temp)
        return temp

    # 外層解析：處理 <<整句>>
    def process_outer(match):
        content = match.group(1)
        if s_on and random.random() < rate:
            # 挖掉整句前，先清除內部的標記符號，轉為純淨答案
            clean_ans = re.sub(r"\[\[(.*?)\]\]|\{\{(.*?)\|(.*?)\}\}", 
                               lambda m: m.group(1) or m.group(2), content)
            questions.append(clean_ans)
            return f" **({len(questions)})** "
        else:
            # 若不挖整句，則處理內部的助詞或讀音
            return process_inner(content)

    # 執行解析
    display_text = re.sub(r"<<(.*?)>>", process_outer, text)
    # 處理那些不在 << >> 裡面的標記
    display_text = process_inner(display_text)
    
    return display_text, questions

# --- 2. Streamlit 介面 ---
def main():
    st.set_page_config(page_title="日文全方位練習器", layout="centered")
    st.title("🇯🇵 日文巢狀練習工具")

    # 設定預設文章
    raw_text = "<<そこで{{友達|ともだち}}[[と]]勉強をします。>> 私は[[毎日]]圖書館[[に]]行きます。"

    # 側邊欄控制
    with st.sidebar:
        st.header("🛠 練習設定")
        p_on = st.checkbox("挖助詞 [[ ]]", value=True)
        r_on = st.checkbox("挖讀音 {{ }}", value=True)
        s_on = st.checkbox("挖整句 << >>", value=True)
        rate = st.slider("挖空機率", 0.0, 1.0, 1.0) # 預設 1.0 確保一定會挖空
        
        if st.button("🔄 刷新題目"):
            if 'quiz_data' in st.session_state:
                del st.session_state['quiz_data']
            st.rerun()

    # 初始化與狀態保持 (確保題目不會因為輸入答案而改變)
    if 'quiz_data' not in st.session_state:
        display, ans = advanced_parser(raw_text, p_on, r_on, s_on, rate)
        st.session_state.quiz_data = {"display": display, "answers": ans}

    data = st.session_state.quiz_data

    # --- 顯示區 ---
    st.info("### 📖 文章題目")
    st.markdown(data["display"])
    st.divider()

    # --- 互動區 ---
    if data["answers"]:
        st.subheader("✍️ 請輸入答案")
        user_inputs = []
        # 使用 columns 讓排版好看一點
        cols = st.columns(2)
        for i, correct_ans in enumerate(data["answers"]):
            with cols[i % 2]:
                u_in = st.text_input(f"空格 ({i+1})", key=f"input_{i}").strip()
                user_inputs.append(u_in)

        if st.button("✅ 檢查答案", type="primary"):
            correct_count = 0
            for idx, (u, a) in enumerate(zip(user_inputs, data["answers"])):
                if u == a:
                    st.success(f"({idx+1}) **{u}** 正確！")
                    correct_count += 1
                else:
                    st.error(f"({idx+1}) 錯誤！你填「{u}」，正確是「{a}」")
            
            st.metric("總分", f"{correct_count} / {len(data['answers'])}")
            if correct_count == len(data["answers"]):
                st.balloons()
    else:
        st.warning("⚠️ 目前沒有任何空格被挖出，請嘗試調整「挖空機率」或勾選練習項目。")

if __name__ == "__main__":
    main()
