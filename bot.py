import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import logging
import platform
import time
from dotenv import load_dotenv

load_dotenv()
discord.opus.load_opus("libopus.so.0")

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("eclipse")

# ─── Constantes ─────────────────────────────────────────────────────────────
PREFIX = "?"
BOT_START = time.time()
COR = discord.Color.from_rgb(88, 24, 169)  # roxo eclipse

# ─── Intents ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ─── Cargo de moderação ──────────────────────────────────────────────────────
CARGO_MOD_ID = 1480304399044575322

def tem_cargo_mod():
    """Permite o uso apenas para quem tiver o cargo de moderação ou for dono do servidor."""
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            raise commands.CheckFailure("Este comando só pode ser usado em um servidor.")
        ids = [r.id for r in ctx.author.roles]
        if CARGO_MOD_ID in ids or ctx.author.id == ctx.guild.owner_id:
            return True
        raise commands.CheckFailure("🚫 Você não tem o cargo necessário para usar este comando.")
    return commands.check(predicate)


# ════════════════════════════════════════════════════════════════════════════
#  EVENTOS
# ════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    logger.info(f"Eclipse está online como {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="o servidor 🌑",
        )
    )
    try:
        synced = await bot.tree.sync()
        logger.info(f"Sincronizados {len(synced)} comando(s) slash")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos: {e}")


@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="🌑 Bem-vindo!",
            description=f"Olá {member.mention}, seja bem-vindo(a) a **{member.guild.name}**!\n"
                        f"Agora somos **{member.guild.member_count}** membros.",
            color=COR,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Eclipse Bot")
        await channel.send(embed=embed)


@bot.event
async def on_member_remove(member: discord.Member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            description=f"**{member.name}** saiu do servidor. 👋",
            color=discord.Color.dark_gray(),
        )
        await channel.send(embed=embed)


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.send(str(error), ephemeral=True)
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membro não encontrado.")
        return
    logger.error(f"Erro no comando '{ctx.command}': {error}")


# ════════════════════════════════════════════════════════════════════════════
#  COMANDOS GERAIS  (prefixo + slash)
# ════════════════════════════════════════════════════════════════════════════

@bot.hybrid_command(name="ping", description="Mostra a latência do bot")
async def ping(ctx: commands.Context):
    ms = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Latência: **{ms}ms**", color=COR)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="info", description="Informações sobre o Eclipse")
async def info(ctx: commands.Context):
    seg = int(time.time() - BOT_START)
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    embed = discord.Embed(title="🌑 Eclipse — Informações", color=COR)
    embed.add_field(name="Bot", value=str(bot.user), inline=True)
    embed.add_field(name="Servidores", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Latência", value=f"{round(bot.latency*1000)}ms", inline=True)
    embed.add_field(name="Uptime", value=f"{h}h {m}m {s}s", inline=True)
    embed.add_field(name="Python", value=platform.python_version(), inline=True)
    embed.add_field(name="discord.py", value=discord.__version__, inline=True)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="Eclipse Bot")
    await ctx.send(embed=embed)


@bot.hybrid_command(name="avatar", description="Exibe o avatar de um usuário")
@app_commands.describe(usuario="O usuário (padrão: você)")
async def avatar(ctx: commands.Context, usuario: discord.Member = None):
    alvo = usuario or ctx.author
    embed = discord.Embed(title=f"🖼️ Avatar de {alvo.display_name}", color=COR)
    embed.set_image(url=alvo.display_avatar.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="servidor", description="Informações sobre o servidor")
