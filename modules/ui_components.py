# modules/ui_components.py
import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

def render_sidebar_main_settings():
    """サイドバーの基本的なグラフ設定UI（凡例を除く）をレンダリングする"""
    settings = {}
    st.sidebar.header("グラフ設定")

    st.sidebar.subheader("軸ラベル")
    settings['x_label'] = st.sidebar.text_input(
        "X軸ラベル", "X軸", help="$で囲むとTex数式になります。例: `時間 $t$ [s]`"
    )
    settings['y_label'] = st.sidebar.text_input(
        "Y軸ラベル", "Y軸", help="$で囲むとTex数式になります。例: `電圧 $V$ [V]`"
    )
    
    settings['tick_length'] = st.sidebar.slider(
        "目盛りの長さ", 5, 15, 5, 1, help="グラフの主目盛りの長さを調整します"
    )

    st.sidebar.subheader("グラフオプション")
    settings['plot_type'] = st.sidebar.selectbox(
        "グラフ種類", ["通常", "片対数 (Y軸対数)", "片対数 (X軸対数)", "両対数"]
    )
    settings['show_legend'] = st.sidebar.checkbox("凡例を表示する", True)
    settings['show_fitting'] = st.sidebar.checkbox("最小二乗法でフィッティングを行う")
    settings['show_error_bars'] = st.sidebar.checkbox("エラーバーを表示する", False)
    return settings

def render_sidebar_second_fit_settings(graph_settings):
    """サイドバーの2本目の近似曲線設定UI（範囲指定のみ）をレンダリングする"""
    settings = {}
    st.sidebar.markdown("---")
    settings['show_fitting_2'] = st.sidebar.checkbox("範囲を指定して2本目の近似線を追加")
    if settings['show_fitting_2']:
        col_fit2_min, col_fit2_max = st.sidebar.columns(2)
        with col_fit2_min:
            # Streamlitの再実行時に値を保持するため、graph_settingsから現在の値を取得
            min_val = graph_settings.get('fit_range_x_min', 0.0)
            settings['fit_range_x_min'] = st.number_input("X軸の最小値", value=min_val, format="%.3f", step=0.1, key="fit_range_min")
        with col_fit2_max:
            max_val = graph_settings.get('fit_range_x_max', 10.0)
            settings['fit_range_x_max'] = st.number_input("X軸の最大値", value=max_val, format="%.3f", step=0.1, key="fit_range_max")
        
        if settings['fit_range_x_min'] >= settings['fit_range_x_max']:
            st.sidebar.error("X軸の最大値は最小値より大きくしてください。")
    return settings

def render_sidebar_axis_range_settings(graph_settings):
    """サイドバーの軸範囲設定UIをレンダリングする"""
    settings = {}
    st.sidebar.subheader("軸範囲設定")
    settings['axis_range_mode'] = st.sidebar.selectbox(
        "軸範囲の指定方法", ["自動", "原点を含める", "手動"], index=0, help="グラフの表示範囲を設定します。"
    )
    settings['force_origin_visible'] = (settings['axis_range_mode'] == "原点を含める")
    settings['manual_x_axis'] = (settings['axis_range_mode'] == "手動")
    if settings['manual_x_axis']:
        col_x_min, col_x_max = st.sidebar.columns(2)
        with col_x_min:
            settings['x_axis_min'] = st.number_input("X軸 最小値", value=0.0, format="%.3f", step=0.1, key="manual_x_min")
        with col_x_max:
            settings['x_axis_max'] = st.number_input("X軸 最大値", value=10.0, format="%.3f", step=0.1, key="manual_x_max")
        if settings.get('x_axis_min', 0.0) >= settings.get('x_axis_max', 10.0):
            st.sidebar.error("X軸の最大値は最小値より大きくしてください。")

    settings['manual_y_axis'] = (settings['axis_range_mode'] == "手動")
    if settings['manual_y_axis']:
        col_y_min, col_y_max = st.sidebar.columns(2)
        with col_y_min:
            settings['y_axis_min'] = st.number_input("Y軸 最小値", value=0.0, format="%.3f", step=0.1, key="manual_y_min")
        with col_y_max:
            settings['y_axis_max'] = st.number_input("Y軸 最大値", value=10.0, format="%.3f", step=0.1, key="manual_y_max")
        if settings.get('y_axis_min', 0.0) >= settings.get('y_axis_max', 10.0):
            st.sidebar.error("Y軸の最大値は最小値より大きくしてください。")
    return settings

