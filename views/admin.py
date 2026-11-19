import streamlit as st

import engine as en
import ui

ui.page_head("Restricted", "Admin Console", "Review every application and check whether the AI treats groups fairly.")

# Login gate
if not st.session_state.get("admin"):
    with st.container(key="card-login"):
        with st.form("login", border=False):
            password = st.text_input("Admin password", type="password")
            if st.form_submit_button("Enter console", icon=":material/lock_open:", type="primary", width="stretch"):
                if password == en.admin_password():
                    st.session_state.admin = True
                    st.rerun()
                st.error("Wrong password.", icon=":material/lock:")
    st.stop()

settings = en.settings()
models, report, test = en.train()


def sync(key):
    if st.session_state[key] is not None:
        settings[key] = st.session_state[key]


# Model controls, shared with the apply page
for key in ("mode", "threshold"):
    st.session_state.setdefault(key, settings[key])
with st.container(key="card-controls"):
    c1, c2, c3 = st.columns([1.2, 1.4, 1.4], vertical_alignment="bottom")
    c1.segmented_control("Screening model", list(en.MODES), key="mode", format_func=lambda m: en.MODES[m][0], on_change=sync, args=("mode",))
    c2.slider("Shortlist cut off", 0.1, 0.9, step=0.05, key="threshold", on_change=sync, args=("threshold",))
    with c3, st.container(horizontal=True):
        st.button("Add 20 samples", icon=":material/group_add:", on_click=en.add_samples)
        st.button("Clear", icon=":material/delete:", on_click=en.clear_applications)

df = en.audit()
if df.empty:
    st.info("No applications yet. Apply from the Apply page or add sample applicants.", icon=":material/inbox:")
    ui.limitations()
    st.stop()

# Headline numbers
gender = en.rates(df, "sex")
ratio = en.impact_ratio(gender)
fair = ratio is not None and ratio >= 0.8
counts = df["sex"].value_counts()
enough = len(counts) == 2 and counts.min() >= 5
k1, k2, k3, k4 = st.columns(4)
with k1:
    ui.tile("Applications", len(df), f"{int(df['shortlisted'].sum())} shortlisted")
with k2:
    ui.tile("Men shortlisted", ui.pct(gender.get("Male")), f"{int((df['sex'] == 'Male').sum())} applied", "accent")
with k3:
    ui.tile("Women shortlisted", ui.pct(gender.get("Female")), f"{int((df['sex'] == 'Female').sum())} applied")
with k4:
    if not enough:
        ui.tile("Fairness ratio", ui.pct(ratio), "Need 5 or more of each gender")
    else:
        ui.tile("Fairness ratio", ui.pct(ratio), "Passes 80% rule" if fair else "Fails 80% rule", "good" if fair else "warn")

# Selection rate charts and gender flip test
left, right = st.columns([1.6, 1])
with left, st.container(key="card-chart"):
    by_gender, by_race = st.tabs(["By gender", "By race"])
    by_gender.altair_chart(ui.rate_chart(gender, "Shortlisted"), theme=None, width="stretch")
    by_race.altair_chart(ui.rate_chart(en.rates(df, "race"), "Shortlisted"), theme=None, width="stretch")
    st.caption("Dashed line: 80% of the best group. Bars below it suggest adverse impact.")
with right, st.container(key="card-flip"):
    changed = int(df["changed"].sum())
    ui.html(f"""
    <div class="flip">
      {ui.icon("swap", 28)}
      <span class="eyebrow">Gender flip test</span>
      <strong>{changed} of {len(df)}</strong>
      <p>applicants get a different decision when only their gender is switched and everything else stays the same.</p>
      <p class="hint">{"This is direct gender bias. Try the fair model." if changed else "Gender alone does not change any decision."}</p>
    </div>
    """)

# Applications table
ui.html('<div class="section-title"><span class="eyebrow">Applications</span></div>')
degree = {num: name for name, num in en.education_levels().items()}
table = df.assign(education=df["education_num"].map(degree), score=(df["score"] * 100).round(1))[
    ["id", "time", "name", "sex", "race", "age", "marital_status", "education", "occupation", "workclass", "hours_per_week", "score", "shortlisted", "changed"]
]
for column in ("race", "marital_status", "education", "occupation", "workclass"):
    table[column] = table[column].map(en.label)
st.dataframe(
    table.iloc[::-1],
    hide_index=True,
    width="stretch",
    column_config={
        "id": "Ref",
        "time": "Time",
        "name": "Name",
        "sex": "Gender",
        "race": "Race",
        "age": "Age",
        "marital_status": "Marital status",
        "education": "Education",
        "occupation": "Occupation",
        "workclass": "Employer",
        "hours_per_week": "Hours",
        "score": st.column_config.ProgressColumn("AI score", format="%.1f%%", min_value=0, max_value=100),
        "shortlisted": st.column_config.CheckboxColumn("Shortlisted"),
        "changed": st.column_config.CheckboxColumn("Flips with gender"),
    },
)

# Model report
with st.expander("Model report", icon=":material/analytics:"):
    st.dataframe(
        [
            {
                "Model": en.MODES[mode][0],
                "Accuracy": round(r["accuracy"] * 100, 1),
                "Recall": round(r["recall"] * 100, 1),
                "Recall for women": round(r["women_recall"] * 100, 1),
                "Gender weight": round(r["gender_weight"], 2),
            }
            for mode, r in report.items()
        ],
        hide_index=True,
        width="stretch",
        column_config={k: st.column_config.NumberColumn(format="%.1f%%") for k in ("Accuracy", "Recall", "Recall for women")},
    )
    st.caption(
        f"Tested on {len(test):,} real records. Gender weight is how much being male raises the score inside the model; 0 means gender is ignored. "
        f"The historical model was trained on labels where {en.HISTORICAL_REJECTION['Female']:.0%} of strong women and "
        f"{en.HISTORICAL_REJECTION['non_white']:.0%} of strong non white candidates were rejected, copying past hiring discrimination."
    )
    st.caption(f"Model: logistic regression with one hot encoding, scikit-learn. Data: UCI Adult census dataset, {len(en.load_data()):,} rows.")

ui.limitations(["The admin console is protected by a simple password for the demo only."])
if st.button("Log out", icon=":material/logout:"):
    st.session_state.admin = False
    st.rerun()
