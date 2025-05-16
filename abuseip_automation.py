import os
import requests
import ipaddress
from dotenv import load_dotenv
import pyfiglet
from rich.console import Console
import json

# Load .env for Key
load_dotenv()

API_KEY = os.getenv("ABUSEIPDB_API_KEY")
if not API_KEY:
    raise ValueError("API-Key not set. Please set 'ABUSEIPDB_API_KEY'.")

DAYS = 30
BASE_URL = "https://api.abuseipdb.com/api/v2"
HEADERS = {
    "Accept": "application/json",
    "Key": API_KEY
}

def print_banner():
    console = Console()
    ascii_banner = pyfiglet.figlet_format("Automated IP Reputation Checker\n(AbuseIPDB)")
    console.print(f"[cyan]{ascii_banner}[/cyan]")
    console.print("[bold green]Author:[/bold green] Deniz Dinc\n")

def is_valid_ip(value):
    try:
        # Nur einzelne IP (kein Netzwerk)
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False

def check_ip(ip):
    url = f"{BASE_URL}/check"
    params = {
        "ipAddress": ip,
        "maxAgeInDays": DAYS
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def main():
    print_banner()
    console = Console()

    input_file = input("Please enter the path to the file containing IPs: ").strip()
    if not os.path.isfile(input_file):
        console.print(f"[red]File '{input_file}' not found![/red]")
        return

    with open(input_file, "r") as f:
        targets = [line.strip() for line in f if line.strip()]

    results_ips = {}

    for target in targets:
        if not is_valid_ip(target):
            console.print(f"[yellow]Skipping invalid IP or CIDR: {target}[/yellow]")
            continue
        try:
            console.print(f"Checking IP: {target}")
            result = check_ip(target)
            results_ips[target] = result
        except requests.HTTPError as e:
            console.print(f"[red]HTTP Error at {target}: {e}[/red]")
            results_ips[target] = {"error": str(e)}
        except Exception as e:
            console.print(f"[red]Error at {target}: {e}[/red]")
            results_ips[target] = {"error": str(e)}

    output_file = "abuseipdb_results_ips.json"
    with open(output_file, "w", encoding="utf-8") as f_ips:
        json.dump(results_ips, f_ips, ensure_ascii=False, indent=4)

    console.print(f"\n[bold green]Results saved to:[/bold green] {output_file}")

if __name__ == "__main__":
    main()
