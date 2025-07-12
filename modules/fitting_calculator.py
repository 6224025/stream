
# modules/fitting_calculator.py
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def calculate_regression_uncertainties(x_numeric, y_numeric, slope, intercept, y_pred):

    n = len(x_numeric)
    if n <= 2: # 自由度が0以下になるため計算不可
        return np.nan, np.nan

    t_value = 1.0  # 包含係数を1に設定
    residuals = y_numeric - y_pred
    # 標準誤差 (RMSE / sqrt(n-2) ではない。残差平方和 / (n-2) の平方根)
    std_error_of_residuals = np.sqrt(np.sum(residuals**2) / (n - 2))
    
    x_mean = np.mean(x_numeric)
    sum_sq_x_dev = np.sum((x_numeric - x_mean)**2)

    if sum_sq_x_dev == 0: # 全てのxが同じ値の場合など
        return np.nan, np.nan

    slope_uncertainty = t_value * std_error_of_residuals / np.sqrt(sum_sq_x_dev)
    intercept_uncertainty = t_value * std_error_of_residuals * np.sqrt(1/n + x_mean**2 / sum_sq_x_dev)
    
    return slope_uncertainty, intercept_uncertainty


def perform_linear_fit_sklearn_with_uncertainty(x_numeric, y_numeric, fit_intercept=True):
    """
    scikit-learnで線形フィットを行い、傾き、切片、R^2、および不確かさを返す。
    """
    print(f"\n--- DEBUG: Entering perform_linear_fit_sklearn_with_uncertainty ---")
    print(f"DEBUG: x_numeric (first 5): {x_numeric[:5]}, type: {type(x_numeric)}, dtype: {getattr(x_numeric, 'dtype', 'N/A')}, shape: {getattr(x_numeric, 'shape', 'N/A')}")
    print(f"DEBUG: y_numeric (first 5): {y_numeric[:5]}, type: {type(y_numeric)}, dtype: {getattr(y_numeric, 'dtype', 'N/A')}, shape: {getattr(y_numeric, 'shape', 'N/A')}")
    print(f"DEBUG: fit_intercept: {fit_intercept}")

    min_points = 2 if fit_intercept else 1
    if len(x_numeric) < min_points or len(y_numeric) < min_points or len(x_numeric) != len(y_numeric):
        print(f"DEBUG: Condition fail: Not enough data points or mismatched length. len(x)={len(x_numeric)}, len(y)={len(y_numeric)}")
        return None, np.nan, None, np.nan, None

    if np.any(np.isnan(x_numeric)) or np.any(np.isinf(x_numeric)) or \
       np.any(np.isnan(y_numeric)) or np.any(np.isinf(y_numeric)):
        print(f"DEBUG: Condition fail: NaN or Inf found in input data.")
        return None, np.nan, None, np.nan, None

    try:
        model = LinearRegression(fit_intercept=fit_intercept)
        X_fit = x_numeric.reshape(-1, 1)
        print(f"DEBUG: X_fit for model.fit (shape): {X_fit.shape}")
        model.fit(X_fit, y_numeric)
        print(f"DEBUG: Model fitting successful.")

        slope = model.coef_[0]
        intercept = model.intercept_ if fit_intercept else 0.0
        print(f"DEBUG: slope: {slope}, intercept: {intercept}")
        
        y_pred = model.predict(X_fit)
        r_squared = r2_score(y_numeric, y_pred)
        print(f"DEBUG: r_squared: {r_squared}")
        
        slope_err, intercept_err = np.nan, np.nan 
        if fit_intercept:
            print(f"DEBUG: Calculating uncertainties...")
            slope_err, intercept_err = calculate_regression_uncertainties(x_numeric, y_numeric, slope, intercept, y_pred)
            print(f"DEBUG: slope_err: {slope_err}, intercept_err: {intercept_err}")
        else:
            print(f"DEBUG: Skipping uncertainties calculation (fit_intercept=False).")


    except Exception as e:
        print(f"DEBUG: Exception during sklearn fitting or uncertainty calculation: {e}")
        import traceback
        traceback.print_exc() # 詳細なトレースバックを出力
        return None, np.nan, None, np.nan, None

    print(f"DEBUG: Returning from perform_linear_fit_sklearn_with_uncertainty: slope={slope}, slope_err={slope_err}, intercept={intercept}, intercept_err={intercept_err}, r_squared={r_squared}")
    return slope, slope_err, intercept, intercept_err, r_squared