async def servidor(ctx: commands.Context):
    g = ctx.guild
    embed = discord.Embed(title=f"🏠 {g.name}", color=COR)
    embed.add_field(name="Dono", value=str(g.owner), inline=True)
    embed.add_field(name="Membros", value=str(g.member_count), inline=True)
    embed.add_field(name="Canais", value=str(len(g.channels)), inline=True)
    embed.add_field(name="Cargos", value=str(len(g.roles)), inline=True)
    embed.add_field(name="Criado em", value=discord.utils.format_dt(g.created_at, "D"), inline=True)
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="perfil", description="Exibe o perfil de um membro")
@app_commands.describe(membro="Membro para ver o perfil (padrão: você)")
async def perfil(ctx: commands.Context, membro: discord.Member = None):
    alvo = membro or ctx.author
    cargos = [r.mention for r in alvo.roles if r.name != "@everyone"]
    embed = discord.Embed(title=f"👤 {alvo.display_name}", color=COR)
    embed.set_thumbnail(url=alvo.display_avatar.url)
    embed.add_field(name="Tag", value=str(alvo), inline=True)
    embed.add_field(name="ID", value=str(alvo.id), inline=True)
    embed.add_field(name="Bot", value="Sim" if alvo.bot else "Não", inline=True)
    embed.add_field(name="Entrou no servidor", value=discord.utils.format_dt(alvo.joined_at, "D"), inline=True)
    embed.add_field(name="Conta criada", value=discord.utils.format_dt(alvo.created_at, "D"), inline=True)
    embed.add_field(
        name=f"Cargos ({len(cargos)})",
        value=" ".join(cargos) if cargos else "Nenhum",
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.hybrid_command(name="ajuda", description="Lista todos os comandos disponíveis")
async def ajuda(ctx: commands.Context):
    embed = discord.Embed(title="🌑 Eclipse — Comandos", color=COR)
    embed.add_field(
        name="⚙️ Gerais",
        value="`/ping` `/info` `/avatar` `/servidor` `/perfil` `/ajuda`",
        inline=False,
    )
    embed.add_field(
        name="🤖 Roblox",
        value="`?script <descrição>` — gera um script LuaU com IA",
        inline=False,
    )
    embed.add_field(
        name="🎙️ Voz",
        value="`?join` `?leave`",
        inline=False,
    )
    embed.add_field(
        name="🛡️ Moderação",
        value="`?kick` `?ban` `?unban` `?limpar` `?mute` `?unmute`",
        inline=False,
    )
    embed.set_footer(text="Use ? ou / antes do comando • Eclipse Bot")
    await ctx.send(embed=embed)


# ════════════════════════════════════════════════════════════════════════════
#  GERADOR DE SCRIPTS ROBLOX (LuaU)
# ════════════════════════════════════════════════════════════════════════════

POLLINATIONS_URL = "https://text.pollinations.ai/"

SYSTEM_PROMPT = (
    "Você é um desenvolvedor expert em Roblox Studio especializado em LuaU. "
    "Quando o usuário pedir um script, gere APENAS o código LuaU limpo e funcional, "
    "sem explicações antes ou depois, somente o bloco de código. "
    "Use boas práticas de LuaU: tipagem onde aplicável, comentários curtos explicando cada parte, "
    "e estrutura organizada. Nunca inclua texto fora do bloco de código."
)

async def gerar_script(pedido: str) -> str:
    import aiohttp, json
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": pedido},
        ],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(POLLINATIONS_URL, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            texto = await resp.text()
            return texto.strip()


@bot.command(name="script")
async def script_cmd(ctx: commands.Context, *, pedido: str = None):
    if not pedido:
        return await ctx.send("❌ Diga o que o script deve fazer.\nExemplo: `?script cria uma parte que explode ao tocar`")

    msg = await ctx.send("⏳ Gerando seu script LuaU, aguarde...")

    try:
        codigo = await gerar_script(pedido)

        # Remove marcadores markdown caso a IA adicione
        for tag in ["```lua", "```luau", "```LuaU", "```"]:
            codigo = codigo.replace(tag, "")
        codigo = codigo.strip()

        # Discord permite no máximo 2000 caracteres por mensagem
        bloco = f"```lua\n{codigo}\n```"
        if len(bloco) <= 2000:
            await msg.edit(content=bloco)
        else:
            # Divide em partes se o script for grande
            await msg.edit(content=f"📜 **Script gerado para:** {pedido}\n*(em partes abaixo)*")
            partes = [codigo[i:i+1900] for i in range(0, len(codigo), 1900)]
            for parte in partes:
                await ctx.send(f"```lua\n{parte}\n```")

    except Exception as e:
        logger.error(f"Erro ao gerar script: {e}")
        await msg.edit(content="❌ Não foi possível gerar o script agora. Tente novamente.")


# ════════════════════════════════════════════════════════════════════════════
#  COMANDOS DE VOZ
# ════════════════════════════════════════════════════════════════════════════

@bot.command(name="join")
async def join(ctx: commands.Context):
    if ctx.author.voice is None:
        return await ctx.send("❌ Você precisa estar em uma call para eu entrar.")
    canal = ctx.author.voice.channel
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(canal)
        return await ctx.send(f"🔊 Mudei para **{canal.name}**.")
    await canal.connect()
    await ctx.send(f"🔊 Entrei em **{canal.name}**.")


@bot.command(name="leave")
async def leave(ctx: commands.Context):
    if ctx.voice_client is None:
        return await ctx.send("❌ Não estou em nenhuma call.")
    canal = ctx.voice_client.channel.name
    await ctx.voice_client.disconnect()
    await ctx.send(f"👋 Saí de **{canal}**.")


# ════════════════════════════════════════════════════════════════════════════
#  COMANDOS DE MODERAÇÃO
# ════════════════════════════════════════════════════════════════════════════

@bot.hybrid_command(name="kick", description="Expulsa um membro do servidor")
@app_commands.describe(membro="Membro a expulsar", motivo="Motivo")
@tem_cargo_mod()
async def kick(ctx: commands.Context, membro: discord.Member, *, motivo: str = "Sem motivo informado"):
    if membro == ctx.author:
        return await ctx.send("❌ Você não pode expulsar a si mesmo.")
    if membro.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Você não pode expulsar alguém com cargo igual ou superior.")
    try:
        await membro.send(embed=discord.Embed(
            title="🌑 Você foi expulso",
            description=f"Servidor: **{ctx.guild.name}**\nMotivo: {motivo}",
            color=discord.Color.red(),
        ))
    except discord.Forbidden:
        pass
    await membro.kick(reason=motivo)
    embed = discord.Embed(title="👟 Membro Expulso", color=discord.Color.orange())
    embed.add_field(name="Usuário", value=str(membro))
    embed.add_field(name="Motivo", value=motivo)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="ban", description="Bane um membro do servidor")
