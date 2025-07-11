# app.py
import streamlit as st
import sys
print("--- sys.path ---") # 追加
for p in sys.path: # 追加
    print(p) # 追加
print("--- end sys.path ---") # 追加
import modules.ui_components as ui
import modules.constants as co
import modules.data_handler as dh
import modules.fitting_calculator as fc
import modules.plot_generator as pg
import matplotlib.font_manager as fm

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
    df_orig = None      # 元の文字列データを保持するDF
    df_numeric = None   # 数値計算用のDF
    error_message_from_parser = None # 初期化

    with data_col:
        # データ入力UI (ui_componentsから)
        raw_data_str_from_ui = ui.render_data_input_area() # raw_data_str のみを受け取る
        
        if raw_data_str_from_ui:
            df_orig, df_numeric, error_message_from_parser = dh.parse_text_data(raw_data_str_from_ui)
            
            if error_message_from_parser:
                st.warning(error_message_from_parser) # data_handlerからのエラーメッセージを表示
                df_orig = None      # エラー時はDataFrameをNoneに
                df_numeric = None
            
            if df_orig is not None: # パース成功したらプレビュー表示 (元のデータを表示)
                st.write("読み込みデータプレビュー:")
                st.dataframe(df_orig.head(), height=200)


    with plot_col:
        st.subheader("グラフ表示")
        # 計算用データフレームが存在し、空でない場合のみプロット処理
        if df_numeric is not None and not df_numeric.empty:
            
            # 計算前にNaN（数値化できなかった文字列など）を含む行を削除
            df_plot_data = df_numeric.dropna()

            if df_plot_data.empty:
                st.warning("グラフにプロットできる有効な数値データがありません。")
            else:
                # --- グラフ描画処理の開始 ---
                
                # 1. FigureとAxesを1回だけ生成
                fig, ax = pg.create_figure_and_axes(graph_settings)

                # 2. 軸スケールを設定
                pg.set_plot_scale(ax, graph_settings["plot_type"])
                
                # 3. 元データをプロット (NaN除去後のデータを使用)
                pg.plot_data_points(ax, df_plot_data, graph_settings)

                # 4. 最終的な軸範囲を計算 (まだ適用はしない)
                final_xlim_calculated, final_ylim_calculated = pg.determine_final_axis_ranges(
                    ax, 
                    graph_settings,
                    df_plot_data['x'].values,
                    df_plot_data['y'].values
                )

                # 5. フィッティング計算 (1本目)
                fit_results_dict_1 = None
                if graph_settings["show_fitting"]:
                    fit_results_dict_1 = fc.calculate_fitting_parameters_v3(
                        df_plot_data['x'].values,
                        df_plot_data['y'].values,
                        graph_settings["plot_type"]
                    )

                # 5b. フィッティング計算 (2本目、範囲指定)
                fit_results_dict_2 = None
                if graph_settings.get("show_fitting_2"):
                    min_x = graph_settings.get('fit_range_x_min', df_plot_data['x'].min())
                    max_x = graph_settings.get('fit_range_x_max', df_plot_data['x'].max())
                    df_fit_range = df_plot_data[(df_plot_data['x'] >= min_x) & (df_plot_data['x'] <= max_x)]
                    if not df_fit_range.empty:
                        fit_results_dict_2 = fc.calculate_fitting_parameters_v3(
                            df_fit_range['x'].values,
                            df_fit_range['y'].values,
                            graph_settings["plot_type"]
                        )

                # 6. 計算された最終X軸範囲に基づいて近似線を描画 (1本目)
                if graph_settings.get("show_fitting", False) and \
                   fit_results_dict_1 is not None and not \
                   fit_results_dict_1.get("error_message"):
                    legend_label_1 = fc.get_fit_equation_string(fit_results_dict_1, graph_settings["plot_type"])
                    pg.plot_fit_line_on_final_axes(
                        ax,
                        final_xlim_calculated, 
                        df_plot_data['x'].values, 
                        fit_results_dict_1, 
                        graph_settings["plot_type"], 
                        graph_settings,
                        legend_label=legend_label_1,
                        line_style='--',
                        color='red'
                    )

                # 6b. 計算された最終X軸範囲に基づいて近似線を描画 (2本目)
                if graph_settings.get("show_fitting_2", False) and \
                   fit_results_dict_2 is not None and not \
                   fit_results_dict_2.get("error_message"):
                    legend_label_2 = fc.get_fit_equation_string(fit_results_dict_2, graph_settings["plot_type"])
                    pg.plot_fit_line_on_final_axes(
                        ax,
                        final_xlim_calculated, 
                        df_plot_data['x'].values, 
                        fit_results_dict_2, 
                        graph_settings["plot_type"], 
                        graph_settings,
                        legend_label=legend_label_2,
                        line_style=':',
                        color='green'
                    )

                # 7. 最終的な軸範囲をグラフに適用し、凡例を表示
                pg.apply_final_axes_and_legend(
                    ax,
                    final_xlim_calculated,
                    final_ylim_calculated,
                    graph_settings
                )

                # 8. グラフをStreamlitに表示
                st.pyplot(fig) 
                
                # --- グラフ描画処理の終了 ---

                # 9. ダウンロードボタンを表示
                ui.render_download_buttons(fig)

                # 10. フィッティング結果のテキスト情報を表示
                fit_info_placeholder = st.empty()
                with fit_info_placeholder.container():
                    # 1本目の結果表示
                    if graph_settings["show_fitting"] and fit_results_dict_1:
                        if fit_results_dict_1.get("error_message"):
                            st.warning(f"1本目のフィッティングエラー: {fit_results_dict_1['error_message']}")
                        else:
                            st.write(f"**フィッティング結果 ({graph_settings.get('fit_legend_label')})**")
                            ui.render_fitting_results_display(
                                fit_results_dict_1.get("equation_latex"),
                                f"$R^2 = {fit_results_dict_1.get('r_squared'):.4f}$" if fit_results_dict_1.get('r_squared') is not None else "",
                                fit_results_dict_1.get("slope_val") is not None, 
                                graph_settings["show_fitting"]
                            )
                    elif graph_settings["show_fitting"]:
                        st.warning("1本目のフィッティングに必要なデータが不足しているか、他の問題が発生しました。")

                    # 2本目の結果表示
                    if graph_settings["show_fitting_2"] and fit_results_dict_2:
                        if fit_results_dict_2.get("error_message"):
                            st.warning(f"2本目のフィッティングエラー: {fit_results_dict_2['error_message']}")
                        else:
                            st.write(f"**フィッティング結果 ({graph_settings.get('fit_legend_label_2')})**")
                            ui.render_fitting_results_display(
                                fit_results_dict_2.get("equation_latex"),
                                f"$R^2 = {fit_results_dict_2.get('r_squared'):.4f}$" if fit_results_dict_2.get('r_squared') is not None else "",
                                fit_results_dict_2.get("slope_val") is not None, 
                                graph_settings["show_fitting_2"]
                            )
                    elif graph_settings["show_fitting_2"]:
                        st.warning("2本目のフィッティングに必要なデータが不足しているか、他の問題が発生しました。")

                # 11. LaTeXデータテーブルのエクスポート機能を表示 (元のデータを渡す)
                ui.render_data_table_latex_export(df_orig, graph_settings)

        elif df_numeric is None and raw_data_str_from_ui and not error_message_from_parser:
            st.warning("グラフを表示するには、まず有効なデータを入力してください。")
        elif df_numeric is None and error_message_from_parser:
            pass 
        elif not raw_data_str_from_ui:
             st.info("左側のテキストエリアにデータを入力すると、ここにグラフが表示されます。")
             