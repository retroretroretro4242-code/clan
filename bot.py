import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")  # Eğer environment variable kullanıyorsanız
# Eğer doğrudan token yazıyorsanız:
# TOKEN = "YOUR_DISCORD_BOT_TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Kanal ID'leri
ISTEK_KANAL_ID = 1476496120258629709  # Başvuru Kanalı
PARTNER_KANAL_ID = 1476579700775190859  # Partner Başvuru Kanalı
PARTNER_BASVURU_KANAL_ID = 1476579800419143781  # Partner Bekleme Kanalı
ONAY_KANAL_ID = 1476579074301366292  # Başvuru Onay Kanalı
EKIP_ALIM_KANAL_ID = 1476579896305254551  # Ekip Alım Kanalı

# Yetkili rollerin ID'lerini belirliyoruz
YETKILI_ROLLER = [
    1476496118157283431,  # Yetkili 1
    1476496118119399575,  # Yetkili 2
    1476496118119399572,  # Yetkili 3
    1476496118119399569   # Yetkili 4
]

# ✅ Ekip Alım Modal
class EkipAlimModal(discord.ui.Modal, title="Ekip Alım Başvuru Formu"):
    isim = discord.ui.TextInput(label="İsim")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    deneyim = discord.ui.TextInput(label="Deneyiminiz", placeholder="Ne kadar deneyiminiz var?")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎮 Ekip Alım Başvurusu", color=0x2ecc71)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Deneyim", value=self.deneyim.value, inline=False)
        # Başvuruyu Ekip Alım Kanalına gönder
        channel = bot.get_channel(EKIP_ALIM_KANAL_ID)
        if channel:
            await channel.send(embed=embed)
        await interaction.response.send_message("Başvurunuz alındı ve ekip alım kanalına gönderildi.", ephemeral=True)

# ✅ Yetkili Alım Modal
class YetkiliAlimModal(discord.ui.Modal, title="Yetkili Alım Başvuru Formu"):
    isim = discord.ui.TextInput(label="İsim")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    deneyim = discord.ui.TextInput(label="Deneyiminiz", placeholder="Ne kadar deneyiminiz var?")
    neden = discord.ui.TextInput(label="Neden Yetkili Olmak İstiyorsunuz?", placeholder="Açıklama")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="👮 Yetkili Alım Başvurusu", color=0x3498db)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Deneyim", value=self.deneyim.value, inline=False)
        embed.add_field(name="Neden", value=self.neden.value, inline=False)
        # Başvuruyu Yetkili Alım Kanalına gönder
        channel = bot.get_channel(EKIP_ALIM_KANAL_ID)
        if channel:
            await channel.send(embed=embed)
        await interaction.response.send_message("Başvurunuz alındı ve yetkili alım kanalına gönderildi.", ephemeral=True)

# ✅ Yardım Modal
class YardimModal(discord.ui.Modal, title="Yardım İsteği Formu"):
    sorun = discord.ui.TextInput(label="Sorununuz", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="💬 Yardım İsteği", color=0xf1c40f)
        embed.add_field(name="Sorun", value=self.sorun.value, inline=False)
        await interaction.response.send_message(embed=embed)

# Yetkili kontrolü
def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

# Kanal kontrolü (istek ve partner komutları için)
def kanal_check(kanal_id):
    async def predicate(interaction: discord.Interaction):
        return interaction.channel.id == kanal_id
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")
    await bot.tree.sync()  # Komutları senkronize et
    print("Komutlar senkronize edildi.")

# ✅ Slash Komutlar
@bot.tree.command(name="ekipalimi")
async def ekipalimi(interaction: discord.Interaction):
    await interaction.response.send_modal(EkipAlimModal())

@bot.tree.command(name="yetkilialimi")
async def yetkilialimi(interaction: discord.Interaction):
    await interaction.response.send_modal(YetkiliAlimModal())

@bot.tree.command(name="yardim")
@kanal_check(ISTEK_KANAL_ID)
async def yardim(interaction: discord.Interaction):
    await interaction.response.send_modal(YardimModal())

# Diğer eski komutları kaldırdım
bot.run(TOKEN)
