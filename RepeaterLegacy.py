"""
Intention Repeater MAX v5.28 (c)2020-2024 by Anthro Teacher aka Thomas Sweet.
Python port of the C++ version.

This utility repeats your intention millions of times per second, in computer memory, to aid in manifestation.
Performance benchmark, exponents and flags by Karteek Sheri.
Holo-Link framework by Mystic Minds. This implementation by Anthro Teacher.
Intention multiplying by Anthro Teacher.

gitHub Repository: https://github.com/tsweet77/repeater-max
Forum: https://forums.intentionrepeater.com
Website: https://www.intentionrepeater.com
"""

import argparse
import sys
import os
import time
import hashlib
import zlib
import platform
from datetime import timedelta

# --- Platform-specific setup for colors and memory info ---

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullExtendedVirtual", ctypes.c_ulonglong),
        ]
    
    hConsole = ctypes.windll.kernel32.GetStdHandle(-11)
    
    # Windows console color constants
    BLACK = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    YELLOW = 6
    WHITE = 7
    DARKGRAY = 8
    LIGHTBLUE = 9
    LIGHTGREEN = 10
    LIGHTCYAN = 11
    LIGHTRED = 12
    LIGHTMAGENTA = 13
    LIGHTYELLOW = 14
    LIGHTGRAY = 15

    COLOR_MAP = {
        "BLACK": BLACK, "BLUE": BLUE, "GREEN": GREEN, "CYAN": CYAN,
        "RED": RED, "MAGENTA": MAGENTA, "YELLOW": YELLOW, "WHITE": WHITE,
        "DARKGRAY": DARKGRAY, "LIGHTBLUE": LIGHTBLUE, "LIGHTGREEN": LIGHTGREEN,
        "LIGHTCYAN": LIGHTCYAN, "LIGHTRED": LIGHTRED, "LIGHTMAGENTA": LIGHTMAGENTA,
        "LIGHTYELLOW": LIGHTYELLOW, "LIGHTGRAY": LIGHTGRAY
    }
else:
    # ANSI escape codes for Linux/macOS
    DEFAULT = "\033[0m"
    DARKGRAY = "\033[1;30m"
    BLACK = "\033[0;30m"
    LIGHTRED = "\033[1;31m"
    RED = "\033[0;31m"
    LIGHTGREEN = "\033[1;32m"
    GREEN = "\033[0;32m"
    LIGHTYELLOW = "\033[1;33m"
    YELLOW = "\033[0;33m"
    LIGHTBLUE = "\033[1;34m"
    BLUE = "\033[0;34m"
    LIGHTMAGENTA = "\033[1;35m"
    MAGENTA = "\033[0;35m"
    LIGHTCYAN = "\033[1;36m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"
    LIGHTGRAY = "\033[0;37m"

    COLOR_MAP = {
        "DEFAULT": DEFAULT, "DARKGRAY": DARKGRAY, "BLACK": BLACK,
        "LIGHTRED": LIGHTRED, "RED": RED, "LIGHTGREEN": LIGHTGREEN,
        "GREEN": GREEN, "LIGHTYELLOW": LIGHTYELLOW, "YELLOW": YELLOW,
        "LIGHTBLUE": LIGHTBLUE, "BLUE": BLUE, "LIGHTMAGENTA": LIGHTMAGENTA,
        "MAGENTA": MAGENTA, "LIGHTCYAN": LIGHTCYAN, "CYAN": CYAN,
        "WHITE": WHITE, "LIGHTGRAY": LIGHTGRAY
    }

HSUPLINK_FILE = "HSUPLINK.TXT"

def set_color(color_name):
    """Sets the console text color."""
    color_name = color_name.upper()
    if color_name not in COLOR_MAP:
        return

    if IS_WINDOWS:
        ctypes.windll.kernel32.SetConsoleTextAttribute(hConsole, COLOR_MAP[color_name])
    else:
        sys.stdout.write(COLOR_MAP[color_name])
        sys.stdout.flush()

