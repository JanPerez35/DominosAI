# gui_client.py
import tkinter as tk
from tkinter import messagebox
import pygame
from game_logic import DominoGame, monte_carlo_ai_move

class DominoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Domino - 4 Players (You vs 3 AI)")
        self.game = DominoGame()

        self.player_colors = ['blue', 'red', 'green', 'purple']

        self.board_frame = tk.Frame(root)
        self.board_frame.pack(pady=10)

        self.hand_frame = tk.Frame(root)
        self.hand_frame.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        self.pass_button = tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)

        self.draw_button = tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.info_frame, text="Your turn!")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.ai_labels = [tk.Label(self.info_frame, text=f"AI {i} has 7 tiles") for i in range(1, 4)]
        for label in self.ai_labels:
            label.pack(side=tk.RIGHT, padx=5)

        self.draw_board()
        self.draw_hand()
        if self.game.current_player != 0:
            self.status_label.config(
                text=f"AI {self.game.current_player} starts with (6|6)"
            )
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text="You start with (6|6)!")

    def toggle_music(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_button.config(text="Play Music")
        else:
            pygame.mixer.music.unpause()
            self.music_button.config(text="Mute Music")
        self.music_on = not self.music_on

    def draw_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        for i, tile in enumerate(self.game.board):
            owner = self.game.board_owners[i]
            tile_str = f"[{tile[0]}|{tile[1]}]"
            color = self.player_colors[owner]
            tk.Label(self.board_frame, text=tile_str, font=('Courier', 14), relief='ridge', padx=6, pady=4, fg=color).pack(side=tk.LEFT)

    def draw_hand(self):
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        hand = self.game.players[0]
        valid_moves = self.game.get_valid_moves(hand)
        for tile in hand:
            tile_str = f"[{tile[0]}|{tile[1]}]"
            btn = tk.Button(self.hand_frame, text=tile_str, font=('Courier', 12), relief='raised', fg='blue',
                            state=tk.NORMAL if tile in valid_moves else tk.DISABLED,
                            command=lambda t=tile: self.play_tile(t))
            btn.pack(side=tk.LEFT, padx=4)

    def play_tile(self, tile):
        if self.game.current_player != 0:
            return  # Not your turn
        try:
            self.game.play_tile(0, tile)
            self.game.current_player = (self.game.current_player + 1) % 4
            self.after_move()
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))

    def pass_turn(self):
        self.game.pass_turn()
        self.game.current_player = (self.game.current_player + 1) % 4
        self.after_move()

    def draw_tile(self):
        tile = self.game.draw_from_stock(0)
        if tile:
            self.status_label.config(text=f"You drew {tile}")
        else:
            self.status_label.config(text="Stock is empty")
        self.draw_hand()

    def after_move(self):
        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_counts()

        if self.game.is_game_over():
            self.end_game()
        else:
            self.root.after(500, self.ai_turn)

    def ai_turn(self):
        if self.game.current_player == 0 or self.game.is_game_over():
            if self.game.is_game_over():
                self.end_game()
            else:
                self.status_label.config(text="Your turn!")
                self.draw_hand()
            return

        cp = self.game.current_player
        hand = self.game.players[cp]
        valid_moves = self.game.get_valid_moves(hand)

        while not valid_moves and self.game.stock:
            drawn = self.game.draw_from_stock(cp)  # Se borra pq no se usa???
            valid_moves = self.game.get_valid_moves(self.game.players[cp])

        move = monte_carlo_ai_move(self.game,cp, simulations=25)
        if move:
            self.game.play_tile(cp, move)
            self.status_label.config(text=f"AI {cp} played {move}")
        else:
            self.game.pass_turn()
            self.status_label.config(text=f"AI {cp} passed")

        self.draw_board()
        self.update_ai_tile_counts()
        self.game.current_player = (self.game.current_player + 1) % 4

        self.root.after(1000, self.ai_turn)  # delay between AI turns

    def update_ai_tile_counts(self):
        for i in range(1, 4):
            self.ai_labels[i - 1].config(text=f"AI {i} has {len(self.game.players[i])} tiles")

    def end_game(self):
        winner = self.game.get_winner()

        # Optional: Print all players' remaining points
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]
        score_lines = "\n".join(
            f"Player {i} ({'You' if i == 0 else 'AI'}): {score} points | Tiles: {hand}"
            for i, score, hand in player_scores
        )
        print("Final scores (lower is better):")
        for i, score, hand in player_scores:
            print(f"Player {i}: {score} points")

        if winner == 0:
            msg = "🎉 You win!"
        elif winner == -1:
            msg = "🤝 It's a tie!"
        else:
            msg = f"🤖 AI {winner} wins!"

        msg += "\nFinal Scores:\n" + score_lines

        messagebox.showinfo("Game Over", msg)
        self.root.quit()


# ---------- Launch ----------
if __name__ == "__main__":
    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()