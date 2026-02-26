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
PARTNER_KANAL_ID = 1476496120258629710  # Partner Bekleme Kanalı
PARTNER_BASVURU_KANAL_ID = 1476579700775190859  # Partner Başvuru Kanalı
ONAY_KANAL_ID = 1476579074301366292  # Başvuru Onay Kanalı
EKIP_ALIM_KANAL_ID = 1476579896305254551  # Ekip Alım Kanalı

# Yetkili rollerin ID'lerini belirliyoruz
YETKILI_ROLLER = [
    1476496118157283431,  # Yetkili rolü 1
    1476496118119399575,  # Yetkili rolü 2
    1476496118119399572,  # Yetkili rolü 3
    1476496118119399569   # Yetkili rolü 4
]

# ✅ Klan Alım Modal
class KlanAlimModal(discord.ui.Modal, title="Klan Alım Formu"):
    klan_isim = discord.ui.TextInput(label="Klan İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    deneyim = discord.ui.TextInput(label="Minecraft Deneyimi (Yıl)", placeholder="Örneğin: 2 yıl")
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            deneyim = int(self.deneyim.value)
        except ValueError:
            await interaction.response.send_message("Geçerli bir yıl bilgisi girin!", ephemeral=True)
            return

        embed = discord.Embed(title="🛡️ Klan Alımı", color=0x2ecc71)
        embed.add_field(name="Klan İsmi", value=self.klan_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Minecraft Deneyimi", value=str(deneyim), inline=False)

        channel = bot.get_channel(EKIP_ALIM_KANAL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("Başvurunuz alındı ve onay için yetkililere iletildi.", ephemeral=True)

# ✅ Yetkili Alım Modal
class YetkiliAlimModal(discord.ui.Modal, title="Yetkili Alım Formu"):
    yetkili_isim = discord.ui.TextInput(label="Yetkili İsmi")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    deneyim = discord.ui.TextInput(label="Deneyim (Yıl)", placeholder="Örneğin: 2 yıl")
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            deneyim = int(self.deneyim.value)
        except ValueError:
            await interaction.response.send_message("Geçerli bir yıl bilgisi girin!", ephemeral=True)
            return

        embed = discord.Embed(title="🛡️ Yetkili Alımı", color=0x2ecc71)
        embed.add_field(name="Yetkili İsmi", value=self.yetkili_isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Deneyim", value=str(deneyim), inline=False)

        channel = bot.get_channel(ONAY_KANAL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("Yetkili başvurusu alındı ve onay için yetkililere iletildi.", ephemeral=True)

# ✅ Diğer Modal
class DigerModal(discord.ui.Modal, title="Diğer Başvuru Formu"):
    basvuru_turu = discord.ui.TextInput(label="Başvuru Türü")
    detay = discord.ui.TextInput(label="Detaylı Açıklama", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📝 Diğer Başvuru", color=0x3498db)
        embed.add_field(name="Başvuru Türü", value=self.basvuru_turu.value, inline=False)
        embed.add_field(name="Detaylı Açıklama", value=self.detay.value, inline=False)
        await interaction.response.send_message(embed=embed)

# Yetkili kontrolü
def kullanici_yetkili():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

# Kanal kontrolü (klanın başvuru ve yetkili alımı için)
def kanal_check(kanal_id):
    async def predicate(interaction: discord.Interaction):
        return interaction.channel.id == kanal_id
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")
    await bot.tree.sync()  # Komutları senkronize et
    print("Komutlar senkronize edildi.")

# Onay ve Red butonlarının işleyişi
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "onay":
            embed = discord.Embed(title="✅ Klan Başvurusu Onaylandı", color=0x2ecc71)
            embed.add_field(name="Klan İsmi", value=interaction.message.embeds[0].fields[0].value, inline=False)
            embed.add_field(name="Açıklama", value=interaction.message.embeds[0].fields[1].value, inline=False)
            embed.add_field(name="Minecraft Deneyimi", value=interaction.message.embeds[0].fields[2].value, inline=False)
            channel = bot.get_channel(ONAY_KANAL_ID)
            if channel:
                await channel.send(embed=embed)
            await interaction.response.send_message("Başvuru onaylandı ve ilgili kanala gönderildi.", ephemeral=True)

        elif interaction.data["custom_id"] == "red":
            await interaction.response.send_message("Başvuru reddedildi.", ephemeral=True)

# ✅ Slash Komutlar
@bot.tree.command(name="klanbasvurusu")
async def klanbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(KlanAlimModal())

@bot.tree.command(name="yetkili_alimi")
@kullanici_yetkili()
async def yetkili_alimi(interaction: discord.Interaction):
    await interaction.response.send_modal(YetkiliAlimModal())

@bot.tree.command(name="diger")
async def diger(interaction: discord.Interaction):
    await interaction.response.send_modal(DigerModal())

bot.run(TOKEN)
