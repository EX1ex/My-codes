import os
import sys
import subprocess
import socket
import random
import time

def install_dependencies():
    packages = ['selenium', 'tqdm', 'pysocks']
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install_dependencies()

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from tqdm import tqdm

class TeleReportExecutor:
    def __init__(self):
        self.blue = '\033[94m'
        self.red = '\033[91m'
        self.white = '\033[0m'
        self.green = '\033[92m'
        self.target_url = ""
        self.report_count = 0
        self.tor_ports = [9050, 9150, 9051, 5090]
        self.active_ports = []
        self.connection_mode = None

    def display_banner(self):
        os.system('clear')
        banner = f"""{self.blue}
 ████████╗███████╗██╗     ███████╗    ██████╗ ███████╗██████╗  ██████╗ ██████╗ ████████╗
 ╚══██╔══╝██╔════╝██║     ██╔════╝    ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
    ██║   █████╗  ██║     █████╗      ██████╔╝█████╗  ██████╔╝██║   ██║██████╔╝   ██║   
    ██║   ██╔══╝  ██║     ██╔══╝      ██╔══██╗██╔══╝  ██╔══██╗██║   ██║██╔══██╗   ██║   
    ██║   ███████╗███████╗███████╗    ██║  ██║███████╗██║  ██║╚██████╔╝██║  ██║   ██║   
    ╚═╝   ╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
    {self.white}
    made by : your_name
    telegram channel : @your_channel
    ---------------------------------------------------------
        """
        print(banner)

    def verify_tor_network(self):
        print(f"{self.blue}[*] Scanning Tor network...{self.white}")
        self.active_ports = []
        for port in self.tor_ports:
            print(f"{self.white}Port {port}: ", end="", flush=True)
            for _ in tqdm(range(10), desc="Checking", leave=False, ncols=40):
                time.sleep(0.02)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                print(f"{self.green}ok!{self.white}")
                self.active_ports.append(port)
            else:
                print(f"{self.red}false!{self.white}")
        
        if not self.active_ports:
            print(f"\n{self.red}[ERROR] Tor is required for this process!{self.white}")
            sys.exit()

    def run(self):
        self.display_banner()
        print(f"{self.blue}[1]{self.white} Normal Connection")
        print(f"{self.blue}[2]{self.white} Multi-Tor Connection")
        self.connection_mode = input(f"\n{self.blue}Choice: {self.white}")
        
        self.target_url = input(f"{self.blue}Target Link: {self.white}")
        
        if self.connection_mode == "2":
            self.verify_tor_network()

        port_idx = 0
        while True:
            driver = None
            try:
                options = Options()
                options.add_argument("--headless")
                
                mode_str = "Normal"
                if self.connection_mode == "2":
                    current_port = self.active_ports[port_idx % len(self.active_ports)]
                    options.set_preference("network.proxy.type", 1)
                    options.set_preference("network.proxy.socks", "127.0.0.1")
                    options.set_preference("network.proxy.socks_port", current_port)
                    options.set_preference("network.proxy.socks_version", 5)
                    mode_str = f"Tor:{current_port}"

                driver = webdriver.Firefox(options=options)
                driver.get(self.target_url)
                time.sleep(3)

                form_data = {
                    "reason": "This content violates terms.",
                    "Your email:": f"user{random.randint(100,999)}@gmail.com",
                    "Your phone number:": f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
                }

                for label, text in form_data.items():
                    try:
                        xpath = f"//*[contains(text(), '{label}')]/following::input[1] | //*[contains(text(), '{label}')]/following::textarea[1]"
                        field = driver.find_element(By.XPATH, xpath)
                        field.send_keys(text)
                    except: pass

                try:
                    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')] | //input[@type='submit']")
                    submit_btn.click()
                    time.sleep(2)
                except: pass

                self.report_count += 1
                print(f"{self.green}Report done {self.report_count} ({mode_str}){self.white}")
                
            except Exception:
                print(f"{self.red}[!] Connection issue. Retrying...{self.white}")
                if self.connection_mode == "2": port_idx += 1
            
            finally:
                if driver: driver.quit()
                time.sleep(1)

if __name__ == "__main__":
    executor = TeleReportExecutor()
    executor.run()