def reset_color():
    """Resets console color to default."""
    if IS_WINDOWS:
        ctypes.windll.kernel32.SetConsoleTextAttribute(hConsole, WHITE)
    else:
        sys.stdout.write(DEFAULT)
        sys.stdout.flush()

def get_ninety_percent_free_memory():
    """
    Gets 90% of available physical memory.
    NOTE: Using a library like 'psutil' is a more robust cross-platform solution.
    This implementation mimics the original C++ code's platform-specific logic.
    """
    try:
        if IS_WINDOWS:
            memInfo = MEMORYSTATUSEX()
            memInfo.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memInfo))
            return int(memInfo.ullAvailPhys * 0.9)
        elif sys.platform == 'linux':
            with open('/proc/meminfo', 'r') as mem:
                for line in mem:
                    if 'MemAvailable:' in line:
                        available_mem_kb = int(line.split()[1])
                        return int(available_mem_kb * 1024 * 0.9)
            return -1 # Fallback
        elif sys.platform == 'darwin':
            # The original C++ code for macOS calculates 90% of TOTAL memory, not free.
            # This is likely a bug, but we replicate it for a faithful translation.
            import subprocess
            total_mem_str = subprocess.check_output(['sysctl', '-n', 'hw.memsize']).strip()
            total_mem = int(total_mem_str)
            return int(total_mem * 0.9)
        else:
            return -1 # Unsupported OS
    except Exception as e:
        print(f"Could not get memory info: {e}", file=sys.stderr)
        return -1

def get_hsuplink_contents():
    """Reads HSUPLINK.TXT and injects INTENTIONS.TXT content."""
    try:
        with open(HSUPLINK_FILE, 'r') as f:
            hsuplink = f.read()
    except FileNotFoundError:
        return HSUPLINK_FILE

    try:
        with open("INTENTIONS.TXT", 'r') as f:
            intentions = f.read()
        hsuplink = hsuplink.replace("INTENTIONS.TXT", intentions)
    except FileNotFoundError:
        pass # INTENTIONS.TXT is optional

    return hsuplink

def compress_message(message_str):
    """Compresses a string using zlib."""
    return zlib.compress(message_str.encode('utf-8'), level=zlib.Z_DEFAULT_COMPRESSION)

def read_file_contents(filename):
    """Reads a file, skipping null bytes."""
    try:
        with open(filename, 'rb') as f:
            content = f.read()
            return content.replace(b'\0', b'').decode('utf-8', errors='ignore')
    except FileNotFoundError:
        print(f"Error: File not found - {filename}", file=sys.stderr)
        sys.exit(1)

