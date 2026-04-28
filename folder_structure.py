#!/usr/bin/env python3
"""
Interactive directory tree viewer with advanced export, undo/back,
and two levels of help.

Usage:
    python folder_structure.py [PATH] [--files] [--max-depth N] [--ascii] [--no-pause]
    If PATH is omitted, interactive mode starts.

Commands must be prefixed with "--" (e.g., --exit, --help).
Type --help for a quick command list, or --help-full for the immersive guide.
"""

import os
import sys
import argparse
import platform

UNICODE = {
    "PIPE": "│   ",
    "TEE":  "├── ",
    "END":  "└── ",
    "SPC":  "    ",
}
ASCII = {
    "PIPE": "|   ",
    "TEE":  "+-- ",
    "END":  "`-- ",
    "SPC":  "    ",
}

def get_symbols(ascii_mode: bool) -> dict:
    return ASCII if ascii_mode else UNICODE

def build_tree(root: str,
               prefix: str = "",
               include_files: bool = False,
               max_depth: int | None = None,
               current_depth: int = 0,
               sym: dict = UNICODE) -> list[str]:
    if max_depth is not None and current_depth >= max_depth:
        return []

    lines = []
    try:
        entries = sorted(os.listdir(root), key=str.casefold)
    except PermissionError:
        lines.append(f"{prefix}{sym['TEE']}[Permission denied]")
        return lines
    except OSError as e:
        lines.append(f"{prefix}{sym['TEE']}[Error: {e}]")
        return lines

    dirs = []
    files = []
    for entry in entries:
        full = os.path.join(root, entry)
        if os.path.isdir(full):
            dirs.append(entry)
        elif include_files:
            files.append(entry)

    items = dirs + files
    count = len(items)

    for i, name in enumerate(items):
        is_last = (i == count - 1)
        connector = sym['END'] if is_last else sym['TEE']
        lines.append(f"{prefix}{connector}{name}")
        full_path = os.path.join(root, name)
        if os.path.isdir(full_path):
            extension = sym['SPC'] if is_last else sym['PIPE']
            lines.extend(
                build_tree(full_path,
                           prefix + extension,
                           include_files=include_files,
                           max_depth=max_depth,
                           current_depth=current_depth + 1,
                           sym=sym)
            )
    return lines

class CommandAction(Exception):
    def __init__(self, command):
        self.command = command

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_command_list():
    print()
    print("Available commands (prefix with '--'):")
    print("  --exit, --quit, --q     Exit the program")
    print("  --clear                 Clear the screen and restart")
    print("  --restart, --break      Restart without clearing")
    print("  --back, --undo          Undo the last step")
    print("  --help, --h, --?        Show this quick help")
    print("  --help-full             Open the full interactive help screen")
    print()

