# modules/data_handler.py
import pandas as pd
import io


def parse_text_data(raw_data_str):
    """
    テキストデータをパースし、元の文字列を保持したDataFrameと、
    数値計算用のDataFrameを返す。
    """
    if not raw_data_str.strip():
        return None, None, "データが入力されていません。"

    try:
        # まずは dtype を指定せずに、文字列として読み込む
        df_orig = pd.read_csv(
            io.StringIO(raw_data_str), sep=r'\s+', header=None,
            names=['x', 'y'], comment='#'
        )
        if df_orig.empty:
            return None, None, "データが読み込めませんでした。入力内容を確認してください。"
        if df_orig.shape[1] != 2:
            return None, None, f"データは2列である必要がありますが、{df_orig.shape[1]}列検出されました。"

        # 計算用の数値データフレームを作成
        # to_numeric を使い、数値に変換できないものは NaN (Not a Number) にする
        df_numeric = df_orig.apply(pd.to_numeric, errors='coerce')

    except Exception as e:
        return None, None, f"データ読み込み中に予期せぬエラーが発生しました: {e}"
    
    # 元のデータフレームと、数値計算用のデータフレーム、エラーメッセージなしを返す
    return df_orig, df_numeric, None