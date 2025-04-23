import random
from collections import deque
import tkinter as tk
from tkinter import messagebox
#importing the performance tracker
from PerformanceMeasure import PerformanceTracker
import copy
import pygame
import sys
import argparse


# -------------- Game Logic --------------

class DominoGame:
    def __init__(self,team_mode,layout):
        self.team_mode = team_mode
        self.layout = layout

        # Defines teams based on layout choice
        if layout == "ai_pairs":
            # human 0 + Ai 1 vs human 2 + AI 3
            self.teams = [[0, 1], [2, 3]]
        else:
            # both humans (0,2) vs both AIs (1,3)
            self.teams = [[0, 2], [1, 3]]

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
        """Checks if move to be made is valid by cheeking the ends"""
        return end in tile

    def get_valid_moves(self, hand):
        '''

        :param hand: Hand the player(human or AI) has
        :return: All valid moves that can be made by the player hand at the moment of turn.
        '''
        if not self.board:
            return hand
        left, right = self.board[0][0], self.board[-1][1]
        return [t for t in hand if self.is_valid_move(t, left) or self.is_valid_move(t, right)]

    def draw_from_stock(self, player):
        '''
        Draws from left over pieces if there are any.
        :param player: current player drawing.
        :return: drawn tile that player didn't have.
        '''
        if self.stock:
            drawn_tile = self.stock.pop()
            self.players[player].append(drawn_tile)
            return drawn_tile
        return None

    def play_tile(self, player, tile):
        '''
        Places a tile on the board for current acting player.
        first checks one side then the other if it's valid to put on the board.
        :param player: current player putting on board.
        :param tile: tile being placed on the board.

        '''
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
        '''
        Adds up all the scores for the game.
        If its in teams adds the scores for the teams together, if not individual scores to determine
        second place onwards.

        '''
        if not self.team_mode:
            # Free-for-all winner: lowest pip count
            player_scores = [(i, sum(tile[0] + tile[1] for tile in hand)) for i, hand in enumerate(self.players)]
            player_scores.sort(key=lambda x: x[1])
            lowest_score = player_scores[0][1]
            tied_players = [i for i, score in player_scores if score == lowest_score]
            return -1 if len(tied_players) > 1 else player_scores[0][0]
        else:
            team_scores = []
            for team in self.teams:
                total = sum(tile[0] + tile[1]
                            for player in team
                            for tile in self.players[player])
                team_scores.append(total)

            if team_scores[0] < team_scores[1]:
                return "Team 1"
            elif team_scores[1] < team_scores[0]:
                return "Team 2"
            else:
                return -1  # tie

# -------------- GUI --------------

