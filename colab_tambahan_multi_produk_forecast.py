
# ============================================================
# TAMBAHAN COLAB: MULTI-PRODUCT FORECASTING
# Copy semua kode ini ke cell paling bawah notebook Colab kamu,
# setelah notebook utama berhasil export hasil CSV.
# ============================================================

import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

OUTPUT_DIR = '/content/drive/MyDrive/output_forecasting_retail_uk'
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_PRODUCTS_TO_FORECAST = 30
FORECAST_HORIZON = 8

def mape_safe(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mask = y_true != 0
    if mask.sum() == 0:
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def evaluate_model(y_true, y_pred):
    y_pred = np.maximum(y_pred, 0)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = mape_safe(y_true, y_pred)
    try:
        r2 = r2_score(y_true, y_pred)
    except Exception:
        r2 = np.nan
    return mae, rmse, mape, r2

def make_weekly_sales_for_product(df_product, stockcode):
    df_selected = df_product[df_product['StockCode'] == stockcode].copy()
    weekly = df_selected.groupby('WeekStart').agg(
        quantity_sold=('Quantity', 'sum'),
        revenue=('TotalSales', 'sum'),
        invoice_count=('InvoiceNo', 'nunique'),
        avg_unit_price=('UnitPrice', 'mean')
    ).reset_index().sort_values('WeekStart')

    if weekly.empty:
        return weekly

    full_weeks = pd.DataFrame({
        'WeekStart': pd.date_range(
            start=weekly['WeekStart'].min(),
            end=weekly['WeekStart'].max(),
            freq='W-MON'
        )
    })

    weekly = full_weeks.merge(weekly, on='WeekStart', how='left')
    weekly['quantity_sold'] = weekly['quantity_sold'].fillna(0)
    weekly['revenue'] = weekly['revenue'].fillna(0)
    weekly['invoice_count'] = weekly['invoice_count'].fillna(0)
    weekly['avg_unit_price'] = weekly['avg_unit_price'].ffill().bfill()
    return weekly

def build_features(weekly):
    ts = weekly.copy()
    ts['time_index'] = np.arange(len(ts))
    ts['year'] = ts['WeekStart'].dt.year
    ts['month'] = ts['WeekStart'].dt.month
    ts['quarter'] = ts['WeekStart'].dt.quarter
    ts['weekofyear'] = ts['WeekStart'].dt.isocalendar().week.astype(int)

    for lag in [1, 2, 3, 4, 8]:
        ts[f'lag_{lag}'] = ts['quantity_sold'].shift(lag)

    ts['rolling_mean_3'] = ts['quantity_sold'].shift(1).rolling(3).mean()
    ts['rolling_mean_4'] = ts['quantity_sold'].shift(1).rolling(4).mean()
    ts['rolling_mean_8'] = ts['quantity_sold'].shift(1).rolling(8).mean()
    ts['rolling_std_4'] = ts['quantity_sold'].shift(1).rolling(4).std()
    ts['lag_revenue_1'] = ts['revenue'].shift(1)
    ts['lag_invoice_1'] = ts['invoice_count'].shift(1)
    return ts.dropna().reset_index(drop=True)

def train_product_model(model_data):
    feature_cols = [
        'time_index', 'year', 'month', 'quarter', 'weekofyear',
        'lag_1', 'lag_2', 'lag_3', 'lag_4', 'lag_8',
        'rolling_mean_3', 'rolling_mean_4', 'rolling_mean_8', 'rolling_std_4',
        'lag_revenue_1', 'lag_invoice_1', 'avg_unit_price'
    ]

    train_size = int(len(model_data) * 0.80)
    train = model_data.iloc[:train_size].copy()
    test = model_data.iloc[train_size:].copy()

    if len(train) < 10 or len(test) < 3:
        return None

    X_train = train[feature_cols]
    y_train = train['quantity_sold']
    X_test = test[feature_cols]
    y_test = test['quantity_sold']

    models = {
        'Moving Average 4 Minggu': None,
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Random Forest Regressor': RandomForestRegressor(
            n_estimators=120, random_state=42, max_depth=5, min_samples_leaf=2
        ),
        'Gradient Boosting Regressor': GradientBoostingRegressor(
            random_state=42, n_estimators=100, learning_rate=0.05, max_depth=3
        )
    }

    results = []
    trained = {}

    for name, model in models.items():
        if name == 'Moving Average 4 Minggu':
            pred = test['rolling_mean_4'].values
        else:
            model.fit(X_train, y_train)
            pred = np.maximum(model.predict(X_test), 0)
            trained[name] = model

        mae, rmse, mape, r2 = evaluate_model(y_test, pred)
        results.append({'Model': name, 'MAE': mae, 'RMSE': rmse, 'MAPE (%)': mape, 'R2': r2})

    metrics = pd.DataFrame(results).sort_values('RMSE').reset_index(drop=True)
    best_name = metrics.iloc[0]['Model']
    best_model = None if best_name == 'Moving Average 4 Minggu' else trained[best_name]

    return {
        'feature_cols': feature_cols,
        'best_model_name': best_name,
        'best_model': best_model,
        'metrics': metrics,
        'mae': metrics.iloc[0]['MAE']
    }

