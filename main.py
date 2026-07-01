import discord
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- ويب سيرفر للـ 24/7 ---
app = Flask(__name__)
@app.route('/')
def home(): return "البوت شغال 24/7!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

# --- كلاس زرار القفل ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.red, custom_id="close_btn")
    async def close(self, button, interaction):
        await interaction.response.send_message("جاري إغلاق التذكرة...")
        await interaction.channel.delete()

# --- كلاس لوحة الأزرار الرئيسية ---
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction, ticket_type):
        channel_name = f"{ticket_type}-{interaction.user.name}"
        if discord.utils.get(interaction.guild.channels, name=channel_name):
            await interaction.response.send_message("❌ لديك تذكرة مفتوحة بالفعل!", ephemeral=True)
            return

        guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), 
                      interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        
        # المنشن للرول الخاص بالإدارة
        support_role_id = 1521078717709942835
        await channel.send(f"أهلاً {interaction.user.mention}! <@&{support_role_id}>، الرجاء المساعدة.", view=CloseTicketView())
        await interaction.response.send_message(f"✅ تم فتح تذكرة {ticket_type}: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary, emoji="🔧", custom_id="support")
    async def support(self, button, interaction): await self.create_ticket(interaction, "support")
    
    @discord.ui.button(label="Partner", style=discord.ButtonStyle.secondary, emoji="🤝", custom_id="partner")
    async def partner(self, button, interaction): await self.create_ticket(interaction, "partner")

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify")
    async def verify(self, button, interaction): await self.create_ticket(interaction, "verify")

    @discord.ui.button(label="Report", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="report")
    async def report(self, button, interaction): await self.create_ticket(interaction, "report")

# --- تشغيل البوت وتسجيل الأزرار ---
@bot.event
async def on_ready():
    bot.add_view(TicketPanelView())
    bot.add_view(CloseTicketView())
    await bot.sync_commands()
    print("✅ البوت شغال والزراير متسجلة بنجاح!")

@bot.slash_command(name="setup", description="إرسال لوحة التذاكر")
async def setup(ctx):
    embed = discord.Embed(title="🎫 نظام التذاكر", description="اضغط الزر المناسب لفتح تذكرتك:", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketPanelView())
    await ctx.respond("تم إرسال اللوحة بنجاح!", ephemeral=True)

bot.run(os.getenv('TOKEN'))
