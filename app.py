# app.py
import streamlit as st
# import pandas as pd # data_handlerで使う
# import numpy as np # fitting_calculator, plot_generatorで使う
# import matplotlib.pyplot as plt # plot_generatorで使う
# from scipy import stats # fitting_calculatorで使う
# import io # data_handlerで使う
import matplotlib_fontja # インポートするだけで効果あり

import modules.constants as co
import modules.ui_components as ui
import modules.data_handler as dh
import modules.fitting_calculator as fc
import modules.plot_generator as pg

# --- アプリケーションの基本設定 ---
st.set_page_config(layout="wide", page_title="簡易グラフ作成アプリ")
st.title("簡易グラフ作成アプリ")

# --- 更新情報表示 ---
notification_was_shown = co.show_initial_update_notification()
if not notification_was_shown:
    st.caption("テキストエリアにスペース区切りの数値データを貼り付けてグラフを作成します。")

# --- サイドバー ---
graph_settings = ui.render_sidebar_graph_settings()
co.display_sidebar_app_info()

# --- メインコンテンツ ---
if not notification_was_shown:
    data_col, plot_col = st.columns([1, 2])

    raw_data_str_from_ui = "" # 初期化
    df_from_data_module = None # 初期化

    with data_col:
        # データ入力UI (ui_componentsから)
        raw_data_str_from_ui, _ = ui.render_data_input_area() # dfはここで使わない
        # データパース (data_handlerから)
        if raw_data_str_from_ui:
            df_from_data_module = dh.parse_text_data(raw_data_str_from_ui)
            if df_from_data_module is not None: # パース成功したらプレビュー表示
                st.write("読み込みデータプレビュー:")
                st.dataframe(df_from_data_module.head(), height=200)


    with plot_col:
        st.subheader("グラフ表示")
        if df_from_data_module is not None and not df_from_data_module.empty:
            # 1. 基本的なFigureとAxesを作成 (plot_generatorから)
            fig, ax = pg.create_figure_and_axes(graph_settings)

            # 2. グラフのスケールを設定 (plot_generatorから)
            pg.set_plot_scale(ax, graph_settings["plot_type"])
            
            # 3. 元データをプロット (plot_generatorから)
            pg.plot_data_points(ax, df_from_data_module, graph_settings)

            # 4. フィッティング計算 (fitting_calculatorから)
            fit_results_dict = None
            if graph_settings["show_fitting"]:
                fit_results_dict = fc.calculate_fitting_parameters_v3( # 関数名変更
                    df_from_data_module['x'].values,
                    df_from_data_module['y'].values,
                    graph_settings["plot_type"]
                )
            
            # 5. フィッティング結果に基づいて近似線を描画 (plot_generatorから)
            if fit_results_dict and not fit_results_dict.get("error_message"):
                 pg.plot_fit_line(ax, df_from_data_module['x'].values, fit_results_dict, graph_settings["plot_type"], graph_settings)

            # 6. 凡例などの最終処理 (plot_generatorから)
            pg.finalize_plot(ax, graph_settings)

            # 7. グラフをStreamlitに表示
            st.pyplot(fig)

            # 8. フィッティング結果のテキスト情報を表示 (ui_componentsから)
            fit_info_placeholder = st.empty()
            with fit_info_placeholder.container():
                if graph_settings["show_fitting"] and fit_results_dict:
                    if fit_results_dict.get("error_message"):
                        st.warning(fit_results_dict["error_message"])
                    else:
                        ui.render_fitting_results_display(
                            fit_results_dict.get("equation_latex"),
                            f"$R^2 = {fit_results_dict.get('r_squared'):.4f}$" if fit_results_dict.get('r_squared') is not None else "",
                            fit_results_dict.get("slope_val") is not None, # 修正: "slope" -> "slope_val"
                            graph_settings["show_fitting"]
                        )
                elif graph_settings["show_fitting"]: # フィッティングONだが結果がない (データ不足など)
                    st.warning("フィッティングに必要なデータが不足しているか、他の問題が発生しました。")


            # 9. ダウンロードボタンを表示 (ui_componentsから)
            ui.render_download_buttons(fig)

        elif df_from_data_module is None and raw_data_str_from_ui:
            st.warning("グラフを表示するには、まず有効なデータを入力してください。")
        else:
            st.info("左側のテキストエリアにデータを入力すると、ここにグラフが表示されます。")