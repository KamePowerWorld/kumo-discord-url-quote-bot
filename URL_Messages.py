import os
import discord
from discord.ext import commands
import re
import yaml

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def load_config():
    with open('config.yml', 'r') as config_file:
        return yaml.load(config_file, Loader=yaml.SafeLoader)

@bot.event
async def on_ready():
    global guild_id 
    print(f'Logged in as {bot.user.name}')

    config = load_config()
    guild_id = config.get('guild_id', None)
    if guild_id:
        guild = bot.get_guild(guild_id)
        
        if guild:
            await guild.chunk()

@bot.event
async def on_message(message:discord.Message):
    global guild_id  # global修飾子を使用して外部のguild_id変数を使用
    guild = message.guild  # メッセージが属するギルドを取得
    if guild and guild.id == guild_id:
        # メッセージリンクの正規表現パターン
        link_pattern = r'https://discord\.com/channels/\d+/\d+/\d+'
        matches = re.findall(link_pattern, message.content)

        for link in matches:
            link_parts = link.split('/')
            if len(link_parts) == 7:  # 正しいリンク形式である場合
                guild_id = int(link_parts[4])
                channel_id = int(link_parts[5])
                message_id = int(link_parts[6])
                guild = bot.get_guild(guild_id)
                channel = guild.get_channel(channel_id)
                msg = await channel.fetch_message(message_id)
                guild = bot.get_guild(guild_id)
                target_channel =  message.channel

                if target_channel:
                    embed = discord.Embed(
                        title="証拠メッセージ",
                        color=discord.Color.red()  # 赤色
                    )

                    embed.add_field(name="ID", value=message.author.name, inline=False)
                    embed.add_field(name="ニックネーム", value=message.author.mention, inline=False)

                    if isinstance(message.author, discord.Member) and message.author.nick is not None:
                        embed.add_field(name="サーバーニックネーム", value=message.author.nick, inline=False)

                    embed.add_field(name='引用メッセージ', value=msg.content, inline=False)
                    await target_channel.send(embed=embed)

    await bot.process_commands(message)

token = os.environ["DISCORD_TOKEN"]
bot.run(token)
