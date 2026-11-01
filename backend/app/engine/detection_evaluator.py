"""Evaluation utilities for binary scam detection experiments.

Ground-truth labels:
    1 = phishing
    0 = legitimate

These metrics measure performance on the supplied labeled dataset,
not real-world certainty for an individual URL.
"""


def evaluate_predictions(
    labels: list[int],
    predictions: list[int],
) -> dict:
    if not labels or len(labels) != len(predictions):
        raise ValueError("Labels and predictions must be nonempty and aligned")

    if any(value not in (0, 1) for value in labels + predictions):
        raise ValueError("Only binary labels 0 and 1 are accepted")

    tp = sum(a == 1 and b == 1 for a, b in zip(labels, predictions))
    tn = sum(a == 0 and b == 0 for a, b in zip(labels, predictions))
    fp = sum(a == 0 and b == 1 for a, b in zip(labels, predictions))
    fn = sum(a == 1 and b == 0 for a, b in zip(labels, predictions))

    def ratio(numerator, denominator):
        return numerator / denominator if denominator else 0.0

    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    specificity = ratio(tn, tn + fp)
    fpr = ratio(fp, fp + tn)
    f1 = ratio(2 * precision * recall, precision + recall)

    return {
        "samples": len(labels),
        "confusion_matrix": {
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
        },
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "false_positive_rate": round(fpr, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(ratio(tp + tn, len(labels)), 4),
    }
