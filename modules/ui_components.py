# modules/ui_components.py
import streamlit as st
import pandas as pd
import io

def render_sidebar_graph_settings():
    """サイドバーにグラフ設定用のUI要素をレンダリングし、設定値を辞書で返す"""
    settings = {}
    # この関数は直接st.sidebarのコンテキストを使用する
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
            st.latex(fit_equation_latex)
        if fit_r_squared_text:
            st.write(fit_r_squared_text)
    elif show_fitting_toggle: # フィッティングオプションがONで、成功しなかった場合
        st.warning("選択されたグラフ種類とデータではフィッティングを実行できませんでした。")
    # エラー発生時は app.py 側で st.error を表示する想定