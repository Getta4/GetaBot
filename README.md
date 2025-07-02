# GetaBot

Play Youtube on Discord.

![HakaTime](https://hackatime-badge.hackclub.com/U091PJDHHQV/DiscordBot
)

## How to use 
( English explanation below )

### 必要なもの

- GetaBot本体 ([ダウンロード](https://www.python.org/downloads/))

- Pythonが実行できる環境 ([インストール](https://www.python.org/downloads/))
  - pipが実行できる環境（ライブラリーをインストールしていない場合）

- ffmpeg（[インストール](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest)）

- BOT TOKEN（[ここ](https://discord.com/developers/applications)からアプリケーションを作成し、BOTタブからTOKENを取得してください。

### 手順

1. Getabot.py , SEフォルダー , [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest) をダウンロード・インストールし、同一ディレクトリに配置してください。  
(ffmpegはbinフォルダー内のexeファイルのみ配置で大丈夫です。)  

#### ディレクトリ

```
/
|- gatabot.py
|
|- SE 
|  |-nun.mp3
|  |-noti.mp3
|
|-ffmpeg.exe
|-ffplay.exe
|-ffprove.exe
|
|-runbot.bat
```

2. 以下のライブラリーをインストールしてください。  
(インストール済みの場合はインストール不要です。3に進んでください。)

```python
pip install discord
```

```python
pip install discord.py[voice]
```

```python
pip install yt-dlp==2025.01.12
```

```python
pip install ffmpeg-python
```  

3. トークンを入力して実行

```Python
～～～～～　省略　～～～～～
###Commands End###
client.run("YourTokenHere") ←ここに取得したTOKENを貼り付けてください。
```

4. **Enjoy!!**

## Commands

Getabotのコマンドはアプリケーションコマンドです。そのため / と入力をすると予測が出てきます。

### join

コマンドを実行した人が参加しているサーバーにBOTを参加させます。

### leave

ボイスチャンネルからBOTを退出させます。

### play [ YoutubeのURL ]

入力したURLの曲を再生します。

### pause

再生中の曲を一時停止します。

### replay

一時停止中の曲を再生再開します。

### stop
再生中の曲を再生停止します。  

## Support

[![email](https://img.shields.io/badge/mail@gtnk.xyz-272727?style=flat&logo=maildotru&logoColor=fff&labelColor=%234285F4&color=383838&link=https%3A%2F%2FGetan9.com%2FWeb%2F)](mailto:mail@gtnk.xyz)  
[![X](https://img.shields.io/badge/%40Get4__-272727?style=flat&logo=X&logoColor=fff&labelColor=060708&color=383838&link=https%3A%2F%2Fx.com%2FGet4_)](https://twitter.com/@Get4_)
[![Discord](https://img.shields.io/badge/get4__-272727?style=flat&logo=Discord&logoColor=fff&labelColor=%235865F2&color=383838)](https://discord.com/app/)

---

# English

## How to Use

### Prerequisites

  * **GetaBot Core** ([Download](https://www.python.org/downloads/))
  
  * **Python Environment** ([Install](https://www.python.org/downloads/))
  
      * `pip` executable environment (if you haven't installed libraries yet)
  
  * **FFmpeg** ([Install](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest))
  
  * **BOT TOKEN** (Create an application [here](https://discord.com/developers/applications) and get the TOKEN from the BOT tab.)

### Steps

1.  Download and install getabot.py, the SE folder, and [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest), then place them in the same directory.
    (For FFmpeg, only the .exe files within the bin folder are needed.)

    #### Directory Structure

    ```

    /
    |- getabot.py
    |
    |- SE
    |  |- nun.mp3
    |  |- noti.mp3
    |
    |- ffmpeg.exe
    |- ffplay.exe
    |- ffprobe.exe
    |
    |- runbot.bat
    
    ```

2.  Install the following libraries.
    (If already installed, skip this step and proceed to step 3.)

    ```python
    pip install discord
    ```

    ```python
    pip install discord.py[voice]
    ```

    ```python
    pip install yt-dlp==2025.01.12
    ```

    ```python
    pip install ffmpeg-python
    ```

3.  Enter your token and run the bot.

    ```python
    ~~~~~~~~~ (Omitted) ~~~~~~~~~
    ###Commands End###
    client.run("YourTokenHere") # Paste your obtained TOKEN here.
    ```

4.  **Enjoy!**

-----

## Commands

GetaBot commands are application commands. Type `/` to see command suggestions.

### join

Makes the bot join the voice channel that the command executor is currently in.

### leave

Makes the bot leave the voice channel.

### play [YouTube URL]

Plays the song from the provided YouTube URL.

### pause

Pauses the currently playing song.

### replay

Resumes a paused song.

### stop

Stops the currently playing song.

## Support

[![email](https://img.shields.io/badge/mail@gtnk.xyz-272727?style=flat&logo=maildotru&logoColor=fff&labelColor=%234285F4&color=383838&link=https%3A%2F%2FGetan9.com%2FWeb%2F)](mailto:mail@gtnk.xyz)  
[![X](https://img.shields.io/badge/%40Get4__-272727?style=flat&logo=X&logoColor=fff&labelColor=060708&color=383838&link=https%3A%2F%2Fx.com%2FGet4_)](https://twitter.com/@Get4_)
[![Discord](https://img.shields.io/badge/get4__-272727?style=flat&logo=Discord&logoColor=fff&labelColor=%235865F2&color=383838)](https://discord.com/app/)