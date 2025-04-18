import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

# Define paths to the game modes
GAME_MODES = {
    "1 Players vs 1 AI":           "DominoGame2Player.py",
    "2 AI Players (Spectate)":     "DominoGame2Player2AI0Human.py",
    "3 Players vs 1 AI":           "DominoGame4Player1AI3Human.py",
    "2 Players vs 2 AI":           "DominoGame4Player2AI2Human.py",
    "1 Player vs  3 AI":           "DominoGame4Player.py",
    "All 4 Players AI (Spectate)": "DominoGame4Player4AI0Human.py"
}

def launch_game(path, team_mode, layout=None):
    """Launches the given script, passing --team and optionally --layout."""
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    args = [sys.executable, path]
    if team_mode:
        args.append("--team")
        if layout:
            args += ["--layout", layout]
    subprocess.Popen(args)

def on_2v2_click(path):
    """
    Handler for the '2 Players vs 2 AI' button.
    If team_mode is checked, ask which layout they want.
    """
    if team_mode_var.get():
        # Ask the user which team setup they want:
        # Yes → both humans on one team (humans_team)
        # No  → mixed human–AI pairs (ai_pairs)
        want_human_team = messagebox.askyesno(
            title="Choose Team Setup",
            message=(
                "Would you like a human team (both humans vs both AIs)?\n\n"
                "Click Yes for Humans Together\n"
                "Click No for Mixed Teams (1 human + 1 AI per team)"
            )
        )
        layout = "humans_team" if want_human_team else "ai_pairs"
        launch_game(path, True, layout)
    else:
        # If checkbox isn’t checked, just launch free‑for‑all
        launch_game(path, False)

# Set up the menu window
root = tk.Tk()
root.title("Domino Game Menu")
root.geometry("600x400")

tk.Label(root, text="Select Game Mode", font=("Helvetica", 16)).pack(pady=20)

# Add checkbox for team mode
team_mode_var = tk.BooleanVar()
team_checkbox = tk.Checkbutton(
    root,
    text="Enable Team Mode (2 vs 2)",
    variable=team_mode_var,
    font=("Helvetica", 12)
)
team_checkbox.pack(pady=10)

# Buttons to launch game modes
for mode, path in GAME_MODES.items():
    if mode == "2 Players vs 2 AI":
        cmd = lambda p=path: on_2v2_click(p)
    else:
        cmd = lambda p=path: launch_game(p, team_mode_var.get())

    btn = tk.Button(
        root,
        text=mode,
        font=("Helvetica", 12),
        width= 30,
        command=cmd
    )
    btn.pack(pady=5)

root.mainloop()
