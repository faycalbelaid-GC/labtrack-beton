"""
Page — Tableaux de bord visuels (Plotly)
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data_manager import get_df, TYPES_ESSAI

# ── Thème Plotly dark lab ──────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0a1208",
    plot_bgcolor="#060a0f",
    font=dict(family="Space Mono, monospace", color="#4a6a4a", size=11),
    title_font=dict(family="Space Mono, monospace", color="#4ade80", size=13),
    xaxis=dict(gridcolor="#1a3a1a", linecolor="#1a3a1a", tickfont=dict(color="#4a6a4a")),
    yaxis=dict(gridcolor="#1a3a1a", linecolor="#1a3a1a", tickfont=dict(color="#4a6a4a")),
    legend=dict(bgcolor="#0a1208", bordercolor="#1a3a1a", borderwidth=1,
                font=dict(color="#94a3b8")),
    margin=dict(l=40, r=20, t=50, b=40),
)

COLORS = {
    "Compression": "#4ade80",
    "Flexion":     "#22d3ee",
    "Traction":    "#fb923c",
}

FORM_COLORS = [
    "#4ade80", "#22d3ee", "#fb923c", "#a78bfa",
    "#f472b6", "#facc15", "#34d399", "#60a5fa",
]

FORM_COLORS_RGBA = [
    "rgba(74,222,128,0.08)",  "rgba(34,211,238,0.08)",
    "rgba(251,146,60,0.08)",  "rgba(167,139,250,0.08)",
    "rgba(244,114,182,0.08)", "rgba(250,204,21,0.08)",
    "rgba(52,211,153,0.08)",  "rgba(96,165,250,0.08)",
]


def render():
    df = get_df()

    if df.empty:
        st.info("Aucune donnée disponible. Ajoutez des essais dans l'onglet Saisie.")
        return

    # ── Filtres sidebar-like ───────────────────────────────────────────────────
    st.markdown('<span class="section-tag">// Filtres</span>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_type = st.multiselect("Type d'essai", TYPES_ESSAI, default=TYPES_ESSAI, key="db_type")
    with f2:
        all_forms = sorted(df["formulation"].unique().tolist())
        sel_form = st.multiselect("Formulation", all_forms, default=all_forms, key="db_form")
    with f3:
        all_ages = sorted(df["age_jours"].unique().tolist())
        sel_age = st.multiselect("Âge (jours)", all_ages, default=all_ages, key="db_age")

    df_f = df[
        df["type_essai"].isin(sel_type) &
        df["formulation"].isin(sel_form) &
        df["age_jours"].isin(sel_age)
    ]

    if df_f.empty:
        st.warning("Aucun essai correspondant aux filtres sélectionnés.")
        return

    # ═══════════════════════════════════════════════════════════════════════════
    # Ligne 1 — KPIs
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<span class="section-tag" style="margin-top:8px">// Indicateurs globaux</span>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, "Essais total", len(df_f), ""),
        (k2, "fc moy. (MPa)", f"{df_f['resistance_MPa'].mean():.1f}", ""),
        (k3, "fc max (MPa)",  f"{df_f['resistance_MPa'].max():.1f}", ""),
        (k4, "CoV (%)",       f"{df_f['resistance_MPa'].std()/df_f['resistance_MPa'].mean()*100:.1f}", ""),
        (k5, "Conformité",    f"{(df_f['conforme']=='✓ Oui').sum()/len(df_f)*100:.0f}%", ""),
    ]
    for col, label, val, sub in kpis:
        with col:
            st.markdown(f"""<div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Ligne 2 — Résistance vs Âge + Distribution
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<span class="section-tag">// Résistance & distribution</span>', unsafe_allow_html=True)
    ch1, ch2 = st.columns([1.6, 1], gap="medium")

    with ch1:
        # Courbe résistance vs âge par formulation
        df_comp = df_f[df_f["type_essai"] == "Compression"]
        if not df_comp.empty:
            fig_age = go.Figure()
            for i, form in enumerate(df_comp["formulation"].unique()):
                df_form = df_comp[df_comp["formulation"] == form]
                agg = df_form.groupby("age_jours")["resistance_MPa"].agg(["mean", "std", "count"]).reset_index()
                color = FORM_COLORS[i % len(FORM_COLORS)]

                # Bande d'incertitude (±std)
                fill_color = FORM_COLORS_RGBA[i % len(FORM_COLORS_RGBA)]
                fig_age.add_trace(go.Scatter(
                    x=list(agg["age_jours"]) + list(agg["age_jours"])[::-1],
                    y=list(agg["mean"] + agg["std"].fillna(0)) + list((agg["mean"] - agg["std"].fillna(0)))[::-1],
                    fill="toself", fillcolor=fill_color,
                    line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False, hoverinfo="skip",
                ))
                # Courbe moyenne
                fig_age.add_trace(go.Scatter(
                    x=agg["age_jours"], y=agg["mean"],
                    mode="lines+markers",
                    name=form[:25],
                    line=dict(color=color, width=2.5),
                    marker=dict(size=8, symbol="circle", color=color,
                                line=dict(color="#060a0f", width=2)),
                    hovertemplate=f"<b>{form[:20]}</b><br>Âge: %{{x}}j<br>fc moy: %{{y:.2f}} MPa<extra></extra>",
                ))

            fig_age.update_layout(
                title="Évolution de la résistance en compression vs Âge",
                xaxis_title="Âge (jours)",
                yaxis_title="fc (MPa)",
                **PLOTLY_LAYOUT,
                height=340,
            )
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("Pas d'essais de compression dans la sélection.")

    with ch2:
        # Histogramme distribution fc
        fig_hist = go.Figure()
        for t in df_f["type_essai"].unique():
            d = df_f[df_f["type_essai"] == t]["resistance_MPa"].dropna()
            if not d.empty:
                fig_hist.add_trace(go.Histogram(
                    x=d, name=t, nbinsx=15,
                    marker_color=COLORS.get(t, "#94a3b8"),
                    opacity=0.75,
                ))
        fig_hist.update_layout(
            title="Distribution des résistances",
            xaxis_title="Résistance (MPa)",
            yaxis_title="Fréquence",
            barmode="overlay",
            **PLOTLY_LAYOUT,
            height=340,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Ligne 3 — Box plot + Scatter conformité
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<span class="section-tag">// Comparaison formulations</span>', unsafe_allow_html=True)
    ch3, ch4 = st.columns(2, gap="medium")

    with ch3:
        # Box plot par formulation
        fig_box = go.Figure()
        for i, form in enumerate(sorted(df_f["formulation"].unique())):
            vals = df_f[df_f["formulation"] == form]["resistance_MPa"].dropna()
            color = FORM_COLORS[i % len(FORM_COLORS)]
            fig_box.add_trace(go.Box(
                y=vals, name=form[:20],
                marker_color=color,
                line_color=color,
                fillcolor="rgba(10,18,8,0.5)",
                boxpoints="all",
                jitter=0.3,
                pointpos=0,
                marker=dict(size=5, opacity=0.6),
            ))
        fig_box.update_layout(
            title="Box Plot — fc par formulation",
            yaxis_title="Résistance (MPa)",
            showlegend=False,
            **PLOTLY_LAYOUT,
            height=360,
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with ch4:
        # Scatter : charge vs résistance, coloré par âge
        fig_sc = px.scatter(
            df_f.dropna(subset=["charge_max_kN", "resistance_MPa"]),
            x="charge_max_kN", y="resistance_MPa",
            color="age_jours",
            symbol="type_essai",
            hover_data=["reference", "formulation", "operateur"],
            color_continuous_scale=[[0, "#1a3a1a"], [0.5, "#4ade80"], [1, "#22d3ee"]],
            labels={"charge_max_kN": "Charge max (kN)", "resistance_MPa": "fc (MPa)",
                    "age_jours": "Âge (j)"},
        )
        fig_sc.update_traces(marker=dict(size=8, line=dict(color="#060a0f", width=1)))
        fig_sc.update_layout(
            title="Charge max vs Résistance (par âge)",
            **PLOTLY_LAYOUT,
            height=360,
            coloraxis_colorbar=dict(
                title="Âge (j)",
                tickfont=dict(color="#4a6a4a"),
                titlefont=dict(color="#4a6a4a"),
            )
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Ligne 4 — Timeline + Camembert conformité
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<span class="section-tag">// Chronologie & conformité</span>', unsafe_allow_html=True)
    ch5, ch6 = st.columns([1.6, 1], gap="medium")

    with ch5:
        # Timeline des essais
        df_timeline = df_f.copy()
        df_timeline["date"] = pd.to_datetime(df_timeline["date"])
        df_agg = df_timeline.groupby(["date", "type_essai"]).size().reset_index(name="n")

        fig_tl = go.Figure()
        for t in TYPES_ESSAI:
            d = df_agg[df_agg["type_essai"] == t]
            if not d.empty:
                fig_tl.add_trace(go.Bar(
                    x=d["date"], y=d["n"],
                    name=t, marker_color=COLORS.get(t, "#94a3b8"),
                ))
        fig_tl.update_layout(
            title="Chronologie des essais",
            xaxis_title="Date",
            yaxis_title="Nombre d'essais",
            barmode="stack",
            **PLOTLY_LAYOUT,
            height=300,
        )
        st.plotly_chart(fig_tl, use_container_width=True)

    with ch6:
        # Donut conformité
        conf_counts = df_f["conforme"].value_counts()
        fig_donut = go.Figure(go.Pie(
            labels=conf_counts.index.tolist(),
            values=conf_counts.values.tolist(),
            hole=0.6,
            marker=dict(colors=["#4ade80", "#ef4444", "#f59e0b"],
                        line=dict(color="#060a0f", width=2)),
            textfont=dict(family="Space Mono", color="#e2e8f0"),
        ))
        fig_donut.update_layout(
            title="Taux de conformité",
            **PLOTLY_LAYOUT,
            height=300,
            annotations=[dict(text=f"{(df_f['conforme']=='✓ Oui').sum()/len(df_f)*100:.0f}%",
                              font=dict(size=22, color="#4ade80", family="Space Mono"),
                              showarrow=False)],
        )
        st.plotly_chart(fig_donut, use_container_width=True)
