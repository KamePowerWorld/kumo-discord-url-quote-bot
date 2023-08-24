import os
import discord
from discord.ext import commands
import re
import yaml

intents = discord.Intents.default()
intents.message_content = True 

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
async def on_message(message):
    if guild.id != guild_id :
        return
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
            target_channel = channel  # 通知を送るチャンネルを指定

            banned_by = None

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target == message.author:
                    banned_by = entry.user
                    break
            
            if target_channel:
                embed = discord.Embed(
                    title=f"{banned_by.name}",
                    color=discord.Color.red()  # 赤色
                )

                embed.add_field(name="ID", value=message.author.name, inline=False)
                embed.add_field(name="ニックネーム", value=message.author.display_name, inline=False)
                
                if isinstance(message.author, discord.Member) and message.author.nick is not None:
                    embed.add_field(name="サーバーニックネーム", value=message.author.nick, inline=False)
                

                embed.set_thumbnail(url=message.author.avatar_url)


                
                await target_channel.send(embed=embed)

    await bot.process_commands(message)

token = os.environ["DISCORD_TOKEN"]
bot.run(token)
