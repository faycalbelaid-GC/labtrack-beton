"""
Page — Analyses statistiques avancées
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data_manager import get_df, TYPES_ESSAI

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


def render():
    df = get_df()

    if df.empty:
        st.info("Aucune donnée disponible.")
        return

    st.markdown('<span class="section-tag">// Paramètres d\'analyse</span>', unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3)
    with a1:
        sel_type = st.selectbox("Type d'essai", TYPES_ESSAI, key="stat_type")
    with a2:
        forms_dispo = sorted(df[df["type_essai"] == sel_type]["formulation"].unique())
        sel_forms = st.multiselect("Formulations à comparer", forms_dispo, default=forms_dispo[:3], key="stat_form")
    with a3:
        age_ref = st.selectbox("Âge de référence (j)", sorted(df["age_jours"].unique()), index=4, key="stat_age")

    df_sel = df[
        (df["type_essai"] == sel_type) &
        (df["formulation"].isin(sel_forms)) &
        (df["age_jours"] == age_ref)
    ].dropna(subset=["resistance_MPa"])

    if df_sel.empty:
        st.warning("Pas de données pour cette combinaison.")
        return

    # ═══════════════════════════════════════════════════════════════════════════
    # Tableau statistiques descriptives
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<span class="section-tag" style="margin-top:8px">// Statistiques descriptives</span>', unsafe_allow_html=True)

    stats_rows = []
    for form in sel_forms:
        vals = df_sel[df_sel["formulation"] == form]["resistance_MPa"].dropna()
        if len(vals) == 0:
            continue
        n = len(vals)
        moy = vals.mean()
        med = vals.median()
        s = vals.std()
        cov = s / moy * 100 if moy > 0 else 0
        # fc,k = fck caractéristique (EN 206 : fcm - 1.65*s)
        fck_est = moy - 1.65 * s
        ci95_low = moy - 1.96 * s / np.sqrt(n)
        ci95_high = moy + 1.96 * s / np.sqrt(n)
        # Test normalité Shapiro-Wilk
        if n >= 3:
            _, p_shapiro = stats.shapiro(vals)
            normalite = "✓ Normale" if p_shapiro > 0.05 else "⚠ Non-normale"
        else:
            normalite = "—"

        stats_rows.append({
            "Formulation": form[:30],
            "n": n,
            "Moyenne (MPa)": round(moy, 2),
            "Médiane (MPa)": round(med, 2),
            "Écart-type": round(s, 2),
            "CoV (%)": round(cov, 1),
            "fck estimé (MPa)": round(fck_est, 1),
            "IC 95% bas": round(ci95_low, 2),
            "IC 95% haut": round(ci95_high, 2),
            "Normalité (Shapiro)": normalite,
        })

    if stats_rows:
        df_stats = pd.DataFrame(stats_rows)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Graphiques stats
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<span class="section-tag">// Visualisations statistiques</span>', unsafe_allow_html=True)
    g1, g2 = st.columns(2, gap="medium")

COLORS_STAT = ["#4ade80", "#22d3ee", "#fb923c", "#a78bfa", "#f472b6", "#facc15"]
COLORS_STAT_RGBA = [
    "rgba(74,222,128,0.08)",  "rgba(34,211,238,0.08)",
    "rgba(251,146,60,0.08)",  "rgba(167,139,250,0.08)",
    "rgba(244,114,182,0.08)", "rgba(250,204,21,0.08)",
]

    with g1:
        # Courbe de densité (KDE)
        fig_kde = go.Figure()
        for i, form in enumerate(sel_forms):
            vals = df_sel[df_sel["formulation"] == form]["resistance_MPa"].dropna()
            if len(vals) < 3:
                continue
            kde = stats.gaussian_kde(vals, bw_method=0.4)
            x_range = np.linspace(vals.min() - 5, vals.max() + 5, 200)
            color = COLORS_STAT[i % len(COLORS_STAT)]
            fill_rgba = COLORS_STAT_RGBA[i % len(COLORS_STAT_RGBA)]
            fig_kde.add_trace(go.Scatter(
                x=x_range, y=kde(x_range),
                name=form[:22], mode="lines",
                line=dict(color=color, width=2.5),
                fill="tozeroy", fillcolor=fill_rgba,
            ))
            # Ligne moyenne
            fig_kde.add_vline(
                x=vals.mean(), line_dash="dash",
                line_color=color, line_width=1, opacity=0.7,
            )

        fig_kde.update_layout(
            title="Densité de probabilité (KDE)",
            xaxis_title="Résistance (MPa)",
            yaxis_title="Densité",
            **PLOTLY_LAYOUT, height=350,
        )
        st.plotly_chart(fig_kde, use_container_width=True)

    with g2:
        # Q-Q plot normalité
        form_qq = sel_forms[0] if sel_forms else None
        if form_qq:
            vals_qq = df_sel[df_sel["formulation"] == form_qq]["resistance_MPa"].dropna().values
            if len(vals_qq) >= 3:
                (osm, osr), (slope, intercept, r) = stats.probplot(vals_qq, dist="norm")
                fig_qq = go.Figure()
                fig_qq.add_trace(go.Scatter(
                    x=osm, y=osr, mode="markers",
                    marker=dict(color="#4ade80", size=9,
                                line=dict(color="#060a0f", width=1.5)),
                    name="Données observées",
                ))
                # Droite théorique
                x_line = np.array([min(osm), max(osm)])
                fig_qq.add_trace(go.Scatter(
                    x=x_line, y=slope * x_line + intercept,
                    mode="lines", line=dict(color="#fb923c", dash="dash", width=2),
                    name="Droite normale théorique",
                ))
                fig_qq.update_layout(
                    title=f"Q-Q Plot normalité — {form_qq[:22]}",
                    xaxis_title="Quantiles théoriques",
                    yaxis_title="Quantiles observés",
                    **PLOTLY_LAYOUT, height=350,
                )
                st.plotly_chart(fig_qq, use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Test ANOVA si plusieurs formulations
    # ═══════════════════════════════════════════════════════════════════════════
    if len(sel_forms) >= 2:
        st.markdown('<span class="section-tag">// Test ANOVA — Comparaison des groupes</span>', unsafe_allow_html=True)

        groupes = [df_sel[df_sel["formulation"] == f]["resistance_MPa"].dropna().values
                   for f in sel_forms if len(df_sel[df_sel["formulation"] == f]) >= 2]

        if len(groupes) >= 2:
            F_stat, p_value = stats.f_oneway(*groupes)
            conclusion = (
                "✅ Les formulations ont des résistances **significativement différentes** (p < 0.05)"
                if p_value < 0.05 else
                "⚠️ Pas de différence significative entre les formulations (p ≥ 0.05)"
            )

            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                st.markdown(f"""<div class="stat-card">
                    <div class="stat-label">Statistique F</div>
                    <div class="stat-value">{F_stat:.2f}</div>
                </div>""", unsafe_allow_html=True)
            with ac2:
                st.markdown(f"""<div class="stat-card">
                    <div class="stat-label">p-value</div>
                    <div class="stat-value" style="font-size:1.6rem">{p_value:.4f}</div>
                </div>""", unsafe_allow_html=True)
            with ac3:
                sig = "< 0.05 ✓" if p_value < 0.05 else "≥ 0.05 ⚠"
                st.markdown(f"""<div class="stat-card">
                    <div class="stat-label">Seuil α = 0.05</div>
                    <div class="stat-value" style="font-size:1.4rem">{sig}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"<br>**Conclusion :** {conclusion}", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Tableau résumé par âge
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<span class="section-tag" style="margin-top:16px">// Évolution fc par âge (tous âges)</span>', unsafe_allow_html=True)

    df_all_ages = df[
        (df["type_essai"] == sel_type) &
        (df["formulation"].isin(sel_forms))
    ].dropna(subset=["resistance_MPa"])

    if not df_all_ages.empty:
        pivot = df_all_ages.groupby(["formulation", "age_jours"])["resistance_MPa"].agg(
            ["mean", "std", "count"]
        ).round(2).reset_index()
        pivot.columns = ["Formulation", "Âge (j)", "fc moy. (MPa)", "Écart-type", "n"]
        st.dataframe(pivot, use_container_width=True, hide_index=True)
