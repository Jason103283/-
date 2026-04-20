import streamlit as st
import re

def main():
    st.set_page_config(page_title="日文助詞多題練習器", page_icon="📚")
    st.title("📚 日文助詞多題練習器")

    # 1. 建立題庫 (Key 是標題，Value 是含標記的內容)
    # 你可以隨時在這裡增加新的文章
    QUIZ_BANK = {
        "基礎練習：自我介紹": "私[[は]]學生です。每天圖書館[[で]]勉強[[を]]します。",
        "進階練習：週末計畫": "週末[[に]]友達[[と]]電影院[[へ]]行きます。之後[[で]]飯[[を]]食べます。",
        "日常對話：買東西": "這張桌子[[は]]五千元[[です]]。那個[[も]]買[[い]]ます。"
    }

    # 2. 側邊欄：選擇題目
    with st.sidebar:
        st.header("設定")
        selected_title = st.selectbox("請選擇練習文章", list(QUIZ_BANK.keys()))
        
        # 讓使用者也可以自己貼上文章
        st.divider()
        custom_text = st.text_area("或者貼上你自己的標記文章：", placeholder="例如：私[[は]]...")
        
        if custom_text:
            current_text = custom_text
        else:
            current_text = QUIZ_BANK[selected_title]

    # 3. 解析邏輯
    pattern = r"\[\[(.*?)\]\]"
    answers = re.findall(pattern, current_text)
    
    # 生成題目顯示文本 (加上編號)
    quiz_display = current_text
    for i, ans in enumerate(answers):
        quiz_display = quiz_display.replace(f"[[{ans}]]", f" **({i+1})** ", 1)

    st.info(f"### 📖 當前練習：{selected_title if not custom_text else '自定義題目'}")
    st.markdown(quiz_display)
    st.divider()

    # 4. 答案輸入區 (使用兩欄排版)
    st.subheader("✍️ 填寫助詞")
    user_inputs = []
    cols = st.columns(2)
    
    for i in range(len(answers)):
        with cols[i % 2]:
            # 注意：這裡使用 selected_title 作為 key 的一部分，確保切換題目時輸入框會重置
            u_input = st.text_input(f"({i+1})", key=f"{selected_title}_{i}").strip()
            user_inputs.append(u_input)

    # 5. 核對結果
    if st.button("送出評分", type="primary"):
        correct_count = 0
        for idx, (user, correct) in enumerate(zip(user_inputs, answers)):
            if user == correct:
                st.success(f"({idx+1}) **{user}** ✅")
                correct_count += 1
            else:
                st.error(f"({idx+1}) **{user}** ❌ (應為：{correct})")
        
        st.metric("總分", f"{correct_count} / {len(answers)}")
        
        if correct_count == len(answers):
            st.balloons()

if __name__ == "__main__":
    main()
