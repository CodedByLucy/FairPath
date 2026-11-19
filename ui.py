from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import engine as en

ICONS = {
    "logo": '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
    "asterisk": '<path d="M12 2v20M3.3 7l17.4 10M3.3 17 20.7 7"/>',
    "arrow": '<path d="M3 12h18M14 5l7 7-7 7"/>',
    "check": '<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/>',
    "cross": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "cpu": '<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M8 17v-6M13 17V7M18 17v-4"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "swap": '<path d="M4 7h14l-3-3M20 17H6l3 3"/>',
}


def icon(name, size=20, stroke=1.6):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
    )


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def load_css():
    html(f"<style>{(Path(__file__).parent / 'style.css').read_text()}</style>")


# Top bar: brand on the left, pill navigation on the right
def nav(pages):
    with st.container(key="nav", horizontal=True, vertical_alignment="center"):
        html(f'<div class="brand">{icon("logo", 22)}<span>FAIRPATH</span></div>')
        with st.container(key="navlinks", horizontal=True, width="content"):
            for page in pages:
                st.page_link(page)


def page_head(eyebrow, title, text):
    html(f'<div class="head"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2><p>{text}</p></div>')


def tile(label, value, note="", tone=""):
    html(f'<div class="tile {tone}"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>')


def pct(value):
    return "N/A" if value is None or pd.isna(value) else f"{value:.0%}"


# Bar chart of selection rate per group, with the 80 percent rule line
def rate_chart(group_rates, title):
    df = group_rates.rename("rate").reset_index().rename(columns={group_rates.index.name: "group"})
    df["group"] = df["group"].map(en.label)
    bars = alt.Chart(df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=48).encode(
        x=alt.X("group:N", title=None, sort="-y", axis=alt.Axis(labelAngle=0, labelLimit=120)),
        y=alt.Y("rate:Q", title=title, axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        color=alt.condition(alt.datum.rate == df["rate"].max(), alt.value("#a78bfa"), alt.value("#3f3f46")),
        tooltip=[alt.Tooltip("group:N", title="Group"), alt.Tooltip("rate:Q", title="Rate", format=".0%")],
    )
    line = alt.Chart(pd.DataFrame({"y": [df["rate"].max() * 0.8]})).mark_rule(strokeDash=[6, 4], color="#f4f4f5").encode(y="y:Q")
    return (
        (bars + line)
        .properties(height=280, background="transparent")
        .configure_view(stroke=None)
        .configure_axis(labelColor="#a1a1aa", titleColor="#a1a1aa", gridColor="#1f1f23", domainColor="#3f3f46", tickColor="#3f3f46", labelFont="Inter", titleFont="Inter")
    )


def limitations(extra=()):
    with st.expander("Limitations and ethics", icon=":material/policy:"):
        points = [
            "The historical model is deliberately trained on biased labels to show how past discrimination is learned. Never use it for real decisions.",
            "All models learn from 1994 US census data, where men earned more. They repeat that history unless we correct it.",
            "Income is used as a stand in for a strong candidate. Real hiring needs skills, interviews and human judgement.",
            "Removing gender and race does not remove bias. Marital status and occupation still act as proxies.",
            "Gender is recorded as only two values, which leaves out non binary people.",
            "Applications are kept only in server memory and are cleared when the app restarts. No data is sent anywhere.",
            *extra,
        ]
        html("<ul class='limits'>" + "".join(f"<li>{p}</li>" for p in points) + "</ul>")
