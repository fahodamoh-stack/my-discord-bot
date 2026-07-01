import discord
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- ويب سيرفر للـ 24/7 ---
app = Flask(__name__)
@app.route('/')
def home(): return "البوت شغال 24/7"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

# --- زرار القفل ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="إغلاق التذكرة", style=discord.ButtonStyle.red, custom_id="close_btn")
    async def close(self, button, interaction):
        await interaction.response.send_message("جاري إغلاق التذكرة...")
        await interaction.channel.delete()

# --- زرار فتح التذكرة ---
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة", style=discord.ButtonStyle.green, custom_id="open_btn")
    async def open_ticket(self, button, interaction):
        # 1. منع فتح أكثر من تكت (بنتأكد إن القناة مش موجودة باسمه)
        channel_name = f"تذكرة-{interaction.user.name}"
        if discord.utils.get(interaction.guild.channels, name=channel_name):
            await interaction.response.send_message("عندك تذكرة مفتوحة بالفعل!", ephemeral=True)
            return

        # 2. إنشاء التكت
        guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), 
                      interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        
        # 3. المنشن (غير 'SUPPORT_ROLE_ID' بأيدي الرول بتاعك)
        support_role = "<1521078717709942835>" 
        await channel.send(f"أهلاً {interaction.user.mention}! {support_role}، فيه شخص محتاج مساعدة.", view=CloseTicketView())
        await interaction.response.send_message(f"تم فتح تذكرتك: {channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(TicketPanelView())
    bot.add_view(CloseTicketView())
    await bot.sync_commands()
    print("✅ البوت شغال والزراير متسجلة!")

@bot.slash_command(name="setup_tickets")
async def setup(ctx):
    await ctx.send("اضغط لفتح تذكرة:", view=TicketPanelView())
    await ctx.respond("تم!", ephemeral=True)

bot.run(os.getenv('TOKEN'))
