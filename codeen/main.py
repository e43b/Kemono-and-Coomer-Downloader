import os

# Function to clear the console screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to download specific posts
def download_posts():
    clear_screen()
    print("Executing script to download specific posts...")
    os.system('python3 code/post.py')
    input("\nPress Enter to return to the menu...")

# Function to download all posts from a profile
def download_all_profile_posts():
    clear_screen()
    print("Executing script to download all posts from a profile...")
    os.system('python3 code/profile.py')
    input("\nPress Enter to return to the menu...")

# Function to download DMs from a profile
def download_dms():
    clear_screen()
    print("Executing script to download DMs from a profile...")
    os.system('python3 code/dm.py')
    input("\nPress Enter to return to the menu...")

# Function to customize download settings
def customize_settings():
    clear_screen()
    print("Executing script to customize download settings...")
    os.system('python3 settings.py')
    input("\nPress Enter to return to the menu...")

# Check and install necessary dependencies
def check_install_dependencies():
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Necessary libraries not found.")
        choice = input("Do you want to install the necessary libraries? (y/n): ").strip().lower()
        if choice == 'y':
            os.system('pip install -r requirements.txt')
        else:
            print("Installation canceled. The program may not function correctly.")
            input("\nPress Enter to continue...")

# Main menu
def menu():
    check_install_dependencies()

    while True:
        clear_screen()
        print("""
 _  __                                                   
| |/ /___ _ __ ___   ___  _ __   ___                     
| ' // _ \ '_ ` _ \ / _ \| '_ \ / _ \                    
| . \  __/ | | | | | (_) | | | | (_) |                   
|_|\_\___|_| |_| |_|\___/|_| |_|\___/                    
 / ___|___   ___  _ __ ___   ___ _ __                    
| |   / _ \ / _ \| '_ ` _ \ / _ \ '__|                   
| |__| (_) | (_) | | | | | |  __/ |                      
 \____\___/ \___/|_| |_| |_|\___|_|          _           
|  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __ 
| | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
| |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
|____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   

Created by E43b
GitHub: https://github.com/e43b
Discord: https://discord.gg/TaPhfXawcE
Project Repository: https://github.com/e43b/Kemono-and-Coomer-Downloader

With this script, you can download various posts or all posts from a profile on Kemono or Coomer, as well as download DMs from Kemono profiles:

Choose an option:
1 - Download 1 post or a few specific posts
2 - Download all posts from a profile
3 - Download DMs from a profile (currently only Kemono has a DM system)
4 - Customize the program's download settings
5 - Exit the program
""")
        option = input("Enter your choice (1/2/3/4/5): ")

        if option == '1':
            download_posts()
        elif option == '2':
            download_all_profile_posts()
        elif option == '3':
            download_dms()
        elif option == '4':
            customize_settings()
        elif option == '5':
            break
        else:
            print("Invalid option! Enter 1, 2, 3, 4, or 5.")
            input("Press Enter to continue...")

# Run the program
if __name__ == "__main__":
    menu()
