import os
import json

# URL of the documentation
DOCUMENTATION_URL = "https://github.com/e43b/Kemono-and-Coomer-Downloader/blob/main/codeen/doc.md"

# Function to load configurations from a JSON file
def load_configurations(file_name):
    try:
        with open(file_name, 'r') as file:
            configurations = json.load(file)
    except FileNotFoundError:
        configurations = {}
    return configurations

# Function to save configurations to a JSON file
def save_configurations(configurations, file_name):
    with open(file_name, 'w') as file:
        json.dump(configurations, file, indent=4)

# Function to display the main menu and get the user's choice
def display_main_menu():
    clear_console()
    print("Configure the System\n")
    print("Enter 1 to configure the post download system")
    print("Enter 2 to configure the profile post download system")
    print("Enter 3 to return to home")
    print("Enter 4 to exit the program")

    choice = input("\nEnter your choice: ")
    return choice

# Function to clear the console screen cross-platform and display the documentation
def clear_console():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')
    print(f"\nIf you have any questions, please refer to the documentation at {DOCUMENTATION_URL}\n")

# Function to add the documentation link to the end of the doc.txt file
def add_doc_link_to_txt():
    with open('doc.txt', 'a') as file:
        file.write(f"\n\nIf you have any questions, please refer to the documentation at {DOCUMENTATION_URL}.")

# Function to configure the general post download system (option 1)
def configure_general_system():
    configurations = load_configurations('code/config.json')

    clear_console()
    print("General Post Download System Configuration:\n")
    print("1. Download Attachments:", "Enabled" if configurations.get('download_attachments', True) else "Disabled")
    print("2. Download Videos:", "Enabled" if configurations.get('download_videos', True) else "Disabled")
    print("3. Save Information:", "Enabled" if configurations.get('save_info_txt', True) else "Disabled")
    print("4. Save Comments:", "Enabled" if configurations.get('save_comments_txt', True) else "Disabled")

    option = input("\nEnter the number of the option you want to configure or '0' to go back: ")

    if option == '1':
        configurations['download_attachments'] = not configurations.get('download_attachments', True)
    elif option == '2':
        configurations['download_videos'] = not configurations.get('download_videos', True)
    elif option == '3':
        configurations['save_info_txt'] = not configurations.get('save_info_txt', True)
    elif option == '4':
        configurations['save_comments_txt'] = not configurations.get('save_comments_txt', True)
    elif option == '0':
        return

    save_configurations(configurations, 'code/config.json')
    configure_general_system()

# Function to configure the profile post download system (option 2)
def configure_profile_system():
    configurations = load_configurations('code/profileconfig.json')

    clear_console()
    print("Profile Post Download System Configuration:\n")
    print("1. Download Attachments:", "Enabled" if configurations.get('download_attachments', True) else "Disabled")
    print("2. Download Videos:", "Enabled" if configurations.get('download_videos', True) else "Disabled")
    print("3. Save Information:", "Enabled" if configurations.get('save_info_txt', True) else "Disabled")
    print("4. Save Comments:", "Enabled" if configurations.get('save_comments_txt', True) else "Disabled")
    print("5. Save Only Posts with Files:", "Enabled" if configurations.get('files_only', False) else "Disabled")
    print("6. Save Only Posts without Files:", "Enabled" if configurations.get('no_files', False) else "Disabled")
    print("7. Save Both Types of Posts:", "Enabled" if configurations.get('both', True) else "Disabled")

    option = input("\nEnter the number of the option you want to configure or '0' to go back: ")

    if option == '1':
        configurations['download_attachments'] = not configurations.get('download_attachments', True)
    elif option == '2':
        configurations['download_videos'] = not configurations.get('download_videos', True)
    elif option == '3':
        configurations['save_info_txt'] = not configurations.get('save_info_txt', True)
    elif option == '4':
        configurations['save_comments_txt'] = not configurations.get('save_comments_txt', True)
    elif option == '5':
        configurations['files_only'] = not configurations.get('files_only', False)
        if configurations['files_only']:
            configurations['no_files'] = False
            configurations['both'] = False
    elif option == '6':
        configurations['no_files'] = not configurations.get('no_files', False)
        if configurations['no_files']:
            configurations['files_only'] = False
            configurations['both'] = False
    elif option == '7':
        configurations['both'] = not configurations.get('both', True)
        if configurations['both']:
            configurations['files_only'] = False
            configurations['no_files'] = False
    elif option == '0':
        return

    save_configurations(configurations, 'code/profileconfig.json')
    configure_profile_system()

# Main function that controls the program flow
def main():
    add_doc_link_to_txt()  # Adds the documentation link to the doc.txt file

    while True:
        choice = display_main_menu()

        if choice == '1':
            configure_general_system()
        elif choice == '2':
            configure_profile_system()
        elif choice == '3':
            # Here you would place the execution of the main.py script
            print("\nExecuting main.py script...")
            os.system('python main.py')
        elif choice == '4':
            print("\nExiting the program...")
            break
        else:
            print("\nInvalid option. Please choose a valid option.")

if __name__ == "__main__":
    main()
