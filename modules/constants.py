# modules/constants.py
import streamlit as st
from streamlit_local_storage import LocalStorage  # ライブラリをインポート

# --- アプリのバージョン情報 ---
APP_VERSION = "v0.1.3"  # アプリを更新するたびにここを変更

_local_storage_instance = None

def get_local_storage():
    """LocalStorageのインスタンスを取得する（シングルトン的に扱う）"""
    global _local_storage_instance
    if _local_storage_instance is None:
        _local_storage_instance = LocalStorage()
    return _local_storage_instance

def load_release_notes(filepath="release_notes.md"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "リリースノートファイルが見つかりません。"

RELEASE_NOTES_HISTORY = load_release_notes()


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
GITHUB_REPO_URL = "https://github.com/6224025/stream"

# --- 初回更新情報表示ロジック ---
def show_initial_update_notification():
    """
    現在のアプリバージョンがlocalStorageに保存されたバージョンと異なる場合、
    またはlocalStorageにバージョン情報がない場合に更新情報を表示する。
    ユーザーが「確認しました」ボタンを押すと、localStorageに現在のバージョンが保存され、
    かつ現在のセッションでは表示されなくなる。
    """
    localS = get_local_storage() # 関数内でインスタンスを取得
    # localStorageから最後に確認したバージョンを取得
    # getItemの第二引数は、キーが存在しない場合のデフォルト値（ここではNone）
    last_seen_version_from_storage = localS.getItem("app_last_seen_version")

    # 現在のバージョンに対する「確認済み」フラグのセッションステートキー
    # これにより、ボタンクリック後に即座に通知を非表示にし、同一セッションでの再表示を防ぐ
    confirmed_this_session_key = f"update_notification_confirmed_for_{APP_VERSION}"

    # 通知を表示すべきかどうかの条件判断
    # 1. localStorageに保存されているバージョンが現在のアプリバージョンと異なる
    # 2. または、localStorageにバージョン情報がまだ保存されていない (初回アクセスなど)
    # 3. かつ、現在のセッションでこのバージョンに対する「確認しました」ボタンがまだ押されていない
    should_display_notification = (
        (last_seen_version_from_storage != APP_VERSION or last_seen_version_from_storage is None) and
        not st.session_state.get(confirmed_this_session_key, False)
    )

    if should_display_notification:
        latest_notes_summary = get_latest_release_notes_summary()

        with st.container():
            st.info(f"✨ アプリがバージョン **{APP_VERSION}** に更新されました！", icon="🎉")
            with st.expander("主な更新内容を見る", expanded=True):
                if latest_notes_summary and not latest_notes_summary.startswith("履歴内にバージョン") and not latest_notes_summary.startswith("バージョン {APP_VERSION} の更新内容の記載がありません。"):
                    st.markdown(latest_notes_summary)
                else: # get_latest_release_notes_summary がエラーメッセージや該当なしメッセージを返した場合
                    st.markdown(f"新しい更新があります。詳細はサイドバーの更新履歴をご確認ください。\n({latest_notes_summary})")

                st.markdown("---")
                st.markdown("より詳細な更新履歴はサイドバーの「アプリ情報」をご確認ください。")

            button_key = f"confirm_update_notification_btn_v{APP_VERSION.replace('.', '_')}"
            if st.button("OK、内容を確認しました！", key=button_key):
                # localStorage に現在のバージョンを保存
                localS.setItem("app_last_seen_version", APP_VERSION)
                # 現在のセッションでこのバージョンを確認済みにする
                st.session_state[confirmed_this_session_key] = True
                st.rerun() # UIを即時更新して通知を消す

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