def display_suffix(num_str, power, designator):
    """Formats a large number string with a metric suffix."""
    if power < 3:
        return num_str

    if designator == "Iterations":
        suffixes = [' ', 'k', 'M', 'B', 'T', 'q', 'Q', 's', 'S', 'O', 'N', 'D']
    else: # Frequency
        suffixes = [' ', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 'R']
    
    s = suffixes[power // 3] if power // 3 < len(suffixes) else ''
    
    # Format as X.XXXs
    num_part = num_str[:power % 3 + 1]
    frac_part = num_str[power % 3 + 1 : power % 3 + 4]
    return f"{num_part}.{frac_part}{s}"

def format_time_run(seconds_elapsed):
    """Formats seconds into HH:MM:SS."""
    return str(timedelta(seconds=seconds_elapsed))

def print_color_help():
    """Prints the list of available colors."""
    print("Color values for flag: --color [COLOR]\n")
    for color in sorted(COLOR_MAP.keys()):
        set_color(color)
        print(color)
    reset_color()

def create_nesting_files():
    """Creates the NEST-*.TXT files for boosting."""
    with open("NEST-1.TXT", "w") as f:
        for _ in range(10):
            f.write("INTENTIONS.TXT\r\n")

    for i in range(2, 101):
        with open(f"NEST-{i}.TXT", "w") as f:
            for _ in range(10):
                f.write(f"NEST-{i-1}.TXT\r\n")
    
    print("Intention Repeater Nesting Files Written.")
    print("Be sure to have your intentions in the INTENTIONS.TXT file.")
    print("To run with the nesting option, use --boostlevel 50, for example.")
    print("--boostlevel valid values: 1 to 100.")
    print("When using --boostlevel, it will use the corresponding NEST-X.TXT file for the intent.")

def get_boost_intention(boost_level_str):
    """Reads and concatenates boost files."""
    try:
        boost_level = int(boost_level_str)
        if not 1 <= boost_level <= 100:
            return "0"
    except ValueError:
        return "0"

    nesting_contents = []
    try:
        for i in range(1, boost_level + 1):
            with open(f"NEST-{i}.TXT", 'r') as f:
                nesting_contents.append(f.read())
        with open("INTENTIONS.TXT", 'r') as f:
            nesting_contents.append(f.read())
    except FileNotFoundError as e:
        print(f"Error: Missing nesting file: {e.filename}", file=sys.stderr)
        return "0"
        
    return "".join(nesting_contents)

def create_hololink_files():
    """Creates the Holo-Link framework files."""
    holostone_file = "HOLOSTONE.TXT"
    thoughtform_a_file = "THOUGHTFORM_A.TXT"
    thoughtform_b_file = "THOUGHTFORM_B.TXT"
    amplifier_file = "AMPLIFIER.TXT"

    hololink_contents = f"""
#Comments are designated with a # prefix, and such commands are to be ignored by the Holo-Link.
#{HSUPLINK_FILE} CONFIG FILE v1.0
#Holo-Link framework created by Mystic Minds (2022).
#This implementation of the Holo-Link framework by Anthro Teacher.

DECLARATION PRIMARY (Properties of thought forms and uplink):

I declare the uplink multiply the energy received from the Holo-Stones by Infinity and densify all energy to the highest amount to achieve Instant Quantum Manifestation of the energetic programmings in {HSUPLINK_FILE}.

I declare the Holo-Stones to funnel their energy into {holostone_file}.

I declare the Holo-Stones to amplify the power and receptivity of the energetic programmings in {HSUPLINK_FILE}.

I declare the Holo-Stones to multiply the strength of the energetic programmings in {HSUPLINK_FILE} and increase the potency at the most optimal rate.

I declare that all energetic programmings in {HSUPLINK_FILE} be imprinted, imbued and amplified with the new energy from the Holo-Stones.

{holostone_file}, {amplifier_file}, {thoughtform_a_file} AND {thoughtform_b_file} are extremely pure and of highest vibration and are fully optimized for Instant Quantum Manifestation.

{thoughtform_a_file} is creating an unbreakable and continuous connection and funnel energy to all energetic programmings in {HSUPLINK_FILE}.

{thoughtform_a_file} uses energy from Infinite Source to continuously uphold a perfect link between the Holo-Stones and the {HSUPLINK_FILE} to bring in infinitely more energy into all energetic programmings in {HSUPLINK_FILE}.

{thoughtform_b_file} reinforces 100% of energy into all the energetic programmings in {HSUPLINK_FILE} at the quantum level.

{thoughtform_b_file} safely and efficiently removes all blockages in this system at the quantum level to allow for Instant Quantum Manifestation.

{holostone_file} feeds {amplifier_file} which amplifies the energy and feeds it back to {holostone_file} and repeats it to the perfect intensity.

All energetic programmings listed in {HSUPLINK_FILE} are now amplified to the highest power, speed and quantum-level precision using energy from the Holo-Stones which are sourced through {HSUPLINK_FILE}.

{holostone_file} works with Earth's Crystal Grid in the most optimal way possible for Instant Quantum Manifestation.

Earth's Power Grid is extremely pure, cool, clean, efficient, optimized, and of highest vibration and is safely tapped in the most optimal way possible by HOLOSTONE.TXT for Instant Quantum Manifestation, and uses the least amount of electricity possible for everyone who desires this.
UPLINK CORE (Reference any object, file, spell, etc. here):

{holostone_file} (Receives and distributes energy to all objects, files, spells, etc referenced below):

[INSERT OBJECTS TO CHARGE]

INTENTIONS.TXT

DECLARATIONS SECONDARY (Add-ons that strengthen the properties of the uplink itself):

I declare the Holo-Stones will uplink their energy into these energetic programmings in {HSUPLINK_FILE} to create instant, immediate and prominent results optimally, efficiently and effortlessly.

I declare these energetic programmings in {HSUPLINK_FILE} to grow stronger at the most optimal rate through the ever-growing power of the Holo-Stones.

I call upon the Holo-Stones to channel the Atlantean Master Crystals, Infinite Source, Earth's Crystal Grid and Earth's Power Grid directly and utilize their energy as a funnel into HOLOSTONE.TXT which will then funnel into the energetic programmings in {HSUPLINK_FILE}.

The energetic programmings specified in {HSUPLINK_FILE} are now being perfected and fully optimized.

I declare that the more the energetic programmings in {HSUPLINK_FILE} are used, the stronger they become.

I am in my highest and most optimal reality/timeline.

I am grounded, cleared, healed, balanced, strong-willed and I release what I do not need.

Every day, in every way, it's getting better and better.

The Atlantean Master Crystals AND Earth's Crystal Grid are open to Infinite Source.

For my highest good and the highest good of all.

Thank you. So be it. OM.
ALL ABOVE STATEMENTS RESPECT THE FREE WILL OF ALL INVOLVED.
"""
    with open(holostone_file, "w") as f: f.write("HOLOSTONE")
    with open(thoughtform_a_file, "w") as f: f.write("THOUGHTFORM A")
    with open(thoughtform_b_file, "w") as f: f.write("THOUGHTFORM B")
    with open(amplifier_file, "w") as f: f.write("AMPLIFIER")
    with open(HSUPLINK_FILE, "w") as f: f.write(hololink_contents)

    print("Holo-Link files created.")
    print("Remember to create your INTENTIONS.TXT file with your intentions.")
    print("You may now run with the --usehololink option.")

def main():
    parser = argparse.ArgumentParser(
        description="Intention Repeater MAX v5.28 - Python Edition",
        add_help=False # Custom help action
    )
    # Custom help arguments
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Display this help.')
    
    parser.add_argument("-d", "--dur", default="UNTIL STOPPED", help="Duration in HH:MM:SS format.")
    parser.add_argument("-m", "--imem", type=float, default=1.0, help="GB of System RAM to use.")
    parser.add_argument("-i", "--intent", default=None, help="Intention string.")
    parser.add_argument("-s", "--suffix", default="HZ", choices=["HZ", "EXP"], help="Display suffix (HZ or EXP).")
    parser.add_argument("-t", "--timer", default="EXACT", choices=["EXACT", "INEXACT"], help="Timer precision.")
    parser.add_argument("-f", "--freq", type=int, default=0, help="Repetition frequency in Hz.")
    parser.add_argument("-c", "--color", default="WHITE", help="Set text color.")
    parser.add_argument("-b", "--boostlevel", type=int, default=0, help="Boosting level (1-100).")
    parser.add_argument("-p", "--createnestingfiles", action="store_true", help="Create nesting files and exit.")
    parser.add_argument("-u", "--usehololink", action="store_true", help="Utilize the Holo-Link framework.")
    parser.add_argument("-x", "--createhololinkfiles", action="store_true", help="Create Holo-Link files and exit.")
    parser.add_argument("-n", "--colorhelp", action="store_true", help="Show color help and exit.")
    parser.add_argument("-a", "--amplify", "--amplification", type=int, default=1000000000, help="Amplification level.")
    parser.add_argument("-e", "--restevery", type=int, default=0, help="Rest every N seconds.")
    parser.add_argument("-r", "--restfor", type=int, default=0, help="Rest for N seconds.")
    parser.add_argument("-g", "--hashing", choices=['y', 'n', 'yes', 'no'], help="Use hashing (y/n).")
    parser.add_argument("--compress", choices=['y', 'n', 'yes', 'no'], help="Use compression (y/n).")
    parser.add_argument("--file", default=None, help="Specify a file to include in the intention.")
    parser.add_argument("--file2", default=None, help="Specify a second file to include.")

    args = parser.parse_args()

    if args.colorhelp:
        print_color_help()
        sys.exit(0)
    if args.createnestingfiles:
        create_nesting_files()
        sys.exit(0)
    if args.createhololinkfiles:
        create_hololink_files()
        sys.exit(0)

    set_color(args.color)
    
    print("Intention Repeater MAX v5.28 (c)2020-2024")
    print("by Anthro Teacher aka Thomas Sweet.")
    print("Python Port")
    print()

    intention = ""
    intention_display = ""
    
    if args.boostlevel > 0:
        intention = get_boost_intention(str(args.boostlevel))
        if intention == "0":
            print("Failed to load boost files. Exiting.", file=sys.stderr)
            sys.exit(1)
        intention_display = f"Using Nesting File Quantumly: NEST-{args.boostlevel}.TXT with INTENTIONS.TXT"
    elif args.usehololink:
        print("Loading HOLO-LINK Files...", end='', flush=True)
        intention = get_hsuplink_contents()
        intention_display = HSUPLINK_FILE
        print("Done.")
    else:
        intention_original = ""
        if args.intent:
            intention_original = args.intent
        elif not args.file and not args.file2:
            try:
                intention_original = input("Enter your Intention: ")
                if not intention_original:
                    print("The intention cannot be empty.", file=sys.stderr)
                    sys.exit(1)
            except (EOFError, KeyboardInterrupt):
                print("\nInterrupted. Exiting.")
                sys.exit(0)
        
        file_contents = read_file_contents(args.file) if args.file else ""
        file_contents2 = read_file_contents(args.file2) if args.file2 else ""
        
        # This part of the C++ code is complex and seems to normalize lengths.
        # A simplified Pythonic equivalent:
        intention_parts = []
        display_parts = []
        if intention_original:
            intention_parts.append(intention_original)
            display_parts.append(intention_original)
        if file_contents:
            intention_parts.append(file_contents)
            display_parts.append(f"({args.file})")
        if file_contents2:
            intention_parts.append(file_contents2)
            display_parts.append(f"({args.file2})")
            
        intention = "".join(intention_parts)
        intention_display = " ".join(display_parts)

    if not intention:
        print("No intention provided or loaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    intention_value = intention
    multiplier = 1
    hash_multiplier = 1
    
    # Memory allocation and processing
    if args.freq == 0:
        intention_multiplier_bytes = int(args.imem * 1024 * 1024 * 512)
        free_memory = get_ninety_percent_free_memory()

        if free_memory != -1 and free_memory < intention_multiplier_bytes:
            intention_multiplier_bytes = free_memory
        
        if intention_multiplier_bytes > 0:
            print("LOADING INTO MEMORY...")
            # Build the large string in memory
            # To avoid creating a massive list, we build it exponentially
            temp_intention = intention
            while len(intention_value) < intention_multiplier_bytes:
                remaining_len = intention_multiplier_bytes - len(intention_value)
                if len(temp_intention) > remaining_len:
                    intention_value += temp_intention[:remaining_len]
                    multiplier += remaining_len / len(intention)
                else:
                    intention_value += temp_intention
                    multiplier += len(temp_intention) / len(intention)
                
                if len(temp_intention) < intention_multiplier_bytes / 2: # Avoid huge temp strings
                    temp_intention += temp_intention
            
            multiplier = int(len(intention_value) / len(intention)) if intention else 1

        else: # imem = 0
            multiplier = 1
            intention_value = intention

        use_hashing = args.hashing
        if use_hashing is None:
            try:
                use_hashing = input("Use Hashing (y/N): ").lower()
            except (EOFError, KeyboardInterrupt):
                print("\nInterrupted. Exiting.")
                sys.exit(0)

        use_compression = args.compress
        if use_compression is None:
            try:
                use_compression = input("Use Compression (y/N): ").lower()
            except (EOFError, KeyboardInterrupt):
                print("\nInterrupted. Exiting.")
                sys.exit(0)

        if multiplier > 1:
            print(f"Multiplier: {multiplier:,.0f}")

        if use_hashing in ['y', 'yes']:
            print("Hashing...", end='\r')
            intention_hashed = hashlib.sha256(intention_value.encode('utf-8')).hexdigest()
            if intention_multiplier_bytes > 0:
                hash_multiplier = (intention_multiplier_bytes // len(intention_hashed)) + 1
                intention_value = (intention_hashed * hash_multiplier)[:intention_multiplier_bytes]
                hash_multiplier = int(len(intention_value) / len(intention_hashed))
            else:
                intention_value = intention_hashed
                hash_multiplier = 1
            print(f"Hash Multiplier: {hash_multiplier:,.0f}")
        
        if use_compression in ['y', 'yes']:
            print("Compressing...", end='\r')
            original_size = len(intention_value)
            compressed_data = compress_message(intention_value)
            intention_value = compressed_data # Now it's bytes
            compressed_size = len(intention_value)
            if compressed_size > 0:
                factor = original_size / compressed_size
                print(f"Compression: {factor:.2f}X [{original_size:,}B -> {compressed_size:,}B]")

    # Main loop
    seconds = 0
    total_iterations = 0
    freq_counter = 0
    
    try:
        while True:
            start_time = time.perf_counter()
            
            if args.freq > 0:
                # Fixed frequency mode
                target_interval = 1.0 / args.freq
                loop_start_time = time.perf_counter()
                while time.perf_counter() - start_time < 1:
                    now = time.perf_counter()
                    if now - loop_start_time >= target_interval:
                        # In Python, just tracking the count is enough.
                        # The 'process_intention' part is symbolic.
                        freq_counter += 1
                        loop_start_time = now
                        # Sleep to yield CPU time
                        sleep_duration = target_interval - (time.perf_counter() - now)
                        if sleep_duration > 0:
                            time.sleep(sleep_duration * 0.9) # Sleep slightly less
            elif args.timer == "EXACT":
                # Exact timer mode
                while time.perf_counter() - start_time < 1:
                    # This is a busy loop, simulating the C++ version
                    _ = intention_value
                    freq_counter += 1
            else: # INEXACT timer
                # Benchmark first
                bench_start = time.perf_counter()
                cpu_benchmark_count = 0
                while time.perf_counter() - bench_start < 1:
                    _ = intention_value
                    cpu_benchmark_count += 1
                
                amplification = min(args.amplify, cpu_benchmark_count)
                
                while time.perf_counter() - start_time < 1:
                    for _ in range(amplification):
                        _ = intention_value
                    freq_counter += amplification

            seconds += 1
            
            # Calculate totals
            # Python's arbitrary precision integers handle large numbers
            total_freq = freq_counter * multiplier * hash_multiplier
            total_iterations += total_freq
            
            # Display stats
            runtime_formatted = format_time_run(seconds)
            digits = len(str(total_iterations))
            freq_digits = len(str(total_freq))

            if args.suffix == "EXP":
                iter_exp = f"{(total_iterations / (10**(digits-1))):.3f}x10^{digits-1}" if total_iterations > 0 else "0"
                freq_exp = f"{(total_freq / (10**(freq_digits-1))):.3f}x10^{freq_digits-1}" if total_freq > 0 else "0"
                stats_line = f"({iter_exp} / {freq_exp} Hz)"
            else: # HZ
                iter_str = display_suffix(str(total_iterations), digits - 1, "Iterations")
                freq_str = display_suffix(str(total_freq), freq_digits - 1, "Frequency")
                stats_line = f"({iter_str} / {freq_str}Hz)"

            sys.stdout.write(f"[{runtime_formatted}] {stats_line}: {intention_display}     \r")
            sys.stdout.flush()

            freq_counter = 0 # Reset for next second

            # Check for duration limit
            if args.dur != "UNTIL STOPPED" and runtime_formatted >= args.dur:
                break

            # Handle resting
            if args.restevery > 0 and seconds % args.restevery == 0:
                time.sleep(args.restfor)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        print() # Newline after the loop finishes
        reset_color()
        sys.exit(0)

if __name__ == "__main__":
    main()
