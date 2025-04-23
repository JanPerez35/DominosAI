import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import os
import sys

# Define paths to the game modes
game_modes = {
    "1 Players vs 1 AI":           "DominoGame2Player.py",
    "2 AI Players (Spectate)":     "DominoGame2Player2AI0Human.py",
    "3 Players vs 1 AI":           "DominoGame4Player1AI3Human.py",
    "2 Players vs 2 AI":           "DominoGame4Player2AI2Human.py",
    "1 Player vs  3 AI":           "DominoGame4Player.py",
    "All 4 Players AI (Spectate)": "DominoGame4Player4AI0Human.py"
}

def launch_game(path, team_mode, layout=None):
    """Launches the given script, passing --team and optionally --layout for Teams"""
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
    Handler for '2 Players vs 2 AI'.
    If team_mode is checked, ask which layout they want.
    2 humans on a team or 1 human 1 AI.
    Otherwise launches the game in free-for-all
    """
    if team_mode_var.get():
        want_human_team = messagebox.askyesno(
            title="Choose Team Setup",
            message=(
                "Would you like a human team (both humans vs both AIs)?\n\n"
                "Yes = Humans Together, No = Mixed Teams (1 human + 1 AI)"
            )
        )
        layout = "humans_team" if want_human_team else "ai_pairs"
        launch_game(path, True, layout)
    else:
        launch_game(path, False)


def on_3p1AI_click(path):
    """
    Handler for '3 Players vs 1 AI'.
    Always ask which human pairs with the AI.
    In case its in teams otherwise skips
    """
    # Ask user which player to pair with the AI
    if team_mode_var.get():

        choice = simpledialog.askinteger(
            title="Choose Team Setup",
            prompt=(
                "Which human should pair with the AI?\n"
                "Enter 1 for Player 1 + AI,\n"
                "2 for Player 2 + AI,\n"
                "3 for Player 3 + AI."
            ),
            minvalue=1,
            maxvalue=3
        )
        if choice is None:
            return
        # layout codes: p1, p2, p3
        layout = f"p{choice}"
        # team_mode True to enable parsing --layout
        launch_game(path, True, layout)
    else:
        launch_game(path, False)


# Set up the menu window
root = tk.Tk()
root.title("Domino Game Menu")
root.geometry("600x450")

tk.Label(root, text="Select Game Mode", font=("Helvetica", 16)).pack(pady=20)

# Checkbox for team mode (applies only to 2v2)
team_mode_var = tk.BooleanVar()
tk.Checkbutton(
    root,
    text="Enable Team Mode (2 vs 2)",
    variable=team_mode_var,
    font=("Helvetica", 12)
).pack(pady=10)

# Buttons to launch game modes
for mode, path in game_modes.items():
    if mode == "2 Players vs 2 AI":
        cmd = lambda p=path: on_2v2_click(p)
    elif mode == "3 Players vs 1 AI":
        cmd = lambda p=path: on_3p1AI_click(p)
    else:
        cmd = lambda p=path: launch_game(p, team_mode_var.get())

    tk.Button(
        root,
        text=mode,
        font=("Helvetica", 12),
        width=30,
        command=cmd
    ).pack(pady=5)

root.mainloop()
