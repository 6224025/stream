import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import io # StringIO と BytesIO のため
import matplotlib_fontja # 日本語文字化け対策 (こちらを使用)

# --- アプリのバージョン情報 ---
APP_VERSION = "v0.3.0" # アプリを更新するたびにここを変更

# --- アプリ情報・リリースノートの内容 (例) ---
# 更新履歴は最新のものが一番上にくるように記述
RELEASE_NOTES_HISTORY = f"""
- **v0.3.0 (YYYY-MM-DD)**
    - 新機能: アプリ更新時に初回のみ更新情報を表示する機能を追加。
    - 修正: 日本語フォントライブラリを `matplotlib-fontja` に変更。
    - 改善: 凡例の表示/非表示ロジックを調整。
    - 改善: 近似直線の描画範囲をグラフのX軸全体に拡大。
    - 改善: データ点の凡例ラベルをユーザーが指定可能に。
    - 修正: 格子線を削除。
- **v0.2.0 (YYYY-MM-DD)**
    - 機能: 軸ラベルの物理量を斜体で表示する説明を追加。
    - 機能: グラフダウンロード機能 (PNG, SVG) を追加。
- **v0.1.0 (YYYY-MM-DD)**
    - 初期リリース: 基本的なグラフ描画、最小二乗法フィッティング機能。
"""

LATEST_RELEASE_NOTES = f"""
### バージョン {APP_VERSION} の主な更新
{RELEASE_NOTES_HISTORY.split('- **v', 1)[1].split('-', 1)[0].strip()}

より詳細な更新履歴はサイドバーの「アプリ情報」をご確認ください。
"""


# --- 初回更新情報表示ロジック ---
def show_update_notification_once():
    """
    現在のアプリバージョンが最後に確認されたバージョンと異なる場合、
    または初めてアクセスされた場合に更新情報を表示する。
    ユーザーが「確認しました」ボタンを押すと、そのセッションでは表示されなくなる。
    """
    # st.session_stateの初期化 (キーが存在しない場合のエラーを防ぐため)
    if 'last_seen_version' not in st.session_state:
        st.session_state.last_seen_version = None
    if 'update_notification_confirmed' not in st.session_state:
        st.session_state.update_notification_confirmed = False


    # 現在のバージョンをまだ確認していない、かつ、今回のセッションでまだ確認ボタンを押していない場合
    if st.session_state.last_seen_version != APP_VERSION and not st.session_state.update_notification_confirmed:
        with st.container(): # 通知用のコンテナ
            st.info(f"✨ アプリがバージョン **{APP_VERSION}** に更新されました！", icon="🎉")
            with st.expander("主な更新内容を見る", expanded=True):
                st.markdown(LATEST_RELEASE_NOTES) # 最新の更新情報のみを抜粋して表示

            if st.button("OK、確認しました！", key="confirm_update_v" + APP_VERSION.replace(".", "_")):
                st.session_state.last_seen_version = APP_VERSION
                st.session_state.update_notification_confirmed = True # このセッションでは確認済み
                st.rerun() # ボタンクリック後にメッセージを消すため再実行
        return True # 通知が表示された
    return False # 通知は表示されなかった

# --- アプリケーションの基本設定 ---
st.set_page_config(layout="wide", page_title="簡易グラフ作成アプリ")
st.title("簡易グラフ作成アプリ")

# --- 更新情報表示 ---
# メインコンテンツの最初に呼び出す
notification_was_shown = show_update_notification_once()

# 通知が表示されている間はメインのUIを非表示にするか、そのまま表示するかは設計次第
# ここではそのまま表示するが、if not notification_was_shown: で囲むことも可能
if not notification_was_shown:
    st.caption("テキストエリアにスペース区切りの数値データを貼り付けてグラフを作成します。")


# --- サイドバー ---
st.sidebar.header("グラフ設定")

st.sidebar.subheader("軸ラベル")
x_label_input = st.sidebar.text_input(
    "X軸ラベル",
    "X軸",
    help="物理量を斜体にするには `$` で囲みます。例: `時間 $t$ [s]`"
)
y_label_input = st.sidebar.text_input(
    "Y軸ラベル",
    "Y軸",
    help="物理量を斜体にするには `$` で囲みます。例: `電圧 $V$ [V]`"
)
data_legend_label = st.sidebar.text_input("データ点の凡例ラベル", "測定データ")

st.sidebar.subheader("グラフオプション")
plot_type = st.sidebar.selectbox(
    "グラフ種類",
    ["通常", "片対数 (Y軸対数)", "片対数 (X軸対数)", "両対数"]
)
show_legend = st.sidebar.checkbox("凡例を表示する", True)
show_fitting = st.sidebar.checkbox("最小二乗法でフィッティングを行う")

st.sidebar.markdown("---")
st.sidebar.header("アプリ情報")
st.sidebar.subheader("バージョン")
st.sidebar.write(f"現在のバージョン: **{APP_VERSION}**")

