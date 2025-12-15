import queue
import random
from subprocess import Popen
import discord
import threading

from utils.video import Video

class channelQueue:
    def __init__(self, current:Popen, ctx:discord.Interaction) -> None:
        self.queue:queue.Queue[Video] = queue.Queue()
        self.current = current
        self.volume = 0.15 # Default volume
        if self.current is not None:
            self.__audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(self.current.stdout, pipe=True), self.volume
            )
        else:
            self.__audio = None
        # self.ctx = ctx
        # Idk why I need ctx

    def add(self, song:str):
        self.queue.put(song)

    def set_current(self, current:Popen):
        self.current = current
        if self.current is not None:
            self.__audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(self.current.stdout, pipe=True), self.volume
            )
        else:
            self.__audio = None

    def next(self) -> Video | None:
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

    def shuffle(self):
        temp_list = []
        while not self.queue.empty():
            temp_list.append(self.queue.get())
        random.shuffle(temp_list)
        for item in temp_list:
            self.queue.put(item)

    def get_queue_list(self) -> list[Video]:
        return list(self.queue.queue)

    @property
    def audio(self):
        return self.__audio

# URL放歌版 但是放到一半會被斷掉

# class channelQueue:
#     def __init__(self, current:str, ctx:discord.Interaction) -> None:
#         self.queue = queue.Queue()
#         self.current = current
#         self.volume = 0.15 # Default volume
#         if self.current is not None:
#             self.__audio = discord.PCMVolumeTransformer(
#                 # discord.FFmpegPCMAudio(self.current.stdout, pipe=True), self.volume
#                 discord.FFmpegPCMAudio(self.current), self.volume
#             )
#         else:
#             self.__audio = None
#         self.ctx = ctx

#     def add(self, song:str):
#         self.queue.put(song)

#     def set_current(self, current:str):
#         self.current = current
#         if self.current is not None:
#             self.__audio = discord.PCMVolumeTransformer(
#                 discord.FFmpegPCMAudio(self.current), self.volume
#             )
#         else:
#             self.__audio = None

#     def next(self) -> str | None:
#         if self.queue.empty():
#             return None
#         return self.queue.get()
    
#     def clear(self):
#         # self.current.terminate()
#         while not self.queue.empty():
#             self.queue.get()
    
#     def set_volume(self, volume:float):
#         self.volume = volume
#         self.__audio.volume = volume

#     @property
#     def audio(self):
#         return self.__audio

music_queue:dict[discord.VoiceClient, channelQueue] = {}