import joblib
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate

def main():
    print("--- Starting Healthcare Model Training with Cross-Validation ---")
    X = np.array([[150.00, 9], [750.00, 9], [12500.00, 9], [200.00, 9], [120.00, 10], [950.00, 11], [15000.00, 14], [180.00, 16]])
    y = np.array([1, 1, 0, 1, 1, 1, 0, 1])
    model = LogisticRegression()
    cv_results = cross_validate(model, X, y, cv=3, scoring=['accuracy', 'precision', 'recall'])
    model.fit(X, y)
    metrics = {"mean_accuracy": round(cv_results['test_accuracy'].mean(), 3), "mean_precision": round(cv_results['test_precision'].mean(), 3), "mean_recall": round(cv_results['test_recall'].mean(), 3)}
    with open("dsps/healthcare/models/model_metrics.json", 'w') as f: json.dump(metrics, f, indent=4)
    print(f"Saved model metrics: {metrics}")
    joblib.dump(model, "dsps/healthcare/models/claim_approval_model.joblib")
    print("Saved final trained model.")

if __name__ == "__main__":
    main()

