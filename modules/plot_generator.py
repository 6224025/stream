# modules/plot_generator.py
import matplotlib.pyplot as plt
import numpy as np


def create_figure_and_axes(graph_settings):
    """基本的なFigureとAxesオブジェクトを作成し、軸ラベル等を設定する"""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlabel(graph_settings["x_label"])
    ax.set_ylabel(graph_settings["y_label"])
    ax.tick_params(direction='in', top=True, right=True, which='both')
    ax.minorticks_on()
    return fig, ax

def set_plot_scale(ax, plot_type):
    """グラフ種類に応じて軸のスケールを設定する"""
    if plot_type == "片対数 (Y軸対数)": ax.set_yscale('log')
    elif plot_type == "片対数 (X軸対数)": ax.set_xscale('log')
    elif plot_type == "両対数":
        ax.set_xscale('log')
        ax.set_yscale('log')
    # "通常" はデフォルトの線形スケール

def plot_data_points(ax, df, graph_settings):
    """元データをプロットする"""
    if graph_settings["show_legend"]:
        ax.plot(df['x'], df['y'], 'o', label=graph_settings["data_legend_label"], markersize=5)
    else:
        ax.plot(df['x'], df['y'], 'o', markersize=5)

def plot_fit_line(ax, x_data_orig, fit_results, plot_type, graph_settings):
    """フィッティング結果に基づいて近似直線/曲線を描画する"""
    if fit_results is None or fit_results.get("slope_val") is None or fit_results.get("error_message"): # 修正: "slope" -> "slope_val"
        return # フィット失敗時は描画しない

    plot_xlim = ax.get_xlim() # 現在のX軸表示範囲
    
    # X軸のスケールに合わせて点を生成
    if ax.get_xscale() == 'log':
        # xlimが負や0を含まないように注意 (通常は自動で調整されるはず)
        x_start = plot_xlim[0] if plot_xlim[0] > 0 else np.finfo(float).eps
        x_end = plot_xlim[1] if plot_xlim[1] > 0 else x_start * 100 # 仮
        if x_start >= x_end: # 範囲がおかしい場合のフォールバック
             x_start = np.min(x_data_orig[x_data_orig > 0]) if np.any(x_data_orig > 0) else 1e-3
             x_end = np.max(x_data_orig[x_data_orig > 0]) if np.any(x_data_orig > 0) else 1e+3
        x_fit_line = np.geomspace(x_start, x_end, 200)

    else:
        x_fit_line = np.linspace(plot_xlim[0], plot_xlim[1], 200)
    # フィット結果からパラメータの値を取得
    slope_val = fit_results.get("slope_val")
    intercept_val = fit_results.get("intercept_val")
    A_val = fit_results.get("A_val")
    B_val = fit_results.get("B_val")

    y_pred_line = np.zeros_like(x_fit_line, dtype=float) # dtypeを指定

    if plot_type == "通常":
        if slope_val is not None and intercept_val is not None:
            y_pred_line = slope_val * x_fit_line + intercept_val
        else: return # パラメータがない場合は描画しない
    elif plot_type == "片対数 (Y軸対数)": # y = A*exp(B*x)
        if A_val is not None and B_val is not None:
            y_pred_line = A_val * np.exp(B_val * x_fit_line)
        else: return
    elif plot_type == "片対数 (X軸対数)": # y = B*ln(x) + A
        if A_val is not None and B_val is not None and np.all(x_fit_line > 0):
             y_pred_line = B_val * np.log(x_fit_line) + A_val
        else: return 
    elif plot_type == "両対数": # y = A*x^B
        if A_val is not None and B_val is not None and np.all(x_fit_line > 0):
            y_pred_line = A_val * (x_fit_line ** B_val)
        else: return
    else: # 未知のプロットタイプ
        return

    # 描画範囲外やNaNになる可能性のある値をフィルタリング
    valid_plot_indices = np.isfinite(y_pred_line)
    if ax.get_yscale() == 'log':
        valid_plot_indices &= (y_pred_line > 0)
    
    if np.any(valid_plot_indices):
        if graph_settings["show_legend"]:
            ax.plot(x_fit_line[valid_plot_indices], y_pred_line[valid_plot_indices], '--', label='近似')
        else:
            ax.plot(x_fit_line[valid_plot_indices], y_pred_line[valid_plot_indices], '--')

def finalize_plot(ax, graph_settings):
    """凡例などを最終処理する"""
    if graph_settings["show_legend"]:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles, labels, loc='best')