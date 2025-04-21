import optuna
import joblib
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, precision_recall_curve
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from datetime import datetime
import mlflow
import mlflow.sklearn
import shap
import matplotlib.pyplot as plt

from app.data import get_stock_data
from app.model.features import generate_features
from app.model.evaluate import evaluate_model

# === Directories ===
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")
OPTUNA_DIR = os.path.join(BASE_DIR, "optuna")
SHAP_DIR = os.path.join(BASE_DIR, "shap")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OPTUNA_DIR, exist_ok=True)
os.makedirs(SHAP_DIR, exist_ok=True)

# === Threshold Tuning ===
def tune_threshold(y_true, probs):
    precisions, recalls, thresholds = precision_recall_curve(y_true, probs)
    f1s = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1s)
    return thresholds[best_idx], f1s[best_idx]

# === Optuna Objective Function ===
def objective(trial, ticker="AAPL"):
    df = get_stock_data(ticker)
    X, y = generate_features(df, ticker=ticker)
    if len(X) < 50:
        raise ValueError("Insufficient data")

    tscv = TimeSeriesSplit(n_splits=5)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model_type = trial.suggest_categorical("model", ["xgb", "lgb"])

        if model_type == "xgb":
            scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)
            model = XGBClassifier(
                n_estimators=trial.suggest_int("n_estimators", 100, 600),
                max_depth=trial.suggest_int("max_depth", 3, 12),
                learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
                subsample=trial.suggest_float("subsample", 0.5, 1.0),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
                eval_metric="logloss",
                use_label_encoder=False,
                scale_pos_weight=scale_pos_weight,
                verbosity=0
            )
        else:
            model = LGBMClassifier(
                n_estimators=trial.suggest_int("n_estimators", 100, 600),
                max_depth=trial.suggest_int("max_depth", 3, 12),
                learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3),
                subsample=trial.suggest_float("subsample", 0.5, 1.0),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
                min_gain_to_split=0.001,
                class_weight='balanced',
                verbosity=-1
            )

        model.fit(X_train, y_train)

        importances = model.feature_importances_
        importance_df = pd.DataFrame({"Feature": X_train.columns, "Importance": importances})
        low_importance = importance_df[importance_df["Importance"] < 1.0]["Feature"].tolist()

        if 0 < len(low_importance) < len(X_train.columns):
            X_train = X_train.drop(columns=low_importance)
            X_val = X_val.drop(columns=low_importance)
            model.fit(X_train, y_train)

        probs = model.predict_proba(X_val)[:, 1]
        threshold, f1 = tune_threshold(y_val, probs)
        scores.append(f1)

    return np.mean(scores)

# === Run Optimization ===
def run_optimization(ticker="AAPL", n_trials=50):
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, ticker), n_trials=n_trials)

    print(f"\n🏁 Best trial for {ticker}:")
    print(study.best_trial)

    # === Final Training ===
    df = get_stock_data(ticker)
    X, y = generate_features(df, ticker=ticker)
    X_train, X_val, y_train, y_val = train_test_split(X, y, shuffle=False, test_size=0.2)

    best_params = study.best_trial.params
    model_type = best_params.pop("model")

    if model_type == "xgb":
        scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)
        model = XGBClassifier(**best_params, eval_metric="logloss", use_label_encoder=False, scale_pos_weight=scale_pos_weight)
    else:
        model = LGBMClassifier(**best_params, min_gain_to_split=0.001, class_weight='balanced')

    model.fit(X_train, y_train)
    evaluate_model(model, X_val, y_val, ticker)

    # === SHAP Analysis ===
    shap_path = None
    try:
        explainer = shap.Explainer(model, X_train)
        shap_values = explainer(X_val)

        fig = plt.figure()
        shap.plots.beeswarm(shap_values, show=False)
        shap_path = os.path.join(SHAP_DIR, f"{ticker}_shap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(shap_path, bbox_inches='tight')
        plt.close(fig)
        print(f"[✓] SHAP summary plot saved to {shap_path}")
    except Exception as e:
        print(f"[!] SHAP generation failed: {e}")

    # === Save Predictions + Probs ===
    preds_df = pd.DataFrame({
        "y_true": y_val.values,
        "y_pred": model.predict(X_val),
        "proba": model.predict_proba(X_val)[:, 1]
    })
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    preds_path = os.path.join(MODEL_DIR, f"{ticker}_preds_{now}.csv")
    preds_df.to_csv(preds_path, index=False)

    # === Save Model & Study ===
    model_path = os.path.join(MODEL_DIR, f"{ticker}_{model_type}_optuna_{now}.pkl")
    study_path = os.path.join(OPTUNA_DIR, f"{ticker}_study_{now}.pkl")
    joblib.dump(model, model_path)
    joblib.dump(study, study_path)

    print(f"[✓] Model saved to {model_path}")
    print(f"[✓] Study saved to {study_path}")

    # === Evaluation Diagnostics ===
    print("\n Diagnostic Evaluation:")
    for name, X_, y_ in [("Train", X_train, y_train), ("Val", X_val, y_val)]:
        preds = model.predict(X_)
        print(f"\n{name} Report:\n", classification_report(y_, preds, digits=4))

    # === MLflow Logging ===
    try:
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment(ticker)

        if mlflow.active_run():
            mlflow.end_run()

        # Cast to float64 to avoid MLflow schema warning
        X_val_float = X_val.astype(np.float64)

        with mlflow.start_run():
            mlflow.set_tag("ticker", ticker)
            mlflow.log_params(study.best_trial.params)
            mlflow.log_metric("f1_score", study.best_value)
            mlflow.sklearn.log_model(
                model,
                "model",
                input_example=X_val_float.iloc[:1],
                signature=mlflow.models.infer_signature(X_val_float, model.predict(X_val))
            )
            mlflow.log_artifact(model_path)
            mlflow.log_artifact(study_path)
            mlflow.log_artifact(preds_path)
            if shap_path:
                mlflow.log_artifact(shap_path)

        print(f"[✓] MLflow logging complete.")
    except Exception as e:
        print(f"[WARNING] MLflow logging failed: {e}")



if __name__ == "__main__":
    run_optimization(ticker="AAPL", n_trials=50)




