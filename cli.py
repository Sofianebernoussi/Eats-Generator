import asyncio
import random
from pathlib import Path
from colorama import Fore, init

from main import AccountGenerator
from otp import IMAPClient

init(autoreset=True)


class CLIInterface:
    def __init__(self):
        self.generator = AccountGenerator()

    def display_banner(self):
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}ACCOUNT GENERATOR - EDUCATIONAL TOOL")
        print(f"{Fore.RED}⚠️  FOR EDUCATIONAL PURPOSES ONLY ⚠️")
        print(f"{Fore.CYAN}{'='*50}\n")

    def display_menu(self):
        print(f"{Fore.GREEN}Select option:")
        print("1) Generate using IMAP")
        print("2) Generate using Hotmail")
        print("3) Exit")
        print(f"{Fore.YELLOW}\nChoice: ", end="")

    async def run(self):
        self.display_banner()

        while True:
            self.display_menu()
            choice = input().strip()

            if choice == '1':
                await self.generate_with_imap()
            elif choice == '2':
                await self.generate_with_hotmail()
            elif choice == '3':
                print(f"\n{Fore.CYAN}Exiting...")
                break
            else:
                print(f"{Fore.RED}Invalid option!")

    async def generate_with_imap(self):
        config = self.generator.config.get('imap', {})

        if not config:
            print(f"{Fore.RED}[!] IMAP configuration not found in config.json")
            return

        # Check for default placeholder values
        username = config.get('username', '')
        password = config.get('password', '')
        domains = config.get('domains', [])

        if username == 'your_email@gmail.com' or password == 'your_app_password':
            print(f"{Fore.RED}[!] ERROR: Default placeholder values detected in config.json")
            print(f"{Fore.YELLOW}[!] Please edit config.json and replace the following with your actual credentials:")
            print(f"{Fore.YELLOW}    - username: your_email@gmail.com")
            print(f"{Fore.YELLOW}    - password: your_app_password")
            return

        if not domains:
            print(f"{Fore.RED}[!] No domains configured in config.json")
            return

        # Check for placeholder domains
        placeholder_domains = ['yourdomain.com', 'anotherdomain.com', '<- MULTIPLE DOMAINS OPTIONAL']
        if any(domain in placeholder_domains for domain in domains):
            print(f"{Fore.RED}[!] ERROR: Default placeholder domains detected in config.json")
            print(f"{Fore.YELLOW}[!] Please edit config.json and replace placeholder domains with real ones:")
            print(f"{Fore.YELLOW}    Remove: yourdomain.com, anotherdomain.com")
            print(f"{Fore.YELLOW}    Add your own domains for IMAP email generation")
            return

        print(f"{Fore.CYAN}How many accounts to generate? ", end="")
        try:
            count = int(input().strip())
            if count <= 0:
                print(f"{Fore.RED}[!] Count must be positive")
                return
        except ValueError:
            print(f"{Fore.RED}[!] Invalid number")
            return

        email_client = IMAPClient(
            config['username'],
            config['password'],
            config.get('server', 'imap.gmail.com')
        )

        successful = 0
        failed = 0

        for i in range(count):
            domain = random.choice(domains)
            print(f"\n{Fore.CYAN}[{i+1}/{count}] Generating account on {domain}...")

            result = await self.generator.create_account(domain, email_client)

            if result:
                successful += 1
            else:
                failed += 1

        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.GREEN}[✓] Successful: {successful}")
        print(f"{Fore.RED}[✗] Failed: {failed}")
        print(f"{Fore.CYAN}{'='*50}\n")

    async def generate_with_hotmail(self):
        hotmail_file = Path('hotmailaccs.txt')

        if not hotmail_file.exists():
            print(f"{Fore.RED}[!] hotmailaccs.txt not found")
            return

        accounts = [line.strip() for line in hotmail_file.read_text().strip().split('\n') if line.strip()]

        if not accounts:
            print(f"{Fore.RED}[!] hotmailaccs.txt is empty")
            return

        # Check for default placeholder values
        placeholder_found = False
        for account in accounts:
            if account.startswith('examplehotmail@hotmail.com:password1234'):
                placeholder_found = True
                break

        if placeholder_found:
            print(f"{Fore.RED}[!] ERROR: Default placeholder values detected in hotmailaccs.txt")
            print(f"{Fore.YELLOW}[!] Please edit hotmailaccs.txt and replace with your actual Hotmail accounts.")
            print(f"{Fore.YELLOW}[!] Format: email@hotmail.com:password (one per line)")
            print(f"{Fore.YELLOW}    Remove: examplehotmail@hotmail.com:password1234")
            print(f"{Fore.YELLOW}    Add your real Hotmail accounts and passwords")
            return

        print(f"{Fore.CYAN}Available Hotmail accounts: {len(accounts)}")
        print(f"{Fore.CYAN}How many accounts to generate? (0 for all): ", end="")

        try:
            count = int(input().strip())
            if count < 0:
                print(f"{Fore.RED}[!] Count cannot be negative")
                return
            if count == 0:
                count = len(accounts)
            if count > len(accounts):
                print(f"{Fore.YELLOW}[!] Only {len(accounts)} hotmail accounts available, using all")
                count = len(accounts)
        except ValueError:
            print(f"{Fore.RED}[!] Invalid number")
            return

        successful = 0
        failed = 0

        for i in range(count):
            account = accounts[i]
            try:
                parts = account.split(':')
                if len(parts) != 2:
                    print(f"{Fore.RED}[!] Invalid format in hotmailaccs.txt line {i+1}")
                    failed += 1
                    continue

                username, password = parts
                email_client = IMAPClient(
                    username,
                    password,
                    'imap.zmailservice.com'
                )
                email_client.username = username

                print(f"\n{Fore.CYAN}[{i+1}/{count}] Generating with {username}...")

                result = await self.generator.create_account('hotmail.com', email_client)

                if result:
                    successful += 1
                else:
                    failed += 1

            except Exception as e:
                print(f"{Fore.RED}[!] Error processing account {i+1}: {e}")
                failed += 1
                continue

        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.GREEN}[✓] Successful: {successful}")
        print(f"{Fore.RED}[✗] Failed: {failed}")
        print(f"{Fore.CYAN}{'='*50}\n")


async def main():
    cli = CLIInterface()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
