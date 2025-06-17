### yt-dlp関連でエラーが出るときは pip install yt-dlp==2024.01.12 で旧バージョンを入れてください。
### 音声関連の機能を使うには ffmpeg をインストールしてディレクトリ内に配置してください。

###インポート＆変数の設定###
import os
from os import environ

import time

import discord
from discord import app_commands
from discord.ext import commands
import datetime
import calendar
import asyncio
import yt_dlp as youtube_dl

intents = discord.Intents.all()
intents.voice_states = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='/', intents=intents)
filename = "" 

#voice_client = None

##ytmusic##

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '[%(id)s]%(title)s.%(ext)s',#'%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, bitrate=256,volume=1.0):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        global filename 
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)#filenameを格納
        #print("[Debug]"+filename)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


###起動時の処理###


@client.event
async def on_ready():
    #起動時のメッセージ
    print("Botは正常に起動しました！")
    print(client.user.name)  # Botの名前
    print(client.user.id)  # ID
    print(discord.__version__)  # discord.pyのバージョン
    print('------')
    
    # アクティビティを設定
    ###以下の行をコメントアウトして、必要に応じてアクティビティを設定してください。
    ###activitytitleを変更すると、～～を視聴中、プレイ中などに変更できます。 playing,steraming,listening,watchingなどから選択できます。詳しくはググってください。
    #await client.change_presence(status=discord.Status.idle,activity=discord.Activity(state = "ステータスの説明",details = "ステータスのタイトル",type=discord.ActivityType.watching, name="～～をプレイ中の～～が入ります",url = "URLはここ"))

    # スラッシュコマンドを同期
    await tree.sync()
    print("Synced slash commands.")
    print('------')


###Commands###


