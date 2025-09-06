import os
import requests
import threading
import time
import colorama
from colorama import Fore, init
import json
import platform

# Only set console title on Windows
if platform.system() == "Windows":
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW("Axi Panel || STATUS: Online ")

init(convert=True)

# Colors
y = Fore.LIGHTYELLOW_EX
b = Fore.LIGHTBLUE_EX
w = Fore.LIGHTWHITE_EX
lr = Fore.LIGHTRED_EX
lb = Fore.LIGHTBLACK_EX
r = Fore.RED
m = Fore.MAGENTA
g = Fore.GREEN

# Load config
if not os.path.exists('settings.json'):
    print(f"{Fore.RED}Error: settings.json not found!")
    exit()

with open('settings.json') as config_file:
    config = json.load(config_file)
    CAPMONSTER = config.get('Capmonster_apikey', '')

done = 0
retries = 0

# Load tokens
if os.path.exists("tokens.txt"):
    with open("tokens.txt", "r") as f:
        tokens = [t.strip() for t in f.readlines() if t.strip()]
else:
    print(f"{Fore.RED}Error: tokens.txt not found!")
    tokens = []

# Helper functions
def removeDuplicates(file):
    lines_seen = set()
    with open(file, "r+") as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
            if i not in lines_seen:
                f.write(i)
                lines_seen.add(i)
        f.truncate()

def save_tokens():
    with open("tokens.txt", "w") as f:
        for token in tokens:
            f.write(token + "\n")

def removeToken(token: str):
    global tokens
    tokens = [t for t in tokens if t != token]
    save_tokens()

def boost(token, invite):
    global done, retries
    try:
        headers = {
            'authorization': token,
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0',
        }

        r = requests.get(
            "https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots",
            headers=headers
        )
        if r.status_code != 200:
            print(f"[{Fore.RED}x{Fore.RESET}] Token failed: {token[:10]}...")
            retries += 1
            return

        slots = r.json()
        if not slots:
            return

        guid = None
        for _ in range(15):
            join_server = requests.post(
                f"https://discord.com/api/v9/invites/{invite}",
                headers=headers,
                json={}
            )
            if join_server.status_code == 200:
                guild_data = join_server.json()
                guid = guild_data.get("guild", {}).get("id")
                done += 1
                print(f"[{Fore.GREEN}+{Fore.WHITE}] Boosted server with token: {token[:10]}...")
                break

    except Exception as e:
        print(f"[{Fore.RED}!{Fore.RESET}] Error boosting: {e}")
        retries += 1

# Auto variables
INVITE = "dePgjtPY"  # Discord invite link code
AMOUNT = 5           # Number of boosts to perform

print(f"{b}Starting boosting process for invite: {INVITE}")

# Remove duplicate tokens first
removeDuplicates("tokens.txt")

# Boost loop
for token in tokens.copy():
    if done >= AMOUNT:
        break
    boost(token, INVITE)
    removeToken(token)

print(f"{Fore.LIGHTBLUE_EX}Completed {done} boosts with {len(tokens)} tokens remaining.")
print(f"{Fore.LIGHTYELLOW_EX}Retries: {retries}")
