# 🧪 LabTrack — Dashboard de suivi d'essais béton

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?logo=plotly)](https://plotly.com/)
[![SciPy](https://img.shields.io/badge/SciPy-1.12%2B-8CAAE6)](https://scipy.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> Application web de **suivi et visualisation d'essais laboratoire** sur éprouvettes béton — Compression, Flexion, Traction — avec analyses statistiques avancées.

Développé dans le cadre d'une thèse de doctorat en Génie Civil — Structures & Matériaux.

---

## ✨ Fonctionnalités

### 📋 Saisie des essais
- Enregistrement complet : type, formulation, âge, dimensions, masse, charge, résistance
- Référencement automatique des éprouvettes
- Suivi de conformité (✓ Oui / ✗ Non / ⚠ À vérifier)
- Export **CSV** et **Excel** (avec feuille résumé statistique)

### 📊 Tableaux de bord (Plotly interactif)
- **Courbe fc vs âge** par formulation (avec bande d'incertitude ± σ)
- **Histogramme** de distribution des résistances
- **Box plot** comparatif par formulation
- **Scatter plot** Charge vs Résistance (coloré par âge)
- **Timeline** chronologique des essais
- **Donut** taux de conformité global

### 📈 Analyses statistiques
- Statistiques descriptives : n, moyenne, médiane, σ, CoV, fck estimé, IC 95%
- **fck caractéristique** selon EN 206 : `fcm - 1.65·s`
- **Test de normalité** Shapiro-Wilk
- **Courbes KDE** (densité de probabilité)
- **Q-Q Plot** de normalité
- **Test ANOVA** comparaison multi-formulations

---

## 🚀 Installation & Lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/labtrack-beton.git
cd labtrack-beton

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Lancer
streamlit run app.py
```

---

## 📁 Structure du projet

```
labtrack-beton/
├── app.py                      # Point d'entrée Streamlit
├── requirements.txt
├── README.md
├── pages/
│   ├── saisie.py               # Formulaire de saisie + registre
│   ├── dashboard.py            # Graphiques Plotly interactifs
│   └── statistiques.py        # Analyses statistiques avancées
└── utils/
    └── data_manager.py         # Gestion des données + export
```

---

## 📐 Méthodes statistiques

| Méthode | Usage | Référence |
|---------|-------|-----------|
| Moyenne, σ, CoV | Variabilité des résultats | NF EN 206 |
| fck = fcm - 1.65·s | Résistance caractéristique | NF EN 206 §8.2 |
| Shapiro-Wilk | Test de normalité | — |
| KDE (Kernel Density) | Estimation densité | — |
| Q-Q Plot | Vérification normalité | — |
| ANOVA (F-test) | Comparaison groupes | — |

---

## 🔮 Évolutions prévues

- [ ] Import de fichiers CSV/Excel existants
- [ ] Rapport PDF automatique par campagne
- [ ] Courbes de résistance normalisées (fc/fc28)
- [ ] Module de comparaison avec valeurs Eurocode
- [ ] Authentification multi-utilisateurs
- [ ] Synchronisation base de données (SQLite)

---

## ⚠️ Note

Les données sont stockées en **mémoire de session** Streamlit. Pour une persistance permanente, connecter une base de données (SQLite, PostgreSQL).

---

## 👤 Auteur

**Fayçal Belaid** — Doctorant en Génie Civil  
Spécialité : Structures & Matériaux · Durabilité du béton

[![GitHub](https://img.shields.io/badge/GitHub-faycalbelaid--GC-181717?logo=github)](https://github.com/faycalbelaid-GC)

---

## 📄 Licence

MIT License
