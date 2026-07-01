import discord
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- ويب سيرفر ---
app = Flask(__name__)
@app.route('/')
def home(): return "البوت شغال 24/7!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

# --- لوحة الأزرار الكبيرة ---
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # 1. زرار الدعم
    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary, emoji="🔧", custom_id="btn_support")
    async def support(self, button, interaction):
        await interaction.response.send_message("تم فتح تذكرة دعم فني!", ephemeral=True)

    # 2. زرار الشراكة
    @discord.ui.button(label="Partner", style=discord.ButtonStyle.secondary, emoji="🤝", custom_id="btn_partner")
    async def partner(self, button, interaction):
        await interaction.response.send_message("تم فتح تذكرة شراكة!", ephemeral=True)

    # 3. زرار التحقق
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="btn_verify")
    async def verify(self, button, interaction):
        await interaction.response.send_message("جاري التحقق...", ephemeral=True)

    # 4. زرار التبليغ
    @discord.ui.button(label="Report", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="btn_report")
    async def report(self, button, interaction):
        await interaction.response.send_message("تم استلام بلاغك!", ephemeral=True)

@bot.event
async def on_ready():
    # لازم نسجل الـ View ده عشان الأزرار تشتغل
    bot.add_view(TicketPanelView())
    await bot.sync_commands()
    print("✅ اللوحة جاهزة والأزرار متسجلة!")

@bot.slash_command(name="setup")
async def setup(ctx):
    embed = discord.Embed(title="نظام التذاكر", description="اضغط الزر المناسب:", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketPanelView())
    await ctx.respond("تم إرسال اللوحة!", ephemeral=True)

bot.run(os.getenv('TOKEN'))
