import queue
from subprocess import Popen
import discord

class channelQueue:
    def __init__(self, current:Popen, ctx:discord.Interaction) -> None:
        self.queue = queue.Queue()
        self.current = current
        self.ctx = ctx

    def add(self, song:str):
        self.queue.put(song)

    def next(self) -> str | None:
        if self.queue.empty():
            return None
        return self.queue.get()
    
    def clear(self):
        while not self.queue.empty():
            self.queue.get()


music_queue:dict[discord.VoiceClient, channelQueue] = {}