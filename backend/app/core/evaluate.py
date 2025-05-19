import os
import json
import logging
import joblib
import mlflow
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

mlflow.set_tracking_uri("http://localhost:5000")

# Setup logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Metrics directory
METRICS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "metrics"))
os.makedirs(METRICS_DIR, exist_ok=True)

def tune_threshold(y_true, y_probs, metric="f1"):
    thresholds = np.linspace(0.0, 1.0, 101)
    best_score = 0
    best_threshold = 0.5

    for t in thresholds:
        y_pred = (y_probs >= t).astype(int)

        if metric == "f1":
            score = f1_score(y_true, y_pred)
        elif metric == "precision":
            score = precision_score(y_true, y_pred)
        elif metric == "recall":
            score = recall_score(y_true, y_pred)
        else:
            raise ValueError("Unsupported metric")

        if score > best_score:
            best_score = score
            best_threshold = t

    print(f"✅ Best threshold for {metric}: {best_threshold:.2f} (score: {best_score:.4f})")
    return best_threshold

def evaluate_model(
    model,
    X_test,
    y_test,
    ticker: str,
    label_names=("Hold/Sell", "Buy"),
    log_to_mlflow=True,
    override_run=False
) -> dict:
    """
    Evaluates a trained model and logs metrics, visualizations, and metadata.
    Returns a dictionary of key evaluation metrics.
    """

    # ─── Predict ──────────────────────────────────────────────────────────────
    y_pred = model.predict(X_test)

    # ─── Metrics ──────────────────────────────────────────────────────────────
    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall    = recall_score(y_test, y_pred, zero_division=0)
    f1        = f1_score(y_test, y_pred, zero_division=0)
    report    = classification_report(y_test, y_pred, target_names=label_names, output_dict=True)

    logger.info(f"📊 Evaluation for {ticker}:")
    logger.info(f"  • Accuracy:  {accuracy:.2%}")
    logger.info(f"  • Precision: {precision:.2%}")
    logger.info(f"  • Recall:    {recall:.2%}")
    logger.info(f"  • F1 Score:  {f1:.2%}")

    # ─── Save JSON report ─────────────────────────────────────────────────────
    json_path = os.path.join(METRICS_DIR, f"{ticker}_report.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=4)
    logger.info(f"✓ Classification report saved ➞ {json_path}")

    # ─── Save confusion matrix image ──────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=label_names,
                yticklabels=label_names)
    plt.title(f"{ticker} — Confusion Matrix")
    plt.tight_layout()

    cm_path = os.path.join(METRICS_DIR, f"{ticker}_confusion_matrix.png")
    plt.savefig(cm_path)
    plt.close()
    logger.info(f"✓ Confusion matrix saved ➞ {cm_path}")

    # ─── MLflow Logging ───────────────────────────────────────────────────────
    if log_to_mlflow:
        try:
            if override_run or mlflow.active_run() is None:
                mlflow.start_run()

            mlflow.log_metrics({
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            })

            mlflow.log_artifact(json_path)
            mlflow.log_artifact(cm_path)
            logger.info("✓ Metrics & artifacts logged to MLflow")

        except Exception as e:
            logger.warning(f"[!] MLflow logging failed: {e}")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

