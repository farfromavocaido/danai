import argparse
from . import tokencount_file, quickprint, printsetup
import os
import sys

def get_key():
    """Capture a single key press."""
    if os.name == 'nt':  # For Windows
        import msvcrt
        return msvcrt.getch().decode('utf-8')
    else:  # For Unix-based systems
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def get_input():
    """Capture multi-character input."""
    input_str = ""
    while True:
        ch = get_key()
        if ch == '\x1b':  # Escape key
            return ch
        elif ch == '\r':  # Enter key
            break
        elif ch.isdigit():
            input_str += ch
            print(ch, end='', flush=True)
        else:
            print("\nInvalid input. Exiting.")
            return None
    return input_str

def tokencount_cli():
    """
    Command-line interface for token counting.
    """
    parser = argparse.ArgumentParser(description="Token Count Command Line Interface")
    parser.add_argument('file', help='File path to count tokens')
    args = parser.parse_args()
    
    # Append current directory to the file path
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, args.file)
    
    if not os.path.isfile(file_path):
        # Search for the file in the current directory and subdirectories
        matches = []
        for root, dirs, files in os.walk(current_directory):
            for file in files:
                if file.lower() == args.file.lower():
                    relative_path = os.path.join(root, file)
                    matches.append(relative_path)
        
        if not matches:
            print(f"No exact matches found for {args.file}.")
            print("Press 'S' to expand the search to partial matches, or any other key to exit: ", end='', flush=True)
            key = get_key()
            print()  # Move to the next line
            if key.lower() != 's':
                print("Exiting.")
                return
            
            # Perform partial match search
            partial_matches = []
            for root, dirs, files in os.walk(current_directory):
                for file in files:
                    if args.file.lower() in file.lower():
                        relative_path = os.path.join(root, file)
                        partial_matches.append(relative_path)
            
            if partial_matches:
                matches = partial_matches
        
        if matches:
            # Sort matches by proximity to the root
            matches.sort(key=lambda x: x.count(os.sep))
            truncated_matches = matches[:20]
            while True:
                if key.lower() == 's':
                    print(f"I can't find that file, but I did find:")
                else:
                    print(f"Exact matches found:")
                
                for i, match in enumerate(truncated_matches, 1):
                    print(f"{i}. {match}")
                
                if len(matches) > 20:
                    print("\nPlease enter the number of the file you want to use, press Return to show 20 more, or Esc to exit: ", end='', flush=True)
                else:
                    print("\nPlease enter the number of the file you want to use or Esc to exit: ", end='', flush=True)
                
                input_str = get_input()
                print()  # Move to the next line
                if input_str == '\x1b':  # Escape key
                    print("Exiting.")
                    return
                elif input_str and input_str.isdigit() and 1 <= int(input_str) <= len(truncated_matches):
                    selected_file = truncated_matches[int(input_str) - 1]
                    file_path = selected_file
                    break
                elif input_str == '' and len(matches) > 20:
                    truncated_matches = matches[:len(truncated_matches) + 20]
                else:
                    print("Invalid input. Exiting.")
                    return

    # Proceed with token counting using the selected file_path
    print(f"Token count for {args.file}: {tokencount_file(file_path)}")

def main():
    """
    Main function that handles the command-line interface.
    """
    parser = argparse.ArgumentParser(description="AI Utils Command Line Interface")
    
    # Define subcommands
    parser.add_argument('command', help='Command to run (token, qq, printsetup)')
    parser.add_argument('arg', nargs='?', help='Argument for the command (if applicable)')

    # Parse the arguments
    args = parser.parse_args()

    # Handle the commands
    if args.command == 'token' and args.arg:
        # Call tokencount_file with one argument
        print(f"Token count for file {args.arg}: {tokencount_file(args.arg)}")
    elif args.command == 'qq' and args.arg:
        # Call quickprint with one argument
        quickprint(args.arg)
    elif args.command == 'printsetup':
        # Call printsetup with no arguments
        printsetup()
    else:
        print(f"Unknown command or missing argument: {args.command}")



        