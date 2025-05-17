import queue
from subprocess import Popen
import discord
import threading

class channelQueue:
    def __init__(self, current:Popen, ctx:discord.Interaction) -> None:
        self.queue = queue.Queue()
        self.current = current
        self.volume = 0.15 # Default volume
        if self.current is not None:
            self.__audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(self.current.stdout, pipe=True), self.volume
            )
        else:
            self.__audio = None
        self.ctx = ctx

    def add(self, song:str):
        self.queue.put(song)

    def next(self) -> str | None:
        if self.queue.empty():
            return None
        return self.queue.get()
    
    def clear(self):
        self.current.terminate()
        while not self.queue.empty():
            self.queue.get()
    
    def set_volume(self, volume:float):
        self.volume = volume
        self.__audio.volume = volume

    @property
    def audio(self):
        return self.__audio

music_queue:dict[discord.VoiceClient, channelQueue] = {}