def render_sidebar_legend_settings(graph_settings, fit_results_1=None, fit_results_2=None):
    """サイドバーの凡例設定UIをレンダリングする"""
    if not graph_settings.get('show_legend', True):
        return {}

    legend_settings = {}
    st.sidebar.subheader("凡例設定")
    
    # 凡例のテキスト入力がリセットされないように、現在の設定値をvalueに渡す
    legend_settings['data_legend_label'] = st.sidebar.text_input(
        "データ点の凡例", graph_settings.get('data_legend_label', "測定値"), key="data_legend_label"
    )

    if graph_settings.get('show_fitting'):
        # 計算済みの近似式をデフォルトの凡例にする
        default_fit_legend = "近似曲線"
        if fit_results_1 and fit_results_1.get("equation_latex"):
            default_fit_legend = fit_results_1.get("equation_latex")
        
        # ユーザーが入力した凡例があればそちらを優先する
        current_legend = graph_settings.get('fit_legend_label', default_fit_legend)
        legend_settings['fit_legend_label'] = st.sidebar.text_input(
            "1本目の近似線の凡例", value=current_legend, key="fit_legend_label_1"
        )

    if graph_settings.get('show_fitting_2'):
        default_fit_legend_2 = "範囲フィット"
        if fit_results_2 and fit_results_2.get("equation_latex"):
            default_fit_legend_2 = fit_results_2.get("equation_latex")
        
        current_legend_2 = graph_settings.get('fit_legend_label_2', default_fit_legend_2)
        legend_settings['fit_legend_label_2'] = st.sidebar.text_input(
            "2本目の近似線の凡例", value=current_legend_2, key="fit_legend_label_2"
        )

    legend_settings['legend_fontsize'] = st.sidebar.slider(
        "凡例の文字サイズ", 15, 20, graph_settings.get('legend_fontsize', 15), 1, help="凡例の文字サイズを設定します"
    )
    return legend_settings

def render_data_input_area():
    """メインエリアにデータ入力UIをレンダリングし、raw_textを返す"""
    raw_data_str = ""

    st.subheader("データ入力")
    raw_data_str = st.text_area(
        "ここにデータを貼り付けてください (スペース区切り、左列: X軸, 右列: Y軸)",
        height=300,
        placeholder="例:\n1.0 2.1\n2.0 3.9\n3.0 6.1\n4.0 8.2\n5.0 9.8"
    )

    return raw_data_str

def render_download_buttons(fig, png_filename="graph.png", svg_filename="graph.svg"):
    """
    Matplotlibのfigureオブジェクトを受け取り、PNGとSVGのダウンロードボタンを描画する。
    """
    if fig is None:
        return

    img_png = io.BytesIO()
    fig.savefig(img_png, format='png', dpi=300, bbox_inches='tight')
    img_png.seek(0)

    img_svg = io.BytesIO()
    fig.savefig(img_svg, format='svg', bbox_inches='tight')
    img_svg.seek(0)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="PNGでダウンロード",
            data=img_png,
            file_name=png_filename,
            mime="image/png",
            use_container_width=True
        )
    with col2:
        st.download_button(
            label="SVGでダウンロード",
            data=img_svg,
            file_name=svg_filename,
            mime="image/svg+xml",
            use_container_width=True
        )

