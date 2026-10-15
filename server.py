"""Local-only dashboard server with user authentication.

Requires Python 3.9+; stdlib only (sqlite3, hashlib, secrets, http.server).
Serves the static dashboard from dist/ and provides a small JSON API for
sign-in, user administration, and password resets.

Email is SIMULATED: messages are appended to outbox.log (and printed to the
console) instead of being sent via SMTP.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import secrets
import sqlite3
import smtplib
import threading
import webbrowser
import sys
import hashlib
import hmac
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
import os
import socket

ROOT = Path(__file__).resolve().parent / 'dist'
DB_PATH = Path(os.environ.get('DB_PATH', str(Path(__file__).resolve().parent / 'users.db')))
OUTBOX = Path(os.environ.get('OUTBOX_PATH', str(Path(__file__).resolve().parent / 'outbox.log')))
SMTP_CONFIG_PATH = Path(__file__).resolve().parent / 'smtp_config.json'
CONFIG_PATH = Path(__file__).resolve().parent / 'server_config.json'
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', '8765'))
COOKIE_NAME = 'anwar_session'
PBKDF2_ROUNDS = 100_000
SESSION_DAYS = 7
RESET_HOURS = 24

ROLES = {'admin': 'Administrator', 'group_executive': 'Group Executive'}
DEFAULT_SBUS = [
    ('Anwar Galvanizing Limited', 'AGL'),
    ('Anwar Ispat Limited', 'AIL'),
    ('Anwar Cement Limited', 'ACL'),
]


# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
def _now():
    return datetime.now(timezone.utc).isoformat()


def db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            sbu TEXT,
            password_hash TEXT,
            password_plain TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reset_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS roles (
            key TEXT PRIMARY KEY,
            label TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sbus (
            name TEXT PRIMARY KEY,
            code TEXT
        );
        """
    )
    # Migration: add the sbu column to pre-existing databases.
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if 'sbu' not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN sbu TEXT")
    if 'password_plain' not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_plain TEXT")
    # Seed default roles and SBUs.
    for key, label in ROLES.items():
        conn.execute("INSERT OR IGNORE INTO roles (key, label) VALUES (?, ?)", (key, label))
    for name, code in DEFAULT_SBUS:
        conn.execute("INSERT OR IGNORE INTO sbus (name, code) VALUES (?, ?)", (name, code))
    conn.commit()
    # Seed a default admin on first run (no password set until reset).
    cur = conn.execute("SELECT COUNT(*) AS n FROM users")
    if cur.fetchone()['n'] == 0:
        conn.execute(
            "INSERT INTO users (name, email, role, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ('Administrator', 'admin@anwargroup.com', 'admin', _now(), _now()),
        )
        conn.commit()
        link = issue_reset_token(conn, 'admin@anwargroup.com')
        if link:
            conn.commit()
            _send_email(conn, 'admin@anwargroup.com', 'Initial administrator account', link)
    conn.close()


# --------------------------------------------------------------------------
# Password hashing
# --------------------------------------------------------------------------
def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), PBKDF2_ROUNDS)
    return f"{salt}${digest.hex()}"


def _verify_password(password, stored):
    if not stored:
        return False
    salt, _, _ = stored.partition('$')
    candidate = _hash_password(password, salt)
    return hmac.compare_digest(candidate, stored)


