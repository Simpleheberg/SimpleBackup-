# SimpleBackup - Sauvegarde Automatique de Sites et Bases de Données

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**SimpleBackup** est un outil de sauvegarde automatique simple et fiable pour vos sites web et bases de données. Créé par [SimpleHeberg](https://simpleheberg.fr) pour faciliter la gestion des sauvegardes d'hébergement.

## ✨ Fonctionnalités

- 🗂️ **Sauvegarde de sites web** : Archivage complet de vos fichiers
- 🗄️ **Sauvegarde de bases de données** : Support MySQL/MariaDB et PostgreSQL
- 🗜️ **Compression automatique** : Fichiers compressés en .tar.gz pour économiser l'espace
- 🔄 **Rotation des sauvegardes** : Suppression automatique des anciennes sauvegardes
- 📝 **Logs détaillés** : Suivi complet de chaque opération
- ⚙️ **Configuration JSON** : Paramétrage simple et lisible
- 🚀 **Automatisation** : Facile à intégrer dans un cron

## 📋 Prérequis

- Python 3.6 ou supérieur
- `mysqldump` pour les bases MySQL/MariaDB
- `pg_dump` pour les bases PostgreSQL
- Droits de lecture sur les dossiers à sauvegarder
- Accès aux bases de données à sauvegarder

### Installation des outils de base de données

**Debian/Ubuntu :**
```bash
# Pour MySQL/MariaDB
sudo apt-get install mysql-client

# Pour PostgreSQL
sudo apt-get install postgresql-client
```

**CentOS/RHEL :**
```bash
# Pour MySQL/MariaDB
sudo yum install mysql

# Pour PostgreSQL
sudo yum install postgresql
```

## 🚀 Installation

1. **Cloner le dépôt :**
```bash
git clone https://github.com/simpleheberg/simple-backup.git
cd simple-backup
```

2. **Rendre le script exécutable :**
```bash
chmod +x backup_automator.py
```

3. **Créer la configuration initiale :**
```bash
./backup_automator.py --init
```

## ⚙️ Configuration

Éditez le fichier `backup_config.json` créé automatiquement :

```json
{
    "backup_dir": "./backups",
    "retention_days": 7,
    "compression": "gz",
    "websites": [
        {
            "name": "mon_site",
            "path": "/var/www/html/monsite",
            "enabled": true
        }
    ],
    "databases": [
        {
            "name": "ma_base",
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "user": "backup_user",
            "password": "mot_de_passe_securise",
            "database": "ma_base_prod",
            "enabled": true
        }
    ]
}
```

### Options de configuration

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `backup_dir` | Dossier de destination des sauvegardes | `./backups` |
| `retention_days` | Nombre de jours de conservation | `7` |
| `compression` | Type de compression | `gz` |
| `websites[].enabled` | Activer/désactiver la sauvegarde | `false` |
| `databases[].type` | Type de base : `mysql`, `mariadb`, `postgresql` | - |
| `databases[].enabled` | Activer/désactiver la sauvegarde | `false` |

## 💡 Utilisation

### Sauvegarde manuelle

```bash
# Utiliser la configuration par défaut
./backup_automator.py

# Utiliser un fichier de configuration personnalisé
./backup_automator.py --config /chemin/vers/config.json
```

### Automatisation avec Cron

Pour exécuter des sauvegardes automatiques quotidiennes à 2h du matin :

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne (adapter le chemin)
0 2 * * * /chemin/vers/backup_automator.py >> /var/log/backup.log 2>&1
```

**Exemples de fréquences :**
- `0 2 * * *` - Tous les jours à 2h00
- `0 */6 * * *` - Toutes les 6 heures
- `0 2 * * 0` - Tous les dimanches à 2h00
- `0 2 1 * *` - Le 1er de chaque mois à 2h00

### Sauvegarde hebdomadaire complète

```bash
# Tous les dimanches à 3h00 du matin
0 3 * * 0 /chemin/vers/backup_automator.py --config /etc/backup/weekly_config.json
```

## 📁 Structure des sauvegardes

Les sauvegardes sont organisées ainsi :

```
backups/
├── logs/
│   └── backup_20240214.log
├── mon_site_website_20240214_020000.tar.gz
├── ma_base_mysql_20240214_020030.sql.gz
└── autre_site_website_20240214_020100.tar.gz
```

### Nomenclature des fichiers

- **Sites web** : `{nom}_website_{date}_{heure}.tar.gz`
- **MySQL/MariaDB** : `{nom}_mysql_{date}_{heure}.sql.gz`
- **PostgreSQL** : `{nom}_postgresql_{date}_{heure}.sql.gz`

## 🔐 Sécurité

### Recommandations importantes

1. **Protégez votre fichier de configuration :**
```bash
chmod 600 backup_config.json
```

2. **Créez un utilisateur dédié aux sauvegardes :**

**MySQL :**
```sql
CREATE USER 'backup_user'@'localhost' IDENTIFIED BY 'mot_de_passe_fort';
GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON *.* TO 'backup_user'@'localhost';
FLUSH PRIVILEGES;
```

**PostgreSQL :**
```sql
CREATE USER backup_user WITH PASSWORD 'mot_de_passe_fort';
GRANT CONNECT ON DATABASE ma_base TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

3. **Stockez les sauvegardes hors du serveur web :**
```json
{
    "backup_dir": "/var/backups/sites",
    ...
}
```

4. **Chiffrez les sauvegardes sensibles :**
```bash
# Exemple de chiffrement avec GPG
gpg --symmetric --cipher-algo AES256 backup.tar.gz
```

## 🔧 Restauration

### Restaurer un site web

```bash
# Extraire l'archive
tar -xzf mon_site_website_20240214_020000.tar.gz -C /var/www/html/

# Vérifier les permissions
chown -R www-data:www-data /var/www/html/mon_site
```

### Restaurer une base MySQL

```bash
# Décompresser et restaurer
gunzip < ma_base_mysql_20240214_020030.sql.gz | mysql -u root -p ma_base_prod
```

### Restaurer une base PostgreSQL

```bash
# Décompresser et restaurer
gunzip < ma_base_postgresql_20240214_020030.sql.gz | psql -U postgres ma_base_prod
```

## 📊 Logs et Monitoring

Les logs sont stockés dans `backups/logs/` avec un fichier par jour :

```
[2024-02-14 02:00:00] - INFO - Starting backup process...
[2024-02-14 02:00:05] - INFO - Backing up website: mon_site
[2024-02-14 02:00:12] - INFO - ✓ Website backup completed: mon_site_website_20240214_020000.tar.gz (45.32 MB)
[2024-02-14 02:00:15] - INFO - Backing up MySQL database: ma_base_prod
[2024-02-14 02:00:28] - INFO - ✓ MySQL backup completed: ma_base_mysql_20240214_020015.sql.gz (12.45 MB)
[2024-02-14 02:00:30] - INFO - Cleaning up backups older than 7 days...
[2024-02-14 02:00:31] - INFO - ✓ Cleaned up 3 old backup(s), freed 123.45 MB
[2024-02-14 02:00:31] - INFO - Backup process completed: 2 successful, 0 failed
```

## 🐛 Dépannage

### Problème : "mysqldump not found"

**Solution :**
```bash
# Installer le client MySQL
sudo apt-get install mysql-client  # Debian/Ubuntu
sudo yum install mysql             # CentOS/RHEL
```

### Problème : "Access denied for user"

**Solution :** Vérifiez les permissions de l'utilisateur de sauvegarde :
```sql
SHOW GRANTS FOR 'backup_user'@'localhost';
```

### Problème : Sauvegardes trop volumineuses

**Solutions :**
- Excluez les fichiers temporaires
- Augmentez la rétention uniquement pour certaines sauvegardes
- Utilisez un stockage externe (NAS, S3, etc.)

### Problème : Échec de compression

**Solution :** Vérifiez l'espace disque disponible :
```bash
df -h
```

## 🎯 Exemples de cas d'usage

### WordPress

```json
{
    "websites": [
        {
            "name": "wordpress_prod",
            "path": "/var/www/html/wordpress",
            "enabled": true
        }
    ],
    "databases": [
        {
            "name": "wordpress_db",
            "type": "mysql",
            "database": "wordpress",
            "enabled": true
        }
    ]
}
```

### PrestaShop / WooCommerce

```json
{
    "websites": [
        {
            "name": "boutique",
            "path": "/var/www/html/prestashop",
            "enabled": true
        }
    ],
    "databases": [
        {
            "name": "boutique_db",
            "type": "mysql",
            "database": "prestashop_prod",
            "enabled": true
        }
    ],
    "retention_days": 14
}
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🌐 À propos de SimpleHeberg

SimpleBackup est développé et maintenu par **[SimpleHeberg](https://simpleheberg.fr)**, votre solution d'hébergement web tout-en-un.

### Nos services
- Hébergement web professionnel
- Création de sites web
- Maintenance et support technique
- Solutions sur-mesure

**Besoin d'hébergement ?** Contactez-nous sur [simpleheberg.fr](https://simpleheberg.fr)

---

**Développé avec ❤️ par SimpleHeberg** | [Site Web](https://simpleheberg.fr) | [Support](mailto:contact@simpleheberg.fr)
