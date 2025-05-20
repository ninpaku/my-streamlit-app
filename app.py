import streamlit as st
import anthropic
from datetime import datetime

# Constants
CLAUDE_API_MODEL = "claude-3-opus-20240229"  # 最新モデルに更新可能

# アプリのタイトルと説明
st.set_page_config(page_title="SEO記事ジェネレーター", layout="wide")
st.title("SEO記事ジェネレーター")
st.markdown("簡単な入力でSEO最適化された記事を生成します。")

# セッション状態変数の初期化
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'article_content' not in st.session_state:
    st.session_state.article_content = ""
if 'article_title' not in st.session_state:
    st.session_state.article_title = ""
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'generated_articles' not in st.session_state:
    st.session_state.generated_articles = []

# Claude APIを呼び出す関数
def generate_article_with_claude(prompt, api_key):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=CLAUDE_API_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system="あなたはSEOに精通したプロのコンテンツライターです。自然でエンゲージメントの高い、SEO最適化された記事を作成することが得意です。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # APIレスポンスから内容を抽出
        if hasattr(message, 'content'):
            if isinstance(message.content, list):
                # 新しいバージョンではコンテンツがリストとして返される
                content_text = ""
                for block in message.content:
                    if hasattr(block, 'text'):
                        content_text += block.text
                    elif isinstance(block, dict) and 'text' in block:
                        content_text += block['text']
                return content_text
            elif isinstance(message.content, str):
                # contentが直接文字列の場合
                return message.content
            else:
                # 文字列表現のあるオブジェクトの場合
                return str(message.content)
        else:
            # その他のAPIレスポンス構造へのフォールバック
            if hasattr(message, 'completion'):
                return message.completion
            elif hasattr(message, 'text'):
                return message.text
            else:
                st.warning("APIレスポンスの形式が予期しないものでした。開発者に連絡してください。")
                return str(message)
                
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        st.error(f"エラーの種類: {type(e).__name__}")
        return None

# 記事生成のプロンプトを作成する関数
def create_article_prompt(title, main_keywords, sub_keywords, purpose, length, audience, tone):
    prompt = f"""
    以下の条件に従った、SEO最適化された記事を作成してください。

    ## 記事タイトル
    {title}

    ## メインキーワード
    {main_keywords}

    ## サブキーワード
    {sub_keywords}

    ## 記事の目的
    {purpose}

    ## 記事の長さ
    {length}

    ## ターゲット読者層
    {audience}

    ## 文章のトーン
    {tone}

    ## 記事作成の注意点
    1. HTMLタグを使わず、Markdown形式で記事を作成してください
    2. 自然な文章で、メインキーワードとサブキーワードを適切に配置してください
    3. 見出し(H2, H3)を効果的に使用してください
    4. 導入部分で読者の関心を引き、結論部分で明確なまとめをしてください
    5. 文章は読みやすく、専門用語は必要に応じて説明を入れてください
    6. 事実に基づいた正確な情報を提供してください

    SEO最適化された完全な記事を作成してください。
    """
    return prompt

# サイドバー: APIキーとナビゲーション
with st.sidebar:
    st.header("設定")
    api_key_input = st.text_input("Claude API キーを入力してください", 
                                   value=st.session_state.api_key, 
                                   type="password",
                                   help="Anthropicのウェブサイトでキーを取得できます")
    
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
    
    st.divider()
    
    # ナビゲーション
    st.header("ナビゲーション")
    nav_options = ["記事作成", "保存した記事", "使い方"]
    selected_nav = st.radio("", nav_options)

