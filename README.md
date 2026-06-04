# 🤖 Organizer Bot — Discord Planner pour étudiants devs

Bot Discord intelligent qui génère des plans de journée optimisés, priorise vos projets et suit votre progression, propulsé par GPT-4o-mini.

---

## ✨ Fonctionnalités

| Commande | Description |
|---|---|
| `/project_add` | Ajouter un projet → l'IA génère les tâches automatiquement |
| `/project_list` | Lister vos projets triés par priorité (urgence + difficulté) |
| `/project_delete` | Supprimer un projet et toutes ses tâches |
| `/task_list` | Voir les tâches d'un projet avec statut et durée |
| `/task_add` | Ajouter manuellement une tâche à un projet |
| `/done` | Marquer une tâche comme terminée (avec vérification propriétaire) |
| `/plan` | Générer le plan optimisé de la journée (via l'IA) |
| `/report` | Rapport hebdomadaire avec barre de progression par projet |

---

## 🚀 Installation

### 1. Cloner et préparer l'environnement

```bash
git clone <votre-repo>
cd organizer_bot
python3 -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Éditez `.env` et remplissez :

```env
DISCORD_TOKEN=votre_token_discord
OPENAI_API_KEY=votre_clé_openai
GUILD_ID=id_de_votre_serveur   # optionnel mais recommandé en dev
```

### 3. Créer le bot Discord

1. Allez sur [discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application** → donnez un nom
3. Onglet **Bot** → **Reset Token** → copiez dans `.env`
4. Activez **"Message Content Intent"** si besoin
5. Onglet **OAuth2 → URL Generator** :
   - Scopes : `bot` + `applications.commands`
   - Permissions : `Send Messages`, `Embed Links`, `Use Slash Commands`
6. Ouvrez l'URL générée pour inviter le bot sur votre serveur

### 4. Obtenir l'OpenAI API Key

Créez une clé sur [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
Le bot utilise `gpt-4o-mini` (rapide et économique).

### 5. Lancer le bot

```bash
python3 bot/main.py
```

---

## 📁 Architecture

```
organizer_bot/
├── bot/
│   ├── main.py              # Point d'entrée + gestion des événements
│   ├── config.py            # Variables d'environnement centralisées
│   ├── commands/
│   │   ├── project.py       # /project_add, /project_list, /project_delete
│   │   ├── tasks.py         # /task_list, /task_add, /done
│   │   ├── plan.py          # /plan
│   │   └── report.py        # /report
│   ├── services/
│   │   ├── ai_service.py    # Appels OpenAI (gpt-4o-mini, JSON mode)
│   │   ├── project_service.py  # CRUD projets/tâches + sécurité
│   │   ├── planner.py       # Orchestration génération de plan
│   │   └── scheduler.py     # Historique des plans
│   └── database/
│       ├── models.py        # SQLAlchemy ORM (User, Project, Task, ScheduleHistory)
│       └── db.py            # Engine + session factory
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Personnalisation du planning

Toutes les contraintes sont configurables via `.env` :

```env
WAKE_UP_TIME=07:30
SCHOOL_START=08:30
SCHOOL_END=12:30
LUNCH_TIME=13:00
SLEEP_HOURS_MIN=7
SLEEP_HOURS_MAX=8
MAX_DEEP_WORK_HOURS=8
MAX_PROJECTS_PER_DAY=2
```

---

## 🔒 Sécurité

- Chaque opération sur un projet ou une tâche vérifie que l'utilisateur Discord en est le propriétaire.
- Le token Discord et la clé OpenAI ne sont jamais committés (`.gitignore`).
