"""
Gestionnaire de données des essais laboratoire
Stockage en session Streamlit + export CSV/Excel
"""
import pandas as pd
import streamlit as st
from datetime import datetime
import io

# ── Colonnes du DataFrame principal ──────────────────────────────────────────
COLONNES = [
    "id", "date", "type_essai", "reference", "formulation",
    "age_jours", "dimension_mm", "masse_g",
    "charge_max_kN", "resistance_MPa",
    "module_GPa", "allongement_pct",
    "operateur", "observations", "conforme"
]

TYPES_ESSAI = ["Compression", "Flexion", "Traction"]

FORMULATIONS = [
    "C20/25 — Témoin",
    "C25/30 — Standard",
    "C30/37 — HP",
    "C35/45 — HP+",
    "C40/50 — THP",
    "Béton fibré acier",
    "Béton fibré polypropylène",
    "Béton avec fumée de silice",
    "Béton avec cendres volantes",
    "Béton avec laitier",
    "Béton recyclé (GR 30%)",
    "Béton recyclé (GR 50%)",
    "Béton autoplaçant (BAP)",
    "Autre / Personnalisée",
]

AGES = [1, 3, 7, 14, 28, 56, 90, 180, 365]

DIMENSIONS = [
    "100×100×100 mm (cube)",
    "150×150×150 mm (cube)",
    "Ø100×200 mm (cylindre)",
    "Ø150×300 mm (cylindre)",
    "100×100×400 mm (prisme)",
    "150×150×600 mm (prisme)",
    "Autre",
]


def init_session():
    """Initialise le stockage en session si absent."""
    if "essais_df" not in st.session_state:
        # Données de démonstration
        st.session_state["essais_df"] = _demo_data()
    if "next_id" not in st.session_state:
        df = st.session_state["essais_df"]
        st.session_state["next_id"] = len(df) + 1


def _demo_data() -> pd.DataFrame:
    """Génère des données de démonstration réalistes."""
    import numpy as np
    np.random.seed(42)

    data = []
    formulations = ["C30/37 — HP", "Béton fibré acier", "Béton avec fumée de silice", "C25/30 — Standard"]
    types = ["Compression", "Compression", "Compression", "Flexion", "Traction"]
    ages_comp = [7, 7, 7, 28, 28, 28, 28, 90, 90]

    # Compression — courbe de résistance vs âge
    base_resistance = {"C30/37 — HP": 38, "Béton fibré acier": 42,
                       "Béton avec fumée de silice": 45, "C25/30 — Standard": 30}
    id_c = 1
    for form in formulations[:3]:
        br = base_resistance[form]
        for age in ages_comp:
            factor = 0.55 if age == 7 else (0.85 if age == 28 else 1.0)
            for rep in range(3):
                res = br * factor + np.random.normal(0, 1.2)
                charge = res * (150**2) / 1000  # kN pour cylindre 150mm
                data.append({
                    "id": id_c,
                    "date": (datetime(2025, 1, 1) + pd.Timedelta(days=id_c * 2)).strftime("%Y-%m-%d"),
                    "type_essai": "Compression",
                    "reference": f"EC-{form[:3].upper()}-{age}J-{rep+1:02d}",
                    "formulation": form,
                    "age_jours": age,
                    "dimension_mm": "Ø150×300 mm (cylindre)",
                    "masse_g": round(np.random.normal(12500, 200), 0),
                    "charge_max_kN": round(charge, 1),
                    "resistance_MPa": round(res, 2),
                    "module_GPa": round(30 + np.random.normal(0, 1), 1),
                    "allongement_pct": None,
                    "operateur": np.random.choice(["F. Belaid", "A. Martin", "S. Dupont"]),
                    "observations": "",
                    "conforme": "✓ Oui" if res >= br * factor * 0.9 else "✗ Non",
                })
                id_c += 1

    # Flexion
    for i in range(12):
        res = np.random.normal(5.2, 0.4)
        data.append({
            "id": id_c,
            "date": (datetime(2025, 3, 1) + pd.Timedelta(days=i * 3)).strftime("%Y-%m-%d"),
            "type_essai": "Flexion",
            "reference": f"EF-C30-28J-{i+1:02d}",
            "formulation": "C30/37 — HP",
            "age_jours": 28,
            "dimension_mm": "100×100×400 mm (prisme)",
            "masse_g": round(np.random.normal(9800, 150), 0),
            "charge_max_kN": round(res * 100 * 100 * 100 / (3 * 300 * 1000), 1),
            "resistance_MPa": round(res, 2),
            "module_GPa": None,
            "allongement_pct": None,
            "operateur": "F. Belaid",
            "observations": "",
            "conforme": "✓ Oui" if res >= 4.5 else "✗ Non",
        })
        id_c += 1

    # Traction
    for i in range(8):
        res = np.random.normal(2.8, 0.3)
        data.append({
            "id": id_c,
            "date": (datetime(2025, 4, 1) + pd.Timedelta(days=i * 2)).strftime("%Y-%m-%d"),
            "type_essai": "Traction",
            "reference": f"ET-BFS-28J-{i+1:02d}",
            "formulation": "Béton avec fumée de silice",
            "age_jours": 28,
            "dimension_mm": "Ø150×300 mm (cylindre)",
            "masse_g": round(np.random.normal(12300, 180), 0),
            "charge_max_kN": round(res * 3.14 * 75**2 / 1000, 1),
            "resistance_MPa": round(res, 2),
            "module_GPa": None,
            "allongement_pct": round(np.random.normal(0.012, 0.002) * 100, 4),
            "operateur": "A. Martin",
            "observations": "",
            "conforme": "✓ Oui" if res >= 2.5 else "✗ Non",
        })
        id_c += 1

    return pd.DataFrame(data, columns=COLONNES)


def get_df() -> pd.DataFrame:
    init_session()
    return st.session_state["essais_df"].copy()


def ajouter_essai(essai: dict) -> int:
    init_session()
    df = st.session_state["essais_df"]
    essai["id"] = st.session_state["next_id"]
    new_row = pd.DataFrame([essai])
    st.session_state["essais_df"] = pd.concat([df, new_row], ignore_index=True)
    st.session_state["next_id"] += 1
    return essai["id"]


def supprimer_essai(essai_id: int):
    df = st.session_state["essais_df"]
    st.session_state["essais_df"] = df[df["id"] != essai_id].reset_index(drop=True)


def export_excel() -> bytes:
    df = get_df()
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Essais")
        # Feuille résumé par formulation
        resume = df.groupby(["formulation", "type_essai"]).agg(
            n_essais=("id", "count"),
            res_moyenne=("resistance_MPa", "mean"),
            res_std=("resistance_MPa", "std"),
            res_min=("resistance_MPa", "min"),
            res_max=("resistance_MPa", "max"),
        ).round(2)
        resume.to_excel(writer, sheet_name="Résumé statistique")
    return buf.getvalue()


def export_csv() -> bytes:
    return get_df().to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
