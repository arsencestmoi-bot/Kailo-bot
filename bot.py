import os
import discord
from discord.ext import commands
from groq import Groq

# Token et clé API récupérés depuis les variables d'environnement
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialisation du client Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# Configuration des intents Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Kailo est en ligne ! Connecté en tant que {bot.user}")

# Commande Ping
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong ! {round(bot.latency * 1000)}ms")

# Commande IA (!ia <question>)
@bot.command()
async def ia(ctx, *, prompt: str):
    async with ctx.typing():
        try:
            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "Tu es Kailo, un assistant amical et efficace sur Discord."},
                    {"role": "user", "content": prompt}
                ],
            )
            response = completion.choices[0].message.content
            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"Erreur avec l'IA : {e}")

# Lancement du bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