def show_help_full():
    clear_screen()
    print("=" * 60)
    print("  FULL COMMAND HELP")
    print("=" * 60)
    print()
    print("  --exit, --quit, --q     Exit the program completely")
    print("  --clear                 Clear the screen & start a fresh directory")
    print("  --restart, --break      Go to the directory prompt (no clearing)")
    print("  --back, --undo          Undo the last prompt – go back one step")
    print("  --help, --h, --?        Quick command list (appears inline)")
    print("  --help-full             This immersive help screen")
    print()
    print("While in this screen, type one of the above to act.")
    print("--back will return you to where you were.")
    print("-" * 60)

    while True:
        try:
            raw = input("--▶ ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise CommandAction("exit")
        if not raw.startswith("--"):
            print("Commands must start with '--'. Type --back to return.")
            continue
        cmd_part = raw[2:].strip().lower()
        if cmd_part in ("back", "undo"):
            clear_screen()
            return
        elif cmd_part in ("exit", "quit", "q"):
            raise CommandAction("exit")
        elif cmd_part in ("restart", "break"):
            raise CommandAction("restart")
        elif cmd_part in ("help-full", "helpfull"):
            continue
        elif cmd_part in ("help", "h", "?"):
            print("Use --back to return, or type another command.")
        else:
            print(f"Unknown command: --{cmd_part}. Use --back to return.")

def get_input(prompt: str) -> str:
    while True:
        try:
            raw = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            raise CommandAction("exit")

        user_input = raw.strip()
        if user_input.startswith("--"):
            cmd_part = user_input[2:].strip().lower()
            if cmd_part in ("exit", "quit", "q"):
                raise CommandAction("exit")
            elif cmd_part == "clear":
                raise CommandAction("clear")
            elif cmd_part in ("restart", "break"):
                raise CommandAction("restart")
            elif cmd_part in ("back", "undo"):
                raise CommandAction("back")
            elif cmd_part in ("help-full", "helpfull"):
                show_help_full()
                continue
            elif cmd_part in ("help", "h", "?"):
                print_command_list()
                continue
            else:
                print(f"Unknown command: --{cmd_part}. Type --help for a list.")
                continue
        else:
            return raw

STAGE_DIR = 0
STAGE_FILES = 1
STAGE_DEPTH = 2
STAGE_TREE = 3
STAGE_EXPORT_ASK = 4
STAGE_EXPORT_NAME = 5
STAGE_EXPORT_EXT = 6
STAGE_EXPORT_DEST = 7
STAGE_EXPORT_DEST_CUSTOM = 8
STAGE_DONE = 9

BACK_MAP = {
    STAGE_DIR: STAGE_DIR,
    STAGE_FILES: STAGE_DIR,
    STAGE_DEPTH: STAGE_FILES,
    STAGE_EXPORT_ASK: STAGE_DEPTH,
    STAGE_EXPORT_NAME: STAGE_EXPORT_ASK,
    STAGE_EXPORT_EXT: STAGE_EXPORT_NAME,
    STAGE_EXPORT_DEST: STAGE_EXPORT_EXT,
    STAGE_EXPORT_DEST_CUSTOM: STAGE_EXPORT_DEST,
}

def main():
    parser = argparse.ArgumentParser(description="Interactive folder tree viewer with export.")
    parser.add_argument("path", nargs="?", help="Starting directory path.")
    parser.add_argument("-f", "--files", action="store_true", help="Include files.")
    parser.add_argument("--max-depth", type=int, default=None, help="Depth limit.")
    parser.add_argument("--ascii", action="store_true", help="Use ASCII tree chars.")
    parser.add_argument("--no-pause", action="store_true", help="Don't pause on exit.")
    args = parser.parse_args()

    if args.path:
        sym = get_symbols(args.ascii)
        abs_path = os.path.abspath(args.path)
        print(f"\nDirectory tree of: {abs_path}\n")
        print(os.path.basename(args.path) or args.path)
        lines = build_tree(args.path, include_files=args.files,
                           max_depth=args.max_depth, sym=sym)
        for line in lines:
            print(line)
        print()
        sys.exit(0)

    print("\n=== Directory Tree Viewer ===")
    print("Commands are prefixed with '--'. Type --help for a quick list, or --help-full for the full guide.\n")

    use_ascii = args.ascii
    stage = STAGE_DIR
    path = include_files = max_depth = None

    while True:
        try:
            if stage == STAGE_DIR:
                while True:
                    try:
                        raw_path = get_input("Enter directory path: ")
                    except CommandAction as e:
                        if e.command == "back":
                            print("Already at the first step.\n")
                            continue
                        raise
                    raw_path = raw_path.strip()
                    if not raw_path:
                        print("Please enter a valid path.\n")
                        continue
                    if not os.path.exists(raw_path):
                        print(f"Error: '{raw_path}' does not exist.\n")
                        continue
                    if not os.path.isdir(raw_path):
                        print(f"Error: '{raw_path}' is not a directory.\n")
                        continue
                    path = raw_path
                    stage = STAGE_FILES
                    break

            elif stage == STAGE_FILES:
                while True:
                    try:
                        ans = get_input("Include files? (y/n) [n]: ").strip().lower()
                    except CommandAction as e:
                        if e.command == "back":
                            stage = BACK_MAP[stage]
                            break
                        raise
                    if ans in ("y", "yes"):
                        include_files = True
                        break
                    if ans in ("n", "no", ""):
                        include_files = False
                        break
                    print("Please answer y or n.\n")
                if stage != STAGE_FILES:
                    continue
                stage = STAGE_DEPTH

            elif stage == STAGE_DEPTH:
                while True:
                    try:
                        depth_str = get_input("Max depth (0 = root folder only, leave blank for unlimited): ").strip()
                    except CommandAction as e:
                        if e.command == "back":
                            stage = BACK_MAP[stage]
                            break
                        raise
                    if depth_str == "":
                        max_depth = None
                        break
                    if depth_str.isdigit():
                        max_depth = int(depth_str)
                        break
                    print("Please enter a number (0 for root only) or leave blank.\n")
                if stage != STAGE_DEPTH:
                    continue
                stage = STAGE_TREE

            elif stage == STAGE_TREE:
                sym = get_symbols(use_ascii)
                abs_path = os.path.abspath(path)
                print(f"\nDirectory tree of: {abs_path}\n")
                print(os.path.basename(path) or path)
                lines = build_tree(path, include_files=include_files,
                                   max_depth=max_depth, sym=sym)
                for line in lines:
                    print(line)
                print()
                stage = STAGE_EXPORT_ASK

            elif stage == STAGE_EXPORT_ASK:
                while True:
                    try:
                        ans = get_input("Export tree to file? (y/n) [n]: ").strip().lower()
                    except CommandAction as e:
                        if e.command == "back":
                            stage = BACK_MAP[stage]
                            break
                        raise
                    if ans in ("n", "no", ""):
                        stage = STAGE_DONE
                        break
                    if ans in ("y", "yes"):
                        stage = STAGE_EXPORT_NAME
                        break
                    print("Please answer y or n.\n")
                if stage == STAGE_EXPORT_ASK:
                    continue

            elif stage == STAGE_EXPORT_NAME:
                while True:
                    try:
                        fname = get_input("Enter filename (without extension) [untitled]: ").strip()
                    except CommandAction as e:
                        if e.command == "back":
                            stage = BACK_MAP[stage]
                            break
                        raise
                    if not fname:
                        fname = "untitled"
                    if os.sep in fname or "/" in fname:
                        print("Filename must not contain path separators.\n")
                        continue
                    export_fname = fname
                    stage = STAGE_EXPORT_EXT
                    break
                if stage != STAGE_EXPORT_NAME:
                    continue

            elif stage == STAGE_EXPORT_EXT:
                while True:
                    try:
                        ext = get_input("Enter extension (e.g. .txt, .docx) [.txt]: ").strip()
                    except CommandAction as e:
                        if e.command == "back":
                            stage = BACK_MAP[stage]
                            break
                        raise
                    if not ext:
                        ext = ".txt"
                    else:
                        if not ext.startswith("."):
                            ext = "." + ext
                        if any(c in ext for c in ('/', '\\', ':', '*', '?', '"', '<', '>', '|')):
                            print("Invalid extension characters.\n")
                            continue
                    export_ext = ext
                    stage = STAGE_EXPORT_DEST
                    break
                if stage != STAGE_EXPORT_EXT:
                    continue

            elif stage == STAGE_EXPORT_DEST:
                while True:
                    print("\nWhere to save?")
                    print("  1) Root folder (the one you just scanned)")
                    print("  2) Script's location")
                    print("  3) Custom path")
                    prompt = "Choose [1, 2, 3] (default 1): "
                    try:
                        choice = get_input(prompt).strip()
                    except CommandAction as e:
                        if e.command == "back":
                            stage = BACK_MAP[stage]
                            break
                        raise
                    if choice == "" or choice == "1":
                        export_dest = os.path.abspath(path)
                        break
                    elif choice == "2":
                        script_dir = os.path.dirname(os.path.realpath(sys.argv[0])) if sys.argv[0] else os.getcwd()
                        export_dest = script_dir
                        break
                    elif choice == "3":
                        stage = STAGE_EXPORT_DEST_CUSTOM
                        break
                    else:
                        print("Please enter 1, 2, 3, or press Enter.\n")
                if stage == STAGE_EXPORT_DEST:
                    full_path = os.path.join(export_dest, export_fname + export_ext)
                    try:
                        sym = get_symbols(use_ascii)
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(f"Directory tree of: {os.path.abspath(path)}\n")
                            root_name = os.path.basename(path) or path
                            f.write(root_name + "\n")
                            tree = build_tree(path, include_files=include_files,
                                              max_depth=max_depth, sym=sym)
                            f.write("\n".join(tree))
                            f.write("\n")
                        print(f"Tree saved to {full_path}")
                    except Exception as e:
                        print(f"Failed to export: {e}")
                    stage = STAGE_DONE
                elif stage != STAGE_EXPORT_DEST_CUSTOM:
                    continue

            elif stage == STAGE_EXPORT_DEST_CUSTOM:
                while True:
                    try:
                        custom = get_input("Enter the full path: ").strip()
                    except CommandAction as e:
                        if e.command == "back":
                            stage = BACK_MAP[stage]
                            break
                        raise
                    if not custom:
                        print("Please enter a valid path or use a different option.\n")
                        continue
                    if os.path.isdir(custom):
                        export_dest = custom
                        break
                    else:
                        print(f"'{custom}' is not a valid directory.\n")
                if stage != STAGE_EXPORT_DEST_CUSTOM:
                    continue
                full_path = os.path.join(export_dest, export_fname + export_ext)
                try:
                    sym = get_symbols(use_ascii)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(f"Directory tree of: {os.path.abspath(path)}\n")
                        root_name = os.path.basename(path) or path
                        f.write(root_name + "\n")
                        tree = build_tree(path, include_files=include_files,
                                          max_depth=max_depth, sym=sym)
                        f.write("\n".join(tree))
                        f.write("\n")
                    print(f"Tree saved to {full_path}")
                except Exception as e:
                    print(f"Failed to export: {e}")
                stage = STAGE_DONE

            elif stage == STAGE_DONE:
                print()
                stage = STAGE_DIR

        except CommandAction as e:
            if e.command == "exit":
                print("Goodbye!")
                break
            elif e.command == "clear":
                clear_screen()
                stage = STAGE_DIR
                continue
            elif e.command == "restart":
                stage = STAGE_DIR
                continue
            elif e.command == "back":
                if stage != STAGE_DIR:
                    stage = BACK_MAP.get(stage, STAGE_DIR)
                else:
                    print("Already at the first step.")
                continue

    if not args.no_pause:
        try:
            input("\nPress Enter to exit...")
        except (EOFError, KeyboardInterrupt):
            pass

if __name__ == "__main__":
    main()