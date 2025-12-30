# Folder Activity App

A Python desktop application with a graphical user interface (GUI) for scanning and renaming folders and files according to specific rules, with logging and undo support.

## Features
- Select a starting folder
- Choose an activity (scan videos, scan pictures, scan images)
- Only one activity can be selected at a time
- For "scan videos":
  - Renames folders under the starting folder to remove periods from folder names
  - Renames files to remove periods from the name (except before the extension)
- Logs all actions with timestamp and sequence
- Undo the last set of changes

## How to Run
1. Make sure you have Python 3.7+ installed.
2. (Recommended) Use the provided virtual environment or create one:
   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   pip install tk
   ```
3. Run the application:
   ```sh
   python main.py
   ```

## Undo Feature
- The Undo button will revert the last set of renames performed by the app.

## Notes
- Only the "scan videos" activity is implemented. Others are placeholders.
- All actions are logged in the UI.

## Customization
- The UI can be further styled or themed as needed.

---

This project was generated and scaffolded with the help of GitHub Copilot.
