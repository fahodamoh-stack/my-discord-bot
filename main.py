import discord
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- 1. جزء الـ Web Server (للـ 24/7) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "البوت شغال 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- 2. كلاسات الأزرار (هنا السر!) ---

# زر فتح التذكرة
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # timeout=None مهم عشان الأزرار متفصلش

    @discord.ui.button(label="فتح تذكرة", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("تم فتح تذكرة لك!", ephemeral=True)
        # هنا تقدر تضيف كود إنشاء قناة جديدة (channel creation)

# زر التحكم في التذكرة (إغلاقها مثلاً)
class TicketManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("جاري إغلاق التذكرة...", ephemeral=True)

# --- 3. إعدادات البوت ---
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    # تسجيل الأزرار عشان البوت يفتكرها لو عمل ريستارت
    bot.add_view(TicketPanelView())
    bot.add_view(TicketManageView())
    await bot.sync_commands()
    print("✅ البوت شغال يا باشا!")

@bot.slash_command(name="setup_tickets")
async def setup(ctx):
    embed = discord.Embed(title="نظام التذاكر", description="اضغط الزر لفتح تذكرة", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketPanelView())
    await ctx.respond("تم إرسال اللوحة", ephemeral=True)

bot.run(os.getenv('TOKEN'))
