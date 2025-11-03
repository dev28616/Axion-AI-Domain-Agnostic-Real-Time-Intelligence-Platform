import joblib
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate

def main():
    print("--- Starting Finance Model Training with Cross-Validation ---")
    X = np.array([[10.50, 8], [2500.00, 11], [45.20, 12], [300.75, 13], [5000.00, 18], [12.00, 9], [3100.00, 14], [55.00, 15], [250.00, 10], [4800.00, 20]])
    y = np.array([0, 1, 0, 0, 1, 0, 1, 0, 0, 1])
    model = LogisticRegression()
    cv_results = cross_validate(model, X, y, cv=5, scoring=['accuracy', 'precision', 'recall'])
    model.fit(X, y)
    metrics = {"mean_accuracy": round(cv_results['test_accuracy'].mean(), 3), "mean_precision": round(cv_results['test_precision'].mean(), 3), "mean_recall": round(cv_results['test_recall'].mean(), 3)}
    with open("dsps/finance/models/model_metrics.json", 'w') as f: json.dump(metrics, f, indent=4)
    print(f"Saved model metrics: {metrics}")
    joblib.dump(model, "dsps/finance/models/fraud_model.joblib")
    print("Saved final trained model.")

if __name__ == "__main__":
    main()

