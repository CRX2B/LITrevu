# LITRevu - Plateforme de Critiques Littéraires

LITRevu est une application web Django permettant aux utilisateurs de demander et publier des critiques de livres. Les utilisateurs peuvent suivre d'autres contributeurs, créer des tickets de demande de critique et poster leurs propres critiques.

## 🚀 Fonctionnalités

- Système d'authentification complet (inscription, connexion, déconnexion)
- Création de tickets pour demander des critiques
- Publication de critiques en réponse aux tickets ou spontanément
- Système d'abonnement entre utilisateurs
- Flux d'actualités personnalisé
- Gestion des images (upload et redimensionnement automatique)

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Un environnement virtuel (recommandé)

## 💻 Installation

1. **Cloner le repository**
```bash
git clone https://github.com/CRX2B/LITRevu.git
cd LITRevu
```

2. **Créer et activer l'environnement virtuel**

Sur Windows :
```bash
python -m venv env
env\Scripts\activate
```

Sur macOS/Linux :
```bash
python3 -m venv env
source env/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
- Créer un fichier `.env` à la racine du projet
- Ajouter les variables suivantes :
```
SECRET_KEY=votre_clé_secrète
DEBUG=True
```

5. **Appliquer les migrations**
```bash
python manage.py migrate
```

6. **Créer un super utilisateur (administrateur)**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

L'application sera accessible à l'adresse : http://127.0.0.1:8000/

## 🎯 Utilisation

1. **Inscription/Connexion**
   - Accédez à la page d'accueil
   - Cliquez sur "Inscription" pour créer un compte
   - Connectez-vous avec vos identifiants

2. **Créer un ticket**
   - Cliquez sur "Créer un ticket"
   - Remplissez le formulaire (titre, description, image optionnelle)
   - Soumettez le ticket

3. **Publier une critique**
   - En réponse à un ticket : cliquez sur "Créer une critique" depuis un ticket
   - Critique spontanée : utilisez "Créer une critique" depuis le menu

4. **Suivre des utilisateurs**
   - Accédez à la page d'abonnements
   - Recherchez des utilisateurs
   - Cliquez sur "Suivre"

## 🔧 Structure du Projet

```
LITRevu/
├── authentication/        # Application de gestion des utilisateurs
├── review/               # Application principale de critiques
├── static/              # Fichiers statiques (CSS, JS)
├── media/               # Fichiers uploadés
├── templates/           # Templates HTML
└── litrevu/            # Configuration du projet
```

## 🛠️ Technologies Utilisées

- Django 4.x
- Python 3.8+
- HTML5/CSS3
- Pillow (traitement d'images)
- SQLite (base de données)

## 🔐 Sécurité

- Protection CSRF active
- Authentification requise pour toutes les actions
- Validation des données utilisateur
- Redimensionnement automatique des images