# --------------------------------------------------------------------------
# Email delivery
# --------------------------------------------------------------------------
def _load_smtp_config():
    cfg = {}
    if SMTP_CONFIG_PATH.is_file():
        try:
            cfg = json.loads(SMTP_CONFIG_PATH.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            cfg = {}
    # Environment variables take precedence (used on cloud hosts).
    if os.environ.get('SMTP_HOST'):
        cfg['host'] = os.environ['SMTP_HOST']
    if os.environ.get('SMTP_PORT'):
        cfg['port'] = int(os.environ['SMTP_PORT'])
    if os.environ.get('SMTP_USERNAME'):
        cfg['username'] = os.environ['SMTP_USERNAME']
    if os.environ.get('SMTP_PASSWORD'):
        cfg['password'] = os.environ['SMTP_PASSWORD']
    return cfg


def _smtp_configured():
    cfg = _load_smtp_config()
    return bool(cfg.get('host') and cfg.get('username') and cfg.get('password'))


def _send_email(conn, email, subject, reset_link):
    user = conn.execute("SELECT name, email FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return
    body = (
        f"Hello {user['name']},\n\n"
        f"An account has been created for you on the Anwar Group Finance Dashboard.\n\n"
        f"To set your password, open the following link within {RESET_HOURS} hours:\n"
        f"{reset_link}\n\n"
        f"If you did not expect this, you can ignore this message.\n"
    )
    # Always log to outbox (audit trail).
    record = (
        f"===== EMAIL =====\n"
        f"To: {user['name']} <{user['email']}>\n"
        f"Subject: {subject}\n"
        f"-----\n{body}\n"
        f"===== END =====\n\n"
    )
    with open(OUTBOX, 'a', encoding='utf-8') as fh:
        fh.write(record)

    # Attempt real SMTP delivery when configured.
    cfg = _load_smtp_config()
    if not _smtp_configured():
        print(f"\n[email:simulated] To {user['email']} — {subject}\n{reset_link}\n")
        return
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = cfg.get('username')
        msg['To'] = user['email']
        msg.set_content(body)
        host = cfg.get('host', 'smtp.gmail.com')
        port = int(cfg.get('port', 587))
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(cfg['username'], cfg['password'])
            server.send_message(msg)
        print(f"\n[email:sent] To {user['email']} — {subject}")
    except Exception as exc:  # noqa: BLE001
        print(f"\n[email:FAILED] To {user['email']} — {exc}. Reset link: {reset_link}\n")


def _issue_reset_link(email):
    conn = db()
    try:
        link = issue_reset_token(conn, email)
        conn.commit()
        return link
    finally:
        conn.close()


def issue_reset_token(conn, email):
    user = conn.execute("SELECT id, name, email FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=RESET_HOURS)
    conn.execute(
        "INSERT INTO reset_tokens (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token, user['id'], _now(), expires.isoformat()),
    )
    return f"{base_url()}/#reset?token={token}"


def base_url():
    """Return the externally-reachable base URL for reset links.

    Priority:
      1. BASE_URL environment variable (used on cloud hosts)
      2. server_config.json ``base_url`` (e.g. http://192.168.1.10:8765)
      3. Auto-detect the LAN IP of this machine.
    """
    env = (os.environ.get('BASE_URL') or '').strip().rstrip('/')
    if env:
        return env
    if CONFIG_PATH.is_file():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
            value = (cfg.get('base_url') or '').strip().rstrip('/')
            if value:
                return value
        except (ValueError, OSError):
            pass
    return f"http://{detect_lan_ip()}:{PORT}"


def detect_lan_ip():
    """Best-effort detection of the machine's LAN IP address."""
    candidates = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            candidates.append(s.getsockname()[0])
        finally:
            s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip and not ip.startswith('127.') and ip not in candidates:
                candidates.append(ip)
    except OSError:
        pass
    return candidates[0] if candidates else '127.0.0.1'


# --------------------------------------------------------------------------
# Sessions
# --------------------------------------------------------------------------
def create_session(conn, user_id):
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    conn.execute(
        "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token, user_id, _now(), expires.isoformat()),
    )
    return token


def user_for_token(token):
    if not token:
        return None
    conn = db()
    try:
        conn.execute(
            "DELETE FROM sessions WHERE expires_at < ?", (_now(),)
        )
        row = conn.execute(
            "SELECT u.id, u.name, u.email, u.role, u.sbu FROM sessions s "
            "JOIN users u ON u.id = s.user_id WHERE s.token = ?", (token,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_session(token):
    conn = db()
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()


def list_roles():
    conn = db()
    try:
        rows = conn.execute("SELECT key, label FROM roles ORDER BY label").fetchall()
        return [{'key': r['key'], 'label': r['label']} for r in rows]
    finally:
        conn.close()


def list_sbus():
    conn = db()
    try:
        rows = conn.execute("SELECT name, code FROM sbus ORDER BY name").fetchall()
        return [{'name': r['name'], 'code': r['code']} for r in rows]
    finally:
        conn.close()


# --------------------------------------------------------------------------
# HTTP handler
# --------------------------------------------------------------------------
class DashboardHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def list_directory(self, path):
        self.send_error(403, 'Directory listing disabled')
        return None

    # ----- helpers -----
    def _cookie(self):
        raw = self.headers.get('Cookie', '')
        for part in raw.split(';'):
            part = part.strip()
            if part.startswith(COOKIE_NAME + '='):
                return part[len(COOKIE_NAME) + 1:]
        return None

    def _current_user(self):
        return user_for_token(self._cookie())

    def _body_json(self):
        length = int(self.headers.get('Content-Length', 0) or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return None

    def _json(self, payload, status=200):
        data = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_cookie(self, payload, status, cookie_token=None):
        data = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        if cookie_token is not None:
            self.send_header('Set-Cookie', f"{COOKIE_NAME}={cookie_token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_DAYS*86400}")
        self.end_headers()
        self.wfile.write(data)

    def _error(self, message, status):
        self._json({'error': message}, status)

    def _set_cookie(self, token, max_age_days=SESSION_DAYS):
        self.send_header('Set-Cookie', f"{COOKIE_NAME}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age_days*86400}")

    def _clear_cookie(self):
        self.send_header('Set-Cookie', f"{COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")

    # ----- API dispatch -----
    def do_POST(self):
        path = self.path.split('?', 1)[0]
        try:
            if path == '/api/login':
                self.api_login()
            elif path == '/api/logout':
                self.api_logout()
            elif path == '/api/reset':
                self.api_reset_password()
            elif path == '/api/users':
                self.api_create_user()
            elif path == '/api/roles':
                self.api_create_role()
            elif path == '/api/sbus':
                self.api_create_sbu()
            elif re.fullmatch(r'/api/users/\d+/reset', path):
                self.api_resend_reset(path)
            else:
                self._error('Not found', 404)
        except Exception as exc:  # noqa: BLE001
            self._error(str(exc), 500)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/api/me':
            self.api_me()
        elif path == '/api/users':
            self.api_list_users()
        elif path == '/api/roles':
            self.api_list_roles()
        elif path == '/api/sbus':
            self.api_list_sbus()
        else:
            # Protect data files: JSON datasets are only served to signed-in users.
            if path.endswith('.json'):
                if not self._current_user():
                    self._error('Not authenticated', 401)
                    return
            super().do_GET()

    def do_DELETE(self):
        path = self.path.split('?', 1)[0]
        if re.fullmatch(r'/api/users/\d+', path):
            self.api_delete_user(path)
        else:
            self._error('Not found', 404)

    def do_PUT(self):
        path = self.path.split('?', 1)[0]
        if re.fullmatch(r'/api/users/\d+', path):
            self.api_update_user(path)
        else:
            self._error('Not found', 404)

    # ----- endpoints -----
    def api_me(self):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        self._json(user)

    def api_login(self):
        body = self._body_json()
        if body is None:
            self._error('Invalid JSON', 400)
            return
        email = (body.get('email') or '').strip().lower()
        password = body.get('password') or ''
        conn = db()
        try:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if not row or not _verify_password(password, row['password_hash']):
                self._error('Invalid email or password', 401)
                return
            if not row['password_hash']:
                self._error('Account has no password yet. Use the reset link sent by email.', 403)
                return
            token = create_session(conn, row['id'])
            conn.commit()
            self._json_cookie({'id': row['id'], 'name': row['name'], 'email': row['email'], 'role': row['role'], 'sbu': row['sbu']}, 200, token)
        finally:
            conn.close()

    def api_logout(self):
        token = self._cookie()
        if token:
            delete_session(token)
        data = json.dumps({'ok': True}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self._clear_cookie()
        self.end_headers()
        self.wfile.write(data)

    def api_reset_password(self):
        body = self._body_json()
        if body is None:
            self._error('Invalid JSON', 400)
            return
        token = body.get('token') or ''
        password = body.get('password') or ''
        if len(password) < 8:
            self._error('Password must be at least 8 characters.', 400)
            return
        conn = db()
        try:
            row = conn.execute(
                "SELECT * FROM reset_tokens WHERE token = ? AND used = 0 AND expires_at > ?",
                (token, _now()),
            ).fetchone()
            if not row:
                self._error('Reset link is invalid or has expired.', 400)
                return
            conn.execute(
                "UPDATE users SET password_hash = ?, password_plain = ?, updated_at = ? WHERE id = ?",
                (_hash_password(password), password, _now(), row['user_id']),
            )
            conn.execute("UPDATE reset_tokens SET used = 1 WHERE token = ?", (token,))
            # Invalidate existing sessions for that user.
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (row['user_id'],))
            conn.commit()
            self._json({'ok': True})
        finally:
            conn.close()

    def api_list_users(self):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        if user['role'] != 'admin':
            self._error('Administrator access required', 403)
            return
        conn = db()
        try:
            rows = conn.execute(
                "SELECT id, name, email, role, sbu, created_at, password_plain, "
                "CASE WHEN password_hash IS NULL OR password_hash = '' THEN 0 ELSE 1 END AS has_password "
                "FROM users ORDER BY created_at"
            ).fetchall()
            self._json([{
                'id': r['id'], 'name': r['name'], 'email': r['email'],
                'role': r['role'], 'sbu': r['sbu'], 'created_at': r['created_at'],
                'has_password': bool(r['has_password']),
                'password': r['password_plain'] or '',
            } for r in rows])
        finally:
            conn.close()

    def api_create_user(self):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        if user['role'] != 'admin':
            self._error('Administrator access required', 403)
            return
        body = self._body_json()
        if body is None:
            self._error('Invalid JSON', 400)
            return
        name = (body.get('name') or '').strip()
        email = (body.get('email') or '').strip().lower()
        role = (body.get('role') or '').strip()
        sbu = (body.get('sbu') or '').strip()
        password = (body.get('password') or '').strip()
        if not name:
            self._error('Name is required.', 400)
            return
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
            self._error('A valid email address is required.', 400)
            return
        if password and len(password) < 8:
            self._error('Password must be at least 8 characters.', 400)
            return
        conn = db()
        try:
            valid_roles = [r['key'] for r in conn.execute("SELECT key FROM roles").fetchall()]
            if role not in valid_roles:
                self._error('Unknown role.', 400)
                return
            exists = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
            if exists:
                self._error('A user with that email already exists.', 409)
                return
            now = _now()
            if password:
                cur = conn.execute(
                    "INSERT INTO users (name, email, role, sbu, password_hash, password_plain, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, email, role, sbu or None, _hash_password(password), password, now, now),
                )
                conn.commit()
                new_id = cur.lastrowid
                self._json({'id': new_id, 'name': name, 'email': email, 'role': role, 'sbu': sbu or None}, 201)
            else:
                cur = conn.execute(
                    "INSERT INTO users (name, email, role, sbu, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, role, sbu or None, now, now),
                )
                conn.commit()
                new_id = cur.lastrowid
                link = issue_reset_token(conn, email)
                conn.commit()
                _send_email(conn, email, 'Set your password', link)
                self._json({'id': new_id, 'name': name, 'email': email, 'role': role, 'sbu': sbu or None, 'reset_link': link}, 201)
        finally:
            conn.close()

    def api_resend_reset(self, path):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        if user['role'] != 'admin':
            self._error('Administrator access required', 403)
            return
        m = re.fullmatch(r'/api/users/(\d+)/reset', path)
        user_id = int(m.group(1))
        conn = db()
        try:
            row = conn.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()
            if not row:
                self._error('User not found', 404)
                return
            link = issue_reset_token(conn, row['email'])
            conn.commit()
            _send_email(conn, row['email'], 'Reset your password', link)
            self._json({'ok': True, 'reset_link': link})
        finally:
            conn.close()

    def api_list_roles(self):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        self._json(list_roles())

    def api_list_sbus(self):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        self._json(list_sbus())

    def api_create_role(self):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        if user['role'] != 'admin':
            self._error('Administrator access required', 403)
            return
        body = self._body_json()
        if body is None:
            self._error('Invalid JSON', 400)
            return
        label = (body.get('label') or '').strip()
        if not label:
            self._error('Role label is required.', 400)
            return
        key = re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')
        if not key:
            self._error('Role label must contain at least one letter or number.', 400)
            return
        conn = db()
        try:
            exists = conn.execute("SELECT 1 FROM roles WHERE key = ?", (key,)).fetchone()
            if exists:
                self._error('A role with that name already exists.', 409)
                return
            conn.execute("INSERT INTO roles (key, label) VALUES (?, ?)", (key, label))
            conn.commit()
            self._json({'key': key, 'label': label}, 201)
        finally:
            conn.close()

    def api_create_sbu(self):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        if user['role'] != 'admin':
            self._error('Administrator access required', 403)
            return
        body = self._body_json()
        if body is None:
            self._error('Invalid JSON', 400)
            return
        name = (body.get('name') or '').strip()
        code = (body.get('code') or '').strip().upper()
        if not name:
            self._error('SBU name is required.', 400)
            return
        conn = db()
        try:
            exists = conn.execute("SELECT 1 FROM sbus WHERE name = ?", (name,)).fetchone()
            if exists:
                self._error('An SBU with that name already exists.', 409)
                return
            conn.execute("INSERT INTO sbus (name, code) VALUES (?, ?)", (name, code or None))
            conn.commit()
            self._json({'name': name, 'code': code or None}, 201)
        finally:
            conn.close()

    def api_delete_user(self, path):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        if user['role'] != 'admin':
            self._error('Administrator access required', 403)
            return
        m = re.fullmatch(r'/api/users/(\d+)', path)
        user_id = int(m.group(1))
        if user_id == user['id']:
            self._error('You cannot delete your own account.', 400)
            return
        conn = db()
        try:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM reset_tokens WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            self._json({'ok': True})
        finally:
            conn.close()

    def api_update_user(self, path):
        user = self._current_user()
        if not user:
            self._error('Not authenticated', 401)
            return
        if user['role'] != 'admin':
            self._error('Administrator access required', 403)
            return
        m = re.fullmatch(r'/api/users/(\d+)', path)
        user_id = int(m.group(1))
        body = self._body_json()
        if body is None:
            self._error('Invalid JSON', 400)
            return
        name = (body.get('name') or '').strip()
        email = (body.get('email') or '').strip().lower()
        role = (body.get('role') or '').strip()
        sbu = (body.get('sbu') or '').strip()
        password = (body.get('password') or '').strip()
        if not name:
            self._error('Name is required.', 400)
            return
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
            self._error('A valid email address is required.', 400)
            return
        if password and len(password) < 8:
            self._error('Password must be at least 8 characters.', 400)
            return
        conn = db()
        try:
            valid_roles = [r['key'] for r in conn.execute("SELECT key FROM roles").fetchall()]
            if role not in valid_roles:
                self._error('Unknown role.', 400)
                return
            exists = conn.execute("SELECT 1 FROM users WHERE email = ? AND id != ?", (email, user_id)).fetchone()
            if exists:
                self._error('A user with that email already exists.', 409)
                return
            if password:
                conn.execute(
                    "UPDATE users SET name = ?, email = ?, role = ?, sbu = ?, password_hash = ?, password_plain = ?, updated_at = ? WHERE id = ?",
                    (name, email, role, sbu or None, _hash_password(password), password, _now(), user_id),
                )
            else:
                conn.execute(
                    "UPDATE users SET name = ?, email = ?, role = ?, sbu = ?, updated_at = ? WHERE id = ?",
                    (name, email, role, sbu or None, _now(), user_id),
                )
            conn.commit()
            self._json({'id': user_id, 'name': name, 'email': email, 'role': role, 'sbu': sbu or None})
        finally:
            conn.close()


def main():
    init_db()
    if not (ROOT / 'index.html').is_file():
        print('Missing dist/index.html. Extract the complete ZIP before starting.')
        return 1
    try:
        server = ThreadingHTTPServer((HOST, PORT), partial(DashboardHandler, directory=str(ROOT)))
    except OSError as exc:
        print(f'Cannot start on port {PORT}: {exc}')
        print('If the dashboard is already running, use its existing window.')
        print('Otherwise close the program using port 8765 and try again.')
        return 1
    url = f'http://{HOST}:{PORT}/'
    print(f'Anwar Group Finance Dashboard')
    print(f'  Local:   http://127.0.0.1:{PORT}/')
    print(f'  Network: {base_url()}/')
    print('Keep this window open. Press Ctrl+C to stop.')
    print('Admin account: admin@anwargroup.com (see outbox.log for the password-set link).')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(f'http://127.0.0.1:{PORT}/')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nDashboard stopped.')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
