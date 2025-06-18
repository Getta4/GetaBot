# GetaBot

Play Youtube on Discord.

![HakaTime](https://hackatime-badge.hackclub.com/U091PJDHHQV/DiscordBot
)

## How to use

### 必要なもの

- Pythonが実行できる環境 ([インストール](https://www.python.org/downloads/))
  - pipが実行できる環境（ライブラリーをインストールしていない場合）

- ffmpeg（[インストール](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest)）

- BOT TOKEN（[ここ](https://discord.com/developers/applications)からアプリケーションを作成し、BOTタブからTOKENを取得してください。

### 手順

1. Getabot.py,SEフォルダー,[ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest) をインストールし、同一ディレクトリに配置してください。  
(ffmpegはbinフォルダー内のexeファイルのみ配置で大丈夫です。)
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

## Support

[![email](https://img.shields.io/badge/mail@m.getan9.com-272727?style=flat&logo=maildotru&logoColor=fff&labelColor=%234285F4&color=383838&link=https%3A%2F%2FGetan9.com%2FWeb%2F)](mailto:mail@m.getan9.com)  
[![X](https://img.shields.io/badge/%40Get4__-272727?style=flat&logo=X&logoColor=fff&labelColor=060708&color=383838&link=https%3A%2F%2Fx.com%2FGet4_)](https://twitter.com/@Get4_)
[![Discord](https://img.shields.io/badge/get4__-272727?style=flat&logo=Discord&logoColor=fff&labelColor=%235865F2&color=383838)](https://discord.com/app/)
