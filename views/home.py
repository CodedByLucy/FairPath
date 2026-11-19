import streamlit as st

import engine as en
import ui

data = en.load_data()
history = en.historical_rates("sex")

# Hero card
with st.container(key="card-hero"):
    ui.html(
        f"""
        <div class="hero">
          <span class="eyebrow">Group 1 . Bias in AI Systems</span>
          <div class="hero-row">
            <h1>Fair<br>-Path</h1>
            <p>An AI that screens job applicants, and a console that shows when it is being unfair.
            Trained on {len(data):,} real census records.</p>
          </div>
        </div>
        """
    )
    with st.container(key="hero-foot", horizontal=True, vertical_alignment="center"):
        ui.html(f'<div class="hero-mark">{ui.icon("asterisk", 64, 2.6)}</div>')
        ui.html(f'<div class="hero-arrow">{ui.icon("arrow", 40, 1.2)}</div>')
        with st.container(key="explore", width="content"):
            st.page_link("views/apply.py", label="Apply", icon=":material/north_east:")

# The problem in numbers
ui.html('<div class="section-title"><span class="eyebrow">What the data says</span></div>')
c1, c2, c3 = st.columns(3)
with c1:
    ui.tile("Men marked strong candidates", ui.pct(history["Male"]), "in the training data", "accent")
with c2:
    ui.tile("Women marked strong candidates", ui.pct(history["Female"]), "in the training data")
with c3:
    ui.tile("Ratio women to men", ui.pct(en.impact_ratio(history)), "the 80% rule needs at least 80%", "warn")

# How it works
ui.html('<div class="section-title"><span class="eyebrow">How it works</span></div>')
steps = [
    ("user", "01  Apply", "A candidate fills one form: age, education, job type, hours, gender and race."),
    ("cpu", "02  AI screens", "A logistic regression model trained on census data gives a match score and a decision."),
    ("chart", "03  Admin audits", "The console compares selection rates, runs a gender flip test and switches to a fair model."),
]
for col, (name, title, text) in zip(st.columns(3), steps):
    with col:
        ui.html(f'<div class="step">{ui.icon(name, 26)}<h4>{title}</h4><p>{text}</p></div>')
