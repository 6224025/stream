# modules/data_handler.py
import pandas as pd
import io
import streamlit as st # エラー/警告表示のため

def parse_text_data(raw_data_str):
    """
    テキストエリアからの入力文字列をパースし、DataFrameを返す。
    エラー時はNoneを返す。
    """
    df = None
    if not raw_data_str:
        return None # 入力がない場合はNoneを返す

    try:
        df = pd.read_csv(
            io.StringIO(raw_data_str), sep=r'\s+', header=None,
            names=['x', 'y'], dtype=float, comment='#'
        )
        if df.empty:
            st.warning("データが読み込めませんでした。入力内容を確認してください。") # UIへのフィードバックはapp.py側でも良い
            return None
        if df.shape[1] != 2:
            st.error(f"データは2列である必要がありますが、{df.shape[1]}列検出されました。")
            return None
        # 正常にパースできたらDataFrameを返す
        # st.write("読み込みデータプレビュー:") # プレビュー表示はui_componentsかapp.pyで行う
        # st.dataframe(df.head(), height=200)
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return None
    
    return df