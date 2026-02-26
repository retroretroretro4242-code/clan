import discord
from discord.ext import commands
from discord.ui import View, Select
import os
from dotenv import load_dotenv

# .env dosyasını yükleyelim
load_dotenv()

# Token'ı .env dosyasından alıyoruz
TOKEN = os.getenv("TOKEN")

# Intents ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Botu oluşturuyoruz
bot = commands.Bot(command_prefix="!", intents=intents)

# Kanal ID'leri
KATEGORI_ID = 1474830960393453619  # Klan kategorisi ID
PARTNER_BASVURU_KANAL_ID = 1476538995231162418  # Partner başvuru kanal ID'si

# Yetkili rollerin ID'leri
YETKILI_ROL = 1384294618195169311  # Yetkili rolü ID

# =============================================

# Partner Başvuru Modal
class PartnerBasvuruModal(discord.ui.Modal, title="Klan Başvuru Formu"):
    klan_isim = discord.ui.TextInput(label="Klan İsmi")
    aciklama = discord.ui.TextInput(label="Klan Açıklaması", style=discord.TextStyle.paragraph)
    deneyim = discord.ui.TextInput(label="Minecraft Deneyimi (Yıl)", placeholder="Örneğin: 2 yıl")
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            deneyim = int(self.deneyim.value)
        except ValueError:
            await interaction.response.send_message("Geçerli bir yıl bilgisi girin!", ephemeral=True)
            return
        
        # Başvuru embed olarak gönderilecek
        embed = discord.Embed(title="🛡️ Klan Başvurusu", color=0x2ecc71)
        embed.add_field(name="Klan İsmi", value=self.klan_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Minecraft Deneyimi", value=str(deneyim), inline=False)

        # Başvuruyu partner başvuru kanalına gönder
        channel = bot.get_channel(PARTNER_BASVURU_KANAL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("Başvurunuz alındı ve onay için yetkililere iletildi.", ephemeral=True)

# Ticket Kategorisi Seçimi
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Ekip Alım", description="Yeni bir ekip alım talebi", emoji="⚔️"),
            discord.SelectOption(label="Yardım", description="Klan hakkında yardım talebi", emoji="🆘"),
            discord.SelectOption(label="Diğer", description="Genel talepler", emoji="❓"),
        ]
        super().__init__(placeholder="Bir kategori seç...", options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(KATEGORI_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(YETKILI_ROL): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Sons of Valtheris Klan Destek",
            description=f"{interaction.user.mention} talebiniz oluşturuldu.\n\nYetkililer en kısa sürede sizinle ilgilenecektir.",
            color=0x2f3136
        )

        await channel.send(f"<@&{YETKILI_ROL}>", embed=embed)

        await interaction.response.send_message(
            f"Ticket oluşturuldu: {channel.mention}",
            ephemeral=True
        )

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# Bot komutları
@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")

    # Komutları Discord'a kaydet
    await bot.tree.sync()
    print("Komutlar başarıyla kaydedildi.")

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="Sons of Valtheris Klan Ticket Sistemi",
        description="📌 **Destek Merkezi**\n\nAşağıdaki seçeneklerden birini seçerek ticket oluşturabilirsiniz.\n\n⚠ Gereksiz ticket açmayın.",
        color=0x2f3136
    )

    embed.set_footer(text="Sons of Valtheris Klanı Destek Sistemi")

    await ctx.send(embed=embed, view=TicketView())

# Partner başvuru komutu
@bot.tree.command(name="partnerbasvurusu")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())

# Ekip alım komutu
@bot.tree.command(name="ekipalimi")
async def ekip_alimi(interaction: discord.Interaction):
    await interaction.response.send_message("Ekip alımı başvurusu aktif.")

# Yardım komutu
@bot.tree.command(name="yardim")
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Yardım Menüsü",
        description="Aşağıdaki komutları kullanarak botu kontrol edebilirsiniz:",
        color=0x3498db
    )
    embed.add_field(name="/ekipalimi", value="Ekip alımı başvurusunu görüntüler.", inline=False)
    embed.add_field(name="/partnerbasvurusu", value="Partner başvuru formunu açar.", inline=False)
    await interaction.response.send_message(embed=embed)

# Botu çalıştırıyoruz
bot.run(TOKEN)
