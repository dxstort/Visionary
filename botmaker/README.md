# Bot Maker (DeepSeek powered)

Discord bot: `/process` describes a bot, DeepSeek writes the code, you get `src.zip` + raw output.

## Setup

1. https://discord.com/developers/applications → New Application → **Bot** tab → **Reset Token** → copy it.
2. **OAuth2 → URL Generator**: scopes `bot` + `applications.commands`; permissions Send Messages, Attach Files, Embed Links. Open the URL, invite to your server.
3. DeepSeek key: https://platform.deepseek.com → API Keys (needs credit).
4. Copy `.env.example` to `.env` and fill in both keys.

```
pip install -r requirements.txt
python main.py
```

When it prints `Slash commands synced`, use `/process prompt: make a moderation bot with warn/kick/ban`.
First-time slash commands can take a minute to appear.

If you get "model not found", change `DEEPSEEK_MODEL` in `.env` to a model your DeepSeek account lists.

Never share or commit your `.env`.
