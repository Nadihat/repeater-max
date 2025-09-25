import argparse
import sys
import time
import os

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='A simple script to repeat intentions hourly from a file or a direct input.',
        add_help=False
    )
    
    # Define mutually exclusive group for --file and --intent
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--file', type=str, help='The file containing the intention.')
    group.add_argument('--intent', type=str, help='The intention string.')
    
    def positive_int(value):
        try:
            ivalue = int(value)
            if ivalue <= 0:
                raise argparse.ArgumentTypeError(f"Invalid positive int value: '{value}'")
            return ivalue
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid int value: '{value}'")
    
    parser.add_argument('--repeats', type=positive_int, help='Number of times to repeat the intention.')
    parser.add_argument('--duration', type=positive_int, help='Duration in seconds to repeat the intentions for.')
    
    # Add help
    parser.add_argument('--help', '-?', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit.')
    
    return parser.parse_args()

def read_intention_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read().strip()
            return content
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        sys.exit(1)

def format_time(seconds):
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:02}"

def prompt_intention_or_file():
    while True:
        user_input = input("Intention (or filename): ").strip()
        if not user_input:
            print("Input cannot be empty. Please enter a valid intention or filename.")
            continue
        if os.path.isfile(user_input):
            return {'file': user_input}
        else:
            return {'intent': user_input}

def prompt_positive_int(prompt_text):
    while True:
        user_input = input(prompt_text).strip()
        try:
            value = int(user_input)
            if value <= 0:
                print("Please enter a positive integer.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

def main():
    args = parse_arguments()
    print("ServitorConnect CLI v3")
    print("by AnthroHeart/Anthro Teacher/Thomas Sweet\n")
    
    # Initialize variables
    file = args.file
    intent = args.intent
    repeats = args.repeats
    duration = args.duration
    
    # Handle Intention or File
    if not (file or intent):
        user_input = prompt_intention_or_file()
        file = user_input.get('file')
        intent = user_input.get('intent')
    
    # Ensure that either file or intent is set
    if file:
        if not os.path.isfile(file):
            print(f"File '{file}' does not exist. Exiting.")
            sys.exit(1)
        source = f"File '{file}'"
        file_contents = read_intention_from_file(file)
    else:
        source = f"Intent '{intent}'"
    
    # Handle Repeats
    if repeats is None:
        repeats = prompt_positive_int("Number of repeats per hour: ")
    
    # Handle Duration
    if duration is None:
        duration = prompt_positive_int("Duration in seconds: ")
    
    # Display source information
    print("\nSource:", source)
    print(f"Repeats per Hour: {repeats}")
    print(f"Duration: {format_time(duration)}")
    
    # Initialize timing
    start_time = time.time()
    end_time = start_time + duration
    next_hour_time = start_time + 3600  # Schedule the first hour mark
    print("\nRepeating Intention...")
    for _ in range(repeats):
        # Assign intention_value based on source
        if file:
            intention_value = file_contents
        else:
            intention_value = intent
    
    try:
        while True:
            current_time = time.time()
            
            if current_time >= end_time:
                # Duration completed
                break
            
            if current_time >= next_hour_time:
                # Assign intention_value
                print("\nRepeating Intention...")
                for _ in range(repeats):
                    # Assign intention_value based on source
                    if file:
                        intention_value = file_contents
                    else:
                        intention_value = intent
                next_hour_time += 3600  # Schedule next hour
            
            # Update timer
            remaining = int(end_time - current_time)
            if remaining < 0:
                remaining = 0
            timer_str = format_time(remaining)
            output = f"{source} Repeated {repeats} Times Hourly: {timer_str}"
            # Print on the same line
            sys.stdout.write('\r' + output)
            sys.stdout.flush()
            time.sleep(1)
        
        print("\nDuration completed.")
    
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user. Exiting gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
