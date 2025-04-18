import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
import copy
import pygame
import sys

'''
Okay so this mode is under construction. 
Now we update it to be 3 players (human) vs 1 AI and add a pass-and-play screen for the human turn.
'''

# -------------- Game Logic --------------

class DominoGame:
    def __init__(self,team_mode,layout):

        self.layout = layout

        # define the two teams based on which human pairs with the AI
        if team_mode:
            if layout == "p1":
                # Player 1 (0) + AI (3) vs Player 2 (1)+Player 3 (2)
                self.teams = [[0, 3], [1, 2]]
            elif layout == "p2":
                # Player 2 + AI vs Player 1+Player 3
                self.teams = [[1, 3], [0, 2]]
            else:  # "p3"
                # Player 3 + AI vs Player 1+Player 2
                self.teams = [[2, 3], [0, 1]]
        else:
            # free‑for‑all: no teams
            self.teams = []

        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)
        # Deal 7 tiles to each of 4 players (players: 0, 1, and 2 = human; 3 = AI)
        self.players = [self.tiles[i*7:(i+1)*7] for i in range(4)]
        self.stock = self.tiles[28:]
        self.board = deque()
        self.board_owners = deque()  # To track who placed each tile
        self.current_player = 0
        self.passes = 0
        self.team_mode = team_mode
        # Find the (6,6) to start the game
        for i, hand in enumerate(self.players):
            if (6, 6) in hand:
                self.current_player = (i + 1) % 4
                hand.remove((6, 6))  # Remove from hand
                self.board.append((6, 6))  # Place it on the board
                self.board_owners.append(i)  # Track who played it
                break

    def is_valid_move(self, tile, end):
        return end in tile

    def get_valid_moves(self, hand):
        if not self.board:
            return hand
        left, right = self.board[0][0], self.board[-1][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]

    def draw_from_stock(self, player):
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None

    def play_tile(self, player, tile):
        if not self.board:
            self.board.append(tile)
            self.board_owners.append(player)
        else:
            left, right = self.board[0][0], self.board[-1][1]
            if self.is_valid_move(tile, left):
                self.board.appendleft(tile if tile[1] == left else (tile[1], tile[0]))
                self.board_owners.appendleft(player)
            elif self.is_valid_move(tile, right):
                self.board.append(tile if tile[0] == right else (tile[1], tile[0]))
                self.board_owners.append(player)
            else:
                raise ValueError("Invalid move")
        self.players[player].remove(tile)
        self.passes = 0

    def pass_turn(self):
        self.passes += 1

    def is_game_over(self):
        return any(len(p) == 0 for p in self.players) or self.passes >= 4

    def get_winner(self):
        if not self.team_mode:
            # Free-for-all winner: lowest pip count
            player_scores = [(i, sum(tile[0] + tile[1] for tile in hand)) for i, hand in enumerate(self.players)]
            player_scores.sort(key=lambda x: x[1])
            lowest_score = player_scores[0][1]
            tied_players = [i for i, score in player_scores if score == lowest_score]
            return -1 if len(tied_players) > 1 else player_scores[0][0]
        else:
            # sum pip‑counts by the two self.teams entries
            scores = []
            for team in self.teams:
                total = sum(pip for player in team
                            for tile in self.players[player]
                            for pip in tile)
                scores.append(total)

            if scores[0] < scores[1]:
                return "Team 1"
            elif scores[1] < scores[0]:
                return "Team 2"
            else:
                return -1  # tie

# -------------- GUI --------------

