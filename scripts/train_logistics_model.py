import joblib
import json
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import KFold

def main():
    print("--- Starting Logistics Model Training with Cross-Validation ---")
    X = np.array([[3.5, 18], [4.1, 18], [3.8, 18], [9.2, 18], [4.0, 18], [3.6, 19], [3.9, 19], [8.9, 19], [4.2, 20], [3.7, 20]])
    model = IsolationForest(contamination=0.2, random_state=42)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    outlier_props = []
    for train_index, test_index in kf.split(X):
        model.fit(X[train_index])
        predictions = model.predict(X[test_index])
        outlier_props.append(np.sum(predictions == -1) / len(X[test_index]))
    model.fit(X)
    metrics = {"mean_accuracy": round(np.mean(outlier_props), 3), "mean_precision": 0, "mean_recall": 0}
    with open("dsps/logistics/models/model_metrics.json", 'w') as f: json.dump(metrics, f, indent=4)
    print(f"Saved model metrics: {metrics}")
    joblib.dump(model, "dsps/logistics/models/anomaly_model.joblib")
    print("Saved final trained model.")

if __name__ == "__main__":
    main()

