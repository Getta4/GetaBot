## memo ##
# yt-dlp関連でエラーが出るときは pip install -U yt-dlp で最新バージョンに更新してください。
# 初回のメッセージ送信はresponse.send_message()、二回目以降はfollowup.send()でおｋ（responseは返り値Noneなので内容を取得したいときはfolowupを使う）
## end memo ##

###インポート＆変数の設定###
import os #動画ファイルの削除に使用します
from os import environ
import time #ファイルの削除が確実にできるように使用
import traceback

import discord #Botの起動に必要なライブラリです
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl #YouTube動画のダウンロード/再生に使います。
from collections import defaultdict, deque #キュー関連に必要

# Botスクリプトのディレクトリを取得し、PATHに追加（同階層のffmpeg.exeやdeno.exeをyt-dlp/discord.pyに認識させるため）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = BASE_DIR + os.pathsep + os.environ.get("PATH", "")

intents = discord.Intents.all()
intents.voice_states = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='/', intents=intents)
filename = "" 

##ytmusic##

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda *args, **kwargs: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(BASE_DIR, '[%(id)s]%(title)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'ffmpeg_location': BASE_DIR,
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

        if stream:
            filename = data['url']
        else:
            # 実際に保存されたファイルパスを取得（requested_downloads を優先）
            if 'requested_downloads' in data and data['requested_downloads']:
                filename = data['requested_downloads'][0].get('filepath') or ytdl.prepare_filename(data)
            else:
                filename = ytdl.prepare_filename(data)

        ffmpeg_executable = os.path.join(BASE_DIR, "ffmpeg.exe")
        if not os.path.exists(ffmpeg_executable):
            ffmpeg_executable = "ffmpeg"

        return cls(discord.FFmpegPCMAudio(filename, executable=ffmpeg_executable, **ffmpeg_options), data=data)

###起動時の処理###
@client.event
async def on_ready():
    #起動時のメッセージ
    print("Botは正常に起動しました！")
    print(f"User name : {client.user.name}")  # Botの名前
    print(f"User ID : {client.user.id} ")  # ID
    print(f"Discord.py Version : {discord.__version__} ")  # discord.pyのバージョン
    print('------------------------')
    
    # アクティビティを設定
    await client.change_presence(status=discord.Status.online)

    # スラッシュコマンドを同期
    await tree.sync()
    print("Synced slash commands.")
    print('------------------------')

### Button ###
class Play_Control_1(discord.ui.View):#再生開始時のボタン設定
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.primary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        await pause_command.callback(interaction)

    @discord.ui.button(label="⏹️/⏭️", style=discord.ButtonStyle.primary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await stop_command.callback(interaction)
        
class Play_Control_2(discord.ui.View):#一時停止時のボタン設定
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        await replay_command.callback(interaction)

    @discord.ui.button(label="⏹️/⏭️", style=discord.ButtonStyle.primary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await stop_command.callback(interaction)

###Commands###
last_bot_message = {} #メッセージを保存し、後で削除

# ボイスチャンネルに参加
@discord.app_commands.guild_only
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
        await interaction.response.send_message("接続しました。", ephemeral=True)

# ボイスチャンネルから退出
@discord.app_commands.guild_only
@tree.command(name="leave", description="ボイスチャンネルから退出させます。")
async def leave_command(interaction: discord.Interaction):
    global filename
    vc = interaction.guild.voice_client
    if filename != "":#前回再生時のファイルを削除
        if vc and vc.is_playing():
            vc.stop()
            time.sleep(1)#アクセス制限に引っかかるのでクッション
        if vc and vc.is_paused():
            vc.stop()
            time.sleep(1)
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                print(f"ファイル削除エラー: {e}")
        filename = ""

    if interaction.guild.voice_client is None:
        await interaction.response.send_message("接続していません。", ephemeral=True)
    else:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("切断しました。", ephemeral=True)

# サーバーごとにキューを管理
music_queues = defaultdict(deque)

async def play_next(interaction, guild_id):
    try:
        global filename
        vc = interaction.guild.voice_client
        if not vc:
            return

        #botの直前のメッセージを削除
        if guild_id in last_bot_message:
            try:
                await last_bot_message[guild_id].delete()
            except Exception:
                pass
            del last_bot_message[guild_id]
        
        if music_queues[guild_id]:
            next_url = music_queues[guild_id].popleft()

            if filename != "":#前回再生時のファイルを削除
                if vc.is_playing():
                    vc.stop()
                    time.sleep(1)#アクセス制限に引っかかるのでクッション
                
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception as e:
                        print(f"ファイル削除エラー: {e}")
                filename = ""

            player = await YTDLSource.from_url(next_url, loop=None)
            vc.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction, guild_id), interaction.client.loop))
            
            # メッセージ送信と保存
            msg = await interaction.followup.send(f'{player.title} を再生します。\n', view=Play_Control_1(timeout=None))
            last_bot_message[guild_id] = msg
            
    except Exception as e:
        print(f"play_next エラー: {e}")
        traceback.print_exc()
        try:
            await interaction.response.send_message("Error!\n動画が正常に取得できませんでした。(年齢制限のかかっている動画は取得できないので、別の動画を指定してください。）\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
            if music_queues[guild_id]:
                await play_next(interaction, guild_id)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("Error!\n動画が正常に取得できませんでした。(年齢制限のかかっている動画は取得できないので、別の動画を指定してください。）\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
            if music_queues[guild_id]:
                await play_next(interaction, guild_id)

@discord.app_commands.guild_only
@tree.command(name="play", description="YouTubeの動画(音声)を再生させます。")
@app_commands.describe(url="YouTubeのURL")
async def play_command(interaction: discord.Interaction, url: str):
    try:
        if interaction.guild.voice_client is None:
            await interaction.response.send_message("ボイスチャンネルに接続していません。", ephemeral=True)
            return
        # URLがYouTubeの動画であるか確認
        valid_prefixes = (
            "https://www.youtube.com/watch",
            "https://youtube.com/watch",
            "https://m.youtube.com/watch",
            "https://music.youtube.com/watch",
            "https://youtu.be/",
            "https://www.youtube.com/shorts/",
            "https://youtube.com/shorts/",
        )
        if not any(url.startswith(p) for p in valid_prefixes):
            await interaction.response.send_message("有効なYouTubeのURLを入力してください。\n(例: https://www.youtube.com/watch?v=... / https://youtu.be/... / https://m.youtube.com/... など)", ephemeral=True)
            return
        
        global filename
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client

        music_queues[guild_id].append(url)

        if vc.is_playing() or vc.is_paused():
            await interaction.response.send_message("現在別の曲を再生中のためキューに曲を追加しました。", ephemeral=True)

        else:#キューに曲がない場合はそのまま再生を開始、再生後にplay_nextで次の曲を再生
            await interaction.response.defer()#応答を遅延(エラー回避)
            await play_next(interaction, guild_id)
    except IndexError:
        await interaction.followup.send("Error!\nurlに入力された値が異常値です。もう一度リンクを確認してください。", ephemeral=True)
    except Exception as e:
        print(f"play_command エラー: {e}")
        traceback.print_exc()
        try:
            await interaction.response.send_message("Error!\n動画が正常に取得できませんでした。(年齢制限のかかっている動画は取得できないので、別の動画を指定してください。）\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
            if music_queues[guild_id]:
                await play_next(interaction, guild_id)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("Error!\n動画が正常に取得できませんでした。(年齢制限のかかっている動画は取得できないので、別の動画を指定してください。）\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
            if music_queues[guild_id]:
                await play_next(interaction, guild_id)

#キューを表示
@discord.app_commands.guild_only
@tree.command(name="show_queue", description="現在のキューを表示します。")
async def show_queue(interaction: discord.Interaction):
    try:
        guild_id = interaction.guild.id
        if music_queues[guild_id]:
            msg = "\n".join(music_queues[guild_id])
            await interaction.response.send_message(f"現在のキュー:\n{msg}\n", ephemeral=True)
        else:
            await interaction.response.send_message("現在キューは空です。", ephemeral=True)
    except:
        try:
            await interaction.response.send_message("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)

# 再生再開
@discord.app_commands.guild_only
@tree.command(name="replay", description="再生を再開します。")
async def replay_command(interaction: discord.Interaction):
    try:
        guild_id = interaction.guild.id
        
        if interaction.guild.voice_client is None:
            await interaction.response.send_message("接続していません。", ephemeral=True)
            return
        #botの直前のメッセージを削除
        if guild_id in last_bot_message:
            try:
                print("OK")
                await last_bot_message[guild_id].delete()
            except Exception:
                pass
            del last_bot_message[guild_id]
        vc = interaction.guild.voice_client
        if vc.is_paused():
            vc.resume()

            await interaction.response.defer()
            msg = await interaction.followup.send("再生を再開しました。", view=Play_Control_1(timeout=None))
            last_bot_message[guild_id] = msg #メッセージを格納し、次回コマンド実行時に削除
            
        else:
            await interaction.response.send_message("何も再生していません。", ephemeral=True)
    except:
        try:
            await interaction.response.send_message("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)

# 再生停止
@discord.app_commands.guild_only
@tree.command(name="stop", description="再生を停止します。キューに次の曲がある場合は次の曲を再生します。")
async def stop_command(interaction: discord.Interaction):
    try:
        guild_id = interaction.guild.id

        if interaction.guild.voice_client is None:
            await interaction.response.send_message("接続していません。", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if not vc.is_playing():
            await interaction.response.send_message("再生していません。", ephemeral=True)
        else:
            #botの直前のメッセージを削除
            if guild_id in last_bot_message:
                try:
                    await last_bot_message[guild_id].delete()
                except Exception:
                    pass
                del last_bot_message[guild_id]

            vc.stop()
            time.sleep(1)#アクセス制限に引っかかるのでクッション
            global filename
            if filename != "":#再生したファイルを削除
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception as e:
                        print(f"ファイル削除エラー: {e}")
                filename = ""
            
            await interaction.response.defer()
            await interaction.followup.send("再生を停止しました。",ephemeral=True)

    except Exception as e:
        print(f"stop_command エラー: {e}")
        traceback.print_exc()
        try:
            await interaction.response.send_message("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
# 一時停止
@discord.app_commands.guild_only
@tree.command(name="pause", description="再生を一時停止します。")
async def pause_command(interaction: discord.Interaction):
    try:
        if interaction.guild.voice_client is None:
            await interaction.response.send_message("接続していません。", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if not vc.is_playing():
            await interaction.response.send_message("再生していません。", ephemeral=True)
        else:
            guild_id = interaction.guild.id

            #botの直前のメッセージを削除
            if guild_id in last_bot_message:
                try:
                    await last_bot_message[guild_id].delete()
                except Exception:
                    pass
                del last_bot_message[guild_id]

            vc.pause()

            await interaction.response.defer()
            msg = await interaction.followup.send("一時停止しました。",view=Play_Control_2(timeout=None))
            last_bot_message[guild_id] = msg #メッセージを格納し、次回コマンド実行時に削除
    except:
        try:
            await interaction.response.send_message("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)

@tree.command(name='hello', description='こんにちは！')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(content='Hello, World!',ephemeral=True)

@tree.command(name="say",description="Botがテキストを送信します")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(text="送信するテキストを設定できます",picture="画像をアップロードできます")
async def say_command(interaction: discord.Interaction,text:str = None,picture:discord.Attachment = None):
    try:
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
    except:
        try:
            await interaction.response.send_message("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send("Error!\n何度もエラーが発生する場合は <@957152000313786459> まで連絡をお願いします。", ephemeral=True)

###Commands End###
if __name__ == '__main__':
    client.run("Your token here")