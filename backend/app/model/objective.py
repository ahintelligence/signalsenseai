from hyperopt import STATUS_OK, hp
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from app.data import get_stock_data
from app.model.features import generate_features

def objective(params):
    df = get_stock_data("AAPL")
    if df is None or df.empty:
        return {'loss': 1.0, 'status': STATUS_OK}

    X, y = generate_features(df)
    if len(X) < 10:
        return {'loss': 1.0, 'status': STATUS_OK}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBClassifier(
        n_estimators=int(params["n_estimators"]),
        max_depth=int(params["max_depth"]),
        learning_rate=params["learning_rate"],
        eval_metric="logloss",
        use_label_encoder=False
    )
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    return {"loss": -acc, "status": STATUS_OK}

search_space = {
    "n_estimators": hp.choice("n_estimators", [100, 200, 300]),
    "max_depth": hp.choice("max_depth", [3, 6, 9]),
    "learning_rate": hp.uniform("learning_rate", 0.01, 0.1),
}
