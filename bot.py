import os
import discord
from discord.ext import commands
from datetime import timedelta
from groq import Groq

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

# Intents nécessaires pour lire les membres et le contenu des messages
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"KAILO est en ligne ! Connecté en tant que {bot.user}")

# --- IA GROQ ---
@bot.command()
async def ia(ctx, *, prompt: str):
    async with ctx.typing():
        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Tu es KAILO, un système d'IA autonome, futuriste, rapide et efficace."},
                    {"role": "user", "content": prompt}
                ],
            )
            response = completion.choices[0].message.content
            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"Erreur IA : {e}")

# --- PROTECTION AUTOMATIQUE (Anti-Spam / Anti-Mention) ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Sécurité : Limite les mentions abusives (@everyone / @here)
    if len(message.mentions) > 5:
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, les mentions de masse sont interdites !", delete_after=5)
        return

    await bot.process_commands(message)

# --- COMMANDES DE MODÉRATION & PROTECTION ---
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **{member.name}** a été banni. Raison : {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 **{member.name}** a été expulsé. Raison : {reason}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int = 10, *, reason: str = "Aucune raison"):
    duration = timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"🤫 **{member.name}** est rendu muet pour {minutes} minutes.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 **{member.name}** n'est plus muet.")

# --- PROFIL INFO ---
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles[1:]] or ["Aucun"]
    created_at = member.created_at.strftime("%d/%m/%Y à %H:%M")
    joined_at = member.joined_at.strftime("%d/%m/%Y à %H:%M") if member.joined_at else "Inconnue"

    embed = discord.Embed(title=f"Profil de {member.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Compte créé le", value=created_at, inline=False)
    embed.add_field(name="📥 Rejoint le", value=joined_at, inline=False)
    embed.add_field(name="🎭 Rôles", value=", ".join(roles), inline=False)
    
    await ctx.send(embed=embed)

# --- GESTION DES ERREURS ---
@ban.error
@kick.error
@mute.error
async def mod_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ Tu n'as pas la permission d'exécuter cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Mentionne un membre valide. Exemple : `!mute @membre 10 raison`")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
