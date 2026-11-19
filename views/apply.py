import streamlit as st

import engine as en
import ui

ui.page_head(
    "Careers . Open role",
    "Job Application",
    "Fill in your details. Our AI screening model reviews your profile and decides if you move to the interview round.",
)

education = en.education_levels()

# Application form
with st.container(key="card-apply"):
    with st.form("apply", border=False, enter_to_submit=False):
        name = st.text_input("Full name", max_chars=60, placeholder="Your name")
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", min_value=17, max_value=90, value=28)
        sex = c2.selectbox("Gender", en.options("sex"))
        race = c1.selectbox("Race", en.options("race"), format_func=en.label, index=en.options("race").index("White"))
        marital = c2.selectbox("Marital status", en.options("marital_status"), format_func=en.label)
        degree = c1.selectbox("Highest education", list(education), format_func=en.label, index=list(education).index("Bachelors"))
        occupation = c2.selectbox("Occupation", en.options("occupation"), format_func=en.label)
        workclass = c1.selectbox("Employer type", en.options("workclass"), format_func=en.label, index=en.options("workclass").index("Private"))
        hours = c2.slider("Hours per week", 1, 99, 40)
        submitted = st.form_submit_button("Submit application", icon=":material/send:", type="primary", width="stretch")

# Decision result
if submitted:
    if not name.strip():
        st.warning("Please enter your name.", icon=":material/error:")
    else:
        record, is_new = en.add_application({
            "name": name.strip(), "age": age, "sex": sex, "race": race, "marital_status": marital,
            "education_num": education[degree], "occupation": occupation, "workclass": workclass, "hours_per_week": hours,
        })
        if not is_new:
            st.info(f"You already submitted this application as reference #{record['id']}. Showing your existing result.", icon=":material/info:")
        value, ok = en.decide(record)
        state, mark, title = ("pass", "check", "Shortlisted for interview") if ok else ("fail", "cross", "Not shortlisted")
        ui.html(f"""
        <div class="result {state}">
          {ui.icon(mark, 40, 1.4)}
          <div class="result-body">
            <span class="eyebrow">Reference #{record['id']}</span>
            <h3>{title}</h3>
            <div class="bar"><i style="width:{value:.0%}"></i></div>
            <small>AI match score {value:.0%}. Shortlist cut off {en.settings()['threshold']:.0%}.</small>
          </div>
        </div>
        """)

ui.limitations()
