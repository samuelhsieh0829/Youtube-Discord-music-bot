class Video:
    def __init__(self, **raw) -> None:
        self.id = raw["video_id"]
        self.title = raw["video_title"]

    def __str__(self) -> str:
        return str(self.__dict__)