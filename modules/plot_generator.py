# modules/plot_generator.py
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib_fontja  # 日本語フォントを有効にするためのインポート
# --- フォントと共通設定 ---

# 日本語用フォントプロパティ（単体動作確認済みのIPAGothic）

jp_font = fm.FontProperties(family='IPAGothic')

# 数式フォントの設定（英語テキスト描画の要）
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False

import matplotlib.ticker as ticker
import numpy as np

def create_figure_and_axes(graph_settings):
    # ... (変更なし) ...
    fig, ax = plt.subplots(figsize=(10, 7))

    # 目盛りのフォーマッターを設定し、不要な桁を削減
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
    
    # 軸ラベルの文字サイズを設定から取得（デフォルトは12）
    fontsize = graph_settings.get("axis_label_fontsize", 14)
    tick_length = graph_settings.get("tick_length", 5)
    
    ax.set_xlabel(graph_settings["x_label"], fontsize=fontsize)
    ax.set_ylabel(graph_settings["y_label"], fontsize=fontsize)
    ax.tick_params(direction='in', top=True, right=True, which='major', length=tick_length)
    ax.tick_params(direction='in', top=True, right=True, which='minor', length=tick_length / 2)
    ax.tick_params(labelsize=12) # 目盛りの文字サイズを設定
    ax.minorticks_on()
    return fig, ax

def set_plot_scale(ax, plot_type):
    # ... (変更なし) ...
    if plot_type == "片対数 (Y軸対数)": ax.set_yscale('log')
    elif plot_type == "片対数 (X軸対数)": ax.set_xscale('log')
    elif plot_type == "両対数":
        ax.set_xscale('log')
        ax.set_yscale('log')

def plot_data_points(ax, df, graph_settings):
    # ... (変更なし) ...
    if graph_settings.get("show_error_bars"):
        y_err = None
        if 'y_error' in df.columns and df['y_error'].notna().any():
            y_err = df['y_error']
        else:
            y_err = df['y'].std() / np.sqrt(df['y'].count())
        
        ax.errorbar(df['x'], df['y'], yerr=y_err, fmt='o', label=graph_settings["data_legend_label"], markersize=5, capsize=3)
    else:
        if graph_settings["show_legend"]:
            ax.plot(df['x'], df['y'], 'o', label=graph_settings["data_legend_label"], markersize=5)
        else:
            ax.plot(df['x'], df['y'], 'o', markersize=5)


def determine_final_axis_ranges(ax, graph_settings, x_data_orig=None, y_data_orig=None):
    """
    データ点プロット後のaxオブジェクトと設定に基づき、最終的なX軸・Y軸の範囲を計算して返す。
    この時点では ax.set_xlim/ylim は行わない。
    """
    # ... (変更なし) ...
    current_xlim_auto = ax.get_xlim()
    current_ylim_auto = ax.get_ylim()

    final_xlim_to_return = list(current_xlim_auto)
    final_ylim_to_return = list(current_ylim_auto)

    if graph_settings.get('force_origin_visible', False) and \
       ax.get_xscale() != 'log' and ax.get_yscale() != 'log':
        final_xlim_to_return[0] = min(0, final_xlim_to_return[0])
        final_xlim_to_return[1] = max(0, final_xlim_to_return[1])
        final_ylim_to_return[0] = min(0, final_ylim_to_return[0])
        final_ylim_to_return[1] = max(0, final_ylim_to_return[1])

    if graph_settings.get('manual_x_axis', False):
        x_min_setting = graph_settings.get('x_axis_min')
        x_max_setting = graph_settings.get('x_axis_max')
        if x_min_setting is not None and x_max_setting is not None and x_min_setting < x_max_setting:
            if ax.get_xscale() == 'log':
                x_min_final_manual = x_min_setting if x_min_setting > 0 else \
                                     (np.min(x_data_orig[x_data_orig>0]) if x_data_orig is not None and np.any(x_data_orig>0) else np.finfo(float).eps)
                x_max_final_manual = x_max_setting if x_max_setting > x_min_final_manual else \
                                     (np.max(x_data_orig[x_data_orig>0]) if x_data_orig is not None and np.any(x_data_orig>0) and np.max(x_data_orig[x_data_orig>0]) > x_min_final_manual else x_min_final_manual * 100)
                if x_min_final_manual < x_max_final_manual:
                    final_xlim_to_return = [x_min_final_manual, x_max_final_manual]
            else:
                final_xlim_to_return = [x_min_setting, x_max_setting]
        else:
            print("Manual X axis range is invalid, using auto/origin-adjusted range.")

    if graph_settings.get('manual_y_axis', False):
        y_min_setting = graph_settings.get('y_axis_min')
        y_max_setting = graph_settings.get('y_axis_max')
        if y_min_setting is not None and y_max_setting is not None and y_min_setting < y_max_setting:
            if ax.get_yscale() == 'log':
                y_min_final_manual = y_min_setting if y_min_setting > 0 else \
                                     (np.min(y_data_orig[y_data_orig>0]) if y_data_orig is not None and np.any(y_data_orig>0) else np.finfo(float).eps)
                y_max_final_manual = y_max_setting if y_max_setting > y_min_final_manual else \
                                     (np.max(y_data_orig[y_data_orig>0]) if y_data_orig is not None and np.any(y_data_orig>0) and np.max(y_data_orig[y_data_orig>0]) > y_min_final_manual else y_min_final_manual * 100)
                if y_min_final_manual < y_max_final_manual:
                    final_ylim_to_return = [y_min_final_manual, y_max_final_manual]
            else:
                final_ylim_to_return = [y_min_setting, y_max_setting]
        else:
            print("Manual Y axis range is invalid, using auto/origin-adjusted range.")

    return tuple(final_xlim_to_return), tuple(final_ylim_to_return)


