import asyncio
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
        print("1) Generate using IMAP (Manual OTP)")
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
        print(f"{Fore.RED}[!] IMAP method is not supported in this demo")
        return

    async def generate_with_hotmail(self):
        hotmail_file = Path('hotmailaccs.txt')
        if not hotmail_file.exists():
            print(f"{Fore.RED}[!] hotmailaccs.txt not found")
            return

        accounts = [line.strip() for line in hotmail_file.read_text().strip().split('\n') if line.strip()]
        
        # --- NOUVELLE OPTION NOM ---
        use_custom_name = input(f"{Fore.CYAN}Do you want to use a specific Name/Surname? (y/n): ").lower().strip() == 'y'
        custom_name = None
        if use_custom_name:
            custom_name = input(f"{Fore.CYAN}Enter full name (e.g. Jean Dupont): ").strip()
        # ---------------------------

        count = 0
        try:
            val = input(f"{Fore.CYAN}How many accounts? (0 for all): ").strip()
            count = int(val) if val else 0
            if count == 0 or count > len(accounts):
                count = len(accounts)
        except ValueError:
            return

        successful = 0
        for i in range(count):
            account = accounts[i]
            try:
                parts = account.split(':')
                if len(parts) != 2: continue
                email, password = parts
                
                email_client = IMAPClient(username=email, password=password)
                
                # ON PASSE LE CUSTOM_NAME ICI
                result = await self.generator.create_account('hotmail.com', email_client, custom_name=custom_name)

                if result: successful += 1

            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
                continue

        print(f"\n{Fore.GREEN}Finished. Success: {successful}")

async def main():
    cli = CLIInterface()
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main())