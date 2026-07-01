import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال يا باشا!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# استدعي الوظيفة دي قبل الـ bot.run
keep_alive()

STAFF_ROLE_ID = 1521078717709942835 

intents = discord.Intents.all()
bot = commands.Bot(intents=intents)

# 1. كلاس للأزرار الـ 6 (اللوحة)
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # timeout=None عشان الأزرار ما تموتش

    # إضافة الأزرار الستة
    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary, custom_id="ticket_support", emoji="🛠️")
    async def support(self, btn, interaction): await self.create_ticket(interaction, "Support")
    
    @discord.ui.button(label="Partner", style=discord.ButtonStyle.secondary, custom_id="ticket_partner", emoji="🤝")
    async def partner(self, btn, interaction): await self.create_ticket(interaction, "Partner")

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, custom_id="ticket_verify", emoji="✅")
    async def verify(self, btn, interaction): await self.create_ticket(interaction, "Verify")

    @discord.ui.button(label="Report", style=discord.ButtonStyle.danger, custom_id="ticket_report", emoji="🚨")
    async def report(self, btn, interaction): await self.create_ticket(interaction, "Report")

    @discord.ui.button(label="Suggestion", style=discord.ButtonStyle.primary, custom_id="ticket_suggestion", emoji="💡")
    async def suggestion(self, btn, interaction): await self.create_ticket(interaction, "Suggestion")

    @discord.ui.button(label="Other", style=discord.ButtonStyle.secondary, custom_id="ticket_other", emoji="📄")
    async def other(self, btn, interaction): await self.create_ticket(interaction, "Other")

    async def create_ticket(self, interaction, ticket_type):
        # هنا كود الفحص (التيكت الواحد)
        guild = interaction.guild
        user = interaction.user
        existing = discord.utils.find(lambda c: c.topic == str(user.id), guild.text_channels)
        if existing:
            return await interaction.response.send_message(f"❌ لديك تذكرة بالفعل: {existing.mention}", ephemeral=True)
        
        role = guild.get_role(STAFF_ROLE_ID)
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            topic=str(user.id),
            overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        )
        # إرسال أزرار التحكم (Claim/Close) داخل التيكت
        await channel.send(f"{user.mention} | {role.mention} تم فتح تذكرة من نوع **{ticket_type}**.", view=TicketManageView())
        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)

# 2. كلاس التحكم داخل التيكت (Claim & Close)
class TicketManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green, custom_id="claim_btn")
    async def claim(self, btn, interaction):
        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]: return await interaction.response.send_message("❌", ephemeral=True)
        await interaction.response.send_message(f"✅ استلمها {interaction.user.mention}")

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id="close_btn")
    async def close(self, btn, interaction):
        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]: return await interaction.response.send_message("❌", ephemeral=True)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    bot.add_view(TicketPanelView()) # تسجيل لوحة الأزرار
    bot.add_view(TicketManageView()) # تسجيل أزرار التحكم
    await bot.sync_commands()
    print("✅ البوت شغال يا باشا!")

@bot.slash_command(name="setup_tickets")
async def setup(ctx):
    embed = discord.Embed(title="نظام التذاكر", description="اضغط الزر لفتح تذكرة", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketPanelView())
    await ctx.respond("تم إرسال اللوحة", ephemeral=True)

bot.run(os.getenv('TOKEN'))