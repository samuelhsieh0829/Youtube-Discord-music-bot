from typing import Optional

import discord
from discord.ext import commands
from discord.app_commands import CommandTree
from utils.yt import YT
from utils.queueSys import music_queue, channelQueue

yt = YT()

class Utils(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot:commands.Bot = bot
        self.yt = YT()

    @discord.app_commands.command(name="stop", description="Stop the music")
    async def stop(self, ctx:discord.Interaction):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice:
            music_queue[voice].clear()
            await voice.disconnect()
            await ctx.response.send_message("Music stopped.")
        else:
            await ctx.response.send_message("I am not connected to a voice channel.")

    @discord.app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, ctx:discord.Interaction):
        await ctx.response.defer()
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice:
            await ctx.followup.send("I am not connected to a voice channel.")
            return

        if voice.is_playing():
            voice.stop()
            await ctx.followup.send("Song skipped.")
        else:
            await ctx.followup.send("No song is currently playing.")

    @discord.app_commands.command(name="volume", description="Set the volume 0~100")
    async def change_volume(self, ctx: discord.Interaction, volume: Optional[int]):
        await ctx.response.defer()
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        try:
            voice = music_queue[voice_client]
        except KeyError:
            await ctx.followup.send("I am not connected to a voice channel.")
            return
        
        if not voice:
            await ctx.followup.send("I am not connected to a voice channel.")
            return
        
        if volume is None:
            await ctx.followup.send(f"Current volume: {int(voice.volume * 100)}%")
            return
        
        if 0 <= volume <= 100:
            voice.set_volume(volume / 100)
            await ctx.followup.send(f"Volume set to {volume}%.")
        else:
            await ctx.followup.send("Volume must be between 0 and 100.")

async def next_song(ctx: discord.Interaction):
    voice = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        return
    
    music_queue[voice].current.terminate()
    # Check if the queue exists and is not empty
    if voice not in music_queue or music_queue[voice].queue.empty():
        await ctx.channel.send("Queue is empty. Leaving the voice channel.")

        if voice in music_queue:
            music_queue.pop(voice)
        await voice.disconnect()
        return

    # Get the next song from the queue
    song_id = music_queue[voice].next()
    if not song_id:
        await ctx.channel.send("No more songs in the queue. Disconnecting.")
        music_queue.pop(voice)
        await voice.disconnect()
        return

    # Search and play the next song
    video = yt.search(song_id, max_results=1)[0]
    await ctx.channel.send(f"Now playing: **{video.title}**")
    audio = yt.stream(video.id)
    music_queue[voice].current = audio
    voice.play(
        music_queue[voice].audio,
        after=lambda _: ctx.client.loop.create_task(next_song(ctx)),
    )

async def setup(bot):
    await bot.add_cog(Utils(bot))