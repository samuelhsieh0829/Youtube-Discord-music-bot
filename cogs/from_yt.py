import discord
from discord.ext import commands
from discord.app_commands import CommandTree
from utils.yt import YT
from utils.queueSys import music_queue, channelQueue
from cogs.utils import next_song
from typing import Optional
from utils.logger import setup_logger

log = setup_logger(__name__)

class YTMusic(commands.Cog):

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.yt = YT()

    @discord.app_commands.command(name="play", description="Play a song")
    async def play(self, ctx: discord.Interaction, song: str, channel: Optional[discord.VoiceChannel] = None):
        await ctx.response.defer()
        log.info(f"Received play request for song: {song}")

        # Check if the user is in a voice channel
        if not ctx.user.voice or not ctx.user.voice.channel:
            if channel is None:
                await ctx.followup.send("❌You must be in a voice channel to use this command.")
                return
            voice_channel = channel
        else:
            voice_channel = ctx.user.voice.channel

        # Search for the song
        videos = self.yt.search(song, max_results=1)
        if not videos:
            await ctx.followup.send(f"❌No results for '{song}'")
            return

        video = videos[0]  # First search result

        # Connect or move the bot to the user's voice channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            log.debug(f"Bot is not connected to any voice channel, connecting to {voice_channel.name}.")
            voice = await voice_channel.connect()
            log.info(f"Connected to voice channel: {voice_channel.name}")
        elif voice.channel != voice_channel:
            await voice.move_to(voice_channel)

        if isinstance(voice, discord.StageChannel):
            member = voice.guild.me
            await member.edit(suppress=False)
        log.debug(f"Preparing to play: {video.title} in channel: {voice.channel.name}")

        # Check if a song is already playing
        if voice.is_playing():
            # Add the song to the queue
            log.info(f"Song is already playing, adding to queue: {video.title}")
            if voice not in music_queue:
                music_queue[voice] = channelQueue(None, ctx)
            music_queue[voice].add(video)
            await ctx.followup.send(f"➕Added to queue: **{video.title}**")
            return
        else:
            log.debug(f"No song is currently playing, starting playback for: {video.title}")

        # Play the song if no music is currently playing
        await ctx.followup.send(f"▶️Now playing: **{video.title}**")
        log.debug(f"Searched song: {video.title}")
        audio = self.yt.stream(video.id)
        music_queue[voice] = channelQueue(audio, ctx)
        if music_queue[voice].audio is None:
            await ctx.followup.send("❌Error: Audio stream is None.")
            return
        log.info(f"Starting playback for: {video.title}")
        voice.play(
            music_queue[voice].audio,
            after=lambda _: self.bot.loop.create_task(next_song(ctx)),
        )

    @play.autocomplete("song")
    async def song_autocomplete(self, ctx:discord.Interaction, current:str):
        videos = self.yt.search(current, max_results=10)
        return [
                discord.app_commands.Choice(name=video.title, value=video.url)
                for video in videos
            ]
    
    @discord.app_commands.command(name="playlist", description="Play a playlist from URL")
    async def playlist(self, ctx: discord.Interaction, url: str, channel: Optional[discord.VoiceChannel] = None, shuffle: Optional[bool] = False):
        await ctx.response.defer()
        log.info(f"Received playlist request for URL: {url}")

        # Check if the user is in a voice channel
        if not ctx.user.voice or not ctx.user.voice.channel:
            if channel is None:
                await ctx.followup.send("❌You must be in a voice channel to use this command.")
                return
            voice_channel = channel
        else:
            voice_channel = ctx.user.voice.channel

        # Fetch playlist videos
        log.debug(f"Fetching playlist videos for URL: {url}")
        result = self.yt.get_playlist_videos(url)
        if result is None:
            await ctx.followup.send(f"❌Failed to retrieve playlist from '{url}'")
            return
        if not result[1]:
            await ctx.followup.send(f"❌No results for playlist '{url}'")
            return
        log.info(f"Playlist fetched successfully for URL: {url}, title: {result[0]}")
        title, videos = result
        await ctx.followup.send(f"🎵Playlist '{title}' with {len(videos)} videos found.")

        # Connect or move the bot to the user's voice channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            log.debug(f"Bot is not connected to any voice channel, connecting to {voice_channel.name}.")
            voice = await voice_channel.connect()
            log.info(f"Connected to voice channel: {voice_channel.name}")
        elif voice.channel != voice_channel:
            await voice.move_to(voice_channel)

        if isinstance(voice, discord.StageChannel):
            member = voice.guild.me
            await member.edit(suppress=False)

        if voice not in music_queue:
            music_queue[voice] = channelQueue(None, ctx)

        for video in videos:
            music_queue[voice].add(video)

        if shuffle:
            music_queue[voice].shuffle()
            log.info(f"Shuffled the playlist before playback.")

        if not voice.is_playing():
            next_video = music_queue[voice].next()
            if not next_video:
                await ctx.followup.send("❌Error retrieving the first video from the playlist.")
                return
            audio = self.yt.stream(next_video.id)
            music_queue[voice].set_current(audio)
            if music_queue[voice].audio is None:
                await ctx.followup.send("❌Error: Audio stream is None.")
                return
            log.info(f"Starting playback for playlist: {title}")
            await ctx.followup.send(f"▶️Now playing from playlist: **{title}**")
            await ctx.followup.send(f"▶️Now playing: **{next_video.title}**")
            voice.play(
                music_queue[voice].audio,
                after=lambda _: self.bot.loop.create_task(next_song(ctx)),
            )
        else:
            await ctx.followup.send(f"➕Playlist {title} added to queue.")

    
async def setup(bot):
    await bot.add_cog(YTMusic(bot))