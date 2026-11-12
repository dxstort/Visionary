import asyncio
import io
import os
import posixpath
import zipfile

import discord
from discord import app_commands
from openai import AsyncOpenAI

try:  # load .env if python-dotenv is installed; plain env vars still work without it
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
REQUEST_TIMEOUT = 180
DISCORD_MSG_LIMIT = 1900  # Discord hard limit is 2000; leave room for a prefix

# Slash commands don't need the privileged message_content intent.
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
client: AsyncOpenAI | None = None

SYSTEM_PROMPT = """You are Super Bot Maker AI. The user will describe a bot they want.
You must generate the COMPLETE, WORKING source code for it - any language, any framework (Python discord.py, discord.js, anything).
Follow these rules strictly:
1. Output ONLY one or more code files, each clearly marked with a header line exactly like:
###FILE: main.py
...code...
Use one header per file. Separate files with a blank line.
2. The code MUST be complete and runnable. Include all imports, config, error handling.
3. Use 'TOKEN_HERE' placeholder for tokens.
4. Never use markdown backticks ``` around code, only the ###FILE: headers.
5. If it's a Discord bot, include slash commands, intents, and a ready event.
6. No extra commentary outside the files, except a one-line summary at the very start starting with [OK].
7. Any command that moderates or changes the server (delete/purge messages, kick, ban, timeout, warn,
   manage roles/channels/nicknames, edit server settings, etc.) MUST require the matching Discord permission:
   - discord.py: add BOTH @app_commands.default_permissions(<perm>=True) and
     @app_commands.checks.has_permissions(<perm>=True), plus @app_commands.guild_only().
   - discord.js: call .setDefaultMemberPermissions(PermissionFlagsBits.<Perm>) and also check
     interaction.memberPermissions.has(...) inside the handler.
   - Handle the missing-permission error with a clear ephemeral reply, e.g. "You need Manage Messages to use this."
     In discord.py this means an @<command>.error handler (or bot.tree.on_error) that catches
     app_commands.MissingPermissions.
   - Also handle the bot itself lacking permission (Forbidden) with a clear message.
   - For actions on members (kick/ban/timeout/role changes), refuse if the target's top role is equal to or
     higher than the invoking user's or the bot's top role, and never act on the server owner or the bot itself.
8. Only request privileged intents (message_content, members, presences) if the bot actually needs them.
   Slash commands, fetching/deleting messages by ID and purging do NOT need message_content; it is only
   needed to read the text of normal messages (prefix commands, auto-mod on message text).
9. Read tokens from an environment variable (e.g. os.getenv("DISCORD_TOKEN")) with 'TOKEN_HERE' as the fallback.
If the request is unclear or impossible, reply with a line starting with [ERROR] and a short reason."""


def safe_filename(name: str) -> str | None:
    """Normalize an AI-supplied path so it can't escape the zip root (no '..', no absolute paths)."""
    name = name.strip().strip("`\"'").replace("\\", "/")
    name = posixpath.normpath(name).lstrip("/")
    if not name or name in (".", "..") or name.startswith("../"):
        return None
    return name


def strip_fences(lines: list[str]) -> list[str]:
    """Drop stray ``` fence lines in case the model ignores rule 4."""
    return [ln for ln in lines if not ln.strip().startswith("```")]


def generate_files(raw: str) -> dict[str, str]:
    files: dict[str, str] = {}
    current: list[str] = []
    current_name: str | None = None

    def flush():
        if current_name and current:
            body = "\n".join(strip_fences(current)).strip("\n")
            if body:
                files[current_name] = body + "\n"

    for line in raw.splitlines():
        if line.startswith("###FILE:"):
            flush()
            current_name = safe_filename(line.split(":", 1)[1])
            current = []
        elif current_name is not None:
            current.append(line)
    flush()
    return files


def make_zip(files: dict[str, str]) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    buf.seek(0)
    return buf


def text_file(text: str, filename: str) -> discord.File:
    return discord.File(io.BytesIO(text.encode("utf-8")), filename=filename)


async def process_prompt(prompt: str) -> dict:
    assert client is not None
    resp = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=8000,
    )
    raw = (resp.choices[0].message.content or "").strip()
    return {"raw": raw, "files": generate_files(raw)}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (discord.py {discord.__version__}) | model: {DEEPSEEK_MODEL}")
    try:
        synced = await tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print("Sync failed:", e)


@tree.command(
    name="process",
    description="Make any bot/code. Describe what you want and it generates src.",
)
@app_commands.describe(
    prompt="Describe the bot or code to build (e.g. 'a moderation discord bot with warn/kick/ban')"
)
async def process(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)

    shown_prompt = prompt if len(prompt) <= 1000 else prompt[:1000] + "..."
    embed = discord.Embed(
        title="Bot Maker",
        description=f"Generating with **{DEEPSEEK_MODEL}**...\n\nPrompt: `{shown_prompt}`",
        color=discord.Color.blurple(),
    )
    await interaction.followup.send(embed=embed)

    try:
        res = await asyncio.wait_for(process_prompt(prompt), timeout=REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        await interaction.followup.send(f"❌ Timed out ({REQUEST_TIMEOUT}s). Try a smaller prompt.")
        return
    except Exception as e:
        await interaction.followup.send(f"❌ API error: {str(e)[:DISCORD_MSG_LIMIT]}")
        return

    raw = res["raw"]
    if not raw:
        await interaction.followup.send("❌ The AI returned an empty response. Try again.")
        return

    if raw.startswith("[ERROR]"):
        await interaction.followup.send(raw[:DISCORD_MSG_LIMIT])
        return

    files = res["files"]
    if not files:
        await interaction.followup.send(
            "❌ No code files found in the AI output. Raw output attached.",
            file=text_file(raw, "raw_output.txt"),
        )
        return

    names = ", ".join(f"`{n}`" for n in files)
    if len(names) > 1500:
        names = names[:1500] + "..."
    embed = discord.Embed(
        title=f"✅ {len(files)} file(s) generated",
        description=(
            f"**Files:** {names}\n\n**How to use:**\n"
            "1. Install deps: `pip install discord.py openai` (or npm deps for JS)\n"
            "2. Replace `TOKEN_HERE` with your token (or use an env var)\n"
            "3. Run the bot\n\n**AI raw output attached too.**"
        ),
        color=discord.Color.green(),
    )
    server = interaction.guild.name if interaction.guild else "DM"
    embed.set_footer(text=f"Generated by {interaction.user}\nServer: {server}")

    await interaction.followup.send(
        embed=embed,
        files=[
            discord.File(make_zip(files), filename="src.zip"),
            text_file(raw, "raw_output.txt"),
        ],
    )


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit("Set DISCORD_TOKEN (env var or .env file).")
    if not DEEPSEEK_API_KEY:
        raise SystemExit("Set DEEPSEEK_API_KEY (env var or .env file).")
    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    bot.run(DISCORD_TOKEN)
