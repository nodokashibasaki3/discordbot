## Discord Bot for HBP 2026

### Functionality
- Reads cabin assignments from a Google Form (exported to Google Sheets → CSV)
- Matches a user's Discord username to their row
- Assigns the corresponding cabin role and gates access to that cabin’s chat channel
- For leaders: ensures a global `Leader` role and a private `leaders-hub` channel

### How It Works?
1. Hacker completes the Google Form
2. Responses go to Google Sheets
3. The sheet is exposed as a CSV (public or tokenized link)
4. The bot fetches the CSV (`CSV_URL`) and builds a username → {cabin, role} map
5. User runs `/assign_me`
6. Bot assigns the cabin role, ensures the cabin channel exists, and (if leader) grants access to `leaders-hub`
7. Bot replies ephemerally with links to the relevant channels

### Environment Variables
- `TOKEN` – Discord bot token
- `CSV_URL` – Public CSV URL of the Google Sheet

### Permissions and Intents (Discord Developer Portal)
- Scopes: `bot`, `applications.commands`
- Bot Permissions (recommended):
  - Manage Roles
  - Manage Channels
  - View Channels
  - Send Messages
- Gateway Intents:
  - Server Members (enable in the portal)
- In `bot.py`: `Intents.default()` with `guilds=True`, `members=True`

### Limitations (CSV Requirements)
- Must include headers:
  - `Discord Username` (exact Discord username, case-insensitive match)
  - `Cabin` (must match an existing role name in the server)
  - `Role` (`leader` or `member`)
- Google Sheets → File → Share/Publish (CSV) or use `export?format=csv` link
- Keep header names stable to avoid breaking the parser

### Local Development & Testing
1. Create a test Discord server (guild) and invite the bot with the permissions above
2. Create cabin roles (e.g., `Red`, `Blue`) that match CSV `Cabin` values
3. Prepare a minimal test CSV and host it (Google Sheets CSV link or local file served via `python -m http.server`)
4. Provide env vars:

``` terminal
export TOKEN={bot_token}
export CSV_URL={link_to_csv} ## sorry kind of lazy to get this rn.
```

5. You might have to install dependencies:

``` terminal
pip install -r requirements.txt
```

6. Run `python bot.py`
7. In your test server, run `/assign_me`

