# modules/ui_components.py
import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components 

def render_sidebar_graph_settings():
    """サイドバーにグラフ設定用のUI要素をレンダリングし、設定値を辞書で返す"""
    settings = {}
    st.sidebar.header("グラフ設定")
    
    st.sidebar.subheader("軸ラベル")
    settings['x_label'] = st.sidebar.text_input(
        "X軸ラベル", "X軸", help="物理量を斜体にするには `$` で囲みます。例: `時間 $t$ [s]`"
    )
    settings['y_label'] = st.sidebar.text_input(
        "Y軸ラベル", "Y軸", help="物理量を斜体にするには `$` で囲みます。例: `電圧 $V$ [V]`"
    )
    settings['data_legend_label'] = st.sidebar.text_input("データ点の凡例ラベル", "測定データ")

    st.sidebar.subheader("グラフオプション")
    settings['plot_type'] = st.sidebar.selectbox(
        "グラフ種類", ["通常", "片対数 (Y軸対数)", "片対数 (X軸対数)", "両対数"]
    )
    settings['show_legend'] = st.sidebar.checkbox("凡例を表示する", True)
    settings['show_fitting'] = st.sidebar.checkbox("最小二乗法でフィッティングを行う")
    # settings['fit_origin'] = st.sidebar.checkbox("原点を通るフィット (通常グラフのみ)", False) # これはフィッティングの計算方法の選択

    st.sidebar.subheader("軸範囲設定")
    settings['force_origin_visible'] = st.sidebar.checkbox("原点(0,0)をグラフに含める", False)
    
    settings['manual_x_axis'] = st.sidebar.checkbox("X軸の範囲を手動で設定する", False)
    if settings['manual_x_axis']:
        col_x_min, col_x_max = st.sidebar.columns(2)
        with col_x_min:
            settings['x_axis_min'] = st.number_input("X軸 最小値", value=0.0, format="%.3f", step=0.1)
        with col_x_max:
            settings['x_axis_max'] = st.number_input("X軸 最大値", value=10.0, format="%.3f", step=0.1)
            if settings['x_axis_min'] >= settings['x_axis_max']:
                st.sidebar.error("X軸の最大値は最小値より大きくしてください。")


    settings['manual_y_axis'] = st.sidebar.checkbox("Y軸の範囲を手動で設定する", False)
    if settings['manual_y_axis']:
        col_y_min, col_y_max = st.sidebar.columns(2)
        with col_y_min:
            settings['y_axis_min'] = st.number_input("Y軸 最小値", value=0.0, format="%.3f", step=0.1)
        with col_y_max:
            settings['y_axis_max'] = st.number_input("Y軸 最大値", value=10.0, format="%.3f", step=0.1)
            if settings['y_axis_min'] >= settings['y_axis_max']:
                st.sidebar.error("Y軸の最大値は最小値より大きくしてください。")
    
    return settings

def render_data_input_area():
    """メインエリアにデータ入力UIをレンダリングし、(raw_text, DataFrame)を返す"""
    df = None
    raw_data_str = "" 
    
    st.subheader("データ入力")
    raw_data_str = st.text_area(
        "ここにデータを貼り付けてください (スペース区切り、左列: X軸, 右列: Y軸)",
        height=300,
        placeholder="例:\n1.0 2.1\n2.0 3.9\n3.0 6.1\n4.0 8.2\n5.0 9.8"
    )

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
        
    return raw_data_str, df

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
            st.latex(fit_equation_latex) # LaTeXで数式をレンダリングして表示
            
            # st.code を使ってLaTeXソースを表示し、コピーボタンを付ける
            st.caption("近似式のLaTeXソース:")
            st.code(fit_equation_latex, language="latex")
            
            # コピーボタン (streamlit-extras を使う場合)
            # try:
            #     from streamlit_extras.st_copy_to_clipboard import st_copy_to_clipboard
            #     st_copy_to_clipboard(fit_equation_latex, button_text="LaTeXソースをコピー")
            # except ImportError:
            #     st.caption("（streamlit-extrasがインストールされていればコピーボタンが表示されます）")

            # コピーボタン (カスタムHTML/JSコンポーネント)
            button_id_eq = f"copy_eq_btn_{hash(fit_equation_latex)}"
            components.html(
                f"""
                <button id="{button_id_eq}" style="margin-top: 5px; padding: 5px 10px; border-radius: 5px; border: 1px solid #ccc; background-color: #f0f0f0; cursor: pointer;">
                    LaTeXソースをコピー
                </button>
                <script>
                document.getElementById("{button_id_eq}").onclick = function() {{
                    navigator.clipboard.writeText(`{fit_equation_latex.replace('`', '\\`')}`) // バッククォートをエスケープ
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
                """,
                height=45,
            )

        if fit_r_squared_text:
            st.write(fit_r_squared_text)
            
    elif show_fitting_toggle: # フィッティングオプションがONで、成功しなかった場合
        st.warning("選択されたグラフ種類とデータではフィッティングを実行できませんでした。")

        # modules/ui_components.py (続き)

def generate_latex_table(df, x_col_name='x', y_col_name='y', x_header='$x$', y_header='$y$'):
    """
    DataFrameをLaTeXのtabular形式の文字列に変換する。
    x_header, y_header はLaTeXで表示する列名。
    """
    if df is None or df.empty:
        return ""
    
    # LaTeXエスケープが必要な文字を処理 (オプションだが推奨)
    # ここでは簡単のため省略。必要なら ' চি_ ' を '\\_' にするなど

    latex_string = "\\begin{tabular}{|c|c|}\n"
    latex_string += "\\hline\n"
    latex_string += f"{x_header} & {y_header} \\\\\n" # ヘッダー行
    latex_string += "\\hline\n"
    
    for index, row in df.iterrows():
        # 数値のフォーマット (例: 小数点以下3桁)
        x_val_str = f"{row[x_col_name]:.3f}"
        y_val_str = f"{row[y_col_name]:.3f}"
        latex_string += f"{x_val_str} & {y_val_str} \\\\\n"
    
    latex_string += "\\hline\n"
    latex_string += "\\end{tabular}"
    
    return latex_string

def render_data_table_latex_export(df, graph_settings):


    """
    入力データをLaTeXのtable形式で表示し、コピーできるようにする。
    """
    if df is None or df.empty:
        return

    st.subheader("データテーブル (LaTeX)")
    
    # ユーザーが軸ラベルとして入力したものをテーブルヘッダーに使う
    # $で囲まれているものはそのまま使う
    x_header_latex = graph_settings.get('x_label', '$x$')
    y_header_latex = graph_settings.get('y_label', '$y$')
    # 単位部分などを除外したい場合は、ここを調整
    # 簡単な例: "時間 $t$ [s]" から "$t$" を抽出 (正規表現などが必要になるかも)
    # ここでは入力された軸ラベルをそのまま使う
    
    latex_table_str = generate_latex_table(df, x_header=x_header_latex, y_header=y_header_latex)
    
    if latex_table_str:
        st.caption("データのLaTeX tableソース:")
        st.code(latex_table_str, language="latex")
        
        button_id_table = f"copy_table_btn_{hash(latex_table_str)}"
        components.html(
            f"""
            <button id="{button_id_table}" style="margin-top: 5px; padding: 5px 10px; border-radius: 5px; border: 1px solid #ccc; background-color: #f0f0f0; cursor: pointer;">
                LaTeX tableソースをコピー
            </button>
            <script>
            document.getElementById("{button_id_table}").onclick = function() {{
                navigator.clipboard.writeText(`{latex_table_str.replace('`', '\\`')}`)
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
            """,
            height=45,
        )