class DominoGUI:
    def __init__(self, root, team_mode, layout):
        self.root = root
        self.root.title("Domino - 3 Players vs 1 AI (Pass-and-Play)")
        # initialize game logic with team_mode and layout
        self.game = DominoGame(team_mode, layout)

        # Color mapping
        if self.game.team_mode:
            # team mode: two teams -> two colors
            palette = ['blue', 'red']
            self.player_colors = [None] * 4
            for team_index, team in enumerate(self.game.teams):
                for player_index in team:
                    self.player_colors[player_index] = palette[team_index]
        else:
            # free-for-all: four distinct colors
            self.player_colors = ['blue', 'red', 'green', 'purple']

        self.game_over = False

        # Main board frame
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.canvas_width = 1000
        self.canvas_height = 300

        self.canvas_scrollbar = tk.Scrollbar(self.board_frame, orient=tk.HORIZONTAL)
        self.canvas_scrollbar.pack(fill=tk.X)

        self.board_canvas = tk.Canvas(
            self.board_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='light gray',
            xscrollcommand=self.canvas_scrollbar.set,
            scrollregion=(0, 0, 5000, 300)
        )
        self.board_canvas.pack(side=tk.TOP, fill=tk.X)
        self.canvas_scrollbar.config(command=self.board_canvas.xview)

        # Scroll buttons
        self.scroll_button_frame = tk.Frame(self.board_frame)
        self.scroll_button_frame.pack(pady=5)
        tk.Button(self.scroll_button_frame, text="Scroll Left", command=self.scroll_left).pack(side=tk.LEFT, padx=5)
        tk.Button(self.scroll_button_frame, text="Scroll Right", command=self.scroll_right).pack(side=tk.LEFT, padx=5)

        # Hand frame
        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        # Info and controls
        self.info_frame = tk.Frame(root)
        self.info_frame.pack()
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        # Legend
        self.legend_frame = tk.Frame(root)
        self.legend_frame.pack(pady=5)
        tk.Label(self.legend_frame, text="Legend:").pack(side=tk.LEFT)
        if self.game.team_mode:
            for team_index, team in enumerate(self.game.teams):
                for p in team:
                    name = ["Player 1","Player 2","Player 3","AI 1"][p]
                    tk.Label(
                        self.legend_frame,
                        text=f"{name} (Team {team_index+1})",
                        fg=self.player_colors[p],
                        font=("Arial", 10, "bold")
                    ).pack(side=tk.LEFT, padx=5)
        else:
            names = ["Player 1","Player 2","Player 3","AI 1"]
            for i, name in enumerate(names):
                tk.Label(
                    self.legend_frame,
                    text=name,
                    fg=self.player_colors[i],
                    font=("Arial", 10, "bold")
                ).pack(side=tk.LEFT, padx=5)

        # Control buttons
        tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile).pack(side=tk.LEFT, padx=5)
        self.music_on = True
        tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music).pack(side=tk.LEFT, padx=5)

        # Status and AI tile count
        self.status_label = tk.Label(self.info_frame, text="Your turn!", font=("Arial", 12))
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.ai_label = tk.Label(self.info_frame, text=f"AI 1 has {len(self.game.players[3])} tiles", font=("Arial", 10))
        self.ai_label.pack(side=tk.RIGHT, padx=5)

        # For pass-and-play
        self.last_human = None

        # Initial draw
        self.draw_board()
        self.draw_hand()
        if self.game.current_player not in [0, 1, 2]:
            self.status_label.config(text=f"AI starts with (6|6)")
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text=self.human_status_text())

    # ... rest of DominoGUI methods ...


    def human_status_text(self):
        # Return appropriate status for human: indicate Player 1, Player 2, and Player 3.
        if self.game.current_player == 0:
            return "Your turn! (Player 1)"
        elif self.game.current_player == 1:
            return "Your turn! (Player 2)"
        elif self.game.current_player == 2:
            return "Your turn! (Player 3)"
        else:
            return ""

    def scroll_left(self):
        self.board_canvas.xview_scroll(-1, "units")

    def scroll_right(self):
        self.board_canvas.xview_scroll(1, "units")

    def toggle_music(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_button.config(text="Play Music")
        else:
            pygame.mixer.music.unpause()
            self.music_button.config(text="Mute Music")
        self.music_on = not self.music_on

    def draw_board(self):
        self.board_canvas.delete("all")
        x, y = 500, 150  # Start position for board drawing
        tile_positions = []

        for i, tile in enumerate(self.game.board):
            owner = self.game.board_owners[i]
            if self.game.team_mode:
                team_colors = {0: 'blue', 1: 'red', 2: 'blue', 3: 'red'}
                color = team_colors[owner]
            else:
                color = self.player_colors[owner]
            is_double = tile[0] == tile[1]

            if is_double:
                # Vertical tile
                self.board_canvas.create_rectangle(x, y, x + 30, y + 60, fill='white', outline=color, width=2)
                self.board_canvas.create_text(x + 15, y + 30, text=f"{tile[0]}\n|\n{tile[1]}", fill=color,
                                              font=('Courier', 10, 'bold'))
                tile_positions.append((x, 60))
                x += 40
            else:
                # Horizontal tile
                self.board_canvas.create_rectangle(x, y, x + 60, y + 30, fill='white', outline=color, width=2)
                self.board_canvas.create_text(x + 30, y + 15, text=f"{tile[0]}|{tile[1]}", fill=color,
                                              font=('Courier', 12, 'bold'))
                tile_positions.append((x, 60))
                x += 70

            self.board_canvas.config(scrollregion=(0, 0, max(x + 100, 1000), 300))
            if tile_positions:
                latest_x = tile_positions[-1][0]
                canvas_view_x = max(latest_x - self.canvas_width // 2, 0)
                self.board_canvas.xview_moveto(canvas_view_x / (max(x + 100, 1000)))

    def draw_hand(self):
        # Clear the hand frame first
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        player = self.game.current_player
        hand = self.game.players[player]
        valid_moves = self.game.get_valid_moves(hand)
        # Display the complete hand (7 tiles at game start, or remaining tiles)
        for tile in hand:
            tile_str = f"[{tile[0]}|{tile[1]}]"
            btn = tk.Button(self.hand_frame, text=tile_str, font=('Courier', 12), relief='raised',
                            fg=self.player_colors[player],
                            state=tk.NORMAL if tile in valid_moves else tk.DISABLED,
                            command=lambda t=tile: self.play_tile(t))
            btn.pack(side=tk.LEFT, padx=4)

    def show_pass_screen(self, next_player):
        # Create a Toplevel modal window that covers the current game window,
        # asking the next human player to press Ready (so that they cannot see the previous hand).
        print(f"Showing pass screen for player {self.game.current_player}")
        pass_screen = tk.Toplevel(self.root)
        pass_screen.grab_set()
        pass_screen.geometry("400x200+400+200")
        pass_screen.title("Pass Device")
        msg = ""
        if next_player == 0:
            msg = "Pass device to Player 1\n\n(Ensure previous hand is not visible.)"
        elif next_player == 1:
            msg = "Pass device to Player 2\n\n(Ensure previous hand is not visible.)"
        elif next_player == 2:
            msg = "Pass device to Player 3\n\n(Ensure previous hand is not visible.)"
        label = tk.Label(pass_screen, text=msg, font=("Arial", 14))
        label.pack(expand=True)
        btn = tk.Button(pass_screen, text="I'm Ready", font=("Arial", 12),
                        command=lambda: self.close_pass_screen(pass_screen))
        btn.pack(pady=10)
        # Wait until user clicks ready.
        self.root.wait_window(pass_screen)

    def close_pass_screen(self, window):
        window.destroy()
        # After closing, update status and show hand for new human turn.
        self.status_label.config(text=self.human_status_text())
        self.draw_hand()

    def after_move(self):
        self.draw_board()
        self.update_ai_tile_counts()
        if self.game.is_game_over():
            self.end_game()
        else:
            # If next turn is human, check if pass screen is needed.
            if self.game.current_player in [0, 1, 2]:
                # Always show pass screen between human turns
                #if self.last_human is None or self.last_human != self.game.current_player:
                print(f"Showing pass screen for player {self.game.current_player}")
                self.show_pass_screen(self.game.current_player)
                self.last_human = self.game.current_player
                self.status_label.config(text=self.human_status_text())
                self.draw_hand()
            else:
                self.last_human = None  # reset since it's an AI's turn
                self.root.after(500, self.ai_turn)

    def play_tile(self, tile):
        try:
            # Use the current player's hand (will be 0 or 2)
            self.game.play_tile(self.game.current_player, tile)
            self.game.current_player = (self.game.current_player + 1) % 4
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    def pass_turn(self):
        self.game.pass_turn()
        self.game.current_player = (self.game.current_player + 1) % 4
        self.after_move()

    def draw_tile(self):
        tile = self.game.draw_from_stock(self.game.current_player)
        if tile:
            self.status_label.config(text=f"You drew {tile}")
        else:
            self.status_label.config(text="Stock is empty")
        self.draw_hand()

    def ai_turn(self):
        # If it’s a human turn or game is over, process accordingly.
        if self.game.current_player in [0, 1, 2] or self.game.is_game_over():
            if self.game.is_game_over():
                self.end_game()
            else:
                self.status_label.config(text=self.human_status_text())
                self.draw_hand()
            return

        cp = self.game.current_player
        hand = self.game.players[cp]
        valid_moves = self.game.get_valid_moves(hand)
        # If no valid move exists, draw from stock until a move is possible or stock empty
        while not valid_moves and self.game.stock:
            self.game.draw_from_stock(cp)
            valid_moves = self.game.get_valid_moves(self.game.players[cp])

        # Use monte-carlo simulation for AI move if possible
        move = self.monte_carlo_ai_move(cp, simulations=25) if valid_moves else None
        if move:
            self.game.play_tile(cp, move)
            self.status_label.config(text=f"AI played {move}")
        else:
            self.game.pass_turn()
            self.status_label.config(text=f"AI passed")
        self.draw_board()
        self.update_ai_tile_counts()
        self.game.current_player = (self.game.current_player + 1) % 4
        self.root.after(1000, self.after_move)

    def monte_carlo_ai_move(self, player_index, simulations=25):
        hand = self.game.players[player_index]
        valid_moves = self.game.get_valid_moves(hand)
        if not valid_moves:
            return None

        move_scores = {}
        for move in valid_moves:
            total_score = 0
            for _ in range(simulations):
                sim_game = copy.deepcopy(self.game)
                try:
                    sim_game.play_tile(player_index, move)
                except:
                    continue
                winner = self.simulate_random_playout(sim_game)
                total_score += 1 if winner == player_index else 0
            move_scores[move] = total_score / simulations

        best_move = max(move_scores, key=move_scores.get)
        return best_move

    def simulate_random_playout(self, sim_game):
        current = sim_game.current_player
        while not sim_game.is_game_over():
            hand = sim_game.players[current]
            valid = sim_game.get_valid_moves(hand)
            if valid:
                sim_game.play_tile(current, random.choice(valid))
            elif sim_game.stock:
                sim_game.draw_from_stock(current)
            else:
                sim_game.pass_turn()
            current = (current + 1) % 4
        return sim_game.get_winner()

    def update_ai_tile_counts(self):
        # Update labels for AI 1 (index 1) and AI 2 (index 3)
        self.ai_label.config(text=f"AI 1 has {len(self.game.players[3])} tiles")

    def end_game(self):
        winner = self.game.get_winner()
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]
        # score_lines = "\n".join(
        #     f"Player {i} ({'You' if i in [0,1,2] else 'AI'}): {score} points | Tiles: {hand}"
        #     for i, score, hand in player_scores
        # )
        # print("Final scores (lower is better):")
        # for i, score, hand in player_scores:
        #     print(f"Player {i}: {score} points")
        #
        # if winner == 0 or winner == 2 or winner == 1:
        #     msg = "🎉 You win!"
        # elif winner == -1:
        #     msg = "🤝 It's a tie!"
        # else:
        #     # For AI wins, indicate which AI won (mapping index 1->AI1 and index 3->AI2)
        #     msg = f"🤖 AI {1 if winner==1 else 2} wins!"
        #
        # msg += "\nFinal Scores:\n" + score_lines
        #
        # messagebox.showinfo("Game Over", msg)
        if self.game.team_mode:
            # Team-based scoring
            team_0_score = sum(score for i, score, _ in player_scores if i in [0, 2])
            team_1_score = sum(score for i, score, _ in player_scores if i in [1, 3])

            team_lines = "\n".join(
                f"Player {i} ({'You' if i in [0, 1, 2] else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )
            msg = "🤝 It's a tie!" if winner == -1 else f"🎉 {winner} wins!"
            msg += f"\n\nTeam A score: {team_0_score}\nTeam B score: {team_1_score}"
            msg += "\n\nFinal Player Scores:\n" + team_lines
        else:
            # Free-for-all scoring
            score_lines = "\n".join(
                f"Player {i} ({'You' if i in [0, 1, 2] else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )

            if winner in [0,1,2]:
                msg = "🎉 You win!"
            elif winner == -1:
                msg = "🤝 It's a tie!"
            else:
                msg = f"🤖 AI {1} wins!"
            msg += "\nFinal Scores:\n" + score_lines
        messagebox.showinfo("Game Over", msg)
        self.root.quit()
# -------------- Run the App --------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--team",
        action="store_true",
        help="Enable team mode"
    )
    parser.add_argument(
        "--layout",
        choices=["p1", "p2", "p3"],
        default="p1",
        help=(
            "p1: Player 1 + AI vs Players 2&3\n"
            "p2: Player 2 + AI vs Players 1&3\n"
            "p3: Player 3 + AI vs Players 1&2"
        )
    )
    args = parser.parse_args()

    team_mode = args.team
    layout   = args.layout

    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    app = DominoGUI(root, team_mode, layout)
    root.mainloop()
    sys.exit()

