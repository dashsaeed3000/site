Here’s a structured README summarizing all the issues you faced, the errors, and how to resolve them. I’ve organized it step by step for clarity.

---

# README — Flask + Gunicorn Deployment Issues and Solutions

## 1. Gunicorn “Address already in use”

**Error:**

```
[ERROR] Connection in use: ('0.0.0.0', 5000)
[Errno 98] Address already in use
```

**Cause:**
Another Gunicorn process is already running and listening on the port.

**Solution:**

```
lsof -i :5000        # Find processes using port 5000
pkill -f gunicorn    # Kill all existing Gunicorn processes
```

---

## 2. Service fails with `status=203/EXEC`

**Error:**

```
Main PID: XXXX (code=exited, status=203/EXEC)
```

**Cause:**
systemd cannot execute the binary because the path is incorrect or the file is missing.

**Solution:**

1. Verify Gunicorn path inside your virtual environment:

```
ls -l ~/site/venv/bin/gunicorn
```

2. Update `/etc/systemd/system/site.service` to use the correct path:

```
WorkingDirectory=/root/site
Environment="PATH=/root/site/venv/bin"
ExecStart=/root/site/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

3. Reload systemd and restart:

```
systemctl daemon-reload
systemctl restart site
```

---

## 3. Gunicorn cannot find Flask app

**Error:**

```
Failed to find attribute 'app' in 'app'
```

**Cause:**
The module path or Flask instance name in `ExecStart` is incorrect.

**Solution:**

* If your Flask instance is in `app/main.py`:

```
ExecStart=/root/site/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

* If your Flask app uses a factory function `create_app()`:

```
ExecStart=/root/site/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "app.main:create_app()"
```

---

## 4. MySQL access denied

**Error:**

```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1698, "Access denied for user 'root'@'localhost'")
```

**Cause:**

* Using `root` for app database access.
* Default MySQL root user on Ubuntu uses `unix_socket` authentication.
* Your app cannot login with a password.

**Solution (recommended):**

1. Create a dedicated database user:

```sql
CREATE DATABASE maten;
CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'saeid1378';
GRANT ALL PRIVILEGES ON maten.* TO 'webuser'@'localhost';
FLUSH PRIVILEGES;
```

2. Update `.env`:

```
DB_URI=mysql+pymysql://webuser:saeid1378@localhost:3306/maten
```

---

## 5. MySQL `caching_sha2_password` authentication requires `cryptography`

**Error:**

```
RuntimeError: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
```

**Cause:**
PyMySQL cannot handle MySQL 8’s default `caching_sha2_password` without `cryptography`.

**Solution 1 — Install cryptography:**

```
source ~/site/venv/bin/activate
pip install cryptography
```

**Solution 2 — Change MySQL user to use `mysql_native_password`:**

```sql
ALTER USER 'webuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'saeid1378';
FLUSH PRIVILEGES;
```

---

## 6. Systemd service file example (corrected)

```ini
[Unit]
Description=Flask App (Python 3.10)
After=network.target

[Service]
User=root
WorkingDirectory=/root/site
Environment="PATH=/root/site/venv/bin"
EnvironmentFile=/root/site/.env
ExecStart=/root/site/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Commands to reload and enable:**

```
systemctl daemon-reload
systemctl restart site
systemctl enable site
systemctl status site -l
lsof -i :5000
```

---

## 7. Checklist for Flask + Gunicorn deployment on Ubuntu

1. Install Python 3.10 and virtual environment.
2. Clone project from GitHub.
3. Create venv and install dependencies:

```
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Install Gunicorn in venv:

```
pip install gunicorn
```

5. Configure `.env` with a proper DB user.
6. Test app manually:

```
python -m app.main
```

7. Configure systemd service.
8. Reload, start, and check status.
9. Ensure port 5000 is free and Gunicorn is listening.

---

This README documents all the errors you encountered, their causes, and the fixes in order.

---

I can also make a **short “one-command setup script”** for this deployment that handles venv, Gunicorn, MySQL user, and systemd if you want. Do you want me to do that?
