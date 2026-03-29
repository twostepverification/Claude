import os
import random
import datetime
import discord
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if not TOKEN:
    print("ERROR: Set the DISCORD_BOT_TOKEN environment variable.")
    print("  export DISCORD_BOT_TOKEN='your-token-here'")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ── Events ───────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Connected to {len(bot.guilds)} server(s)")
    await bot.change_presence(activity=discord.Game(name="!help for commands"))


@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}! Type `!help` to see what I can do.")


# ── Help ─────────────────────────────────────────────────────────────

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Bot Commands",
        description="Here's everything I can do:",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="!hello", value="I'll greet you back", inline=False)
    embed.add_field(name="!ask <question>", value="Ask me anything and I'll respond", inline=False)
    embed.add_field(name="!flip", value="Flip a coin", inline=False)
    embed.add_field(name="!roll [sides]", value="Roll a die (default 6 sides)", inline=False)
    embed.add_field(name="!pick <option1> | <option2> | ...", value="I'll pick one for you", inline=False)
    embed.add_field(name="!poll <question> | <opt1> | <opt2> ...", value="Create a reaction poll (up to 9 options)", inline=False)
    embed.add_field(name="!remind <seconds> <message>", value="Set a reminder", inline=False)
    embed.add_field(name="!info", value="Server info", inline=False)
    embed.add_field(name="!avatar [@user]", value="Show someone's avatar", inline=False)
    embed.set_footer(text="I also reply when you mention me!")
    await ctx.send(embed=embed)


# ── Conversational ───────────────────────────────────────────────────

GREETINGS = [
    "Hey {user}! What's good?",
    "Hello {user}! Great to see you.",
    "Yo {user}! How's it going?",
    "What's up {user}! Ready to chat?",
    "Hi there {user}!",
]

RESPONSES = {
    "how are you": "I'm doing great, thanks for asking! How about you?",
    "what can you do": "Type `!help` to see all my commands!",
    "who are you": "I'm your friendly server bot! I'm here to chat and help out.",
    "thank": "You're welcome! Happy to help.",
    "good morning": "Good morning! Hope you have an awesome day!",
    "good night": "Good night! Sleep well and see you tomorrow!",
    "bye": "See you later! Don't be a stranger.",
}

FALLBACK_REPLIES = [
    "That's interesting! Tell me more.",
    "Hmm, I'll have to think about that one.",
    "I hear you! What else is on your mind?",
    "Good point! Anything else you wanna talk about?",
    "That's a great question. I'm not sure, but I appreciate you asking!",
    "I'm just a bot, but I'm doing my best! Try `!help` for things I can definitely do.",
]


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(random.choice(GREETINGS).format(user=ctx.author.display_name))


@bot.command(name="ask")
async def ask(ctx, *, question: str = None):
    if not question:
        await ctx.send("You gotta ask me something! Usage: `!ask <your question>`")
        return

    lower = question.lower()
    for keyword, reply in RESPONSES.items():
        if keyword in lower:
            await ctx.send(reply)
            return

    await ctx.send(random.choice(FALLBACK_REPLIES))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Reply when mentioned
    if bot.user in message.mentions:
        content = message.content.lower()
        for keyword, reply in RESPONSES.items():
            if keyword in content:
                await message.reply(reply)
                await bot.process_commands(message)
                return
        await message.reply(
            f"Hey {message.author.display_name}! You called? Type `!help` to see what I can do."
        )

    await bot.process_commands(message)


# ── Fun ──────────────────────────────────────────────────────────────

@bot.command(name="flip")
async def flip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"🪙 **{result}!**")


@bot.command(name="roll")
async def roll(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("A die needs at least 2 sides!")
        return
    result = random.randint(1, sides)
    await ctx.send(f"🎲 You rolled a **{result}** (d{sides})")


@bot.command(name="pick")
async def pick(ctx, *, choices: str = None):
    if not choices or "|" not in choices:
        await ctx.send("Give me options separated by `|`\nExample: `!pick pizza | tacos | sushi`")
        return
    options = [c.strip() for c in choices.split("|") if c.strip()]
    if len(options) < 2:
        await ctx.send("I need at least 2 options to pick from!")
        return
    await ctx.send(f"I pick... **{random.choice(options)}**!")


# ── Poll ─────────────────────────────────────────────────────────────

NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]


@bot.command(name="poll")
async def poll(ctx, *, content: str = None):
    if not content or "|" not in content:
        await ctx.send("Usage: `!poll Question? | Option 1 | Option 2 | ...`")
        return

    parts = [p.strip() for p in content.split("|")]
    question = parts[0]
    options = parts[1:]

    if len(options) < 2:
        await ctx.send("I need at least 2 options for a poll!")
        return
    if len(options) > 9:
        await ctx.send("Max 9 options for a poll!")
        return

    description = "\n".join(f"{NUMBER_EMOJIS[i]} {opt}" for i, opt in enumerate(options))
    embed = discord.Embed(
        title=f"📊 {question}",
        description=description,
        color=discord.Color.gold(),
    )
    embed.set_footer(text=f"Poll by {ctx.author.display_name}")

    msg = await ctx.send(embed=embed)
    for i in range(len(options)):
        await msg.add_reaction(NUMBER_EMOJIS[i])


# ── Remind ───────────────────────────────────────────────────────────

@bot.command(name="remind")
async def remind(ctx, seconds: int = None, *, message: str = None):
    if seconds is None or message is None:
        await ctx.send("Usage: `!remind <seconds> <message>`\nExample: `!remind 60 Take a break`")
        return
    if seconds < 1 or seconds > 86400:
        await ctx.send("Reminder must be between 1 second and 24 hours (86400s).")
        return

    await ctx.send(f"Got it! I'll remind you in {seconds}s.")

    import asyncio
    await asyncio.sleep(seconds)
    await ctx.send(f"⏰ {ctx.author.mention} Reminder: **{message}**")


# ── Info / Utility ───────────────────────────────────────────────────

@bot.command(name="info")
async def info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, color=discord.Color.green())
    embed.add_field(name="Owner", value=str(guild.owner), inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


@bot.command(name="avatar")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=discord.Color.purple())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


# ── Run ──────────────────────────────────────────────────────────────

bot.run(TOKEN)