def plot_fit_line_on_final_axes(ax, final_xlim_to_use, x_data_orig, fit_results, plot_type, graph_settings, legend_label, line_style, color):
    """
    指定された最終X軸範囲 (final_xlim_to_use) に基づいて近似直線/曲線を描画する。
    凡例ラベル、線のスタイル、色を引数で指定できる。
    """
    if fit_results is None or fit_results.get("slope_val") is None or fit_results.get("error_message"):
        return

    current_x_scale = ax.get_xscale()

    if current_x_scale == 'log':
        x_start_for_line = final_xlim_to_use[0] if final_xlim_to_use[0] > 0 else np.finfo(float).eps
        x_end_for_line = final_xlim_to_use[1]
        if x_start_for_line >= x_end_for_line: # フォールバック
             x_data_positive = x_data_orig[x_data_orig > 0]
             x_start_for_line = np.min(x_data_positive) if np.any(x_data_positive) else 1e-3
             x_end_for_line = np.max(x_data_positive) if np.any(x_data_positive) else 1e+3
             if x_start_for_line >= x_end_for_line: x_start_for_line=1e-1; x_end_for_line=1e1;
        x_fit_line = np.geomspace(x_start_for_line, x_end_for_line, 200)
    else: # 線形スケール
        x_fit_line = np.linspace(final_xlim_to_use[0], final_xlim_to_use[1], 200)

    slope_val = fit_results.get("slope_val")
    intercept_val = fit_results.get("intercept_val")
    A_val = fit_results.get("A_val")
    B_val = fit_results.get("B_val")
    y_pred_line = np.zeros_like(x_fit_line, dtype=float)

    can_plot_fit = True
    if plot_type == "通常":
        if slope_val is not None and intercept_val is not None: y_pred_line = slope_val * x_fit_line + intercept_val
        else: can_plot_fit = False
    elif plot_type == "片対数 (Y軸対数)":
        if A_val is not None and B_val is not None: y_pred_line = A_val * np.exp(B_val * x_fit_line)
        else: can_plot_fit = False
    elif plot_type == "片対数 (X軸対数)":
        if A_val is not None and B_val is not None and np.all(x_fit_line > 0): y_pred_line = B_val * np.log(x_fit_line) + A_val
        else: can_plot_fit = False
    elif plot_type == "両対数":
        if A_val is not None and B_val is not None and np.all(x_fit_line > 0): y_pred_line = A_val * (x_fit_line ** B_val)
        else: can_plot_fit = False
    else:
        can_plot_fit = False

    if can_plot_fit and np.any(y_pred_line):
        valid_plot_indices = np.isfinite(y_pred_line)
        if ax.get_yscale() == 'log':
            valid_plot_indices &= (y_pred_line > 0)

        if np.any(valid_plot_indices):
            if graph_settings.get("show_legend", True):
                ax.plot(x_fit_line[valid_plot_indices], y_pred_line[valid_plot_indices], linestyle=line_style, color=color, label=legend_label)
            else:
                ax.plot(x_fit_line[valid_plot_indices], y_pred_line[valid_plot_indices], linestyle=line_style, color=color)


def apply_final_axes_and_legend(ax, final_xlim, final_ylim, graph_settings):
    """最終的な軸範囲を適用し、凡例を表示する"""
    # ... (変更なし) ...
    if final_xlim is not None and final_xlim[0] < final_xlim[1]:
        ax.set_xlim(final_xlim)
    if final_ylim is not None and final_ylim[0] < final_ylim[1]:
        ax.set_ylim(final_ylim)

    if graph_settings.get("show_legend", True):
        handles, labels = ax.get_legend_handles_labels()
        if handles: # 凡例エントリが実際に存在する場合のみ表示
            legend_fontsize = graph_settings.get("legend_fontsize", 20)
            ax.legend(handles, labels, loc='best', fontsize=legend_fontsize)