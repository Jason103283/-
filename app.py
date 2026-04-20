import streamlit as st
import re
import random

def nested_parser(text, p_on, r_on, s_on, rate, questions):
    """
    支援巢狀結構的解析器。
    順序：先處理整句 << >>，若不挖空，再處理內部的 {{ }} 與 [[ ]]。
    """
    
    # 處理整句模式 <<...>>
    def process_sentence(match):
        content = match.group(1)
        # 如果整句模式開啟且抽中挖空
        if s_on and random.random() < rate:
            # 這裡需要把內部的標記先清理掉，再存入答案，否則答案會帶有 [[ ]]
            clean_ans = re.sub(r"\[\[(.*?)\]\]|\{\{(.*?)\|(.*?)\}\}", 
                               lambda m: m.group(1) or m.group(2), content)
            questions.append(clean_ans)
            return f" **({len(questions)})** "
        else:
            # 如果不挖整句，則「遞迴」處理內部的助詞與讀音
            return process_inner(content)

    # 處理內部標記 [[ ]] 與 {{ }}
    def process_inner(inner_text):
        # 處理助詞 [[ ]]
        def handle_p(m):
            ans = m.group(1)
            if p_on and random.random() < rate:
                questions.append(ans)
                return f" **({len(questions)})** "
            return ans

        # 處理讀音 {{ | }}
        def handle_r(m):
            kanji, reading = m.group(1), m.group(2)
            if r_on and random.random() < rate:
                questions.append(reading)
                return f"{kanji}**({len(questions)})**"
            return kanji

        # 先跑助詞取代，再跑讀音取代
        inner_text = re.sub(r"\[\[(.*?)\]\]", handle_p, inner_text)
        inner_text = re.sub(r"\{\{(.*?)\|(.*?)\}\}", handle_r, inner_text)
        return inner_text

    # 啟動解析：從最外層的 << >> 開始
    # 我們使用一個正則來抓取所有的 <<...>> 以及不在 <<...>> 裡面的內容
    # 簡單做法：先處理 << >>，剩下的再處理一遍 inner
    final_text = re.sub(r"<<(.*?)>>", process_sentence, text)
    # 處理那些「不在 << >> 裡面」的剩餘標記
    final_text = process_inner(final_text)
    
    return final_text

# --- Streamlit 介面部分 ---
def main():
    st.title("🧪 巢狀功能測試")

    # 你提供的複合句子
    raw_text = "<<そこで{{友達|とも道}}[[と]]勉強をします。>>"
    
    with st.sidebar:
        st.header("測試設定")
        p_on = st.checkbox("挖助詞", value=True)
        r_on = st.checkbox("挖讀音", value=True)
        s_on = st.checkbox("挖整句", value=True)
        rate = st.slider("挖空率", 0.0, 1.0, 0.5)
        if st.button("刷新題目"): st.rerun()

    if 'quiz_data' not in st.session_state or st.sidebar.button("手動刷新"):
        qs = []
        display = nested_parser(raw_text, p_on, r_on, s_on, rate, qs)
        st.session_state.quiz_data = (display, qs)

    display, answers = st.session_state.quiz_data

    st.info("### 生成結果：")
    st.write(display)
    
    st.write("---")
    st.subheader("答案列表（驗證用）：")
    st.write(answers)

if __name__ == "__main__":
    main()
