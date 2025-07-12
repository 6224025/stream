import streamlit as st
import sys
import modules.ui_components as ui
import modules.constants as co
import modules.data_handler as dh
import modules.fitting_calculator as fc
import modules.plot_generator as pg

st.set_page_config(layout="wide", page_title="簡易グラフ作成アプリ")
st.title("簡易グラフ作成アプリ")

notification_was_shown = co.show_initial_update_notification()

# サイドバーのメイン設定は常にレンダリング
graph_settings = ui.render_sidebar_main_settings()

# メインコンテンツの表示制御
if not notification_was_shown:
    # --- データ入力 ---
    data_col, plot_col = st.columns([1, 2])
    with data_col:
        raw_data_str = ui.render_data_input_area()
        df_orig, df_numeric, error_message = dh.parse_text_data(raw_data_str)
        if error_message:
            st.warning(error_message)
        if df_orig is not None:
            st.write("読み込みデータプレビュー:")
            st.dataframe(df_orig.head(), height=200)

    # --- フィッティング計算（UI描画の前） ---
    fit_results_1 = None
    if graph_settings.get('show_fitting') and df_numeric is not None and not df_numeric.empty:
        df_plot_data = df_numeric.dropna()
        if not df_plot_data.empty:
            fit_results_1 = fc.calculate_fitting_parameters_v3(
                df_plot_data['x'].values, df_plot_data['y'].values, graph_settings["plot_type"]
            )

    # --- サイドバー（凡例設定） ---
    legend_settings = ui.render_sidebar_legend_settings(graph_settings, fit_results_1)
    graph_settings.update(legend_settings)

    co.display_sidebar_app_info()

    # --- グラフ描画 ---
    with plot_col:
        st.subheader("グラフ表示")
        if df_numeric is not None and not df_numeric.empty:
            df_plot_data = df_numeric.dropna()
            if df_plot_data.empty:
                st.warning("グラフにプロットできる有効な数値データがありません。")
            else:
                fig, ax = pg.create_figure_and_axes(graph_settings)
                pg.set_plot_scale(ax, graph_settings["plot_type"])
                pg.plot_data_points(ax, df_plot_data, graph_settings)

                final_xlim, final_ylim = pg.determine_final_axis_ranges(
                    ax, graph_settings, df_plot_data['x'].values, df_plot_data['y'].values
                )

                if graph_settings.get("show_fitting") and fit_results_1 and not fit_results_1.get("error_message"):
                    pg.plot_fit_line_on_final_axes(
                        ax, final_xlim, df_plot_data['x'].values, fit_results_1, 
                        graph_settings["plot_type"], graph_settings, 
                        legend_label=graph_settings.get("fit_legend_label", ""),
                        line_style='--', color='red'
                    )

                # (2本目のフィッティングロジックはここに続く...)

                pg.apply_final_axes_and_legend(ax, final_xlim, final_ylim, graph_settings)
                st.pyplot(fig)
                ui.render_download_buttons(fig)

                # フィッティング結果表示
                if graph_settings.get("show_fitting") and fit_results_1:
                    ui.render_fitting_results_display(
                        fit_results_1.get("equation_latex"),
                        f"$R^2 = {fit_results_1.get('r_squared'):.4f}$" if fit_results_1.get('r_squared') is not None else "",
                        fit_results_1.get("slope_val") is not None,
                        graph_settings.get("show_fitting")
                    )

                ui.render_data_table_latex_export(df_orig, graph_settings)

        elif raw_data_str and not error_message:
            st.warning("グラフを表示するには、まず有効なデータを入力してください。")
        elif not raw_data_str:
            st.info("左側のテキストエリアにデータを入力すると、ここにグラフが表示されます。")
             