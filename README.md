# 🚨 TP Fil Rouge – DevSecOps & Python Scripting

## 🎯 Objectif

Créer un outil de surveillance sécurisé qui :

- 🔁 Appelle une API (simulée localement)
- 💾 Sauvegarde les résultats dans des fichiers
- 📋 Utilise des logs structurés
- 🔐 Respecte les bonnes pratiques DevSecOps
- ✅ Passe les audits (Bandit, pip-audit)

---

## 🗂️ Structure du projet

```
.
├── monitor.py
├── fake_api.py
├── .env
├── .env.example
├── requirements.txt
├── logs/
└── reports/
```

---

## 📦 Installation

1. Créez un environnement virtuel :

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

📄 Exemple de `requirements.txt` :

```
requests
python-dotenv
fastapi
uvicorn
mysql-connector-python  # optionnel
```

---

## 🧪 API simulée

Le fichier `fake_api.py` démarre une API locale FastAPI protégée par token.

### ▶️ Lancer l’API :

```bash
uvicorn fake_api:app --reload
```

Elle écoute sur :  
🔗 `http://127.0.0.1:8000/status?app=NomApp`

### 🔐 Sécurité

L’accès est protégé par un token à transmettre dans l'en-tête :

```
Authorization: Bearer <API_TOKEN>
```

💡 **Bonus** : Ajouter une route `POST /login` qui retourne le token si `username` et `password` sont valides.

---

## 👁️ Script de surveillance (`monitor.py`)

Fonctionnalités :

- 📥 Charge les secrets depuis `.env`
- 📡 Appelle l’API avec gestion du timeout
- 📁 Sauvegarde les résultats dans `reports/`
- 🪵 Loggue les événements dans `logs/`
- 📋 Permet de surveiller plusieurs applications (via liste ou fichier)

---

## 🛡️ Audit sécurité

### 🔍 Analyse statique avec Bandit

```bash
pip install bandit
bandit -r .
```

### 🧬 Audit des dépendances avec pip-audit

```bash
pip install pip-audit
pip-audit
```

🧰 Créez un fichier `check_code.py` qui lance automatiquement ces deux commandes.

---

## 📝 Fichier `.env`

Exemple de contenu :

```env
API_TOKEN=VotreTokenIci
API_URL=http://127.0.0.1:8000/status
APPS=App1,App2,App3
```

Un fichier `.env.example` doit être fourni pour le partage sans secrets sensibles.

---

## 🧾 Bonnes pratiques de logs

- 🌀 Utiliser `logging` avec `RotatingFileHandler`
- 📅 Format horodaté et lisible : `[%(asctime)s] [%(levelname)s] %(message)s`
- 🚫 Ne jamais logguer de secrets
- 📂 Créer automatiquement le répertoire `logs/` si nécessaire

---

## 🐬 Bonus – Sauvegarde en base MySQL (optionnel)

Script SQL de création de la table :

```sql
CREATE TABLE app_status (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME,
  app_name VARCHAR(255),
  status VARCHAR(50),
  response_time FLOAT
);
```

Utilisez `mysql-connector-python` pour l’insertion des données.

---

## ✅ Résultat attendu

Exécution du script :

```bash
python monitor.py
```

Attendus :

- ✅ Un log propre dans `logs/`
- ✅ Un fichier JSON dans `reports/` au format `YYYY-MM-DD-App.json`
- ✅ Aucun secret en clair
- ✅ Audits OK (Bandit + pip-audit)