# ボイスチャンネルに参加
@tree.command(name="join", description="自分が参加しているボイスチャンネルにBOTを参加させます。")
async def join_command(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("あなたはボイスチャンネルに接続していません。", ephemeral=True)
        return
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.move_to(channel)
        await interaction.response.send_message("既に接続していたので移動しました。", ephemeral=True)
    else:
        await channel.connect(self_deaf=True)
        await interaction.response.send_message("接続しました。")

# ボイスチャンネルから退出
@tree.command(name="leave", description="ボイスチャンネルから退出させます。")
async def leave_command(interaction: discord.Interaction):
    global filename
    if not filename == "":#前回再生時のファイルを削除
        os.remove(filename)
        filename = ""

    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
    else:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("切断しました。")

# YouTubeの音声を再生
@tree.command(name="play", description="YouTubeの動画(音声)を再生させます。")
@app_commands.describe(url="YouTubeのURL")
async def play_command(interaction: discord.Interaction, url: str):
    global filename
    if not filename == "":#前回再生時のファイルを削除
        os.remove(filename)
        filename = ""
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
        return
    vc = interaction.guild.voice_client
    if vc.is_playing():
        await interaction.response.send_message("再生中です。", ephemeral=True)
        return
    await interaction.response.defer()
    player = await YTDLSource.from_url(url, loop=None)
    vc.play(player)
    await interaction.followup.send(f'{player.title} を再生します。')

# 再生再開
@tree.command(name="replay", description="再生を再開します。")
async def replay_command(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
        return
    vc = interaction.guild.voice_client
    if vc.is_paused():
        vc.resume()
        await interaction.response.send_message("再生を再開しました。", ephemeral=True)
    else:
        await interaction.response.send_message("NuLL", ephemeral=True)

# 再生停止
@tree.command(name="stop", description="再生を停止します。")
async def stop_command(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
        return
    vc = interaction.guild.voice_client
    if not vc.is_playing():
        await interaction.response.send_message("再生していません。", ephemeral=True)
    else:
        vc.stop()
        time.sleep(1)#アクセス制限に引っかかるのでクッション
        global filename
        if not filename == "":#再生したファイルを削除
            os.remove(filename)
            filename = ""
        await interaction.response.send_message("停止しました。", ephemeral=True)

# 一時停止
@tree.command(name="pause", description="再生を一時停止します。")
async def pause_command(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
        return
    vc = interaction.guild.voice_client
    if not vc.is_playing():
        await interaction.response.send_message("再生していません。", ephemeral=True)
    else:
        vc.pause()
        await interaction.response.send_message("一時停止しました。", ephemeral=True)

# ﾇﾝ
@tree.command(name="nun", description="ﾇﾝ")
async def nun_command(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
        return
    vc = interaction.guild.voice_client
    if vc.is_paused():
        vc.resume()
        await interaction.response.send_message("再生を再開しました。", ephemeral=True)
    else:
        vc.play(discord.FFmpegPCMAudio("SE/nun.mp3"), bitrate=256)
        await interaction.response.send_message("ﾇﾝ", ephemeral=True)

# ﾉﾁ!
@tree.command(name="noti", description="ﾉﾁ!")
async def noti_command(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
        return
    vc = interaction.guild.voice_client
    if vc.is_paused():
        vc.resume()
        await interaction.response.send_message("再生を再開しました。", ephemeral=True)
    else:
        vc.play(discord.FFmpegPCMAudio("SE/noti.mp3"), bitrate=256)
        await interaction.response.send_message("ﾉﾁ!✋️", ephemeral=True)

@tree.command(name='hello', description='こんにちは！')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(content='Hello, World!',ephemeral=True)

@tree.command(name='urls', description='下駄のURLを表示します')
async def urls_command(interaction: discord.Interaction):
    await interaction.response.send_message(content='=== 下駄のURL === \n・Twitter \nhttps://twitter.com/get4_\n・Youtube\nhttps://www.youtube.com/@getq_\n・Steam\nhttps://steamcommunity.com/id/Get4_',ephemeral=True)
    
@discord.app_commands.guild_only
@tree.command(name="say",description="Botがテキストを送信します")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(text="送信するテキストを設定できます",picture="画像をアップロードできます")
async def say_command(interaction: discord.Interaction,text:str = None,picture:discord.Attachment = None):
    if text == None and picture == None:#何も内容がないとき(エラー文)
        await interaction.response.send_message(content="Error!!\nコマンドに引数が指定されていません。\n必ず一つ以上引数を指定して実行してください。",ephemeral=True)

    elif text == None:#画像のみの送信
        embed=discord.Embed(title="",color=0xff0000)
        embed.set_image(url=picture.url)#URLでEmbedに画像を貼る
        await interaction.response.send_message(embed=embed)

    elif picture == None:#文字のみ送信
        await interaction.response.send_message(text)

    else:
        embed=discord.Embed(title="",color=0xff0000)
        embed.set_image(url=picture.url)#URLでEmbedに画像を貼る
        await interaction.response.send_message(text,embed=embed)


@discord.app_commands.guild_only
@tree.command(name="dm",description="下駄にメッセージを送信します")
@app_commands.describe(mention="(必須)DMに下駄へのメンションを含めるかを設定できます",text="送信するテキストを設定できます",picture="画像をアップロードできます")
async def DM_command(interaction: discord.Interaction,mention:bool,text:str = None,picture:discord.Attachment = None):
    if mention == None:#メンションの指定がないとき
        await interaction.response.send_message(content="Error!!\nmentionの指定がされていません。\nメンションの指定をしてください。",ephemeral=True)
        print("[Debug]Error!! DMコマンドに引数が指定されませんでした")
    elif text == None and picture == None:#何も内容がないとき(エラー文)
        await interaction.response.send_message(content="Error!!\nコマンドにmention以外の引数が指定されていません。\n必ずmention以外の引数を一つ以上指定して実行してください。",ephemeral=True)
        print("[Debug]Error!! DMコマンドに引数が指定されませんでした")
        print('------')
    elif text == None:#画像のみの送信
        if mention == True:#メンションあり
            embed=discord.Embed(title="",color=0xff0000)
            embed.set_image(url=picture.url)#URLでEmbedに画像を貼る
            user = await client.fetch_user("957152000313786459")
            await user.send("<@957152000313786459>")
            await user.send(embed=embed)
            await interaction.response.send_message(content="送信が完了しました！",ephemeral=True)
        else:
            embed=discord.Embed(title="",color=0xff0000)
            embed.set_image(url=picture.url)#URLでEmbedに画像を貼る
            user = await client.fetch_user("957152000313786459")
            await user.send(embed=embed)
            await interaction.response.send_message(content="送信が完了しました！",ephemeral=True)
    elif picture == None:#文字のみ送信
        if mention == True:#メンションあり
            user = await client.fetch_user("957152000313786459")
            await user.send("<@957152000313786459>\n")
            await user.send(text)
            await interaction.response.send_message(content="送信が完了しました！",ephemeral=True)
        else:
            user = await client.fetch_user("957152000313786459")
            await user.send(text)
            await interaction.response.send_message(content="送信が完了しました！",ephemeral=True)
    else:#両方送信
        if mention == True:#メンションあり
            embed=discord.Embed(title="",color=0xff0000)
            embed.set_image(url=picture.url)#URLでEmbedに画像を貼る
            user = await client.fetch_user("957152000313786459")
            await user.send("<@957152000313786459>\n")
            await user.send(text)
            await user.send(embed=embed)
            await interaction.response.send_message(content="送信が完了しました！",ephemeral=True)
        else:
            embed=discord.Embed(title="",color=0xff0000)
            embed.set_image(url=picture.url)#URLでEmbedに画像を貼る
            user = await client.fetch_user("957152000313786459")
            await user.send(text)
            await user.send(embed=embed)
            await interaction.response.send_message(content="送信が完了しました！",ephemeral=True)

###Commands End###
client.run(" Token Here ")
