"""
Page — Saisie des essais laboratoire
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data_manager import (
    ajouter_essai, get_df, supprimer_essai,
    TYPES_ESSAI, FORMULATIONS, AGES, DIMENSIONS
)


def render():
    col_form, col_table = st.columns([1, 1.6], gap="large")

    with col_form:
        st.markdown('<span class="section-tag">// Nouvel essai</span>', unsafe_allow_html=True)

        type_essai = st.selectbox("Type d'essai", TYPES_ESSAI)

        c1, c2 = st.columns(2)
        with c1:
            ref = st.text_input("Référence éprouvette", placeholder="EC-C30-28J-01")
        with c2:
            date_essai = st.date_input("Date d'essai", value=date.today())

        formulation = st.selectbox("Formulation / Mélange", FORMULATIONS)

        c3, c4 = st.columns(2)
        with c3:
            age = st.selectbox("Âge (jours)", AGES, index=4)
        with c4:
            dimension = st.selectbox("Dimension", DIMENSIONS)

        c5, c6 = st.columns(2)
        with c5:
            masse = st.number_input("Masse (g)", min_value=0.0, value=12500.0, step=10.0)
        with c6:
            charge = st.number_input("Charge max (kN)", min_value=0.0, value=530.0, step=1.0)

        resistance = st.number_input("Résistance mesurée (MPa)", min_value=0.0, value=30.0, step=0.1, format="%.2f")

        # Champs selon type d'essai
        module = None
        allongement = None
        if type_essai == "Compression":
            module = st.number_input("Module d'élasticité (GPa)", min_value=0.0, value=30.0, step=0.5, format="%.1f")
        elif type_essai == "Traction":
            allongement = st.number_input("Allongement à rupture (%)", min_value=0.0, value=0.012, step=0.001, format="%.4f")

        operateur = st.text_input("Opérateur", placeholder="Nom de l'opérateur")
        observations = st.text_area("Observations", placeholder="Aspect de la rupture, anomalies...", height=80)

        # Conformité
        conforme = st.radio("Résultat conforme ?", ["✓ Oui", "✗ Non", "⚠ À vérifier"], horizontal=True)

        st.markdown("")
        if st.button("➕ Enregistrer l'essai"):
            if not ref:
                st.error("⚠ La référence est obligatoire.")
            else:
                essai = {
                    "date": str(date_essai),
                    "type_essai": type_essai,
                    "reference": ref,
                    "formulation": formulation,
                    "age_jours": age,
                    "dimension_mm": dimension,
                    "masse_g": masse,
                    "charge_max_kN": charge,
                    "resistance_MPa": resistance,
                    "module_GPa": module,
                    "allongement_pct": allongement,
                    "operateur": operateur,
                    "observations": observations,
                    "conforme": conforme,
                }
                new_id = ajouter_essai(essai)
                st.success(f"✅ Essai #{new_id} enregistré — {ref}")
                st.balloons()

    with col_table:
        st.markdown('<span class="section-tag">// Registre des essais</span>', unsafe_allow_html=True)

        df = get_df()

        # Filtres rapides
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filtre_type = st.multiselect("Type", TYPES_ESSAI, default=TYPES_ESSAI, label_visibility="collapsed")
        with fc2:
            filtre_age = st.multiselect("Âge (j)", sorted(df["age_jours"].unique().tolist()),
                                        default=sorted(df["age_jours"].unique().tolist()),
                                        label_visibility="collapsed")
        with fc3:
            filtre_conf = st.multiselect("Conformité", ["✓ Oui", "✗ Non", "⚠ À vérifier"],
                                         default=["✓ Oui", "✗ Non", "⚠ À vérifier"],
                                         label_visibility="collapsed")

        df_filtered = df[
            df["type_essai"].isin(filtre_type) &
            df["age_jours"].isin(filtre_age) &
            df["conforme"].isin(filtre_conf)
        ]

        # Stats rapides
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f"""<div class="stat-card">
                <div class="stat-label">Total essais</div>
                <div class="stat-value">{len(df_filtered)}</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            moy = df_filtered["resistance_MPa"].mean()
            st.markdown(f"""<div class="stat-card">
                <div class="stat-label">Résist. moy.</div>
                <div class="stat-value">{moy:.1f}</div>
                <div class="stat-sub">MPa</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            conf_pct = (df_filtered["conforme"] == "✓ Oui").sum() / max(len(df_filtered), 1) * 100
            st.markdown(f"""<div class="stat-card">
                <div class="stat-label">Conformité</div>
                <div class="stat-value">{conf_pct:.0f}%</div>
            </div>""", unsafe_allow_html=True)
        with s4:
            n_form = df_filtered["formulation"].nunique()
            st.markdown(f"""<div class="stat-card">
                <div class="stat-label">Formulations</div>
                <div class="stat-value">{n_form}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tableau
        cols_affich = ["id", "date", "type_essai", "reference", "formulation",
                       "age_jours", "resistance_MPa", "conforme", "operateur"]
        st.dataframe(
            df_filtered[cols_affich].rename(columns={
                "id": "N°", "date": "Date", "type_essai": "Type",
                "reference": "Référence", "formulation": "Formulation",
                "age_jours": "Âge (j)", "resistance_MPa": "fc (MPa)",
                "conforme": "Conformité", "operateur": "Opérateur"
            }),
            use_container_width=True,
            hide_index=True,
            height=320,
        )

        # Export
        st.markdown('<span class="section-tag" style="margin-top:16px">// Export</span>', unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        with ec1:
            from utils.data_manager import export_csv
            st.download_button(
                "⬇️ Exporter CSV",
                data=export_csv(),
                file_name="essais_laboratoire.csv",
                mime="text/csv",
            )
        with ec2:
            from utils.data_manager import export_excel
            st.download_button(
                "⬇️ Exporter Excel",
                data=export_excel(),
                file_name="essais_laboratoire.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
