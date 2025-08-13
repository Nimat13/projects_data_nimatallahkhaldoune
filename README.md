
# 🏗️ Projet HIL_AUTO_KPI - Documentation

## 📂 Structure du projet

```
HIL_AUTO_KPI/
├── data/
│   ├── logs/                     # Fichiers logs bruts
│   │   ├── autorun_decide_log.log
│   │   ├── dsb-_autorun_control_log.log
│   │   └── Hil_Synthesis_logs.log
│   └── synthesis_data/         # Données transformées
│       ├── comment.[csv|json]       # Commentaires des procédures
│       ├── kpi_variable.[csv|json]  # Indicateurs de performance
│       ├── procedure.[csv|json]     # Données des procédures
│       └── procedure_*.[csv|json]   # Définitions/digitalisation
├── filebeat/                    # Configuration Filebeat
│   ├── filebeat.yml
│   └── filebeat.json.yml
├── logstash/                    # Pipelines de traitement
│   ├── config/
│   ├── logstash.conf
│   ├── logstashs.conf           # Config secondaire
│   └── logstash.yml
├── docker-compose.yml           # Orchestration des containers
├── fetch_synthesis_data.py      # Script original (JSON brut)
├── fetch_synthesis_data_modified.py  # JSON sans 'items'
├── fetch_synthesis_data_latest.py    # CSV optimisé
└── README.md                    # Ce fichier
```

## 🚀 Première installation

1. **Cloner le dépôt** (branche `development`)

2. **Générer les données** (Exécuter dans le terminal à la racine du projet) :

```bash
# Version JSON brut
python fetch_synthesis_data.py

# Version JSON sans 'items'
python fetch_synthesis_data_modified.py

# Version CSV optimisée (recommandé)
python fetch_synthesis_data_latest.py

# ⚠️ Les fichiers existants seront écrasés
```

3. **Démarrer la stack Docker**

```bash
docker-compose up -d
```

---

## 🔧 Dépannage courant

### 🟠 Cas 1 : Données non visibles dans Kibana

```bash
# Accéder au container Filebeat
docker exec -it filebeat bash

# Nettoyer le registry
rm -rf /usr/share/filebeat/data/registry/*

# Redémarrer les services
exit
docker-compose restart filebeat logstash
```

### 🔴 Cas 2 : Réinitialisation complète

```bash
docker-compose down -v  # Supprime les volumes (supprimer esdata manuellement si nécessaire)
docker-compose up -d    # Redémarrage propre
```

---

## 👀 Monitoring

### Logs en temps réel

```bash
docker-compose logs -f logstash
```

### Configuration Kibana

- Créer des **Data Views** pour chaque index
- Sélectionner le champ temporel : `@timestamp`
- Importer `export.ndjson` dans **Saved Objects** (Kibana)

---

## 🛠 Bonnes pratiques

1. **Format des fichiers** :
   - `CSV` pour les données tabulaires (sans en-têtes)
   - `JSON` pour les logs ou structures hiérarchiques
   - Toujours ajouter **une ligne vide** à la fin de chaque fichier

2. **Structure optimale (CSV recommandé)** :

```csv
valeur1,valeur2,valeur3
valeur4,valeur5,valeur6
# id,champ1,champ2
```

---

## 🚧 Améliorations prévues

| Problème                        | Action prévue                                                  |
|---------------------------------|----------------------------------------------------------------|
| Données bench non récupérées    | Implémenter l'authentification + extraire cotation/correlation |
| Métadonnées manquantes          | Ajouter `created_at`, `updated_at`                             |
| Lien KPI - Procédure absent     | Ajouter `group_type` ou référence croisée                      |