def render_fitting_results_display(fit_equation_latex, fit_r_squared_text, fit_successful, show_fitting_toggle):
    """
    フィッティング結果の情報を表示するUI。
    fit_info_placeholder.container() の中で呼び出すことを想定。
    """
    if fit_successful:
        st.write(f"**フィッティング結果:**")
        if fit_equation_latex:
            st.caption("近似式のLaTeXソース:")
            fit_equation_latex_for_code = "$"+fit_equation_latex.replace("±", "\\pm")+"$"
            st.code( fit_equation_latex_for_code, language="latex")

            button_id_eq = f"copy_eq_btn_{hash(fit_equation_latex_for_code)}"
            components.html(
                f'''
                <button id="{button_id_eq}" style="margin-top: 5px; padding: 5px 10px; border-radius: 5px; border: 1px solid #ccc; background-color: #f0f0f0; cursor: pointer;">
                    LaTeXソースをコピー
                </button>
                <script>
                document.getElementById("{button_id_eq}").onclick = function() {{
                    navigator.clipboard.writeText(`{fit_equation_latex_for_code.replace('`', '\`')}`)
                    .then(() => {{
                        let btn = document.getElementById("{button_id_eq}");
                        let originalText = btn.innerText;
                        btn.innerText = "コピーしました!";
                        setTimeout(() => {{ btn.innerText = originalText; }}, 2000);
                    }})
                    .catch(err => {{
                        console.error('クリップボードへのコピーに失敗しました: ', err);
                        alert('コピーに失敗しました。コンソールでエラーを確認してください。');
                    }});
                }}
                </script>
                ''',
                height=45,
            )

    elif show_fitting_toggle:
        st.warning("選択されたグラフ種類とデータではフィッティングを実行できませんでした。")

def generate_latex_table(df, x_col_name='x', y_col_name='y', x_header='$x$', y_header='$y$'):
    """
    DataFrameをLaTeXのtabular形式の文字列に変換する。
    x_header, y_header はLaTeXで表示する列名。
    """
    if df is None or df.empty:
        return ""

    # LaTeXのソースコードを行ごとにリストとして作成
    # st.code()で正しく改行を表示するため、各行をリストの要素とし、最後に \n で結合する
    lines = [
        "\\begin{tabular}{cc}",
        "\\label{tab:table_label}",
        "\\caption{string}",
        "\\centering",
        "\\hline\\hline",
        f"{x_header} & {y_header} \\\\", # LaTeXの改行は \\
        "\\hline"
    ]

    # データ行を追加
    for index, row in df.iterrows():
        x_val_str = str(row[x_col_name])
        y_val_str = str(row[y_col_name])
        lines.append(f"{x_val_str} & {y_val_str} \\\\")

    # テーブルの終わり
    lines.extend([
        "\\hline\\hline",
        "\\end{tabular}"
    ])

    # Pythonの改行文字 `\n` で各行を結合して、単一の複数行文字列を返す
    return "\n".join(lines)

def render_data_table_latex_export(df, graph_settings):

    if df is None or df.empty:
        return

    st.subheader("データテーブル (LaTeX)")

    x_header_latex = graph_settings.get('x_label', '$x$')
    y_header_latex = graph_settings.get('y_label', '$y$')

    latex_table_str = generate_latex_table(df, x_header=x_header_latex, y_header=y_header_latex)

    if latex_table_str:
        st.caption("データのLaTeX tableソース:")
        st.code(latex_table_str, language="latex")

        button_id_table = f"copy_table_btn_{hash(latex_table_str)}"
        components.html(
            f'''
            <button id="{button_id_table}" style="margin-top: 5px; padding: 5px 10px; border-radius: 5px; border: 1px solid #ccc; background-color: #f0f0f0; cursor: pointer;">
                LaTeX ソースをコピー
            </button>
            <script>
            document.getElementById("{button_id_table}").onclick = function() {{
                navigator.clipboard.writeText(`{latex_table_str.replace('`', '\`').replace('\\', '\\\\')}`)
                .then(() => {{
                    let btn = document.getElementById("{button_id_table}");
                    let originalText = btn.innerText;
                    btn.innerText = "コピーしました!";
                    setTimeout(() => {{ btn.innerText = originalText; }}, 2000);
                }})
                .catch(err => {{
                    console.error('クリップボードへのコピーに失敗しました: ', err);
                    alert('コピーに失敗しました。コンソールでエラーを確認してください。');
                }});
            }}
            </script>
            ''',
            height=45,
        )
