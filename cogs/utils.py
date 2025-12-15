from typing import Optional

import discord
from discord.ext import commands
from discord.app_commands import CommandTree
from utils.yt import YT
from utils.queueSys import music_queue, channelQueue
from utils.logger import setup_logger

log = setup_logger(__name__)

yt = YT()

class Utils(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot:commands.Bot = bot
        self.yt = YT()

    @discord.app_commands.command(name="stop", description="Stop the music")
    async def stop(self, ctx:discord.Interaction):
        log.info(f"Received stop request from {ctx.user.name}")
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice:
            log.debug(f"Stopping music and disconnecting from {voice.channel.name}")
            music_queue[voice].clear()
            await voice.disconnect()
            log.info(f"Successfully stopped music and disconnected from voice channel")
            await ctx.response.send_message("⏹️Music stopped.")
        else:
            log.warning(f"Stop command used but bot is not in a voice channel")
            await ctx.response.send_message("I am not connected to a voice channel.")

    @discord.app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, ctx:discord.Interaction):
        await ctx.response.defer()
        log.info(f"Received skip request from {ctx.user.name}")
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice:
            log.debug(f"Skip command used but bot is not in a voice channel")
            await ctx.followup.send("I am not connected to a voice channel.")
            return

        if voice.is_playing():
            log.info(f"Skipping current song in {voice.channel.name}")
            voice.stop()
            await ctx.followup.send("Song skipped.")
        else:
            log.debug(f"Skip command used but no song is playing")
            await ctx.followup.send("No song is currently playing.")

    @discord.app_commands.command(name="volume", description="Set the volume 0~100")
    async def change_volume(self, ctx: discord.Interaction, volume: Optional[int]):
        await ctx.response.defer()
        log.info(f"Received volume request from {ctx.user.name}: {volume}")
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        try:
            voice = music_queue[voice_client]
        except KeyError:
            log.debug(f"Volume command used but bot is not in a voice channel")
            await ctx.followup.send("I am not connected to a voice channel.")
            return
        
        if not voice:
            log.debug(f"Volume command used but no music queue found")
            await ctx.followup.send("I am not connected to a voice channel.")
            return
        
        if volume != 0 and not volume:
            log.info(f"Current volume query in {voice.channel.name}: {int(voice.volume * 100)}%")
            await ctx.followup.send(f"🔊Current volume: {int(voice.volume * 100)}%")
            return
        
        if 0 <= volume <= 100:
            log.info(f"Setting volume to {volume}%")
            voice.set_volume(volume / 100)
            await ctx.followup.send(f"🔊Volume set to {volume}%.")
        else:
            log.warning(f"Invalid volume value requested: {volume}")
            await ctx.followup.send("Volume must be between 0 and 100.")

    @discord.app_commands.command(name="shuffle", description="Shuffle the current queue")
    async def shuffle(self, ctx: discord.Interaction):
        log.info(f"Received shuffle request from {ctx.user.name}")
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        try:
            voice = music_queue[voice_client]
        except KeyError:
            log.debug(f"Shuffle command used but bot is not in a voice channel")
            await ctx.response.send_message("I am not connected to a voice channel.")
            return
        
        if not voice:
            log.debug(f"Shuffle command used but no music queue found")
            await ctx.response.send_message("I am not connected to a voice channel.")
            return
        
        voice.shuffle()
        log.info(f"Shuffled the queue in {voice_client.channel.name}")
        await ctx.response.send_message("🔀Queue shuffled.")

    @discord.app_commands.command(name="queue", description="View the current queue")
    async def view_queue(self, ctx: discord.Interaction):
        log.info(f"Received queue view request from {ctx.user.name}")
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        try:
            voice = music_queue[voice_client]
        except KeyError:
            log.debug(f"Queue command used but bot is not in a voice channel")
            await ctx.response.send_message("I am not connected to a voice channel.")
            return
        
        if not voice:
            log.debug(f"Queue command used but no music queue found")
            await ctx.response.send_message("I am not connected to a voice channel.")
            return
        
        if voice.queue.empty():
            log.info(f"Queue is empty in {voice_client.channel.name}")
            await ctx.response.send_message("The queue is currently empty.")
            return
        
        await ctx.response.defer()

        queue_list = voice.get_queue_list()
        if len(queue_list) < 25:
            embed = discord.Embed(title="Current Queue", color=discord.Color.blurple())
            for idx, video in enumerate(queue_list, start=1):
                embed.add_field(name=f"{idx}. {video.title}", value=video.url, inline=False)
            
            log.info(f"Displayed queue with {len(queue_list)} songs in {voice_client.channel.name}")
        else:
            index = 0
            embed = discord.Embed(title="Current Queue", color=discord.Color.blurple())
            while index < len(queue_list):
                for i in range(index, index+24):
                    if i >= len(queue_list):
                        break
                    video = queue_list[i]
                    embed.add_field(name=f"{i+1}. {video.title}", value=video.url, inline=False)
                    index += 1
                await ctx.channel.send(embed=embed)
                embed = discord.Embed(color=discord.Color.blurple())

        

async def next_song(ctx: discord.Interaction):
    log.debug("next_song function called")
    voice = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
    if not voice or not voice.is_connected():
        log.warning("next_song called but voice client is not connected")
        return
    
    log.debug("Terminating current audio process")
    music_queue[voice].current.terminate()

    # Check if the queue exists and is not empty
    if voice not in music_queue or music_queue[voice].queue.empty():
        log.info(f"{voice.channel.name} Queue is empty, disconnecting.")
        await ctx.channel.send("Queue is empty. Leaving the voice channel.")

        if voice in music_queue:
            music_queue.pop(voice)
        await voice.disconnect()
        return

    # Get the next song from the queue
    video = music_queue[voice].next()
    if not video:
        log.info("Queue returned no video, disconnecting")
        await ctx.channel.send("No more songs in the queue. Disconnecting.")
        music_queue.pop(voice)
        await voice.disconnect()
        return
    # song_id = music_queue[voice].next()
    # if not song_id:
    #     log.warning("Queue returned no song ID, disconnecting")
    #     await ctx.channel.send("No more songs in the queue. Disconnecting.")
    #     music_queue.pop(voice)
    #     await voice.disconnect()
    #     return

    # Search and play the next song

    # log.info(f"Searching for next song: {song_id}")
    # results = yt.search(song_id, max_results=1)
    # if not results:
    #     log.error(f"No results found for song_id: {song_id}")
    #     await ctx.channel.send("No results found.")
    #     await next_song(ctx)
    #     return
    
    # video = results[0]  # First search result
    # for result in results:
    #     if result.id == song_id:
    #         video = result
    #         break
    log.info(f"Playing next song: {video.title}")
    await ctx.channel.send(f"▶️Now playing: **{video.title}**")
    audio = yt.stream(video.id)
    music_queue[voice].set_current(audio)
    log.debug(f"Starting playback for: {video.title}")
    voice.play(
        music_queue[voice].audio,
        after=lambda _: ctx.client.loop.create_task(next_song(ctx)),
    )

async def setup(bot):
    await bot.add_cog(Utils(bot))