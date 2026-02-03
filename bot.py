import discord
from discord.ui import View, Button

from config import TOKEN, CHANNEL_ID, TURN_TIME
from game import state
from game.rps import bot_choice, check_winner
from game.wordchain import (
    load_memory,
    save_memory,
    learn,
    generate,
    last_word
)

# ===== DISCORD SETUP =====
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# ===== RPS VIEW =====
class RPSView(View):
    def __init__(self, player):
        super().__init__(timeout=30)
        self.player = player
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user == self.player

    @discord.ui.button(label="✂️ Kéo", style=discord.ButtonStyle.primary)
    async def keo(self, interaction, button):
        self.choice = "keo"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🪨 Búa", style=discord.ButtonStyle.primary)
    async def bua(self, interaction, button):
        self.choice = "bua"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="📄 Bao", style=discord.ButtonStyle.primary)
    async def bao(self, interaction, button):
        self.choice = "bao"
        self.stop()
        await interaction.response.defer()


# ===== EVENTS =====
@client.event
async def on_ready():
    load_memory()
    print("🤖 Bot đã online")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    content = message.content.strip().lower()
    if not content:
        return

    # Bot học mọi câu
    learn(content)
    save_memory()

    # ===== !stats → KÉO BÚA BAO =====
    if content == "!stats":
        view = RPSView(message.author)
        await message.channel.send("🎮 Chọn **Kéo – Búa – Bao**:", view=view)
        await view.wait()

        if not view.choice:
            await message.channel.send("⏰ Hết thời gian chọn")
            return

        bot_pick = bot_choice()
        result = check_winner(view.choice, bot_pick)

        if result == "draw":
            await message.channel.send(
                f"⚖️ Hòa! Bot cũng ra **{bot_pick}**\nGõ `!stats` để chơi lại"
            )
            return

        state.reset()

        if result == "player":
            state.turn_owner = message.author
            await message.channel.send(
                f"✅ Bạn thắng! Bot ra **{bot_pick}**\n👉 Bạn đi trước!"
            )
        else:
            state.turn_owner = client.user
            await message.channel.send(
                f"❌ Bot thắng! Bot ra **{bot_pick}**\n👉 Bot đi trước!"
            )

            # Bot nói trước
            reply = generate(None)
            if reply:
                state.used.add(reply)
                state.current_last = last_word(reply)
                state.set_deadline(TURN_TIME)
                await message.channel.send(f"🤖 {reply}")

        return

    # ===== GAME LOOP =====
    if not state.turn_owner:
        return

    if state.is_timeout():
        await message.channel.send(
            f"⏰ Hết thời gian! **{state.turn_owner.name}** thua!"
        )
        state.reset()
        return

    if message.author != state.turn_owner:
        return

    if state.current_last:
        if content.split()[0][0] != state.current_last:
            await message.channel.send(
                f"❌ Phải bắt đầu bằng chữ **{state.current_last}**"
            )
            return

    reply = generate(last_word(content))
    if not reply or reply in state.used:
        await message.channel.send("😵 Bot không nghĩ ra! Bạn thắng 🎉")
        state.reset()
        return

    state.used.add(reply)
    state.current_last = last_word(reply)
    state.set_deadline(TURN_TIME)

    await message.channel.send(f"🤖 {reply}")


# ===== RUN =====
client.run(TOKEN)
