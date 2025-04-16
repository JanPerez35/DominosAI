import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
import copy
import pygame

'''
Okay so this mode is under construction. It currently has 3 AI against a player but
the order is not clear of who goes when. There is not a feature to have teams or have multiple
human players yet. Also the window is kinda hard to view when there are this many players.
Now we update it to be 2 players (human) vs 2 AI and add a pass-and-play screen for the human turn.
'''

# -------------- Game Logic --------------

class DominoGame:
    def __init__(self):
        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)
        # Deal 7 tiles to each of 4 players (players: 0 and 2 = human; 1 and 3 = AI)
        self.players = [self.tiles[i*7:(i+1)*7] for i in range(4)]
        self.stock = self.tiles[28:]
        self.board = deque()
        self.board_owners = deque()  # To track who placed each tile
        self.current_player = 0
        self.passes = 0
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
        # Calculate total pip count for each player
        player_scores = []
        for i, hand in enumerate(self.players):
            total = sum(tile[0] + tile[1] for tile in hand)
            player_scores.append((i, total))

        # Sort players by score (lowest total wins)
        player_scores.sort(key=lambda x: x[1])
        lowest_score = player_scores[0][1]
        tied_players = [i for i, score in player_scores if score == lowest_score]

        if len(tied_players) > 1:
             return -1  # Tie
        else:
             return player_scores[0][0]  # Index of the winning player

# -------------- GUI --------------

class DominoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Domino - 2 Players vs 2 AI (Pass-and-Play)")
        self.game = DominoGame()

        self.player_colors = ['blue', 'red', 'green', 'purple']
        # In our new order, player indices:
        # 0: Player 1 (human, blue)
        # 1: AI 1 (red)
        # 2: Player 2 (human, green)
        # 3: AI 2 (purple)

        # Layout (keeping original aesthetic)
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.canvas_width = 1000
        self.canvas_height = 300

        self.canvas_scrollbar = tk.Scrollbar(self.board_frame, orient=tk.HORIZONTAL)
        self.canvas_scrollbar.pack(fill=tk.X)

        self.board_canvas = tk.Canvas(self.board_frame, width=self.canvas_width, height=self.canvas_height,
                                      bg='light gray', xscrollcommand=self.canvas_scrollbar.set,
                                      scrollregion=(0, 0, 5000, 300))
        self.board_canvas.pack(side=tk.TOP, fill=tk.X)
        self.canvas_scrollbar.config(command=self.board_canvas.xview)

        self.scroll_button_frame = tk.Frame(self.board_frame)
        self.scroll_button_frame.pack(pady=5)

        self.scroll_left_btn = tk.Button(self.scroll_button_frame, text=" Scroll Left", command=self.scroll_left)
        self.scroll_left_btn.pack(side=tk.LEFT, padx=5)

        self.scroll_right_btn = tk.Button(self.scroll_button_frame, text="Scroll Right ", command=self.scroll_right)
        self.scroll_right_btn.pack(side=tk.LEFT, padx=5)

        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        # Legend Frame (update to show the two human players and 2 AI)
        self.legend_frame = tk.Frame(root)
        self.legend_frame.pack(pady=5)

        self.legend_label = tk.Label(self.legend_frame, text="Legend:")
        self.legend_label.pack(side=tk.LEFT)

        legend_info = [
            ("Player 1", 'blue'),
            ("Player 2", 'red'),
            ("Player 3", 'green'),
            ("Player 4", 'purple'),
        ]
        for name, color in legend_info:
            label = tk.Label(self.legend_frame, text=f"{name}", fg=color, font=("Arial", 10, 'bold'))
            label.pack(side=tk.LEFT, padx=5)

        # Buttons
        self.pass_button = tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)

        self.draw_button = tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        # Labels
        self.status_label = tk.Label(self.info_frame, text="Your turn!", font=("Arial", 12))
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Only for the AIs
        # self.ai_labels = [
        #     tk.Label(self.info_frame, text=f"AI 1 has 7 tiles", font=("Arial", 10)),
        #     tk.Label(self.info_frame, text=f"AI 2 has 7 tiles", font=("Arial", 10))
        # ]
        # for label in self.ai_labels:
        #     label.pack(side=tk.RIGHT, padx=5)

        # For pass-and-play between human players (Player 1 and Player 2)
        self.last_human = None  # To check which human last played

        self.draw_board()
        self.draw_hand()
        # If game started on non-human turn, process accordingly.
        # if self.game.current_player not in [0, 2]:
        #     self.status_label.config(text=f"AI {self.game.current_player} starts with (6|6)")
        #     self.root.after(1000, self.ai_turn)
        # else:
        self.status_label.config(text=self.human_status_text())

    def human_status_text(self):
        # Return appropriate status for human: indicate Player.
        if self.game.current_player == 0:
            return "Your turn! (Player 1)"
        elif self.game.current_player ==1:
            return "Your turn! (Player 2"
        elif self.game.current_player ==2:
            return "Your turn! (Player 3)"
        else:
            return "Your turn! (Player 2)"

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
        pass_screen = tk.Toplevel(self.root)
        pass_screen.grab_set()
        pass_screen.geometry("400x200+400+200")
        pass_screen.title("Pass Device")
        msg = ""
        if next_player == 0:
            msg = "Pass device to Player 1\n\n(Ensure previous hand is not visible.)"
        elif next_player==1:
            msg= "Pass device to Player 2\n\n(Ensure previous hand is not visible.)"
        elif next_player == 2:
            msg = "Pass device to Player 3\n\n(Ensure previous hand is not visible.)"
        elif next_player == 3:
            msg = "Pass device to Player 4\n\n(Ensure previous hand is not visible.)"
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
        if self.game.is_game_over():
            self.end_game()
        else:
            self.last_human = self.game.current_player
            self.show_pass_screen(self.game.current_player)
            self.status_label.config(text=self.human_status_text())
            self.draw_hand()

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


    def end_game(self):
        winner = self.game.get_winner()
        # Optional: Print all players' remaining points
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]
        score_lines = "\n".join(
            f"Player {i} ({'You' if i in [0,2] else 'AI'}): {score} points | Tiles: {hand}"
            for i, score, hand in player_scores
        )
        print("Final scores (lower is better):")
        for i, score, hand in player_scores:
            print(f"Player {i}: {score} points")

        if winner == 0 or winner == 2:
            msg = "🎉 You win!"
        elif winner == -1:
            msg = "🤝 It's a tie!"
        else:
            # For AI wins, indicate which AI won (mapping index 1->AI1 and index 3->AI2)
            msg = f"🤖 AI {1 if winner==1 else 2} wins!"

        msg += "\nFinal Scores:\n" + score_lines

        messagebox.showinfo("Game Over", msg)
        self.root.quit()

# -------------- Run the App --------------

if __name__ == "__main__":
    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")  # Ensure this file exists in your directory
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()