with st.sidebar.expander("更新履歴を見る", expanded=False):
    st.markdown(RELEASE_NOTES_HISTORY)

st.sidebar.subheader("フィードバック")
# ご自身のGitHubリポジトリのURLに置き換えてください
GITHUB_REPO_URL = "https://github.com/yourusername/your-repo-name" # 例
st.sidebar.markdown(f"""
バグ報告や機能要望は、お気軽に[GitHub Issues]({GITHUB_REPO_URL}/issues)までお寄せください。

[ソースコードはこちら]({GITHUB_REPO_URL})
""")


# --- メインコンテンツ (通知が表示されていない場合、または通知と並行して表示する場合) ---
if not notification_was_shown: # 通知がメインコンテンツをブロックしないようにするならこのifは不要
    data_col, plot_col = st.columns([1, 2])

    with data_col:
        st.subheader("データ入力")
        raw_data_str = st.text_area(
            "ここにデータを貼り付けてください (スペース区切り、左列: X軸, 右列: Y軸)",
            height=300,
            placeholder="例:\n1.0 2.1\n2.0 3.9\n3.0 6.1\n4.0 8.2\n5.0 9.8"
        )

        df = None
        if raw_data_str:
            try:
                df = pd.read_csv(
                    io.StringIO(raw_data_str), sep=r'\s+', header=None,
                    names=['x', 'y'], dtype=float, comment='#'
                )
                if df.empty:
                    st.warning("データが読み込めませんでした。入力内容を確認してください。")
                    df = None
                elif df.shape[1] != 2:
                    st.error(f"データは2列である必要がありますが、{df.shape[1]}列検出されました。")
                    df = None
                else:
                    st.write("読み込みデータプレビュー:")
                    st.dataframe(df.head(), height=200)
            except Exception as e:
                st.error(f"データ読み込みエラー: {e}")
                df = None
        else:
            st.info("テキストエリアにデータを入力してください。")

    with plot_col:
        st.subheader("グラフ表示")
        if df is not None and not df.empty:
            fig, ax = plt.subplots(figsize=(10, 7))

            # データプロット
            if show_legend:
                ax.plot(df['x'], df['y'], 'o', label=data_legend_label, markersize=5)
            else:
                ax.plot(df['x'], df['y'], 'o', markersize=5)

            ax.set_xlabel(x_label_input)
            ax.set_ylabel(y_label_input)
            ax.tick_params(direction='in', top=True, right=True, which='both')
            ax.minorticks_on()

            original_x_data = df['x'].copy()
            original_y_data = df['y'].copy()
            x_data_for_fit = original_x_data.values
            y_data_for_fit = original_y_data.values
            
            current_xlim_before_scale_change = ax.get_xlim()
            current_ylim_before_scale_change = ax.get_ylim()

            if plot_type == "片対数 (Y軸対数)":
                ax.set_yscale('log')
            elif plot_type == "片対数 (X軸対数)":
                ax.set_xscale('log')
            elif plot_type == "両対数":
                ax.set_xscale('log')
                ax.set_yscale('log')
            
            # スケール変更後に軸範囲が自動調整されるが、場合によっては明示的な設定が必要
            # ここでは、元のデータ範囲に基づいて再設定することを試みる（特に通常スケール）
            if plot_type == "通常":
                 if not np.allclose(current_xlim_before_scale_change, ax.get_xlim()): # 軸範囲が変わっていたら
                     ax.set_xlim(current_xlim_before_scale_change)
                 if not np.allclose(current_ylim_before_scale_change, ax.get_ylim()):
                     ax.set_ylim(current_ylim_before_scale_change)

            fit_info_placeholder = st.empty()

            if show_fitting:
                fit_successful = False
                fit_equation_latex = ""
                fit_r_squared_text = ""
                
                # グラフの現在のX軸表示範囲を取得してフィットラインを描画
                plot_xlim = ax.get_xlim()
                x_fit_line = np.linspace(plot_xlim[0], plot_xlim[1], 200)

                try:
                    if plot_type == "通常":
                        slope, intercept, r_value, _, _ = stats.linregress(x_data_for_fit, y_data_for_fit)
                        y_pred_line = slope * x_fit_line + intercept
                        if show_legend:
                            ax.plot(x_fit_line, y_pred_line, '--', label='近似直線')
                        else:
                            ax.plot(x_fit_line, y_pred_line, '--')
                        fit_equation_latex = rf"y = {slope:.4f}x + {intercept:.4f}"
                        fit_r_squared_text = f"$R^2 = {(r_value**2):.4f}$"
                        fit_successful = True

                    elif plot_type == "片対数 (Y軸対数)":
                        valid_indices = y_data_for_fit > 0
                        if not np.any(valid_indices): st.warning("フィッティングエラー: Y軸対数のため、正のYデータが必要です。")
                        else:
                            slope, intercept, r_value, _, _ = stats.linregress(x_data_for_fit[valid_indices], np.log(y_data_for_fit[valid_indices]))
                            A, B = np.exp(intercept), slope
                            y_pred_line = A * np.exp(B * x_fit_line)
                            valid_pred_indices = y_pred_line > 0 # 0以下は対数プロットできない
                            if show_legend:
                                ax.plot(x_fit_line[valid_pred_indices], y_pred_line[valid_pred_indices], '--', label='近似曲線')
                            else:
                                ax.plot(x_fit_line[valid_pred_indices], y_pred_line[valid_pred_indices], '--')
                            fit_equation_latex = rf"y = {A:.4e} e^{{({B:.4f})x}}"
                            fit_r_squared_text = f"$R^2$ (対数空間) $= {(r_value**2):.4f}$"
                            fit_successful = True
                    
                    elif plot_type == "片対数 (X軸対数)":
                        valid_indices = x_data_for_fit > 0
                        if not np.any(valid_indices): st.warning("フィッティングエラー: X軸対数のため、正のXデータが必要です。")
                        else:
                            slope, intercept_fit, r_value, _, _ = stats.linregress(np.log(x_data_for_fit[valid_indices]), y_data_for_fit[valid_indices])
                            A, B_const = slope, intercept_fit
                            valid_x_fit_line_indices = x_fit_line > 0
                            y_pred_line = A * np.log(x_fit_line[valid_x_fit_line_indices]) + B_const
                            if show_legend:
                                ax.plot(x_fit_line[valid_x_fit_line_indices], y_pred_line, '--', label='近似曲線')
                            else:
                                ax.plot(x_fit_line[valid_x_fit_line_indices], y_pred_line, '--')
                            fit_equation_latex = rf"y = {A:.4f} \ln(x) + {B_const:.4f}"
                            fit_r_squared_text = f"$R^2$ (X対数空間) $= {(r_value**2):.4f}$"
                            fit_successful = True

                    elif plot_type == "両対数":
                        valid_indices = (x_data_for_fit > 0) & (y_data_for_fit > 0)
                        if not np.any(valid_indices): st.warning("フィッティングエラー: 両対数のため、正のXおよびYデータが必要です。")
                        else:
                            slope, intercept_fit, r_value, _, _ = stats.linregress(np.log(x_data_for_fit[valid_indices]), np.log(y_data_for_fit[valid_indices]))
                            A, B_power = np.exp(intercept_fit), slope
                            valid_x_fit_line_indices = x_fit_line > 0
                            y_pred_line_temp = A * (x_fit_line[valid_x_fit_line_indices] ** B_power)
                            valid_y_pred_indices = y_pred_line_temp > 0
                            final_x_to_plot = x_fit_line[valid_x_fit_line_indices][valid_y_pred_indices]
                            final_y_to_plot = y_pred_line_temp[valid_y_pred_indices]
                            if show_legend:
                                ax.plot(final_x_to_plot, final_y_to_plot, '--', label='近似曲線')
                            else:
                                ax.plot(final_x_to_plot, final_y_to_plot, '--')
                            fit_equation_latex = rf"y = {A:.4e} x^{{({B_power:.4f})}}"
                            fit_r_squared_text = f"$R^2$ (両対数空間) $= {(r_value**2):.4f}$"
                            fit_successful = True
                    
                    if fit_successful:
                        with fit_info_placeholder.container():
                            st.write(f"**フィッティング結果:**")
                            st.latex(fit_equation_latex)
                            st.write(fit_r_squared_text)
                    elif show_fitting:
                        fit_info_placeholder.warning("選択されたグラフ種類とデータではフィッティングを実行できませんでした。")
                except Exception as e:
                    fit_info_placeholder.error(f"フィッティング中にエラーが発生しました: {e}")
            
            if show_legend:
                handles, labels = ax.get_legend_handles_labels()
                if handles: ax.legend(handles, labels, loc='best')

            st.pyplot(fig)

            fn_png, fn_svg = "graph.png", "graph.svg"
            img_png, img_svg = io.BytesIO(), io.BytesIO()
            fig.savefig(img_png, format='png', dpi=300, bbox_inches='tight')
            fig.savefig(img_svg, format='svg', bbox_inches='tight')
            img_png.seek(0); img_svg.seek(0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("PNGでダウンロード", img_png, fn_png, "image/png", use_container_width=True)
            with col2:
                st.download_button("SVGでダウンロード", img_svg, fn_svg, "image/svg+xml", use_container_width=True)

        elif df is None and raw_data_str:
            st.warning("グラフを表示するには、まず有効なデータを入力してください。")
        else:
            st.info("左側のテキストエリアにデータを入力すると、ここにグラフが表示されます。")

# --- requirements.txt に含めるべきもの ---
# streamlit
# pandas
# numpy
# matplotlib
# scipy
# matplotlib-fontja # 日本語フォント用
# openpyxl (将来のExcel対応のため)
# setuptools (python3.12でdistutils関連エラーが出る場合)