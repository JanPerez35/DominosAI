# game_logic.py
import random
from collections import deque
import copy

class DominoGame:
    def __init__(self):
        self.tiles = [(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(self.tiles)
        self.players = [self.tiles[i*7:(i+1)*7] for i in range(4)]
        self.stock = self.tiles[28:]
        self.board = deque()
        self.board_owners = deque()
        self.current_player = 0
        self.passes = 0
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

        # Check for a tie (two or more players with the same lowest score)
        lowest_score = player_scores[0][1]
        tied_players = [i for i, score in player_scores if score == lowest_score]

        if len(tied_players) > 1:
            return -1  # Tie
        else:
            return player_scores[0][0]  # Index of the winning player


# --- AI Logic ---

def monte_carlo_ai_move(game: DominoGame, player_index: int, simulations: int = 25):
    hand = game.players[player_index]
    valid_moves = game.get_valid_moves(hand)
    if not valid_moves:
        return None

    move_scores = {}
    for move in valid_moves:
        total_score = 0
        for _ in range(simulations):
            sim_game = copy.deepcopy(game)
            try:
                sim_game.play_tile(player_index, move)
            except:
                continue
            winner = simulate_random_playout(sim_game)
            total_score += 1 if winner == player_index else 0
        move_scores[move] = total_score / simulations

    best_move = max(move_scores, key=move_scores.get)
    return best_move

def simulate_random_playout(sim_game: DominoGame):
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