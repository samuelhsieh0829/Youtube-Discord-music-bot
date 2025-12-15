from discord.ext import commands, tasks
import discord
import os
from discord import FFmpegPCMAudio
import discord.types
import typing
from dotenv import load_dotenv
from utils.queueSys import music_queue, channelQueue
import asyncio
from utils.logger import setup_logger

log = setup_logger(__name__)

load_dotenv()

dc_token = os.getenv("DC_TOKEN")

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

errors:list[str] = []

cogs = ["cogs.from_yt", "cogs.utils", "cogs.local"]

@bot.event
async def on_ready():
    log.info(f"logged in as {bot.user.name}")
    try:
        await bot.tree.sync()
    except Exception:
        log.exception("Failed to sync commands")

@bot.tree.command(name="manage", description="Manage commands")
async def manage(ctx:discord.Interaction):
    await ctx.response.defer(ephemeral=True)
    
    if ctx.user.id != 551395982756282369:
        log.warning(f"{ctx.user.name} tried to manage cogs.")
        await ctx.followup.send("❌You can manage your brain first :)")
        return
    
    embed = discord.Embed(title="Manage commands", description="Manage the commands of the bot", color=discord.Color.blurple())
    for cog in cogs:
        enabled = cog in bot.extensions
        embed.add_field(name=cog, value=enabled, inline=False)
    
    class SelectView(discord.ui.View):
        def __init__(self, timeout=60):
            super().__init__(timeout=timeout)
        
        @discord.ui.select(placeholder="Select a cog", 
                           options=[discord.SelectOption(label=cog, value=cog) for cog in cogs])
        async def select(self, ctx:discord.Interaction, select:discord.ui.Select):
            if select.values[0] in bot.extensions:
                await bot.unload_extension(select.values[0])
            else:
                await bot.load_extension(select.values[0])
            await ctx.response.send_message(f"✅Successfully {'un' if select.values[0] not in bot.extensions else ''}loaded {select.values[0]}.", ephemeral=True)

    await ctx.followup.send(embed=embed, view=SelectView())

@bot.tree.error
async def on_command_error(ctx:discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.CommandNotFound):
        await ctx.response.send_message("❌Command unaviailable or not found.")
        log.error(error)
    else:
        try:
            await ctx.response.send_message(f"❌An error occurred")
            errors.append({"type": str(type(error)), "error": str(error)})
            log.error(type(error), error)
        except discord.errors.InteractionResponded:
            return

@bot.tree.command(name="error", description="View error logs")
async def view_errors(ctx:discord.Interaction):
    if ctx.user.id != 551395982756282369:
        log.warning(f"{ctx.user.name} tried to view error logs.")
        await ctx.response.send_message("❌You can view your own errors first :)")
        return
    
    await ctx.response.defer(ephemeral=True)
    if not errors:
        await ctx.followup.send("No errors logged.")
        return
    
    embeds = []
    for i in errors:
        embed = discord.Embed(title=i["type"], description=i["error"], color=discord.Color.red())
        embeds.append(embed)

    log.info(f"Sent {len(embeds)} error logs to {ctx.user.name}.")
    for embed in embeds:
        await ctx.followup.send(embed=embed, ephemeral=True)

async def main():
    log.info("Loading cogs...")
    for cog in cogs:
        await bot.load_extension(cog)
    log.info("Starting bot...")
    await bot.start(dc_token)

if __name__ == "__main__":
    asyncio.run(main())