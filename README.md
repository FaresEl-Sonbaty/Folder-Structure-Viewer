# Folder Structure Viewer

A cross‑platform terminal tool that displays the complete folder‑and‑subfolder tree of any directory.  
It supports optional file listing, depth limits, ASCII/Unicode tree characters, step‑by‑step prompts, undo, full‑screen help, persistent settings, and export to file.

## Features

- Beautiful tree‑view with Unicode box‑drawing characters (ASCII mode available).
- Optionally include files with their extensions.
- Adjustable maximum depth (0 = root only, blank = unlimited).
- Interactive step‑by‑step prompts with error recovery.
- **Commands** (prefixed with `--`) at any prompt:
  - `--exit` `--clear` `--restart` `--back` `--help` `--help-full` `--settings`
- Undo (`--back`) returns to the previous question.
- Immersive full‑screen help (`--help-full`) and an extensive settings panel (`--settings`).
- **Persistent settings** saved in `folder_structure_settings.json`:
  - Toggle default value display in prompts.
  - Change default filename, extension, auto‑export behaviour, etc.
  - Per‑step automation: automatically apply defaults or ask.
  - Presets: *Ask all*, *Skip all*, *Factory default*.
- Export the tree to a text file with a detailed wizard:
  - Choose filename, extension, destination (root folder, script folder, custom path).
  - If the file already exists, you can overwrite, rename, or cancel.
- Double‑click friendly: console stays open after exit (except with `--no-pause`).
- Command‑line one‑shot mode for scripting.

## Installation

1. Ensure Python 3.7+ is installed.
2. Download `folder_structure.py` (or clone the repository).
3. Place it anywhere you like.

## Usage

### Interactive mode
Double‑click the script, or run:
```bash
python folder_structure.py
```
Follow the prompts. At any prompt you can type a command (e.g. `--help`).

### Command‑line one‑shot mode
```bash
python folder_structure.py "D:\MyFolder" --files --max-depth 2 --ascii
```
This prints the tree and exits without entering interactive mode.

Available flags:
- `--files` / `-f` : include files
- `--max-depth N` : limit depth (0 = root only)
- `--ascii` : use ASCII tree drawing characters
- `--no-pause` : do not pause on exit (useful in scripts)

### Giving an AI agent context about your project  
When working with an AI coding assistant or any LLM on a large project, the AI often needs to understand the folder structure, key files, and how things are organised.  
This tool lets you quickly generate a **complete directory tree** and share it in your prompt:

1. Run the tool on your project root (e.g. `D:\Projects\MyApp`).  
2. Include files (`--files`) so the AI sees actual file names.  
3. Set a depth limit that captures your source layout (e.g. `--max-depth 3`).  
4. Export the tree to a `.txt` file, or simply copy it from the terminal.  
5. Paste the tree into your conversation alongside your other instructions.

**Example command to generate a project overview:**
```bash
python folder_structure.py "C:\Users\Fares\Code\MyProject" --files --max-depth 3 > project_tree.txt
```
You can also use the interactive export wizard and choose to save the tree in a convenient location.  

This gives the AI a clear map of your repository, making it easier for the model to understand file relationships and provide more accurate, context‑aware answers.
## Settings

Type `--settings` at any prompt to open the settings panel. Changes are saved automatically and persist across runs. You can:
- Show/hide default values in prompts.
- Modify all default answers (filename, extension, include files, export, depth).
- Toggle **auto‑apply** for each step individually.
- Switch between presets: **Ask all**, **Skip all**, or revert to factory defaults.

The settings file is created next to the script as `folder_structure_settings.json`. Deleting it restores defaults.

## Examples

**Folders only, depth limited to 2**
```
Enter directory path: C:\Users\Me\Documents
Include files? (y/n) (default: n): n
Max depth (0 = root folder only, leave blank for unlimited) (default: unlimited): 2
```
**Folders + files, with ASCII, exported to .txt**
```
Enter directory path: D:\Projects
Include files? (y/n) (default: n): y
Max depth … : [leave blank]
Export tree to file? (y/n) (default: n): y
Enter filename (without extension) (default: untitled): project_tree
Enter extension (e.g. .txt, .docx) (default: .txt): .txt
Where to save?
  1) Root folder (the one you just scanned)
  2) Script's location
  3) Custom path
Choose [1, 2, 3] (default: 1): 1
Tree saved to D:\Projects\project_tree.txt
```

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Fares El-Sonbaty
---

**Enjoy!**
