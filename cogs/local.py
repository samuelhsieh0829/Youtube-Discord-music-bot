import discord
from discord.ext import commands
from discord.app_commands import CommandTree
from utils.yt import YT
from utils.queueSys import music_queue, channelQueue
from cogs.utils import next_song

class LocalMusic(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.yt = YT()

    @discord.app_commands.command(name="list", description="List all downloaded music")
    async def list_music(self, ctx:discord.Interaction):
        music = self.yt.list_music()
        if not music:
            await ctx.response.send_message("No music found.")
        else:
            await ctx.response.send_message("\n".join(music))

    @discord.app_commands.command(name="download", description="Download a song")
    async def download(self, ctx:discord.Interaction, url:str):
        song = url
        await ctx.response.defer()
        result = self.yt.download(song)
        if result[0]:
            await ctx.followup.send(f"{song} has been successfully downloaded.")
        else:
            await ctx.followup.send(f"Error: {result[1]}")

    @discord.app_commands.command(name="play_from_file", description="Play a downloaded song")
    async def play_from_file(self, ctx:discord.Interaction, song:str):
        await ctx.response.defer()
        if song not in self.yt.list_music():
            await ctx.followup.send(f"{song} not found.")
            return
        
        # Check if the user is in a voice channel
        if not ctx.user.voice or not ctx.user.voice.channel:
            await ctx.followup.send("You must be in a voice channel to use this command.")
            return
        
        voice_channel = ctx.user.voice.channel

        # Connect or move the bot to the user's voice channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            voice = await voice_channel.connect()
        elif voice.channel != voice_channel:
            await voice.move_to(voice_channel)

        # Check if a song is already playing
        if voice.is_playing():
            music_queue[voice].clear()
            voice.stop()
        
        await ctx.followup.send(f"Now playing: **{self.yt.get_music_title(song)}**")
        voice.play(discord.FFmpegPCMAudio(f"music\\{song}"))

    @play_from_file.autocomplete("song")
    async def song_autocomplete(self, ctx:discord.Interaction, current:str):
        return [
                discord.app_commands.Choice(name=music, value=music)
                for music in self.yt.list_music()
            ]

async def setup(bot):
    await bot.add_cog(LocalMusic(bot))
    