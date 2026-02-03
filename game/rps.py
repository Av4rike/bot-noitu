import random
CHOICES = ["keo", "bua", "bao"]
def bot_choice():
    return random.choice(CHOICES)
def check_winner(player, bot):
    if player == bot:
        return "draw"
    win = {
        "keo": "bao",
        "bua": "keo",
        "bao": "bua"
    }
    if win[player] == bot:
        return "player"
    return "bot"