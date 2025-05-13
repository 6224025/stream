# app.py
import streamlit as st

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
    error_message_from_parser = None # 初期化

    with data_col:
        # データ入力UI (ui_componentsから)
        raw_data_str_from_ui = ui.render_data_input_area() # raw_data_str のみを受け取る
        
        df_from_data_module = None # 初期化
        error_message_from_parser = None # 初期化

        if raw_data_str_from_ui:
            df_from_data_module, error_message_from_parser = dh.parse_text_data(raw_data_str_from_ui)
            
            if error_message_from_parser:
                st.warning(error_message_from_parser) # data_handlerからのエラーメッセージを表示
                df_from_data_module = None # エラー時はDataFrameをNoneに
            
            if df_from_data_module is not None: # パース成功したらプレビュー表示
                st.write("読み込みデータプレビュー:")
                st.dataframe(df_from_data_module.head(), height=200)


    with plot_col:
        st.subheader("グラフ表示")
        if df_from_data_module is not None and not df_from_data_module.empty:
            # --- グラフ描画処理の開始 ---
            
            # 1. FigureとAxesを1回だけ生成
            fig, ax = pg.create_figure_and_axes(graph_settings)

            # 2. 軸スケールを設定
            pg.set_plot_scale(ax, graph_settings["plot_type"])
            
            # 3. 元データをプロット
            pg.plot_data_points(ax, df_from_data_module, graph_settings) # この時点でMatplotlibが自動で軸範囲を設定

            # 4. 最終的な軸範囲を計算 (まだ適用はしない)
            final_xlim_calculated, final_ylim_calculated = pg.determine_final_axis_ranges(
                ax, # データプロット後のaxを渡す
                graph_settings,
                df_from_data_module['x'].values,
                df_from_data_module['y'].values
            )

            # 5. フィッティング計算
            fit_results_dict = None
            if graph_settings["show_fitting"]:
                fit_results_dict = fc.calculate_fitting_parameters_v3( # または最新の関数名
                    df_from_data_module['x'].values,
                    df_from_data_module['y'].values,
                    graph_settings["plot_type"]
                )
            
            # 6. 計算された最終X軸範囲に基づいて近似線を描画
            if graph_settings.get("show_fitting", False) and \
               fit_results_dict is not None and not \
               fit_results_dict.get("error_message"):
                pg.plot_fit_line_on_final_axes(
                    ax,
                    final_xlim_calculated, # 計算された最終X範囲を渡す
                    df_from_data_module['x'].values, 
                    fit_results_dict, 
                    graph_settings["plot_type"], 
                    graph_settings
                )

            # 7. 最終的な軸範囲をグラフに適用し、凡例を表示
            pg.apply_final_axes_and_legend(
                ax,
                final_xlim_calculated,
                final_ylim_calculated,
                graph_settings
            )

            # 8. グラフをStreamlitに表示 (これが唯一の st.pyplot であるべき)
            st.pyplot(fig) 
            
            # --- グラフ描画処理の終了 ---


           # 9. ダウンロードボタンを表示 (グラフの下など)
            ui.render_download_buttons(fig) # これもグラフとは別のUI要素


            # 10. フィッティング結果のテキスト情報を表示 (グラフの下など)
            fit_info_placeholder = st.empty() # これはグラフとは別のUI要素
            with fit_info_placeholder.container():
                if graph_settings["show_fitting"] and fit_results_dict:
                    if fit_results_dict.get("error_message"):
                        st.warning(fit_results_dict["error_message"])
                    else:
                        ui.render_fitting_results_display( # ui_components の関数
                            fit_results_dict.get("equation_latex"),
                            f"$R^2 = {fit_results_dict.get('r_squared'):.4f}$" if fit_results_dict.get('r_squared') is not None else "",
                            fit_results_dict.get("slope_val") is not None, # 成功判定
                            graph_settings["show_fitting"]
                        )
                elif graph_settings["show_fitting"]:
                    st.warning("フィッティングに必要なデータが不足しているか、他の問題が発生しました。")

            
          
             # 11. LaTeXデータテーブルのエクスポート機能を表示
            ui.render_data_table_latex_export(df_from_data_module, graph_settings)


        elif df_from_data_module is None and raw_data_str_from_ui and not error_message_from_parser:
            # データはあるがパースに失敗し、かつ明示的なエラーメッセージがない場合 (通常は発生しにくい)
            st.warning("グラフを表示するには、まず有効なデータを入力してください。")
        elif df_from_data_module is None and error_message_from_parser:
            # パースエラーがあった場合は、data_colでメッセージ表示済みなので、plot_colでは特に何もしないか、
            # 別のメッセージを表示しても良い
            pass # または st.info("正しいデータを入力するとグラフが表示されます。")
        elif not raw_data_str_from_ui:
             st.info("左側のテキストエリアにデータを入力すると、ここにグラフが表示されます。")