import argparse
from . import tokencount_file, quickprint, printsetup

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