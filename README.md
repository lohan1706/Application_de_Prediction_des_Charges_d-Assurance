# AssurPredict 🚀

Application web de prédiction de primes d'assurance maladie basée sur l'IA (Gradient Boosting).

## Fonctionnalités

- ✅ Inscription / Connexion sécurisée
- ✅ Gestion profil utilisateur (âge, BMI, région, fumeur)
- ✅ Prédiction ML de prime d'assurance
- ✅ Formulaire éditable pour simulation
- ✅ Historique des prédictions
- ✅ Interface responsive (Tailwind CSS)

## Stack

- **Backend** : Django 4.x
- **BDD** : SQLite (dev) / PostgreSQL (prod)
- **Frontend** : HTML5 + Tailwind CSS
- **ML** : Scikit-learn (Gradient Boosting)
- **Tests** : Django TestCase + unittest.mock

## Installation

```bash
git clone https://github.com/lohan1706/Application_de_Prediction_des_Charges_d-Assurance.git
cd Assur_Aimant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Accédez à http://localhost:8000

## Tests

```bash
# Tous les tests
python manage.py test

# Tests par app
python manage.py test accounts profiles prediction assur_predict
```

## Architecture

```
accounts/     → Authentification (login/signup)
profiles/     → Gestion profil utilisateur
prediction/   → Prédictions ML
assur_predict/→ Page d'accueil + modèle ML
```

## Flux utilisateur

1. **Inscription** → Créer compte
2. **Profil** → Remplir informations personnelles
3. **Prédiction** → Voir prime estimée (éditable pour simulation)
4. **Historique** → Consulter prédictions précédentes

## Configuration

Créer `.env` à la racine :
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

## Modèle ML

- **Type** : Gradient Boosting Regressor
- **Features** : age, sex, bmi, children, smoker, region
- **Target** : charges (prime en €)
- **Performance** : R² ≈ 0.87

---

© 2026 AssurPredict | [GitHub](https://github.com/lohan1706)