def calculate_fitting_parameters_v3(x_data_orig, y_data_orig, plot_type): # fit_origin は一旦削除
    """
    scikit-learnと提示された不確かさ計算を用いてフィッティング計算を行う。
    """
    x_transformed_np = x_data_orig.copy()
    y_transformed_np = y_data_orig.copy()
    valid_indices = np.ones(len(x_data_orig), dtype=bool)

    fit_results = {
        "slope_val": None, "slope_err": np.nan,
        "intercept_val": None, "intercept_err": np.nan,
        "A_val": None, "A_err": np.nan, # 指数/べき関数の係数とその誤差
        "B_val": None, "B_err": np.nan, # 指数/べき関数の指数部とその誤差
        "r_squared": None, "equation_latex": "", "equation_text": "",
        "x_transformed": None, "y_transformed": None,
        "valid_indices": None, "error_message": None
    }

    # データの対数変換
    if plot_type == "通常":
        pass
    elif plot_type == "片対数 (Y軸対数)":
        valid_indices = y_data_orig > 0
        if not np.any(valid_indices):
            fit_results["error_message"] = "Y軸対数のため、正のYデータが必要です。"
            return fit_results
        y_transformed_np = np.log(y_data_orig[valid_indices])
        x_transformed_np = x_data_orig[valid_indices]
    elif plot_type == "片対数 (X軸対数)":
        valid_indices = x_data_orig > 0
        if not np.any(valid_indices):
            fit_results["error_message"] = "X軸対数のため、正のXデータが必要です。"
            return fit_results
        x_transformed_np = np.log(x_data_orig[valid_indices])
        y_transformed_np = y_data_orig[valid_indices]
    elif plot_type == "両対数":
        valid_indices = (x_data_orig > 0) & (y_data_orig > 0)
        if not np.any(valid_indices):
            fit_results["error_message"] = "両対数のため、正のXおよびYデータが必要です。"
            return fit_results
        x_transformed_np = np.log(x_data_orig[valid_indices])
        y_transformed_np = np.log(y_data_orig[valid_indices])

    fit_results["x_transformed"] = x_transformed_np
    fit_results["y_transformed"] = y_transformed_np
    fit_results["valid_indices"] = valid_indices

    if x_transformed_np.size == 0 or y_transformed_np.size == 0:
        if not fit_results["error_message"]:
            fit_results["error_message"] = "フィットに使用できる有効なデータ点がありません。"
        return fit_results

    # フィット実行 (切片ありをデフォルトとする)
    s_val, s_err, i_val, i_err, r_sq = \
        perform_linear_fit_sklearn_with_uncertainty(x_transformed_np, y_transformed_np, fit_intercept=True)

    if s_val is None: # ここで s_val が None になっているか確認
        if not fit_results["error_message"]: # 他のエラーがなければ
            fit_results["error_message"] = "フィット計算に失敗しました。"
        print(f"DEBUG: s_val is None, returning with error message.")
        return fit_results
    

    fit_results.update({
        "slope_val": s_val, "slope_err": s_err,
        "intercept_val": i_val, "intercept_err": i_err,
        "r_squared": r_sq
    })
    
    # ±記号の後の誤差は、値が存在する場合のみ表示 (有効数字は仮)
    s_e_str = f" \pm {s_err:.3f}" if not np.isnan(s_err) else ""
    i_e_str = f" \pm {i_err:.3f}" if not np.isnan(i_err) else ""


    if plot_type == "通常":
        fit_results.update({
            "B_val": s_val, "B_err": s_err, "A_val": i_val, "A_err": i_err,
            "equation_text": f"y = ({s_val:.3f}{s_e_str})x + ({i_val:.3f}{i_e_str})",
            "equation_latex": rf"$y = ({s_val:.3f}{s_e_str})x + ({i_val:.3f}{i_e_str})$"
        })
    elif plot_type == "片対数 (Y軸対数)": # intercept = ln(A), slope = B
        A_v = np.exp(i_val)
        # 誤差伝播: δA = A * δ(lnA) = A * i_err
        A_e = A_v * i_err if not np.isnan(i_err) else np.nan
        B_v, B_e = s_val, s_err
        
        A_e_str = f" \pm {A_e:.1e}" if not np.isnan(A_e) else ""
        B_e_str = f" \pm {B_e:.2f}" if not np.isnan(B_e) else ""

        fit_results.update({
            "A_val": A_v, "A_err": A_e, "B_val": B_v, "B_err": B_e,
            "equation_text": f"y = ({A_v:.2e}{A_e_str}) exp(({B_v:.2f}{B_e_str})x)",
            "equation_latex": rf"$y = ({A_v:.2e}{A_e_str}) e^{{({B_v:.2f}{B_e_str})x}}$"
        })
    elif plot_type == "片対数 (X軸対数)": # intercept = A (切片), slope = B (ln(x)の係数)
        A_v, A_e = i_val, i_err
        B_v, B_e = s_val, s_err

        A_e_str = f" \pm {A_e:.2f}" if not np.isnan(A_e) else ""
        B_e_str = f" \pm {B_e:.2f}" if not np.isnan(B_e) else ""
        fit_results.update({
            "A_val": A_v, "A_err": A_e, "B_val": B_v, "B_err": B_e,
            "equation_text": f"y = ({B_v:.2f}{B_e_str}) ln(x) + ({A_v:.2f}{A_e_str})",
            "equation_latex": rf"$y = ({B_v:.2f}{B_e_str}) \ln(x) + ({A_v:.2f}{A_e_str})$"
        })
    elif plot_type == "両対数": # intercept = ln(A), slope = B
        A_v = np.exp(i_val)
        A_e = A_v * i_err if not np.isnan(i_err) else np.nan
        B_v, B_e = s_val, s_err

        A_e_str = f" \pm {A_e:.1e}" if not np.isnan(A_e) else ""
        B_e_str = f" \pm {B_e:.2f}" if not np.isnan(B_e) else ""
        fit_results.update({
            "A_val": A_v, "A_err": A_e, "B_val": B_v, "B_err": B_e,
            "equation_text": f"y = ({A_v:.2e}{A_e_str}) x^({B_v:.2f}{B_e_str})",
            "equation_latex": rf"$y = ({A_v:.2e}{A_e_str}) x^{{({B_v:.2f}{B_e_str})}}$"
        })
        
    return fit_results

def get_fit_equation_string(fit_results, plot_type):
    """
    近似式の凡例用の文字列を生成する。
    """
    if not fit_results or fit_results.get("error_message"):
        return "近似曲線" # デフォルトの凡例

    A_val = fit_results.get("A_val")
    B_val = fit_results.get("B_val")

    if A_val is None or B_val is None:
        return "近似曲線"

    if plot_type == "通常":
        # y = Bx + A
        return f"$y = {B_val:.3f}x {A_val:+.3f}$"
    elif plot_type == "片対数 (Y軸対数)":
        # y = A * exp(Bx)
        return f"$y = {A_val:.2e} e^{{{B_val:.2f}x}}$"
    elif plot_type == "片対数 (X軸対数)":
        # y = B * ln(x) + A
        return f"$y = {B_val:.2f} \\ln(x) {A_val:+.2f}$"
    elif plot_type == "両対数":
        # y = A * x^B
        return f"$y = {A_val:.2e} x^{{{B_val:.2f}}}$"
    
    return "近似曲線"