class DominoGUI:
    def __init__(self, root, team_mode, layout, tracker):
        self.root = root
        self.root.title("Domino - 2 Players vs 2 AI (Pass-and-Play)")
        self.tracker = PerformanceTracker() #tracker added
        # initialize game logic with both flags
        self.game = DominoGame(team_mode, layout)

        # ─── Color mapping ───────────────────────────────────────────────
        if self.game.team_mode:
            # Team mode: two teams → two colors
            palette = ['blue', 'red']
            self.player_colors = [None] * 4
            for team_index, team in enumerate(self.game.teams):
                for player_index in team:
                    self.player_colors[player_index] = palette[team_index]
        else:
            # Free-for-all: four distinct colors
            self.player_colors = ['blue', 'red', 'green', 'purple']
        # ─────────────────────────────────────────────────────────────────

        self.game_over = False

        # Layout (keeping original aesthetic)
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
        #scrolling on the game
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

        # Legend Frame
        self.legend_frame = tk.Frame(root)
        self.legend_frame.pack(pady=5)
        tk.Label(self.legend_frame, text="Legend:").pack(side=tk.LEFT)

        if self.game.team_mode:
            # Team legend with team numbers
            for team_index, team in enumerate(self.game.teams):
                for p in team:
                    name = (
                        "Player 1" if p == 0 else
                        "AI 1" if p == 1 else
                        "Player 2" if p == 2 else
                        "AI 2"
                    )
                    tk.Label(
                        self.legend_frame,
                        text=f"{name} (Team {team_index + 1})",
                        fg=self.player_colors[p],
                        font=("Arial", 10, "bold")
                    ).pack(side=tk.LEFT, padx=5)
        else:
            # Free-for-all legend, no teams
            names = ["Player 1", "AI 1", "Player 2", "AI 2"]
            for i, name in enumerate(names):
                tk.Label(
                    self.legend_frame,
                    text=name,
                    fg=self.player_colors[i],
                    font=("Arial", 10, "bold")
                ).pack(side=tk.LEFT, padx=5)

        # Control Buttons
        self.pass_button = tk.Button(self.controls_frame, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)
        self.draw_button = tk.Button(self.controls_frame, text="Draw Tile", command=self.draw_tile)
        self.draw_button.pack(side=tk.LEFT, padx=5)

        self.music_on = True
        self.music_button = tk.Button(self.controls_frame, text="Mute Music", command=self.toggle_music)
        self.music_button.pack(side=tk.LEFT, padx=5)

        # Status & AI tile‐counts
        self.status_label = tk.Label(self.info_frame, text="Your turn!", font=("Arial", 12))
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.ai_labels = [
            tk.Label(self.info_frame, text=f"AI 1 has {len(self.game.players[1])} tiles", font=("Arial", 10)),
            tk.Label(self.info_frame, text=f"AI 2 has {len(self.game.players[3])} tiles", font=("Arial", 10))
        ]
        for label in self.ai_labels:
            label.pack(side=tk.RIGHT, padx=5)

        # For pass-and-play between human players
        self.last_human = None

        # Initial draw/setup
        self.draw_board()
        self.draw_hand()
        if self.game.current_player not in [0, 2]:
            self.status_label.config(text=f"AI {self.game.current_player} starts with (6|6)")
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text=self.human_status_text())

    def human_status_text(self):
        # Return appropriate status for human: indicate Player 1 or Player 2.
        if self.game.current_player == 0:
            return "Your turn! (Player 1)"
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
        '''
        Draws current state of the board
        '''
        self.board_canvas.delete("all")
        x, y = 500, 150  # Start position for board drawing
        tile_positions = []
        #puts color on the tiles depending on team.
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
        '''
        Draws current state of the hand for the player in turn.
        '''
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
        pass_screen.geometry("600x400+350+200")
        pass_screen.title("Pass Device")
        msg = ""
        if next_player == 0:
            msg = "Pass device to Player 1\n\n(Ensure previous hand is not visible.)"
        elif next_player == 2:
            msg = "Pass device to Player 2\n\n(Ensure previous hand is not visible.)"
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
        '''
        Called after a player makes a move to update the loop logic.
        '''
        self.draw_board()
        self.update_ai_tile_counts()
        if self.game.is_game_over():
            self.end_game()
        else:
            # If next turn is human, check if pass screen is needed.
            if self.game.current_player in [0, 2]:
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
        '''

        :param tile: tile to be played in that turn
        if tile thrown out of turn or not valid will say so.

        '''
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
        if self.game.current_player in [0, 2] or self.game.is_game_over():
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
            #plays the move made by monte_carlo simulation if possible for current AI player
            self.game.play_tile(cp, move)
            self.status_label.config(text=f"AI {1 if cp==1 else 2} played {move}")
        else:
            self.game.pass_turn()
            self.status_label.config(text=f"AI {1 if cp==1 else 2} passed")
        self.draw_board()
        self.update_ai_tile_counts()
        self.game.current_player = (self.game.current_player + 1) % 4
        self.root.after(1000, self.after_move)

    def monte_carlo_ai_move(self, player_index, simulations=30):
        '''
        Makes the simulations for all possible moves.
        :param player_index: current AI player using the simulation
        :param simulations: times to run monte_carlo simulations
        :return: best possible move found.
        '''
        hand = self.game.players[player_index]
        valid_moves = self.game.get_valid_moves(hand)
        if not valid_moves:
            return None

        move_scores = {}
        #makes a simulation for all valid moves.
        for move in valid_moves:
            total_score = 0
            for _ in range(simulations):
                sim_game = copy.deepcopy(self.game)
                try:
                    sim_game.play_tile(player_index, move)
                except:
                    continue
                winner = self.simulate_random_playout(sim_game)
                #if winner in the simulated game is the AI agent move gets a point
                total_score += 1 if winner == player_index else 0
            move_scores[move] = total_score / simulations
        #chooses best move based on currently applicable moves
        best_move = max(move_scores, key=move_scores.get)
        return best_move

    def simulate_random_playout(self, sim_game):
        '''
        Simulates a random outcome for the current game and simulates what the highest score play would be
        :param sim_game: recreation of current game state to be simulated.
        :return: winner of simulated game.
        '''
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
        self.ai_labels[0].config(text=f"AI 1 has {len(self.game.players[1])} tiles")
        self.ai_labels[1].config(text=f"AI 2 has {len(self.game.players[3])} tiles")

    '''
    Starts a new game.
    '''
    def start_new_game(self,teamMode, layout):
        self.game = DominoGame(teamMode, layout)
        self.game_over = False
        self.last_human = None

        # Clear canvas (but keep the widget)
        self.board_canvas.delete("all")

        # Clear player hand
        for widget in self.hand_frame.winfo_children():
            widget.destroy()

        self.draw_board()
        self.draw_hand()
        self.update_ai_tile_counts()

        if self.game.current_player in [0, 2]:
            self.status_label.config(text=f"AI {1 if self.game.current_player == 1 else 2} starts with (6|6)!")
            self.root.after(1000, self.ai_turn)
        else:
            self.status_label.config(text=f"You start with (6|6)!")

    def end_game(self):
        '''
        Print out all winners and scores for the game played.
        After terminate window.
        '''
        winner = self.game.get_winner()
        # Optional: Print all players' remaining points
        
        player_scores = [
            (i, sum(t[0] + t[1] for t in hand), hand)
            for i, hand in enumerate(self.game.players)
        ]
        if self.game.team_mode:
            # Team-based scoring
            team_0_score = sum(score for i, score, _ in player_scores if i in [0, 2])
            team_1_score = sum(score for i, score, _ in player_scores if i in [1, 3])

            team_lines = "\n".join(
                f"Player {i} ({'You' if i in [0, 1, 2] else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )
            msg = "🤝 It's a tie!" if winner == -1 else f"🎉 {winner} wins!"
            msg += f"\n\nTeam 0 & 2 score: {team_0_score}\nTeam 1 & 3 score: {team_1_score}"
            msg += "\n\nFinal Player Scores:\n" + team_lines

            messagebox.showinfo("Game Over", msg)
            #Performance Tracking 
            self.tracker.update_tracker_team_mode(winner, True, team_0_score, team_1_score)
            self.tracker.report()
        else:
            # Free-for-all scoring
            score_lines = "\n".join(
                f"Player {i} ({'You' if i in [0, 2] else 'AI'}): {score} points | Tiles: {hand}"
                for i, score, hand in player_scores
            )

            if winner in [0, 2]:
                msg = "🎉 You win!"
            elif winner == -1:
                msg = "🤝 It's a tie!"
            else:
                msg = f"🤖 AI {1 if winner == 1 else 2} wins!"
            msg += "\nFinal Scores:\n" + score_lines
            messagebox.showinfo("Game Over", msg)

            tracker_scores = [score for i, score, hand in player_scores]
            #Performance Tracking 
            self.tracker.update_tracker_4_player(winner, tracker_scores[0], tracker_scores[1], tracker_scores[2], tracker_scores[3], "2v2")
            self.tracker.report()

        #Play again option
        play_again = messagebox.askyesno(
            title="Play again?",
            message="Would you like to play again?"
        )
        if play_again:
            self.start_new_game(team_mode,layout)
        else:
            self.root.quit()

# -------------- Run the App --------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--team",
        action="store_true",
        help="Enable team mode"
    )
    parser.add_argument(
        "--layout",
        choices=["ai_pairs", "humans_team"],
        default="ai_pairs",
        help=(
            "ai_pairs: each human teams with an AI\n"
            "humans_team: both humans vs both AIs"
        )
    )
    args = parser.parse_args()

    team_mode = args.team
    layout   = args.layout

    pygame.mixer.init()
    pygame.mixer.music.load("BGM.mp3")
    pygame.mixer.music.play(-1)

    tracker = PerformanceTracker() #tracker added   
    root = tk.Tk()
    # pass both flags into your GUI
    app = DominoGUI(root, team_mode, layout, tracker)
    root.mainloop()
    sys.exit()
