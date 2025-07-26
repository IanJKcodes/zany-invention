import discord
from discord.ext import commands
import yt_dlp
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- HARDCODED TOKEN FOR TESTING ---
DISCORD_BOT_TOKEN = "MTM5ODQ3NDUxMjM1NzUyNzY5NQ.G5uRxW.riaQ1bPmAsCk5HZu2mwUw8Gz6B4M52VL7nzGWA"
SPOTIFY_CLIENT_ID = "63533997999b4d9495402c7ae535e958"
SPOTIFY_CLIENT_SECRET = "16d609882c8b4beab3b695176d3ba2ac"
# -----------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'options': '-vn'}

def get_youtube_url(search_query):
    with yt_dlp.YoutubeDL({'quiet': True, 'format': 'bestaudio'}) as ydl:
        info = ydl.extract_info(f"ytsearch:{search_query}", download=False)['entries'][0]
        return info['webpage_url']

@bot.event
async def on_ready():
    print(f'✅ Bot connected as {bot.user}')

@bot.command()
async def play(ctx, *, query):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
    else:
        await ctx.send("Join a voice channel first.")
        return

    if "spotify.com" in query:
        try:
            track = sp.track(query)
            query = f"{track['name']} {track['artists'][0]['name']}"
        except:
            await ctx.send("Spotify track fetch failed.")
            return

    url = get_youtube_url(query)
    vc = ctx.voice_client
    if vc.is_playing():
        vc.stop()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        vc.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS))

    await ctx.send(f"🎶 Now playing: {query}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped and left channel.")

bot.run(DISCORD_BOT_TOKEN)
