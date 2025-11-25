import asyncio
from pathlib import Path
from colorama import Fore, init

from main import AccountGenerator
from otp import IMAPClient  # Assure-toi que IMAPClient est bien importable

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
        print(f"{Fore.RED}[!] IMAP method is not supported in SOCKS5 version")
        print(f"{Fore.YELLOW}[!] Please use manual OTP entry instead")
        print(f"{Fore.YELLOW}[!] Run the main.py directly for manual mode")
        return

    async def generate_with_hotmail(self):
        hotmail_file = Path('hotmailaccs.txt')
        if not hotmail_file.exists():
            print(f"{Fore.RED}[!] hotmailaccs.txt not found")
            return

        accounts = [line.strip() for line in hotmail_file.read_text().strip().split('\n') if line.strip()]
        if not accounts:
            print(f"{Fore.RED}[!] hotmailaccs.txt is empty")
            return

        # Vérifie les placeholders
        if any(acc.startswith('examplehotmail@hotmail.com:password1234') for acc in accounts):
            print(f"{Fore.RED}[!] ERROR: Default placeholder values detected in hotmailaccs.txt")
            print(f"{Fore.YELLOW}[!] Please replace with actual Hotmail accounts.")
            return

        print(f"{Fore.CYAN}Available Hotmail accounts: {len(accounts)}")
        count = 0
        try:
            count = int(input(f"{Fore.CYAN}How many accounts to generate? (0 for all): ").strip())
            if count < 0:
                print(f"{Fore.RED}[!] Count cannot be negative")
                return
            if count == 0 or count > len(accounts):
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
                    print(f"{Fore.RED}[!] Invalid format in line {i+1}")
                    failed += 1
                    continue

                email_address, password = parts
                print(f"\n{Fore.CYAN}[{i+1}/{count}] Generating with {email_address}...")
                print(f"{Fore.YELLOW}[*] You will need to enter OTP manually")

                # Crée un IMAPClient avec le compte Hotmail
                email_client = IMAPClient(username=email_address, password=password)

                # Appelle la fonction create_account avec 'hotmail.com' et l'objet email_client
                result = await self.generator.create_account('hotmail.com', email_client)

                if result:
                    successful += 1
                else:
                    failed += 1

            except Exception as e:
                print(f"{Fore.RED}[!] Error processing account {i+1}: {e}")
                import traceback
                traceback.print_exc()
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
