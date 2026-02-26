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
ISTEK_KANAL_ID = 1475095722864017478
PARTNER_BASVURU_KANAL_ID = 1476579700775190859
PARTNER_ONAY_KANAL_ID = 1476496120258629710  # Partner başvuru onay kanalı
EKIP_ALIM_KANAL_ID = 1476579896305254551
KATEGORI_ID = 1474830960393453619  # Klan kategorisi ID

# Yetkili rollerin ID'lerini belirliyoruz
YETKILI_ROLLER = [
    1476496118157283431,
    1476496118119399575,
    1476496118119399572,
    1476496118119399569
]

# ✅ Partner Başvuru Modal
class PartnerBasvuruModal(discord.ui.Modal, title="Partner Başvuru Formu"):
    isim = discord.ui.TextInput(label="İsim")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    sunucu_uyelik = discord.ui.TextInput(label="Sunucu Üyelik (Sayı)", placeholder="Örneğin: 1500")
    sunucu_link = discord.ui.TextInput(label="Sunucu Linki", placeholder="https://")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            sunucu_uyelik = int(self.sunucu_uyelik.value)  # Sayıya dönüştürme
        except ValueError:
            await interaction.response.send_message("Sunucu üyelik sayısını geçerli bir sayı olarak girmeniz gerekiyor!", ephemeral=True)
            return

        embed = discord.Embed(title="🤝 Partner Başvurusu", color=0x2ecc71)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Sunucu Üyelik", value=str(sunucu_uyelik), inline=False)
        embed.add_field(name="Sunucu Linki", value=self.sunucu_link.value, inline=False)

        # Başvuru bilgilerini partner başvuru kanalına gönder
        channel = bot.get_channel(PARTNER_BASVURU_KANAL_ID)
        if channel:
            # Onay ve Red butonları ekleniyor
            view = discord.ui.View()
            onay_button = discord.ui.Button(label="Onayla", style=discord.ButtonStyle.green, custom_id="onay")
            red_button = discord.ui.Button(label="Reddet", style=discord.ButtonStyle.red, custom_id="red")
            view.add_item(onay_button)
            view.add_item(red_button)

            await channel.send(embed=embed, view=view)

        await interaction.response.send_message("Başvurunuz alındı ve onay için yetkililere iletildi.", ephemeral=True)

# ✅ Onay ve Red butonlarının işleyişi
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "onay":
            # Onaylandığında partner başvurusu bilgilerini Partner Onay kanalına gönder
            embed = discord.Embed(title="✅ Partner Başvurusu Onaylandı", color=0x2ecc71)
            embed.add_field(name="İsim", value=interaction.message.embeds[0].fields[0].value, inline=False)
            embed.add_field(name="Açıklama", value=interaction.message.embeds[0].fields[1].value, inline=False)
            embed.add_field(name="Sunucu Üyelik", value=interaction.message.embeds[0].fields[2].value, inline=False)
            embed.add_field(name="Sunucu Linki", value=interaction.message.embeds[0].fields[3].value, inline=False)
            channel = bot.get_channel(PARTNER_ONAY_KANAL_ID)
            if channel:
                await channel.send(embed=embed)
            await interaction.response.send_message("Başvuru onaylandı ve ilgili kanala gönderildi.", ephemeral=True)

        elif interaction.data["custom_id"] == "red":
            # Başvuru reddedildiğinde kullanıcıya mesaj gönder
            await interaction.response.send_message("Başvuru reddedildi.", ephemeral=True)

# ✅ Ekip Alım ve Klan Alım
class AlimModal(discord.ui.Modal, title="Ekip / Klan Alım Formu"):
    isim = discord.ui.TextInput(label="İsim")
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph)
    deneyim = discord.ui.TextInput(label="Minecraft Deneyimi (Yıl)", placeholder="Örneğin: 2 yıl")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            deneyim = int(self.deneyim.value)
        except ValueError:
            await interaction.response.send_message("Geçerli bir yıl bilgisi girin!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🛡️ Klan/Ekip Alım Başvurusu", color=0x2ecc71)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Minecraft Deneyimi", value=str(deneyim), inline=False)

        # Başvuru bilgilerini ekip alım kanalı veya başka bir kanal gönderebilirsiniz
        channel = bot.get_channel(EKIP_ALIM_KANAL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("Başvurunuz alındı ve yetkililere iletildi.", ephemeral=True)

@bot.tree.command(name="ekipalimi")
async def ekip_alim(interaction: discord.Interaction):
    await interaction.response.send_modal(AlimModal())

# ✅ Yetkili Alım
class YetkiliAlimModal(discord.ui.Modal, title="Yetkili Alım Formu"):
    isim = discord.ui.TextInput(label="İsim")
    deneyim = discord.ui.TextInput(label="Yetkili Deneyimi (Yıl)", placeholder="Örneğin: 1 yıl")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            deneyim = int(self.deneyim.value)
        except ValueError:
            await interaction.response.send_message("Geçerli bir yıl bilgisi girin!", ephemeral=True)
            return
        
        embed = discord.Embed(title="👑 Yetkili Alım Başvurusu", color=0x2ecc71)
        embed.add_field(name="İsim", value=self.isim.value, inline=False)
        embed.add_field(name="Yetkili Deneyimi", value=str(deneyim), inline=False)

        # Başvuru bilgilerini yetkili alım kanalına gönder
        channel = bot.get_channel(EKIP_ALIM_KANAL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("Başvurunuz alındı ve yetkililere iletildi.", ephemeral=True)

@bot.tree.command(name="yetkilialimi")
async def yetkili_alim(interaction: discord.Interaction):
    await interaction.response.send_modal(YetkiliAlimModal())

# ✅ Partner Başvurusu Slash Komutu
@bot.tree.command(name="partnerbasvurusu")
async def partnerbasvurusu(interaction: discord.Interaction):
    await interaction.response.send_modal(PartnerBasvuruModal())

@bot.event
async def on_ready():
    print(f"Bot hazır: {bot.user}")
    await bot.tree.sync()  # Komutları senkronize et
    print("Komutlar senkronize edildi.")

bot.run(TOKEN)
