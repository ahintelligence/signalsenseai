from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import lightgbm as lgb

def train_stacked_model(X_train, y_train):
    base_learners = [
        ("xgb", XGBClassifier(use_label_encoder=False, eval_metric="logloss")),
        ("rf", RandomForestClassifier()),
        ("lgb", lgb.LGBMClassifier())
    ]
    final_model = LogisticRegression()
    model = StackingClassifier(estimators=base_learners, final_estimator=final_model)
    model.fit(X_train, y_train)
    return model