def forecast_product_future(weekly, model, model_name, feature_cols, horizon=8):
    history = weekly.copy().reset_index(drop=True)
    rows = []
    last_date = history['WeekStart'].max()
    avg_price = history['avg_unit_price'].dropna().iloc[-1]

    for step in range(1, horizon + 1):
        future_date = last_date + pd.Timedelta(weeks=step)
        qty = history['quantity_sold'].values

        row = {
            'time_index': len(history),
            'year': future_date.year,
            'month': future_date.month,
            'quarter': ((future_date.month - 1) // 3) + 1,
            'weekofyear': int(future_date.isocalendar().week),
            'lag_1': qty[-1],
            'lag_2': qty[-2] if len(qty) >= 2 else qty[-1],
            'lag_3': qty[-3] if len(qty) >= 3 else qty[-1],
            'lag_4': qty[-4] if len(qty) >= 4 else qty[-1],
            'lag_8': qty[-8] if len(qty) >= 8 else qty[-1],
            'rolling_mean_3': np.mean(qty[-3:]) if len(qty) >= 3 else np.mean(qty),
            'rolling_mean_4': np.mean(qty[-4:]) if len(qty) >= 4 else np.mean(qty),
            'rolling_mean_8': np.mean(qty[-8:]) if len(qty) >= 8 else np.mean(qty),
            'rolling_std_4': np.std(qty[-4:], ddof=1) if len(qty) >= 4 else 0,
            'lag_revenue_1': history['revenue'].iloc[-1],
            'lag_invoice_1': history['invoice_count'].iloc[-1],
            'avg_unit_price': avg_price
        }

        if model_name == 'Moving Average 4 Minggu':
            pred = row['rolling_mean_4']
        else:
            pred = model.predict(pd.DataFrame([row])[feature_cols])[0]

        pred = max(float(pred), 0)
        pred_round = int(round(pred))

        rows.append({
            'Forecast_Week_Number': step,
            'Forecast_Date': future_date,
            'Predicted_Quantity': pred_round
        })

        new_row = {
            'WeekStart': future_date,
            'quantity_sold': pred_round,
            'revenue': pred_round * avg_price,
            'invoice_count': row['lag_invoice_1'],
            'avg_unit_price': avg_price
        }
        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

    return pd.DataFrame(rows)

eligible = product_summary[
    (product_summary['active_weeks'] >= 25) &
    (product_summary['invoice_count'] >= 80)
].copy()

if eligible.empty:
    eligible = product_summary.copy()

eligible['score'] = (
    eligible['total_quantity'].rank(pct=True) * 0.45 +
    eligible['total_revenue'].rank(pct=True) * 0.30 +
    eligible['invoice_count'].rank(pct=True) * 0.15 +
    eligible['active_weeks'].rank(pct=True) * 0.10
)

candidate_products = eligible.sort_values('score', ascending=False).head(MAX_PRODUCTS_TO_FORECAST)

print('Jumlah produk yang akan diprediksi:', len(candidate_products))
display(candidate_products[['StockCode', 'Description', 'total_quantity', 'total_revenue', 'invoice_count', 'active_weeks', 'score']].head(10))

all_forecasts = []
all_metrics = []
all_weekly = []

for _, product in candidate_products.iterrows():
    stockcode = product['StockCode']
    desc = product['Description']
    print('Memproses:', stockcode, '-', desc)

    try:
        weekly = make_weekly_sales_for_product(df_product, stockcode)
        if weekly.empty or len(weekly) < 20:
            print('  skip: data mingguan sedikit')
            continue

        weekly['StockCode'] = stockcode
        weekly['Description'] = desc
        all_weekly.append(weekly)

        model_data = build_features(weekly)
        if len(model_data) < 15:
            print('  skip: data model sedikit')
            continue

        result = train_product_model(model_data)
        if result is None:
            print('  skip: training tidak cukup')
            continue

        forecast = forecast_product_future(
            weekly,
            result['best_model'],
            result['best_model_name'],
            result['feature_cols'],
            horizon=FORECAST_HORIZON
        )

        safety = int(np.ceil(result['mae']))
        forecast['StockCode'] = stockcode
        forecast['Description'] = desc
        forecast['Best_Model'] = result['best_model_name']
        forecast['Model_MAE'] = result['mae']
        forecast['Safety_Stock'] = safety
        forecast['Recommended_Stock_Weekly'] = forecast['Predicted_Quantity'] + safety
        forecast['Historical_Total_Quantity'] = product['total_quantity']
        forecast['Historical_Total_Revenue'] = product['total_revenue']
        forecast['Historical_Invoice_Count'] = product['invoice_count']
        forecast['Historical_Active_Weeks'] = product['active_weeks']

        all_forecasts.append(forecast)

        metrics = result['metrics'].copy()
        metrics['StockCode'] = stockcode
        metrics['Description'] = desc
        all_metrics.append(metrics)

    except Exception as e:
        print('  error:', e)

multi_product_forecast = pd.concat(all_forecasts, ignore_index=True)
multi_product_model_metrics = pd.concat(all_metrics, ignore_index=True)
multi_product_weekly_sales = pd.concat(all_weekly, ignore_index=True)

summary_2w = multi_product_forecast[
    multi_product_forecast['Forecast_Week_Number'] <= 2
].groupby(['StockCode', 'Description']).agg(
    Predicted_Quantity_2_Weeks=('Predicted_Quantity', 'sum'),
    Safety_Stock=('Safety_Stock', 'max'),
    Best_Model=('Best_Model', 'first'),
    Model_MAE=('Model_MAE', 'first'),
    Historical_Total_Quantity=('Historical_Total_Quantity', 'first'),
    Historical_Total_Revenue=('Historical_Total_Revenue', 'first'),
    Historical_Invoice_Count=('Historical_Invoice_Count', 'first'),
    Historical_Active_Weeks=('Historical_Active_Weeks', 'first')
).reset_index()

summary_2w['Recommended_Stock_2_Weeks'] = np.ceil(
    summary_2w['Predicted_Quantity_2_Weeks'] + summary_2w['Safety_Stock']
).astype(int)

q75 = summary_2w['Predicted_Quantity_2_Weeks'].quantile(0.75)
q40 = summary_2w['Predicted_Quantity_2_Weeks'].quantile(0.40)

summary_2w['Potensi_Laris'] = np.where(
    summary_2w['Predicted_Quantity_2_Weeks'] >= q75,
    'Sangat Laris',
    np.where(summary_2w['Predicted_Quantity_2_Weeks'] >= q40, 'Cukup Laris', 'Rendah')
)

summary_2w = summary_2w.sort_values('Predicted_Quantity_2_Weeks', ascending=False).reset_index(drop=True)
summary_2w['Rank_2_Weeks'] = np.arange(1, len(summary_2w) + 1)

multi_product_forecast.to_csv(os.path.join(OUTPUT_DIR, 'multi_product_forecast.csv'), index=False)
multi_product_model_metrics.to_csv(os.path.join(OUTPUT_DIR, 'multi_product_model_metrics.csv'), index=False)
multi_product_weekly_sales.to_csv(os.path.join(OUTPUT_DIR, 'multi_product_weekly_sales.csv'), index=False)
summary_2w.to_csv(os.path.join(OUTPUT_DIR, 'multi_product_summary_2weeks.csv'), index=False)

print('Selesai export multi-product forecasting ke:', OUTPUT_DIR)
display(summary_2w.head(10))
