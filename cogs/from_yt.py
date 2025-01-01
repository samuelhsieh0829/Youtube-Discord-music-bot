import discord
from discord.ext import commands
from discord.app_commands import CommandTree
from utils.yt import YT
from utils.queueSys import music_queue, channelQueue
from cogs.utils import next_song
from typing import Optional

class YTMusic(commands.Cog):

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.yt = YT()

    @discord.app_commands.command(name="play", description="Play a song")
    async def play(self, ctx: discord.Interaction, song: str, channel: Optional[discord.VoiceChannel] = None):
        await ctx.response.defer()

        # Check if the user is in a voice channel
        if not ctx.user.voice or not ctx.user.voice.channel:
            if channel is None:
                await ctx.followup.send("You must be in a voice channel to use this command.")
                return
            voice_channel = channel
        else:
            voice_channel = ctx.user.voice.channel

        # Search for the song
        videos = self.yt.search(song, max_results=1)
        if not videos:
            await ctx.followup.send(f"No results for '{song}'")
            return

        video = videos[0]  # First search result

        # Connect or move the bot to the user's voice channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            voice = await voice_channel.connect()
        elif voice.channel != voice_channel:
            await voice.move_to(voice_channel)

        if isinstance(voice, discord.StageChannel):
            member = voice.guild.me
            await member.edit(suppress=False)

        # Check if a song is already playing
        if voice.is_playing():
            # Add the song to the queue
            if voice not in music_queue:
                music_queue[voice] = channelQueue(None, ctx)
            music_queue[voice].add(video.url)
            await ctx.followup.send(f"Added to queue: **{video.title}**")
            return

        # Play the song if no music is currently playing
        await ctx.followup.send(f"Now playing: **{video.title}**")
        audio = self.yt.stream(video.id)
        music_queue[voice] = channelQueue(audio, ctx)
        voice.play(
            discord.FFmpegPCMAudio(audio.stdout, pipe=True),
            after=lambda _: self.bot.loop.create_task(next_song(ctx)),
        )

    @play.autocomplete("song")
    async def song_autocomplete(self, ctx:discord.Interaction, current:str):
        videos = self.yt.search(current, max_results=10)
        return [
                discord.app_commands.Choice(name=video.title, value=video.url)
                for video in videos
            ]
    
async def setup(bot):
    await bot.add_cog(YTMusic(bot))