# ナビゲーションに基づいたメインコンテンツ
if selected_nav == "記事作成":
    # ステップバイステップのフォーム
    st.header("記事情報の入力")
    
    # ステップ1: 基本情報
    if st.session_state.current_step == 1:
        with st.form("basic_info_form"):
            st.markdown("### 基本情報")
            title = st.text_input("記事タイトル", 
                                 help="記事のタイトルを入力してください")
            
            main_keywords = st.text_input("メインキーワード", 
                                        help="最も重要なSEOキーワードをカンマ区切りで入力してください")
            
            sub_keywords = st.text_input("サブキーワード", 
                                       help="補助的なSEOキーワードをカンマ区切りで入力してください")
            
            submit_basic = st.form_submit_button("次へ")
            
            if submit_basic and title and main_keywords:
                st.session_state.article_title = title
                st.session_state.main_keywords = main_keywords
                st.session_state.sub_keywords = sub_keywords
                st.session_state.current_step = 2
                st.rerun()
    
    # ステップ2: コンテンツ詳細
    elif st.session_state.current_step == 2:
        with st.form("content_details_form"):
            st.markdown("### コンテンツ詳細")
            
            purpose = st.text_area("記事の目的・ゴール", 
                                 help="この記事で達成したい目標を入力してください")
            
            length_options = {"短め (約800語)": "約800語の簡潔な記事", 
                             "標準 (約1500語)": "約1500語の標準的な記事", 
                             "詳細 (約2500語以上)": "約2500語以上の詳細な記事"}
            length = st.selectbox("記事の長さ", options=list(length_options.keys()))
            
            audience = st.text_input("ターゲット読者層", 
                                    help="この記事の対象となる読者層を記述してください")
            
            submit_details = st.form_submit_button("次へ")
            back_to_basic = st.form_submit_button("戻る")
            
            if back_to_basic:
                st.session_state.current_step = 1
                st.rerun()
                
            if submit_details and purpose and audience:
                st.session_state.purpose = purpose
                st.session_state.length = length_options[length]
                st.session_state.audience = audience
                st.session_state.current_step = 3
                st.rerun()
    
    # ステップ3: スタイル設定
    elif st.session_state.current_step == 3:
        with st.form("style_preferences_form"):
            st.markdown("### スタイル設定")
            
            tone_options = {"カジュアル": "親しみやすく会話的な文体", 
                           "フォーマル": "丁寧で正式な文体", 
                           "専門的": "業界の専門家向けの専門用語を含む文体",
                           "教育的": "わかりやすく説明する教育的な文体",
                           "説得力のある": "読者を説得するための文体"}
            tone = st.selectbox("文章のトーン", options=list(tone_options.keys()))
            
            submit_style = st.form_submit_button("記事を生成")
            back_to_details = st.form_submit_button("戻る")
            
            if back_to_details:
                st.session_state.current_step = 2
                st.rerun()
                
            if submit_style:
                st.session_state.tone = tone_options[tone]
                
                # APIキーが入力されているか確認
                if not st.session_state.api_key:
                    st.error("Claude API キーが入力されていません。サイドバーからキーを入力してください。")
                else:
                    # ローディングメッセージを表示
                    with st.spinner("記事を生成中...これには1〜2分かかる場合があります"):
                        # Claudeで記事を生成
                        prompt = create_article_prompt(
                            st.session_state.article_title,
                            st.session_state.main_keywords,
                            st.session_state.sub_keywords,
                            st.session_state.purpose,
                            st.session_state.length,
                            st.session_state.audience,
                            st.session_state.tone
                        )
                        
                        article_content = generate_article_with_claude(prompt, st.session_state.api_key)
                        
                        if article_content:
                            st.session_state.article_content = article_content
                            
                            # 生成された記事を履歴に保存
                            article_data = {
                                "title": st.session_state.article_title,
                                "content": article_content,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "metadata": {
                                    "main_keywords": st.session_state.main_keywords,
                                    "sub_keywords": st.session_state.sub_keywords,
                                    "purpose": st.session_state.purpose,
                                    "length": st.session_state.length,
                                    "audience": st.session_state.audience,
                                    "tone": st.session_state.tone
                                }
                            }
                            st.session_state.generated_articles.append(article_data)
                            st.session_state.current_step = 4
                            st.rerun()
    
    # ステップ4: プレビューとエクスポート
    elif st.session_state.current_step == 4:
        st.markdown("### 生成された記事")
        
        article_tabs = st.tabs(["プレビュー", "編集", "エクスポート"])
        
        with article_tabs[0]:
            st.markdown(f"## {st.session_state.article_title}")
            st.markdown(st.session_state.article_content)
        
        with article_tabs[1]:
            edited_title = st.text_input("タイトル", value=st.session_state.article_title)
            edited_content = st.text_area("記事内容", value=st.session_state.article_content, height=500)
            
            if st.button("変更を保存"):
                st.session_state.article_title = edited_title
                st.session_state.article_content = edited_content
                
                # 生成記事リストの更新
                for article in st.session_state.generated_articles:
                    if article["title"] == st.session_state.article_title:
                        article["title"] = edited_title
                        article["content"] = edited_content
                        break
                
                st.success("記事が更新されました")
                st.rerun()
        
        with article_tabs[2]:
            export_format = st.selectbox("エクスポート形式", ["Markdown (.md)", "テキスト (.txt)"])
            
            if st.download_button(
                label="記事をダウンロード",
                data=st.session_state.article_content,
                file_name=f"{st.session_state.article_title}.{'md' if export_format == 'Markdown (.md)' else 'txt'}",
                mime="text/plain"
            ):
                st.success("記事がダウンロードされました")
        
        # 新しい記事作成や修正のためのボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("新しい記事を作成"):
                st.session_state.current_step = 1
                st.session_state.article_content = ""
                st.session_state.article_title = ""
                st.rerun()
        
        with col2:
            if st.button("記事を改善する"):
                st.session_state.current_step = 3
                st.rerun()

