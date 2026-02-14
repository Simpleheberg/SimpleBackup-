# SimpleBackup - Automatic Website & Database Backup Tool

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**SimpleBackup** is a simple and reliable automatic backup tool for your websites and databases. Created by [SimpleHeberg](https://simpleheberg.fr) to simplify hosting backup management.

## ✨ Features

- 🗂️ **Website Backup**: Complete archiving of your files
- 🗄️ **Database Backup**: MySQL/MariaDB and PostgreSQL support
- 🗜️ **Automatic Compression**: Files compressed in .tar.gz to save space
- 🔄 **Backup Rotation**: Automatic deletion of old backups
- 📝 **Detailed Logs**: Complete tracking of each operation
- ⚙️ **JSON Configuration**: Simple and readable settings
- 🚀 **Automation**: Easy to integrate with cron

## 📋 Requirements

- Python 3.6 or higher
- `mysqldump` for MySQL/MariaDB databases
- `pg_dump` for PostgreSQL databases
- Read permissions on folders to backup
- Access to databases to backup

### Installing Database Tools

**Debian/Ubuntu:**
```bash
# For MySQL/MariaDB
sudo apt-get install mysql-client

# For PostgreSQL
sudo apt-get install postgresql-client
```

**CentOS/RHEL:**
```bash
# For MySQL/MariaDB
sudo yum install mysql

# For PostgreSQL
sudo yum install postgresql
```

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/simpleheberg/simple-backup.git
cd simple-backup
```

2. **Make the script executable:**
```bash
chmod +x backup_automator.py
```

3. **Create initial configuration:**
```bash
./backup_automator.py --init
```

## ⚙️ Configuration

Edit the automatically created `backup_config.json` file:

```json
{
    "backup_dir": "./backups",
    "retention_days": 7,
    "compression": "gz",
    "websites": [
        {
            "name": "my_site",
            "path": "/var/www/html/mysite",
            "enabled": true
        }
    ],
    "databases": [
        {
            "name": "my_database",
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "user": "backup_user",
            "password": "secure_password",
            "database": "my_prod_db",
            "enabled": true
        }
    ]
}
```

### Configuration Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `backup_dir` | Backup destination folder | `./backups` |
| `retention_days` | Number of days to keep backups | `7` |
| `compression` | Compression type | `gz` |
| `websites[].enabled` | Enable/disable backup | `false` |
| `databases[].type` | Database type: `mysql`, `mariadb`, `postgresql` | - |
| `databases[].enabled` | Enable/disable backup | `false` |

## 💡 Usage

### Manual Backup

```bash
# Use default configuration
./backup_automator.py

# Use custom configuration file
./backup_automator.py --config /path/to/config.json
```

### Automation with Cron

To run automatic daily backups at 2 AM:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path)
0 2 * * * /path/to/backup_automator.py >> /var/log/backup.log 2>&1
```

**Frequency examples:**
- `0 2 * * *` - Every day at 2:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 2 * * 0` - Every Sunday at 2:00 AM
- `0 2 1 * *` - 1st of each month at 2:00 AM

### Weekly Full Backup

```bash
# Every Sunday at 3:00 AM
0 3 * * 0 /path/to/backup_automator.py --config /etc/backup/weekly_config.json
```

## 📁 Backup Structure

Backups are organized as follows:

```
backups/
├── logs/
│   └── backup_20240214.log
├── my_site_website_20240214_020000.tar.gz
├── my_db_mysql_20240214_020030.sql.gz
└── other_site_website_20240214_020100.tar.gz
```

### File Naming Convention

- **Websites**: `{name}_website_{date}_{time}.tar.gz`
- **MySQL/MariaDB**: `{name}_mysql_{date}_{time}.sql.gz`
- **PostgreSQL**: `{name}_postgresql_{date}_{time}.sql.gz`

## 🔐 Security

### Important Recommendations

1. **Protect your configuration file:**
```bash
chmod 600 backup_config.json
```

2. **Create a dedicated backup user:**

**MySQL:**
```sql
CREATE USER 'backup_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON *.* TO 'backup_user'@'localhost';
FLUSH PRIVILEGES;
```

**PostgreSQL:**
```sql
CREATE USER backup_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE my_db TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

3. **Store backups outside the web server:**
```json
{
    "backup_dir": "/var/backups/sites",
    ...
}
```

4. **Encrypt sensitive backups:**
```bash
# Example encryption with GPG
gpg --symmetric --cipher-algo AES256 backup.tar.gz
```

## 🔧 Restoration

### Restore a Website

```bash
# Extract the archive
tar -xzf my_site_website_20240214_020000.tar.gz -C /var/www/html/

# Check permissions
chown -R www-data:www-data /var/www/html/my_site
```

### Restore a MySQL Database

```bash
# Decompress and restore
gunzip < my_db_mysql_20240214_020030.sql.gz | mysql -u root -p my_prod_db
```

### Restore a PostgreSQL Database

```bash
# Decompress and restore
gunzip < my_db_postgresql_20240214_020030.sql.gz | psql -U postgres my_prod_db
```

## 📊 Logs and Monitoring

Logs are stored in `backups/logs/` with one file per day:

```
[2024-02-14 02:00:00] - INFO - Starting backup process...
[2024-02-14 02:00:05] - INFO - Backing up website: my_site
[2024-02-14 02:00:12] - INFO - ✓ Website backup completed: my_site_website_20240214_020000.tar.gz (45.32 MB)
[2024-02-14 02:00:15] - INFO - Backing up MySQL database: my_prod_db
[2024-02-14 02:00:28] - INFO - ✓ MySQL backup completed: my_db_mysql_20240214_020015.sql.gz (12.45 MB)
[2024-02-14 02:00:30] - INFO - Cleaning up backups older than 7 days...
[2024-02-14 02:00:31] - INFO - ✓ Cleaned up 3 old backup(s), freed 123.45 MB
[2024-02-14 02:00:31] - INFO - Backup process completed: 2 successful, 0 failed
```

## 🐛 Troubleshooting

### Issue: "mysqldump not found"

**Solution:**
```bash
# Install MySQL client
sudo apt-get install mysql-client  # Debian/Ubuntu
sudo yum install mysql             # CentOS/RHEL
```

### Issue: "Access denied for user"

**Solution:** Check backup user permissions:
```sql
SHOW GRANTS FOR 'backup_user'@'localhost';
```

### Issue: Backups too large

**Solutions:**
- Exclude temporary files
- Increase retention only for specific backups
- Use external storage (NAS, S3, etc.)

### Issue: Compression failure

**Solution:** Check available disk space:
```bash
df -h
```

## 🎯 Use Case Examples

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
            "name": "shop",
            "path": "/var/www/html/prestashop",
            "enabled": true
        }
    ],
    "databases": [
        {
            "name": "shop_db",
            "type": "mysql",
            "database": "prestashop_prod",
            "enabled": true
        }
    ],
    "retention_days": 14
}
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the project
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🌐 About SimpleHeberg

SimpleBackup is developed and maintained by **[SimpleHeberg](https://simpleheberg.fr)**, your all-in-one web hosting solution.

### Our Services
- Professional web hosting
- Website creation
- Maintenance and technical support
- Custom solutions

**Need hosting?** Contact us at [simpleheberg.fr](https://simpleheberg.fr)

---

**Developed with ❤️ by SimpleHeberg** | [Website](https://simpleheberg.fr) | [Support](mailto:contact@simpleheberg.fr)
