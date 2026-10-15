# Anwar Group Finance Dashboard — local project

## Start on your Windows laptop

1. Download the project ZIP and right-click **Extract All**. Do not run it from inside the ZIP.
2. Place the extracted `Anwar-Finance-Dashboard` folder somewhere convenient, such as Documents.
3. Install Python 3.9 or later if it is not already installed. Use the official Python installer and select **Add Python to PATH**. No additional Python packages are required.
4. Double-click **START-DASHBOARD.bat**. A terminal window starts the app and opens your browser.
5. If the browser does not open, visit **http://127.0.0.1:8765/** in current Microsoft Edge or Chrome.
6. Keep the terminal open while using the app. Press **Ctrl+C** in that window to stop it.

Do not open `dist/index.html` directly: the application loads its JSON datasets through the local server.

## Included functionality

The source snapshot matches the dashboard updated on 15 October 2026, commit `33cee7a168e1236ddccf8cceed3ea259031fa9cf`. Its layout, financial calculations, controls and existing source datasets are preserved.

- Performance overview and Board review
- AI insights using existing deterministic financial rules
- Profit drivers and comparison analytics
- Product economics
- Break-even & targets
- Profit & cash quality
- Departments and Target vs achievement
- Cost analysis and Cash & working capital
- What-If planning and Statement detail
- Expanded SBU comparison
- Financial reconciliation
- Data Upload with multiple-file imports and eight blank Excel templates

Includes AGL, AIL and ACL source snapshots, SBU switching, year/month/rolling filters, chart focus/tooltips, source evidence, table search/sorting and exports. Missing values remain blank. No external AI service or API key is configured.

## Uploading and retaining data

Open **Data Upload**, select the destination SBU and segment, choose one or more XLSX files, review the detected worksheets and import. Each imported SBU/segment replaces that segment's dataset; include all periods you want retained. Other SBUs and segments remain unchanged.

Uploads and planning assumptions are saved in this browser profile on this laptop. They are not written back into the bundled JSON or Excel files and do not sync to the hosted dashboard or other devices. Keep using the same browser profile and exact address `http://127.0.0.1:8765/`. Using localhost, a different port, another browser or private browsing creates separate browser storage. Clearing site data removes browser-saved uploads and plans. Retain your original Excel files as backups; CSV exports are not complete application backups.

Refresh reloads saved browser data and recalculates. Upload a revised workbook to change financial figures. This package contains the bundled source snapshot, not any additional browser-only uploads made on the hosted site after that snapshot.

## Local operation

The server binds only to your laptop's loopback address. It does not publish the dashboard or make it available to colleagues. No cloud login is required for this local copy. Anyone with access to the extracted files or your browser profile can access the included data.

After Python is installed, the dashboard assets and current rule-based insights work without internet access. Optional generative AI would require a separate server-side integration and internet access; do not place API keys in browser files.

## Developer commands and structure

Run `python server.py` from the project directory, or `python server.py --no-browser` to start without opening a browser. On macOS/Linux use `python3 server.py`.

- `dist/`: complete editable frontend, source JSON and templates.
- `server.py`: dependency-free local static server.
- `START-DASHBOARD.bat`: Windows launcher.
- `PROJECT-SPECIFICATION.md`: dashboard build and analysis specification exported from the saved skill.

No npm install, database service or build step is needed. Preserve the script order in `dist/index.html`: later modules override earlier definitions. Restarting the server is unnecessary for most frontend changes; refresh the page.

## Troubleshooting and verification

- **Python not found:** install Python, enable PATH and reopen the launcher.
- **Port in use:** check whether this app is already running. Reuse the existing window or close the other program on port 8765. Do not change ports casually because browser data is origin-specific.
- **Missing files:** extract the whole ZIP, keeping `dist` alongside `server.py`.
- **Blank historical figures:** the source may contain Budget but no Actual values; these are intentionally not relabelled.
- **Excel import fails:** use the supplied templates, correct SBU/segment and cached Excel values. Preserve identifiers, dates and headers.

Package checks cover copied-source equality, asset/JSON integrity, JavaScript syntax and Python syntax. Windows launcher execution and visual browser testing must still be confirmed on your laptop.
