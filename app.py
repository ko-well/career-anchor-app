import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="キャリア・アンカー診断＆自己PR設計", layout="wide")

# 👇 ココが変更点です（タブを大きく・目立たせるデザインを追加しました）
st.markdown("""
<style>
h1, h2, h3 { color: #1A5276 !important; }
.stProgress > div > div > div > div { background-color: #3498DB !important; }
[data-testid="stFormSubmitButton"] button { background-color: #E67E22 !important; color: white !important; font-size: 20px !important; width: 100% !important; border-radius: 10px !important; }

/* タブのデザインを大きく、目立たせる設定 */
button[data-baseweb="tab"] {
    background-color: #F2F4F4 !important; /* 少しグレーの背景をつけてボタンっぽく */
    border: 1px solid #D5DBDB !important;
    border-radius: 5px 5px 0 0 !important;
    padding: 10px 20px !important;
    margin-right: 5px !important;
}
button[data-baseweb="tab"] p {
    font-size: 18px !important; /* 文字サイズを大きく */
    font-weight: bold !important; /* 文字を太く */
    color: #2C3E50 !important;
}
/* 選ばれているタブのデザイン */
button[aria-selected="true"] {
    background-color: #EBF5FB !important; /* 薄い青色の背景 */
    border-bottom: 3px solid #3498DB !important; /* 下に青い太線を引く */
}
button[aria-selected="true"] p {
    color: #2874A6 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🌱 自己PR作成ステップ2：キャリア・アンカー診断")
st.write("ここでは，あなたが仕事をする上で「絶対に譲れない軸（キャリア・アンカー）」を特定し，自己PRの設計図を完成させます。")

# --- APIキー設定 ---
st.sidebar.header("🔑 セキュリティ設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password")

# --- 質問データ ---
questions = [
    "ある分野の専門性を高め，専門家としての自信を持って活動できるようになりたい",
    "組織・グループの人々の活動を指導・統括して成果を上げたとき充実感を感じる",
    "仕事の進め方も，時間の配分も自分で決められるような仕事につきたい",
    "雇用が保証され，収入も安定することのほうが，自己決定や自由裁量より大切だ",
    "独自に仕事を始められるようなアイディアや，チャンスがないかと注意している",
    "社会福祉への貢献感に満ち足りているようなキャリアを実現したい",
    "難しい課題に挑戦し続けていけるようなキャリアに張り合いを感じる",
    "自分自身の関心，家族への配慮などを軽視するような組織には入りたくない",
    "専門分野，担当分野での専門性を高め続けていくことに真の充実感がある",
    "組織体の執行責任者として，多くの人に影響を与えるような立場で仕事をしたい",
    "課題，優先順位，手順などを自分で決められるときに大きな喜びを感じる",
    "自分の将来の保証をしてくれないような会社に勤めても仕方がない",
    "会社組織の中で昇進を望むよりも，自分のビジネスを始めることを考えたい",
    "自分の能力が人々のために役立っていると実感できるようなキャリアを選びたい",
    "困難な状況に立ち向かい，それを克服できた時こそ，真の達成感を味わえる",
    "自分の関心，家族への配慮，仕事上の要請をうまく調和させることを常に考える",
    "上級管理職を目指すより，自分に向いた仕事で能力を発揮するキャリアを選びたい",
    "できれば組織の最高執行者になって，キャリア上の成功感を味わいたいと思う",
    "自分自身の自由・自主性が十分に認められることが，キャリア上の成功感となる",
    "安定感・安全感の得られる会社・仕事であることが自分にとって最も重要である",
    "自分自身の創造性が実を結んだときこそ最高の達成感を味わえる",
    "生きやすく働きやすい会社作りに役立てれば，組織内の昇進を上回る喜びになる",
    "解決困難／勝算不明の状況を克服したときの達成感こそがキャリア成功感といえる",
    "自分，家族，友人，仕事の調和を保つことが，キャリアの上で最も大切である",
    "自分に最適の専門領域から外されるくらいなら，その組織を辞めることを考える",
    "特定の専門分野の責任者となるより，広い範囲を統括する仕事／活動の方が好きだ",
    "安全・安定の保証より，制約・制限なく自由に活動できるキャリアを選択する",
    "経済的安定と雇用・身分の保証を実感できるときに仕事の満足も感じる",
    "自分自身のアイディアで何かを実現できたときの満足感が最高だ",
    "人間と社会に貢献できるような仕事／活動につくことが私の願いだ",
    "自分の問題解決能力や競争的能力が試されるような仕事にこそ価値を感じる",
    "仕事と私生活のバランスを失わないようにすることが，昇進より大切だ",
    "仕事上の充実感が得られるのは，自分独自の能力・専門力を発揮できているときだ",
    "会社の上級職位への昇進コースから外されるようなら，退社／転社を考える",
    "自己決定と自己裁量が著しく制限されるようなら，その職を離れることを考える",
    "安定感に満ちた組織の中でないとキャリアを真剣に考えることができない",
    "自分の会社を創り，自分のビジネスを始めたいという願望を持っている",
    "社会福祉に貢献したい自分の願いを認めないような会社は嫌だ",
    "上級管理職よりも，困難な問題解決に取り組む仕事の方がやりがいがある",
    "家族を含む自分の私生活が乱されないような仕事につくことは重要だ"
]

categories = ["特定専門", "総合管理", "自由自律", "安全安定", "創意創業", "奉仕貢献", "挑戦克服", "生活様式"]

# --- 診断画面 ---
if 'step' not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1:
    st.subheader("1. キャリア・アンカー診断（40問）")
    
    st.info("""
    **【注意点 1】**
    次の40項目について，該当する点数（1～6）を選んでください。深く考えすぎず，自分自身のホンネで、10分以内（1項目につき約15秒）に全項目へ直感で記入しましょう。

    **【注意点 2】**
    全項目の入力が終わったら、最後のページ（31-40問）の下で、最高点（通常は6または5）を付けた項目の中から、**特に強く該当する項目を「3つ」選んでください**（＋印の代わりになります）。
    """)
    
    with st.form("diagnosis_form"):
        user_name = st.text_input("お名前（苗字またはニックネームで可）", value="あなた")
        st.write("---")
        
        # 👇 ココが変更点です（操作案内のテキストを追加しました）
        st.markdown("💡 **【操作方法】 10問ごとにページが分かれています。入力が終わったら、下の「11-20問」などの文字（タブ）をクリックして次のページへ進んでください。**")
        
        scores = []
        tab1, tab2, tab3, tab4 = st.tabs(["1-10問", "11-20問", "21-30問", "31-40問 ＆ 提出へ"])
        
        with tab1:
            for i in range(0, 10):
                scores.append(st.radio(f"Q{i+1}: {questions[i]}", [1, 2, 3, 4, 5, 6], index=2, horizontal=True, key=f"q{i}"))
        with tab2:
            for i in range(10, 20):
                scores.append(st.radio(f"Q{i+1}: {questions[i]}", [1, 2, 3, 4, 5, 6], index=2, horizontal=True, key=f"q{i}"))
        with tab3:
            for i in range(20, 30):
                scores.append(st.radio(f"Q{i+1}: {questions[i]}", [1, 2, 3, 4, 5, 6], index=2, horizontal=True, key=f"q{i}"))
        
        with tab4:
            for i in range(30, 40):
                scores.append(st.radio(f"Q{i+1}: {questions[i]}", [1, 2, 3, 4, 5, 6], index=2, horizontal=True, key=f"q{i}"))
            
            st.markdown("---")
            st.write("🌟 **【＋印の選択】特に強く該当する項目を3つ選んでください**")
            top3_selections = st.multiselect(
                "最高点（6や5）を付けた質問の中から、あなたにとって「特に重要だ」と思うものを最大3つまで選んでください。",
                options=[f"Q{i+1}: {questions[i]}" for i in range(40)],
                max_selections=3
            )
            
            st.write("") 
            submitted = st.form_submit_button("診断結果を表示する")
        
        if submitted:
            # 計算処理
            cat_scores = []
            for j in range(8):
                avg = sum([scores[j + (k * 8)] for k in range(5)]) / 5.0
                cat_scores.append(avg)
            
            max_idx = cat_scores.index(max(cat_scores))
            st.session_state.top_anchor = categories[max_idx]
            st.session_state.user_name = user_name
            st.session_state.top3_selections = top3_selections
            st.session_state.all_results = "\n".join([f"{categories[i]}: {cat_scores[i]}" for i in range(8)])
            st.session_state.step = 2
            st.rerun()

# --- 深掘り＆統合画面 ---
elif st.session_state.step == 2:
    st.subheader(f"診断結果：あなたのアンカーは「{st.session_state.top_anchor}」です")
    st.success(f"{st.session_state.user_name}さんの仕事における「譲れない軸」は『{st.session_state.top_anchor}』である可能性が高いです。")
    
    if st.session_state.top3_selections:
        st.info("💡 **あなたが特に強くこだわっているポイント（＋印）**\n" + "\n".join([f"・{item}" for item in st.session_state.top3_selections]))

    st.markdown("---")
    st.subheader("2. AIキャリアコンサルタントによる深掘りと統合")
    st.write("この軸をより具体化し，第1段階の「棚卸しシート」と組み合わせて自己PRの設計図を作ります。")

    with st.form("integration_form"):
        st.write(f"**【AIからの質問】**")
        st.write(f"『{st.session_state.top_anchor}』という価値観を大切にするあなたは，これまでの経験の中でどのような時に一番やりがいを感じましたか？また，今回の就職ではどのような環境を求めていますか？")
        anchor_answer = st.text_area("AIへの回答（箇条書きでも構いません）")
        
        st.write("---")
        st.write("**【前回の振り返り】**")
        inventory_data = st.text_area("第1段階で作成した「棚卸し完了シート（資料1）」の内容をここに貼り付けてください。")
        
        st.write("---")
        st.write("**【応募先の情報】**")
        job_info = st.text_input("応募したい職種や業界（例：医療事務，IT企業の営業など）")
        
        submit_final = st.form_submit_button("自己PR設計図（資料2）を生成する")

    if submit_final:
        if not api_key:
            st.error("⚠️ APIキーを入力してください。")
        elif not inventory_data:
            st.warning("⚠️ 棚卸しシート（資料1）の内容を貼り付けてください。")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            あなたは温かいキャリアコンサルタントです。
            クライアントの「事実（棚卸しシート）」と「価値観（キャリア・アンカー）」を統合し，戦略的な自己PR設計図を作成してください。

            【クライアント情報】
            - 呼称：{st.session_state.user_name}
            - キャリア・アンカー結果：{st.session_state.top_anchor}
            - 特に強く該当した質問（＋印）：{st.session_state.top3_selections}
            - アンカーに対する本人の思い：{anchor_answer}
            - 第1段階の棚卸しデータ：{inventory_data}
            - 応募先：{job_info}

            【出力要件】
            1. 【承認と解説】
            診断結果の「{st.session_state.top_anchor}」と，特に強く該当した質問の傾向から，{st.session_state.user_name}さんの強みを改めて温かく肯定してください。

            2. 【自己PRの“看板”タイトル】
            資料に基づき，一言で強みが伝わるキャッチコピーを3案提案してください。

            3. 【自己PRの設計図（PREP法 または STAR法）】
            棚卸しデータの中から最も強みが伝わるエピソードを1つに絞り，{job_info}のニーズに合わせて構成案を作成してください。
            ※想像で補完する部分は必ず「**太字**」にすること。

            【制約条件】
            ・読点は必ず「，」を使用すること。
            """
            
            with st.spinner('AIがあなたの価値観と経験を統合しています...'):
                try:
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    top3_text = "\n".join(st.session_state.top3_selections) if st.session_state.top3_selections else "特になし"
                    final_text = f"""【キャリア・アンカー診断結果】
{st.session_state.all_results}
（第一アンカー：{st.session_state.top_anchor}）

【特に強く該当した項目（＋印）】
{top3_text}

【あなたの価値観への回答】
{anchor_answer}

【AIによる自己PR設計図（資料2）】
{response.text}
"""
                    st.download_button(
                        label="📝 自己PR設計図（資料2）を保存する",
                        data=final_text,
                        file_name="self_pr_blueprint.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

# --- ポータルサイトへ戻るボタン ---
st.markdown("---")
st.write("※診断をやり直す場合はブラウザを更新してください。")
st.link_button("🏠 C.HARIGOMA キャリア支援ポータルへ戻る", "https://harigoma-career.streamlit.app/")
