# modules/constants.py
import streamlit as st

# --- アプリのバージョン情報 ---
APP_VERSION = "v0.1.1"  # アプリを更新するたびにここを変更


def load_release_notes(filepath="release_notes.md"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "リリースノートファイルが見つかりません。"

RELEASE_NOTES_HISTORY = load_release_notes() 


# modules/constants.py 内の get_latest_release_notes_summary() 関数を再度置き換え

def get_latest_release_notes_summary():
    """最新バージョンのリリースノートの要約を取得する"""
    print(f"--- DEBUG: get_latest_release_notes_summary ---")
    print(f"DEBUG: APP_VERSION = '{APP_VERSION}' (length: {len(APP_VERSION)})")
    
    # APP_VERSION が既に "v" を含んでいるので、プレフィックス生成時には "v" を追加しない
    if APP_VERSION.startswith('v'):
        version_identifier_for_prefix = APP_VERSION 
    else:
        version_identifier_for_prefix = f"v{APP_VERSION}" # APP_VERSION が "0.3.1" のような場合

    version_line_prefix_to_find = f"- **{version_identifier_for_prefix}" # 修正点
    
    print(f"DEBUG: version_line_prefix_to_find = '{version_line_prefix_to_find}' (length: {len(version_line_prefix_to_find)})")
    try:
        lines = RELEASE_NOTES_HISTORY.strip().split('\n')
        
        start_extraction_index = -1
        # version_line_prefix も同様に修正 (または version_line_prefix_to_find を使う)
        # version_line_prefix = f"- **{version_identifier_for_prefix}" # 修正点

        for i, line in enumerate(lines):
            # バージョン行を特定 (先頭の空白を無視して比較)
            if line.strip().startswith(version_line_prefix_to_find): # 修正したプレフィックスを使用
                start_extraction_index = i + 1 
                break
        
        if start_extraction_index == -1 or start_extraction_index >= len(lines):
            return f"履歴内にバージョン {APP_VERSION} の記載が見つかりませんでした。"

        summary_lines = []
        for i in range(start_extraction_index, len(lines)):
            current_line = lines[i]
            # 次のバージョンヘッダーが見つかったら終了
            if current_line.strip().startswith("- **v"):
                break
            

            if current_line.strip() and (current_line.startswith("    - ") or current_line.startswith("\t- ")): # インデントとマーカーで判断
                summary_lines.append(current_line.strip()) # 先頭・末尾の空白を除去して追加
            elif current_line.strip() and not current_line.strip().startswith("- **v"): # 単純にインデントされた行で、次のバージョンヘッダでないもの

                 pass # より具体的な条件を設定するために一旦コメントアウト


        if not summary_lines: # 上記の条件で何も取れなかった場合のフォールバック
            temp_summary_lines = []
            for i in range(start_extraction_index, len(lines)):
                current_line_for_fallback = lines[i]
                if current_line_for_fallback.strip().startswith("- **v"): # 次のバージョンヘッダ
                    break
                if current_line_for_fallback.strip(): # 空行でなければ追加
                    temp_summary_lines.append(current_line_for_fallback.strip())
            summary_lines = temp_summary_lines


        if not summary_lines:
            # このメッセージは、バージョン行は見つかったが、その下に内容がなかった場合
            return f"バージョン {APP_VERSION} の更新内容の記載がありません。"
            
        return "\n".join(summary_lines)

    except Exception as e:
        print(f"Error in get_latest_release_notes_summary: {e}")
        return "最新の更新情報を取得中にエラーが発生しました。"


# --- GitHubリポジトリ情報 ---
# ご自身のGitHubリポジトリのURLに置き換えてください
GITHUB_REPO_URL = "https://github.com/6224025/stream" # 例

# --- 初回更新情報表示ロジック ---
def show_initial_update_notification():
    """
    現在のアプリバージョンが最後に確認されたバージョンと異なる場合、
    または初めてアクセスされた場合に更新情報を表示する。
    ユーザーが「確認しました」ボタンを押すと、そのセッションでは表示されなくなる。
    """
    if 'last_seen_version' not in st.session_state:
        st.session_state.last_seen_version = None
    if 'update_notification_confirmed_for_current_session' not in st.session_state:
        st.session_state.update_notification_confirmed_for_current_session = False

    # 現在のバージョンをまだ確認していない、かつ、このセッションでまだ確認ボタンを押していない場合
    if (st.session_state.last_seen_version != APP_VERSION and
            not st.session_state.update_notification_confirmed_for_current_session):

        latest_notes_summary = get_latest_release_notes_summary()

        with st.container():
            st.info(f"✨ アプリがバージョン **{APP_VERSION}** に更新されました！", icon="🎉")
            with st.expander("主な更新内容を見る", expanded=True):
                if latest_notes_summary:
                    st.markdown(latest_notes_summary)
                else:
                    st.markdown("新しい更新があります。詳細はサイドバーの更新履歴をご確認ください。")
                st.markdown("---")
                st.markdown("より詳細な更新履歴はサイドバーの「アプリ情報」をご確認ください。")

            # ボタンのキーにバージョンを含めることで、バージョンアップ時にキーが衝突するのを防ぐ
            button_key = f"confirm_update_notification_v{APP_VERSION.replace('.', '_')}"
            if st.button("OK、内容を確認しました！", key=button_key):
                st.session_state.last_seen_version = APP_VERSION
                st.session_state.update_notification_confirmed_for_current_session = True
                try:
                    st.experimental_rerun() # Streamlitのバージョンが0.88.0以降なら利用可能
                except AttributeError:
                    # experimental_rerun がない古いバージョンの場合のフォールバック
                    # この場合、即座には消えず、次のインタラクションで消える
                    pass
                st.rerun() # Streamlit 1.13.0 以降で推奨される方法

        return True  # 通知が表示されたことを示す
    return False # 通知は表示されなかった

# --- サイドバーにアプリ情報を表示する関数 ---
def display_sidebar_app_info():
    """サイドバーにアプリのバージョン情報と更新履歴を表示する"""
    st.sidebar.markdown("---")
    st.sidebar.header("アプリ情報")
    st.sidebar.subheader("バージョン")
    st.sidebar.write(f"現在のバージョン: **{APP_VERSION}**")

    with st.sidebar.expander("更新履歴を見る", expanded=False):
        st.markdown(RELEASE_NOTES_HISTORY)

    st.sidebar.subheader("フィードバック")
    st.sidebar.markdown(f"""
    バグ報告や機能要望は、お気軽に[GitHub Issues]({GITHUB_REPO_URL}/issues)までお寄せください。

    [ソースコードはこちら]({GITHUB_REPO_URL})
    """)

# --- "release" という名前で呼び出せるようにまとめる ---
class ReleaseInfo:
    def __init__(self):
        self.app_version = APP_VERSION
        self.history = RELEASE_NOTES_HISTORY
        self.github_url = GITHUB_REPO_URL

    def show_update_notification(self):
        """初回更新通知を表示する"""
        return show_initial_update_notification()

    def render_sidebar_info(self):
        """サイドバーにアプリ情報を表示する"""
        display_sidebar_app_info()

# グローバルなインスタンスを作成 (オプション)
# release_manager = ReleaseInfo()