import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA = Path(__file__).parent / "data" / "adult.csv"
CATEGORICAL = ["workclass", "occupation", "marital_status", "race", "sex"]
NUMERIC = ["age", "education_num", "hours_per_week"]
PROTECTED = ["race", "sex"]
HISTORICAL_REJECTION = {"Female": 0.7, "non_white": 0.5}
MODES = {
    "historical": ("Historical model (biased data)", CATEGORICAL + NUMERIC),
    "standard": ("Standard model", CATEGORICAL + NUMERIC),
    "fair": ("Fair model (blind)", [f for f in CATEGORICAL + NUMERIC if f not in PROTECTED]),
}

LABELS = {
    "Married-civ-spouse": "Married",
    "Married-spouse-absent": "Married, spouse away",
    "Married-AF-spouse": "Married, armed forces spouse",
    "Never-married": "Never married",
    "Self-emp-not-inc": "Self employed",
    "Self-emp-inc": "Self employed, company",
    "Federal-gov": "Federal government",
    "Local-gov": "Local government",
    "State-gov": "State government",
    "Without-pay": "Unpaid",
    "Exec-managerial": "Executive or manager",
    "Prof-specialty": "Professional specialist",
    "Tech-support": "Technical support",
    "Adm-clerical": "Admin or clerical",
    "Craft-repair": "Craft or repair",
    "Machine-op-inspct": "Machine operator",
    "Transport-moving": "Transport",
    "Handlers-cleaners": "Handler or cleaner",
    "Farming-fishing": "Farming or fishing",
    "Protective-serv": "Protective services",
    "Priv-house-serv": "Household services",
    "Other-service": "Other services",
    "Asian-Pac-Islander": "Asian or Pacific Islander",
    "Amer-Indian-Eskimo": "American Indian or Eskimo",
    "Assoc-acdm": "Associate degree, academic",
    "Assoc-voc": "Associate degree, vocational",
    "Prof-school": "Professional school",
    "Some-college": "Some college",
    "HS-grad": "High school graduate",
}


def label(value):
    return LABELS.get(value, str(value).replace("-", " "))


# Dataset loading: cleaned UCI Adult census records built by prepare_data.py, label 1 means the person earned over 50K (used as "strong candidate")
@st.cache_data
def load_data():
    df = pd.read_csv(DATA)
    df["label"] = (df["income"] == ">50K").astype(int)
    return df


def options(column):
    return sorted(load_data()[column].unique())


def education_levels():
    pairs = load_data()[["education", "education_num"]].drop_duplicates().sort_values("education_num")
    return dict(zip(pairs["education"], pairs["education_num"]))


# Historical hiring data: a simulated biased recruiter rejected most strong women and non white candidates
def historical_labels(df, seed=42):
    keep = np.where(df["sex"] == "Female", 1 - HISTORICAL_REJECTION["Female"], 1.0)
    keep = keep * np.where(df["race"] != "White", 1 - HISTORICAL_REJECTION["non_white"], 1.0)
    rejected = np.random.default_rng(seed).random(len(df)) >= keep
    return df["label"].where(~rejected, 0)


def gender_weight(model):
    names = list(model[0].get_feature_names_out())
    coef = model[-1].coef_[0]
    if "cat__sex_Male" not in names:
        return 0.0
    return float(coef[names.index("cat__sex_Male")] - coef[names.index("cat__sex_Female")])


# Model training: historical learns from biased labels, standard from true labels, fair without gender and race
@st.cache_resource
def train():
    df = load_data()
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
    models, report = {}, {}
    for mode, (_, features) in MODES.items():
        cat = [c for c in CATEGORICAL if c in features]
        num = [c for c in NUMERIC if c in features]
        labels = historical_labels(train_df) if mode == "historical" else train_df["label"]
        prep = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cat), ("num", StandardScaler(), num)])
        model = make_pipeline(prep, LogisticRegression(max_iter=1000)).fit(train_df[features], labels)
        pred = model.predict(test_df[features])
        women = (test_df["sex"] == "Female").to_numpy()
        models[mode] = model
        report[mode] = {
            "accuracy": accuracy_score(test_df["label"], pred),
            "recall": recall_score(test_df["label"], pred),
            "women_recall": recall_score(test_df["label"][women], pred[women]),
            "gender_weight": gender_weight(model),
        }
    return models, report, test_df


def score(df, mode):
    return train()[0][mode].predict_proba(df[MODES[mode][1]])[:, 1]


# Shared memory: applications and admin settings live in server memory, shared by every visitor until restart
@st.cache_resource
def applications():
    return []


@st.cache_resource
def settings():
    return {"mode": "historical", "threshold": 0.5}


def add_application(data, allow_duplicate=False):
    apps = applications()
    if not allow_duplicate:
        for record in apps:
            if all(record.get(k) == v for k, v in data.items()):
                return record, False
    record = {"id": 1001 + len(apps), "time": datetime.now().strftime("%d %b %H:%M"), **data}
    apps.append(record)
    return record, True


def add_samples(n=20):
    sample = train()[2].sample(n)
    for row in sample.to_dict("records"):
        add_application({"name": "Sample applicant", **{k: row[k] for k in CATEGORICAL + NUMERIC}}, allow_duplicate=True)


def clear_applications():
    applications().clear()


def decide(record):
    s = settings()
    value = float(score(pd.DataFrame([record]), s["mode"])[0])
    return value, value >= s["threshold"]


# Bias audit: scores every application, then re-scores it with only the gender flipped
def audit():
    apps = applications()
    if not apps:
        return pd.DataFrame()
    s = settings()
    df = pd.DataFrame(apps)
    df["score"] = score(df, s["mode"])
    df["shortlisted"] = df["score"] >= s["threshold"]
    flipped = df.assign(sex=df["sex"].map({"Male": "Female", "Female": "Male"}))
    df["flip_score"] = score(flipped, s["mode"])
    df["changed"] = (df["flip_score"] >= s["threshold"]) != df["shortlisted"]
    return df


def rates(df, column):
    return df.groupby(column)["shortlisted"].mean()


def impact_ratio(group_rates):
    if len(group_rates) < 2 or group_rates.max() == 0:
        return None
    return group_rates.min() / group_rates.max()


def historical_rates(column):
    return load_data().groupby(column)["label"].mean()


def admin_password():
    return os.environ.get("ADMIN_PASSWORD", "admin123")