elif selected_nav == "保存した記事":
    st.header("保存された記事")
    
    if not st.session_state.generated_articles:
        st.info("保存された記事はありません。「記事作成」から新しい記事を生成してください。")
    else:
        # 保存された記事のリストを表示
        for i, article in enumerate(st.session_state.generated_articles):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{article['title']}**")
                st.caption(f"作成日時: {article['created_at']}")
            
            with col2:
                if st.button("表示", key=f"view_{i}"):
                    st.session_state.article_title = article['title']
                    st.session_state.article_content = article['content']
                    st.session_state.current_step = 4
                    st.rerun()
            
            with col3:
                if st.button("削除", key=f"delete_{i}"):
                    st.session_state.generated_articles.pop(i)
                    st.rerun()
            
            st.divider()

elif selected_nav == "使い方":
    st.header("使い方")
    
    st.markdown("""
    ### SEO記事ジェネレーターの使い方
    
    #### 1. 準備
    - サイドバーからClaude APIキーを入力してください
    - APIキーは[Anthropicのウェブサイト](https://console.anthropic.com/)で取得できます
    
    #### 2. 記事作成のステップ
    1. **基本情報の入力**
       - 記事タイトル: 明確で魅力的なタイトルを入力
       - メインキーワード: 最も重要なSEOキーワード（カンマ区切り）
       - サブキーワード: 補助的なキーワード（カンマ区切り）
    
    2. **コンテンツ詳細の入力**
       - 記事の目的・ゴール: この記事で達成したい目標
       - 記事の長さ: 短め/標準/詳細から選択
       - ターゲット読者層: 記事の対象となる読者
    
    3. **スタイル設定**
       - 文章のトーン: カジュアル/フォーマル/専門的など
    
    4. **記事のプレビューと編集**
       - プレビュー: 生成された記事を確認
       - 編集: 必要に応じて記事を編集
       - エクスポート: 記事をダウンロード
    
    #### 3. 保存された記事
    - 生成した記事はセッション中保存されます
    - 「保存した記事」から過去に生成した記事を表示できます
    
    #### 4. 記事生成のコツ
    - メインキーワードは具体的かつ関連性の高いものを選びましょう
    - 記事の目的を明確に記述すると、より質の高い記事が生成されます
    - ターゲット読者を具体的に設定すると、読者に響く内容になります
    """)
