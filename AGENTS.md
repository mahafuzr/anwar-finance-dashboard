# AGENTS.md — Anwar Finance Dashboard

Local-only financial dashboard for Anwar Group (AGL / AIL / ACL SBUs). Plain HTML/CSS/JS frontend + stdlib-only Python server, now with multi-user authentication and role/SBU-based access control.

## How to run

```powershell
# from C:\Users\GO\Anwar-Finance-Dashboard
python server.py            # opens browser automatically
python server.py --no-browser
```

- Serves `dist/` at `http://127.0.0.1:8765/` (LAN: `http://172.17.18.8:8765/`).
- Binds `0.0.0.0:8765` (all interfaces). Keep terminal open; Ctrl+C stops.
- No npm, no build step. Restart is needed only for `server.py` changes; frontend changes just need a hard refresh (`Ctrl+Shift+R`) — but the browser aggressively caches JS, so a hard reload is often required after editing.

## File map

| File | Role |
|------|------|
| `server.py` | Stdlib-only HTTP server + JSON API. Auth (SQLite), simulated→real Gmail email, role/SBU endpoints. **Source of truth for backend.** |
| `dist/index.html` | App shell: `<style>` block, auth screen, app shell, dialogs (upload review, evidence, **editUserDialog**), user-menu header. |
| `dist/theme.css` | **Design override layer** loaded last. Navy/blue palette (`--navy:#003060`, `--blue:#2070d0`), Inter font, status flags, auth + admin styles. |
| `dist/reference.css` | Original base styles (sidebar, tables, cards, charts). |
| `dist/app.js` | Core render/bind/helpers. Builds nav from `views`. |
| `dist/multi.js` | Multi-SBU portfolio, upload/progress meters, IndexedDB persistence. |
| `dist/auth.js` | **Auth + admin panel + access control.** Loaded last. Sign-in/reset UI, admin panel (add user/role/SBU, active-users table with Edit/Resend/Delete), SBU/role-based menu gating. |
| `dist/upload.js` | Data upload view + revised template converters. |
| other `dist/*.js` | Feature modules (drivers, economics, pricing, review-menus, etc.) — do not break their script load order in `index.html`. |
| `users.db` | SQLite: users, sessions, reset_tokens, roles, sbus. |
| `outbox.log` | Audit trail of every email (simulated + real). |
| `smtp_config.json` | Gmail SMTP credentials (real email delivery). |
| `server_config.json` | `base_url` for reset links (must match how users reach the app). |
| `cloudflared.exe` | Downloaded but **blocked** by network (port 7844). |
| `START-DASHBOARD.bat` | Windows launcher. |

## Authentication system

- Sign-in gate: app hidden until `/api/me` returns a session. Reset links (`#reset?token=…`) always take priority and show the set-password screen even when logged in.
- Sessions: HttpOnly cookie `anwar_session`, 7-day expiry, PBKDF2-hashed passwords.
- Passwords are stored **both hashed (`password_hash`) and plaintext (`password_plain`)** so admin can always recover credentials — deliberately requested tradeoff.
- Email: real Gmail SMTP via `smtp_config.json` (App Password). Falls back to `outbox.log` if not configured. Every email is logged to `outbox.log`.

### Default / known accounts (plaintext in `users.db`)

| Email | Role | Password | SBU |
|-------|------|----------|-----|
| `admin@anwargroup.com` | admin | `Admin@12345` | all |
| `mahafuzr@gmail.com` | admin | `admin@4321` | all |
| `mahafuzr.rahman@anwargroup.com` | hod | `Hod@12345` | (varies) |

## Roles & access control

- Roles are **dynamic** (`roles` table, seeded with `admin`/`group_executive`; more can be added from the admin panel). Only `admin` has full access + the Admin menu.
- `sbus` table (seeded AGL/AIL/ACL) drives the "Data access (SBU)" field.
- Access control in `dist/auth.js` `applyAccessControl()`: non-admins have the Admin nav item **removed** and the SBU dropdown restricted to their assigned SBU; `#admin` hash is auto-redirected for non-admins.

## Admin panel (in-app)

Sections: Add a user (Name/Email/Role/Data-access-SBU/Password optional), Active users table (Edit / Resend reset link / Delete, shows plaintext password), Add new role, Add new SBU. Admin view hides the finance toolbar/footer/SBU strip.

## Publishing / network

- **Same Wi-Fi**: already works at `http://172.17.18.8:8765/`.
- **Cloudflare Tunnel**: blocked by this network (outbound port 7844 to `region.v2.argotunnel.com` fails; `api.cloudflare.com:443` works).
- **Port-forward plan**: public IP `115.127.82.117`, LAN `172.17.18.8`, router `172.17.18.1`, port `8765`. Needs (1) Windows Firewall inbound rule for TCP 8765 (admin), (2) router port-forward 8765→172.17.18.8, (3) set `server_config.json` `base_url` to `http://115.127.82.117:8765`, (4) test from another network. Note: IP may be dynamic/CGNAT; if unreachable from outside, port-forward won't work.

## Conventions / gotchas

- Currency BDT; comma-formatted; blank ≠ zero.
- JS is served with `Cache-Control: no-store`, but browsers still cache hard — hard-refresh after edits.
- `server.py` needs restart after backend changes.
- Email App Password is `fxcbcqqgyhtvhmck` for `mahafuzr@gmail.com` (stored in `smtp_config.json`).
- Do not break script order in `index.html`; `auth.js` must load last.
