import streamlit as st
import re

def main():
    # 設定網頁標題與圖示
    st.set_page_config(page_title="日文助詞填空練習", page_icon="🇯🇵")
    st.title("🇯🇵 日文助詞填空練習")
    st.markdown("請根據文章內容，在下方的輸入框填入正確的助詞。")

    # 1. 準備文本資料 (實際開發時可改為從檔案讀取或讓使用者輸入)
    if 'raw_text' not in st.session_state:
        st.session_state.raw_text = "私は毎日[[で]]圖書館[[に]]行きます。そこで友達[[と]]勉強[[を]]します。"

    raw_text = st.session_state.raw_text
    pattern = r"\[\[(.*?)\]\]"
    
    # 2. 解析答案與生成題目文本
    answers = re.findall(pattern, raw_text)
    # 這裡我們將標記處換成帶有編號的 ( )，方便使用者對應
    display_text = raw_text
    for i in range(len(answers)):
        display_text = display_text.replace(f"[[{answers[i]}]]", f" **({i+1})** ", 1)

    # 3. 顯示題目區塊
    st.info(f"### 📖 練習文章：\n{display_text}")

    # 4. 建立輸入區塊 (使用 Columns 讓排版整齊)
    st.subheader("✍️ 請輸入答案")
    user_inputs = []
    
    # 建立多欄位輸入，每橫列 2 個
    cols = st.columns(2)
    for i in range(len(answers)):
        with cols[i % 2]:
            ans = st.text_input(f"第 ({i+1}) 題", key=f"q_{i}").strip()
            user_inputs.append(ans)

    # 5. 提交與結果核對
    if st.button("檢查答案", type="primary"):
        correct_count = 0
        st.divider()
        st.subheader("📊 測驗結果")

        for idx, (user, correct) in enumerate(zip(user_inputs, answers)):
            if user == correct:
                st.success(f"第 ({idx+1}) 題：**{user}** ✅ 正確")
                correct_count += 1
            else:
                st.error(f"第 ({idx+1}) 題：**{user}** ❌ 錯誤 (正確答案：{correct})")

        # 顯示總結與完整原文
        score_ratio = correct_count / len(answers)
        if score_ratio == 1:
            st.balloons()
            st.success(f"太棒了！全對！得分：{correct_count}/{len(answers)}")
        else:
            st.warning(f"再接再厲！得分：{correct_count}/{len(answers)}")

        # 顯示移除標記後的完整文章
        full_sentence = re.sub(r"\[\[|\]\]", "", raw_text)
        st.markdown("### 📝 完整原文複習：")
        st.write(full_sentence)

if __name__ == "__main__":
    main()
