import tkinter as tk
import subprocess
import os
import sys


# Define paths to the game modes
GAME_MODES = {
    "1 Players vs 1 AI": "DominoGame2Player.py",
    "2 AI Players (Spectate)": "DominoGame2Player2AI0Human.py",
    "3 Players vs 1 AI": "DominoGame4Player1AI3Human.py",
    "2 Players vs 2 AI": "DominoGame4Player2AI2Human.py",
    "1 Player vs  3 AI": "DominoGame4Player.py",
    "All 4 Players AI (Spectate)": "DominoGame4Player4AI0Human.py"
}

def launch_game(path, team_mode):
    if os.path.exists(path):
        args = [sys.executable, path]
        if team_mode:
            args.append("--team")
        subprocess.Popen(args)
    else:
        print(f"File not found: {path}")

# Set up the menu window
root = tk.Tk()
root.title("Domino Game Menu")
root.geometry("600x400")

tk.Label(root, text="Select Game Mode", font=("Helvetica", 16)).pack(pady=20)

# Add checkbox for team mode
team_mode_var = tk.BooleanVar()
team_checkbox = tk.Checkbutton(root, text="Enable Team Mode (2 vs 2)", variable=team_mode_var, font=("Helvetica", 12))
team_checkbox.pack(pady=10)

# Buttons to launch game modes
for mode, path in GAME_MODES.items():
    btn = tk.Button(root, text=mode, font=("Helvetica", 12), width=30,
                    command=lambda p=path: launch_game(p, team_mode_var.get()))
    btn.pack(pady=5)

root.mainloop()