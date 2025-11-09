import os
import json
from xgboost import XGBClassifier

# MODEL_FILENAME = os.path.join(os.path.dirname(__file__), "xgboost_model_with_no_feature_filtration.json")
MODEL_FILENAME = os.path.join(os.path.dirname(__file__), "xgboostv1.json")
FEATURES_FILENAME = os.path.join(os.path.dirname(__file__), "features.json")

META_KEYS = {"url", "domain", "path", "query", "fragment"}

def run():
    model = XGBClassifier()
    model.load_model(MODEL_FILENAME)

    with open(FEATURES_FILENAME, "r", encoding="utf-8") as f:
        data = json.load(f)

    feature_obj = data["features"][0]

    numeric_items = {
        k: v for k, v in feature_obj.items()
        if k not in META_KEYS and isinstance(v, (int, float))
    }

    feature_names = numeric_items.keys()
    vector = [numeric_items[key] for key in feature_names]

    prediction = int(model.predict([vector])[0])
    malicious_prob = float(model.predict_proba([vector])[0][1])

    print("Model Prediction: ", prediction)
    if prediction == 1:
        return 30
    return -30

if __name__ == "__main__":
    print(run())