@app_commands.describe(membro="Membro a banir", motivo="Motivo")
@tem_cargo_mod()
async def ban(ctx: commands.Context, membro: discord.Member, *, motivo: str = "Sem motivo informado"):
    if membro == ctx.author:
        return await ctx.send("❌ Você não pode banir a si mesmo.")
    if membro.top_role >= ctx.author.top_role:
        return await ctx.send("❌ Você não pode banir alguém com cargo igual ou superior.")
    try:
        await membro.send(embed=discord.Embed(
            title="🌑 Você foi banido",
            description=f"Servidor: **{ctx.guild.name}**\nMotivo: {motivo}",
            color=discord.Color.red(),
        ))
    except discord.Forbidden:
        pass
    await membro.ban(reason=motivo)
    embed = discord.Embed(title="🔨 Membro Banido", color=discord.Color.red())
    embed.add_field(name="Usuário", value=str(membro))
    embed.add_field(name="Motivo", value=motivo)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="unban", description="Desbane um usuário pelo ID")
@app_commands.describe(user_id="ID do usuário")
@tem_cargo_mod()
async def unban(ctx: commands.Context, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await ctx.guild.unban(user)
        await ctx.send(embed=discord.Embed(
            title="✅ Desbanido",
            description=f"**{user}** foi desbanido.",
            color=discord.Color.green(),
        ))
    except discord.NotFound:
        await ctx.send("❌ Usuário não encontrado ou não está banido.")
    except ValueError:
        await ctx.send("❌ ID inválido.")


@bot.hybrid_command(name="limpar", description="Apaga mensagens do canal (1–100)")
@app_commands.describe(quantidade="Quantidade de mensagens")
@tem_cargo_mod()
async def limpar(ctx: commands.Context, quantidade: int):
    if not 1 <= quantidade <= 100:
        return await ctx.send("❌ Informe um número entre 1 e 100.", ephemeral=True)
    await ctx.defer(ephemeral=True)
    deleted = await ctx.channel.purge(limit=quantidade)
    await ctx.send(f"✅ **{len(deleted)}** mensagem(ns) apagada(s).", ephemeral=True)


@bot.hybrid_command(name="mute", description="Silencia um membro temporariamente")
@app_commands.describe(membro="Membro a silenciar", minutos="Duração em minutos", motivo="Motivo")
@tem_cargo_mod()
async def mute(ctx: commands.Context, membro: discord.Member, minutos: int = 10, *, motivo: str = "Sem motivo"):
    import datetime
    duration = datetime.timedelta(minutes=minutos)
    await membro.timeout(duration, reason=motivo)
    embed = discord.Embed(title="🔇 Membro Silenciado", color=COR)
    embed.add_field(name="Usuário", value=str(membro))
    embed.add_field(name="Duração", value=f"{minutos} minuto(s)")
    embed.add_field(name="Motivo", value=motivo)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="unmute", description="Remove o silêncio de um membro")
@app_commands.describe(membro="Membro a dessilenciar")
@tem_cargo_mod()
async def unmute(ctx: commands.Context, membro: discord.Member):
    await membro.timeout(None)
    await ctx.send(embed=discord.Embed(
        title="🔊 Silêncio Removido",
        description=f"**{membro}** pode falar novamente.",
        color=discord.Color.green(),
    ))


# ════════════════════════════════════════════════════════════════════════════
#  INICIALIZAÇÃO
# ════════════════════════════════════════════════════════════════════════════

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN não encontrado!")
        return
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
