# Youtube Discord music bot
透過yt-dlp串流Youtube音樂到Discord語音頻道中

## .env
- `DC_TOKEN` = discord機器人的token
- `YT_TOKEN` = (可選)在Google Cloud Platform上可取得Youtube Data API V3的token

**YT_TOKEN用於取得影片搜尋建議，目前程式使用yt-dlp的搜尋功能取代** <br>
若要使用Youtube API，須將`utils/yt.py`中的22\~34行取消註解，並且將36\~61行註解 <br>
- 兩者使用上基本無差異，但Youtube API有使用額度限制(使用幾次就會被403)，yt-dlp則未知(目前未遇到被403)
- 建議使用yt-dlp即可(較方便且無限制)

## 指令
- `/play song:str channel:VoiceChannel(Optional)` 使用者可以選擇一個語音頻道，從Youtube查詢音樂並播放
- - 若未選擇頻道，將自動選定為使用者所在的語音頻道
  - 若機器人正在播放音樂，則會將選擇的音樂加入列隊中
  - 列隊中的音樂會依序播放
  - 當所有列隊中的音樂接播放完畢，機器人將自動退出語音頻道
- `/skip` 在機器人播放音樂時，可以透過此指令來提前結束正在播放的音樂
  - 若此時列隊中還有音樂，將開始播放下一首
  - 反之，則會離開語音頻道
- `/download url:str` 指定Youtube音樂連結，即可將音樂下載至機器人的本地端，儲存在`music`資料夾
- `/list` 將`music`資料夾內的檔案全部列舉出來
- `/play_from_file song:str` 使用者須先進入一個語音頻道，使用此指令可取得在`music`資料夾內的音樂並播放
  - 與`/play`不同，此模式暫時沒有列隊功能
  - 使用此指令時，會停止目前正在播放的任何音訊，若有`/play`的列隊，會直接被清除
  - 目前此功能尚未完成
  - 目前問題:
    - 在語音頻道內沒有聲音，但頭像會亮
    - 指令執行後會卡在"正在思考"
    - 似乎無法取得音檔的資料(如標題)
- `/stop` 可以停止機器人正在播放的音訊並且使其退出語音頻道
- `/volume volume:int` 在機器人播放音樂時，可以輸入0~100的整數調整機器人放出音訊的音量
- `/manage` 會跳出一個介面，查看指令啟用狀態
  - 可以從下拉選單中選擇一組指令，切換其狀態
  - 切換狀態即load、unload cog
  - cog的分組如下
    - `cogs.from_yt`: `/play`
    - `cogs.utils`: `/stop`、`/skip` (以及播放下一首的函式，目前不確定unload是否影響此函式)
    - `cogs.local`: `/play_from_file`、`/list`、`/download`
  - 只有`main.py:34`中的Discord使用者ID(那一串數字)，即機器人擁有者可使用此指令
