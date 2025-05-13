# modules/data_handler.py
import pandas as pd
import io
# import streamlit as st # st.warning/error はここでは使わない

def parse_text_data(raw_data_str):
    """
    テキストエリアからの入力文字列をパースし、DataFrameとエラーメッセージを返す。
    成功時: (DataFrame, None)
    失敗時: (None, "エラーメッセージ")
    """
    if not raw_data_str.strip(): # 空白のみの入力も考慮
        return None, "データが入力されていません。"

    try:
        df = pd.read_csv(
            io.StringIO(raw_data_str), sep=r'\s+', header=None,
            names=['x', 'y'], dtype=float, comment='#'
        )
        if df.empty:
            return None, "データが読み込めませんでした。入力内容を確認してください。"
        if df.shape[1] != 2:
            return None, f"データは2列である必要がありますが、{df.shape[1]}列検出されました。"

    except Exception as e:
        # ユーザーフレンドリーなエラーメッセージを検討
        if "could not convert string to float" in str(e).lower():
            return None, "数値に変換できないデータが含まれています。スペース区切りの数値か確認してください。"
        return None, f"データ読み込み中に予期せぬエラーが発生しました: {e}"
    
    return df, None # 成功時はエラーメッセージなし