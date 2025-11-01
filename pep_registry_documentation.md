# Documentation Technique du Registre PPE Modulaire

Ce document présente l'architecture finale du système de registre des Personnes Politiquement Exposées (PPE), conçu pour être modulaire et facilement déployable.

## 1. Architecture du Projet et Modularité

Le projet est organisé autour d'une architecture ETL (Extract-Transform-Load) et d'une API de service, avec une séparation claire des responsabilités :

| Répertoire | Contenu | Rôle |
| :--- | :--- | :--- |
| `pep_registry/config/` | Fichiers de configuration JSON par pays (ex: `ma.json`). | **Modularité :** Définit les sources, les poids de confiance, les mots-clés et les définitions spécifiques à chaque juridiction. |
| `pep_registry/sql/` | Schéma de la base de données (`schema.sql`). | **Auditabilité :** Définit les tables `pep_master`, `pep_version`, `audit_log` et `source_document` pour garantir le versioning et la traçabilité. |
| `pep_registry/src/etl/` | Classes Python pour le pipeline ETL. | **Cœur du Système :** Gère l'extraction, la normalisation, le scoring de confiance, la déduplication et les exports quotidiens. |
| `pep_registry/src/api/` | Fichier principal de l'API REST (`main.py`). | **Accès aux Données :** Expose les données du registre via une API FastAPI. |
| `Dockerfile` & `docker-compose.yml` | Fichiers de conteneurisation. | **Déploiement Facile :** Permet un déploiement portable et simple. |

## 2. Stratégie de Déploiement à Coût Zéro (ou très faible)

Pour un déploiement permanent et économique, nous recommandons de séparer l'API et la base de données :

| Composant | Service Cloud Recommandé | Coût (Plan Gratuit) | Rôle |
| :--- | :--- | :--- | :--- |
| **Base de Données (PostgreSQL)** | **Supabase** | **Gratuit** (pour les projets de petite taille) | Stockage permanent des données audités. |
| **API REST (FastAPI)** | **Render** | **Gratuit** (pour les services web avec limites) | Sert l'API et exécute le pipeline ETL quotidien. |

### Déploiement Local (avec Docker Compose)

Pour tester le système localement ou sur un serveur unique, utilisez Docker Compose :

1.  **Prérequis :** Installer Docker et Docker Compose.
2.  **Lancer le Système :**
    ```bash
    docker-compose up --build -d
    ```
    *   L'API sera accessible sur `http://localhost:8000`.
    *   La base de données sera initialisée avec le schéma.
3.  **Exécuter le Pipeline ETL (manuellement) :**
    ```bash
    docker-compose run etl
    ```

### Déploiement Cloud (Supabase + Render)

1.  **Déploiement de la Base de Données (Supabase) :**
    *   Créez un nouveau projet Supabase (plan gratuit).
    *   Récupérez les identifiants de connexion (URL de la base de données, nom d'utilisateur, mot de passe).
    *   Exécutez le schéma SQL (`pep_registry/sql/schema.sql`) sur votre base de données Supabase.
2.  **Déploiement de l'API (Render) :**
    *   Poussez le code sur un dépôt Git (GitHub, GitLab, etc.).
    *   Créez un nouveau **Web Service** sur Render.
    *   Connectez-le à votre dépôt Git.
    *   Render détectera automatiquement le `Dockerfile` et construira l'image.
    *   **Variables d'Environnement :** Configurez les variables d'environnement sur Render pour que l'API puisse se connecter à Supabase (e.g., `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`).

## 3. Modularité pour un Nouveau Pays (Ex: Sénégal - SN)

Pour étendre le système à un nouveau pays, le processus est le suivant :

1.  **Créer le Fichier de Configuration :** Créez un nouveau fichier `sn.json` dans `pep_registry/config/`.
    *   Copiez le contenu de `ma.json`.
    *   Mettez à jour `country_code` à "SN".
    *   **Mettez à jour les sources :** Remplacez les URL marocaines par les sources officielles et les médias sénégalais.
    *   **Mettez à jour les mots-clés :** Adaptez les titres de poste (ex: "Préfet", "Maire de Dakar").
2.  **Exécuter le Pipeline (Cloud) :**
    *   Si vous utilisez Render, vous pouvez créer un **Cron Job** ou un **Background Worker** qui exécute la commande suivante quotidiennement, en spécifiant le code pays :
        ```bash
        python src/etl/pep_etl.py SN
        ```
    Le système utilisera automatiquement les sources, les poids et les définitions du fichier `sn.json`.

## 4. Conclusion

Le projet est désormais conteneurisé et prêt pour un déploiement cloud permanent à faible coût. L'utilisation de Docker et des services cloud gratuits simplifie au maximum la charge technique.
