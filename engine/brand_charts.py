# fit_engine.py

from engine.brand_charts import brand_charts

WEIGHTS = {
    "shoulder": 0.40,
    "sleeve": 0.25,
    "bust": 0.15,
    "waist": 0.10,
    "hip": 0.10
}

def score_measure(user_value, brand_range):
    """
    Returns a score between 0 and 1 based on closeness to brand range.
    """
    low, high = brand_range
    mid = (low + high) / 2

    # If user is exactly at mid → perfect score
    diff = abs(user_value - mid)

    # Max acceptable difference = half the range
    max_diff = (high - low) / 2

    if diff >= max_diff:
        return 0.0

    return 1 - (diff / max_diff)


def compute_fit_score(store, size_label, user_measurements):
    """
    Computes a 0–10 fit score for a given store + size.
    """

    if store not in brand_charts:
        return 5.0, "No brand chart available"

    if size_label not in brand_charts[store]:
        return 5.0, "No size chart for this size"

    chart = brand_charts[store][size_label]

    total = 0
    weight_sum = 0
    explanation = []

    for key, weight in WEIGHTS.items():
        if key in chart and user_measurements.get(key) is not None:
            score = score_measure(user_measurements[key], chart[key])
            total += score * weight
            weight_sum += weight

            explanation.append(f"{key}: {round(score * 10, 1)}/10")

    if weight_sum == 0:
        return 5.0, "Insufficient data"

    final_score = (total / weight_sum) * 10
    return round(final_score, 1), "; ".join(explanation)
