import os
import json
import csv
import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def save_metrics(report, ticker, METRICS_DIR):
    os.makedirs(METRICS_DIR, exist_ok=True)

    report_path = os.path.join(METRICS_DIR, f"{ticker}_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
    logger.info(f"Saved classification report → {report_path}")
    return report_path

def save_confusion_matrix(cm, ticker, METRICS_DIR):
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Hold/Sell", "Buy"], yticklabels=["Hold/Sell", "Buy"])
    plt.tight_layout()
    plot_path = os.path.join(METRICS_DIR, f"{ticker}_confusion_matrix.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path

def compare_models(tickers, METRICS_DIR):
    results = {}
    for t in tickers:
        path = os.path.join(METRICS_DIR, f"{t}_report.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            report = json.load(f)
        results[t] = {
            "accuracy": report["accuracy"],
            "precision": report["Buy"]["precision"],
            "recall": report["Buy"]["recall"],
            "f1_score": report["Buy"]["f1-score"],
        }

    with open(os.path.join(METRICS_DIR, "comparison.json"), "w") as f:
        json.dump(results, f, indent=4)

    with open(os.path.join(METRICS_DIR, "comparison.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ticker", "Accuracy", "Precision", "Recall", "F1 Score"])
        for t, m in results.items():
            writer.writerow([t, m["accuracy"], m["precision"], m["recall"], m["f1_score"]])

    try:
        df = pd.DataFrame(results).T
        ax = df.plot(kind="bar", figsize=(10, 6), ylim=(0, 1), rot=0, title="Model Comparison")
        ax.set_ylabel("Score")
        plt.tight_layout()
        plot_path = os.path.join(METRICS_DIR, "comparison_plot.png")
        plt.savefig(plot_path)
        plt.close()
    except Exception as e:
        logger.warning(f"Failed to generate plot: {e}")

    return results
