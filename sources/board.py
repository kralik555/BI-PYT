import numpy as np
import gui
import pygame

pygame.init()


class Piece:
    piece_types = ["king", "queen", "bishop", "rook", "knight", "pawn"]

    def __init__(self, color, tile, piece_type):
        """
        Defines piece class
        Has color, type and tile where it currently is
        """
        self.color = color
        self.tile = tile
        self.piece_type = piece_type


class Board:
    def __init__(self):
        """
        Creates empty board
        Creates tables for where which pieces have higher values
        Dictionary of pieces and their positions
        """
        self.board = [0 for _ in range(64)]
        self.to_move = "white"
        self.chosen = -1
        self.castling = "KQkq"
        self.squares_to_edge_dict = {}
        self.en_passant = None
        self.half_moves = 0
        self.full_moves = 0
        self.player_color = "white"
        self.ai_color = "black"
        self.piece_values = {"pawn": 100, "queen": 900, "rook": 500, "bishop": 300, "knight": 300, "king": 100000}
        self.pieces = {"pawn": {"white": [], "black": []},
                       "bishop": {"white": [], "black": []},
                       "knight": {"white": [], "black": []},
                       "rook": {"white": [], "black": []},
                       "queen": {"white": [], "black": []},
                       "king": {"white": [], "black": []}}
        self.states = []
        self.searching = False
        self.piece_square_tables = {
            "pawn": np.array([0,  0,  0,  0,  0,  0,  0,  0,
                             50, 50, 50, 50, 50, 50, 50, 50,
                             10, 10, 20, 30, 30, 20, 10, 10,
                             5,  5, 10, 25, 25, 10,  5,  5,
                             0,  0,  0, 20, 20,  0,  0,  0,
                             5, -5, -10,  0,  0, -10, -5,  5,
                             5, 10, 10, -32, -31, 10, 10,  5,
                             0,  0,  0,  0,  0,  0,  0,  0]),
            "knight": np.array([-50, -40, -30, -30, -30, -30, -40, -50,
                                -40, -20,  0,  0,  0,  0, -20, -40,
                               -30,  0, 10, 15, 15, 10,  0, -30,
                               -30,  5, 15, 20, 20, 15,  5, -30,
                               -30,  0, 15, 20, 20, 15,  0, -30,
                               -30,  5, 10, 15, 15, 10,  5, -30,
                               -40, -20, 0, 5, 5, 0, -20, -40,
                               -50, -40, -30, -30, -30, -30, -40, -50]),
            "bishop": np.array([-20, -10, -10, -10, -10, -10, -10, -20,
                               -10,  0,  0,  0,  0,  0,  0, -10,
                               -10,  0,  5, 10, 10,  5,  0, -10,
                               -10,  5,  5, 10, 10,  5,  5, -10,
                               -10,  0, 10, 10, 10, 10,  0, -10,
                               -10, 10, 10, 10, 10, 10, 10, -10,
                               -10,  5,  0,  0,  0,  0,  5, -10,
                               -20, -10, -10, -10, -10, -10, -10, -20]),
            "rook": np.array([0,  0,  0,  0,  0,  0,  0,  0,
                             5, 10, 10, 10, 10, 10, 10,  5,
                             -5,  0,  0,  0,  0,  0,  0, -5,
                             -5,  0,  0,  0,  0,  0,  0, -5,
                             -5,  0,  0,  0,  0,  0,  0, -5,
                             -5,  0,  0,  0,  0,  0,  0, -5,
                             -5,  0,  0,  0,  0,  0,  0, -5,
                             0,  0,  0,  5,  5,  0,  0,  0]),
            "queen": np.array([-20, -10, -10, -5, -5, -10, -10, -20,
                              -10,  0,  0,  0,  0,  0,  0, -10,
                              -10,  0,  5,  5,  5,  5,  0, -10,
                              -5,  0,  5,  5,  5,  5,  0, -5,
                              0,  0,  5,  5,  5,  5,  0, -5,
                              -10,  5,  5,  5,  5,  5,  0, -10,
                              -10,  0,  5,  0,  0,  0,  0, -10,
                              -20, -10, -10, -5, -5, -10, -10, -20]),
            "king": np.array([-30, -40, -40, -50, -50, -40, -40, -30,
                             -30, -40, -40, -50, -50, -40, -40, -30,
                             -30, -40, -40, -50, -50, -40, -40, -30,
                             -30, -40, -40, -50, -50, -40, -40, -30,
                             -20, -30, -30, -40, -40, -30, -30, -20,
                             -10, -20, -20, -20, -20, -20, -20, -10,
                             20, 20,  0,  0,  0,  0, 20, 20,
                             20, 30, 10,  0,  0, 10, 30, 20])}

    def display_pieces(self):
        """
        Calls display function for each piece on the board
        """
        for i in self.board:
            if i != 0:
                sprite = pygame.image.load(f"Sprites/{i.color}_{i.piece_type}.png")
                gui.display_piece(self.player_color, sprite, i.tile)

    def moves(self, tile):
        """
        Returns moves that can be done from a tile
        based on what piece type there is on the tile
        """
        if self.board[tile] == 0:
            return []
        if self.board[tile].piece_type in ["bishop", "queen", "rook"]:
            return self.sliding_moves(tile)
        if self.board[tile].piece_type == "king":
            return self.king_moves(tile)
        if self.board[tile].piece_type == "knight":
            return self.knight_moves(tile)
        if self.board[tile].piece_type == "pawn":
            return self.pawn_moves(tile)

    def pawn_moves(self, tile):
        """
        Returns moves of a pawn on a tile
        With capturing and en passant
        """
        moves = []
        if self.board[tile].color == "white":
            if self.board[tile + 8] == 0:
                moves.append((tile, tile + 8))
            if tile // 8 == 1:
                if self.board[tile + 8] == 0 and self.board[tile + 16] == 0:
                    moves.append((tile, tile + 16))
            if self.board[tile + 7] != 0 and tile % 8 != 0:
                if self.board[tile + 7].color != self.board[tile].color:
                    moves.append((tile, tile + 7))
            if tile + 9 in range(64):
                if self.board[tile + 9] != 0 and tile % 8 != 7:
                    if self.board[tile + 9].color != self.board[tile].color:
                        moves.append((tile, tile + 9))
            # en passant
            if self.en_passant == tile + 7 or self.en_passant == tile + 9:
                moves.append((tile, self.en_passant))
        else:  # same things, but for black
            if self.board[tile - 8] == 0:
                moves.append((tile, tile - 8))
            if tile // 8 == 6:
                if self.board[tile - 8] == 0 and self.board[tile - 16] == 0:
                    moves.append((tile, tile - 16))
            if self.board[tile - 7] != 0 and tile % 8 != 7:
                if self.board[tile - 7].color != self.board[tile].color:
                    moves.append((tile, tile - 7))
            if self.board[tile - 9] != 0 and tile % 8 != 0:
                if self.board[tile - 9].color != self.board[tile].color:
                    moves.append((tile, tile - 9))
            if self.en_passant == tile - 7 or self.en_passant == tile - 9:
                moves.append((tile, self.en_passant))
        return moves

    def king_moves(self, tile):
        """
        Returns all moves of king on tile
        Considers illegal moves and removes them from possible moves
        Includes castling
        """
        directions = [9, 1, -7, 8, -8, -9, -1, 7]
        colors = ["white", "black"]
        opponent_color = colors[colors.index(self.board[tile].color) - 1]
        moves = []
        att_sq = self.attacked_squares(opponent_color)
        f = self.get_fen()
        if tile % 8 == 7:  # making sure he can't go out of the board
            directions = directions[3:]
        elif tile % 8 == 0:
            directions = directions[:-3]
        for direction in directions:
            if tile + direction in range(64):  # the 8 tiles around king (less if he is at the edge of the board)
                if self.board[tile + direction] != 0:  # adds tile if friendly piece is not on tile
                    if self.board[tile + direction].color == self.board[tile].color:
                        continue
                    removed = self.board[tile + direction]
                    self.board[tile + direction] = 0
                    rem_king = self.board[tile]
                    self.board[tile] = 0
                    if tile + direction in self.attacked_squares(opponent_color):
                        self.board[tile + direction] = removed
                        self.board[tile] = rem_king
                        continue
                    self.board[tile + direction] = removed
                    self.board[tile] = rem_king
                else:
                    removed = self.board[tile + direction]
                    self.board[tile + direction] = 0
                    rem_king = self.board[tile]
                    self.board[tile] = 0
                    if tile + direction in self.attacked_squares(opponent_color):
                        self.board[tile + direction] = removed
                        self.board[tile] = rem_king
                        continue
                    self.board[tile + direction] = removed
                    self.board[tile] = rem_king
                moves.append((tile, tile + direction))

        if self.board[tile].color == "white" and tile == 4 and tile not in att_sq:
            if "K" in f.split(" ")[2] and self.board[tile + 1] == 0 and self.board[tile + 2] == 0 \
                    and tile + 1 not in att_sq and tile + 2 not in att_sq:
                moves.append((tile, tile + 2))
            if "Q" in f.split(" ")[2] and self.board[tile - 1] == 0 and self.board[tile - 2] == 0 \
                    and self.board[tile - 3] == 0 and tile - 1 not in att_sq \
                    and tile - 2 not in att_sq:
                moves.append((tile, tile - 2))
        if self.board[tile].color == "black" and tile == 60 and tile not in att_sq:
            if "k" in f.split(" ")[2] and self.board[tile + 1] == 0 and self.board[tile + 2] == 0 \
                    and tile + 1 not in att_sq and tile + 2 not in att_sq:
                moves.append((tile, tile + 2))
            if "q" in f.split(" ")[2] and self.board[tile - 1] == 0 and self.board[tile - 2] == 0 \
                    and self.board[tile - 3] == 0 and tile - 1 not in att_sq \
                    and tile - 2 not in att_sq:
                moves.append((tile, tile - 2))
        i = 0
        # looks for captures but excludes them if the tile would be attacked after the capture
        removed = self.board[tile]
        self.board[tile] = 0
        while i < len(moves):
            if moves[i][1] in att_sq:
                moves.pop(i)
            else:
                i += 1
        self.board[tile] = removed
        return moves

    def simple_king_moves(self, color):
        """
        Returns the 8 tiles around king
        Less if king is at the edge
        """
        directions = [9, 1, -7, 8, -8, -9, -1, 7]
        king_tile = self.pieces["king"][color][0]
        moves = []
        if king_tile % 8 == 7:
            for i in directions[3::]:
                if king_tile + i in range(64):
                    moves.append(king_tile + i)
        elif king_tile % 8 == 0:
            for i in directions[:-3:]:
                if king_tile + i in range(0, 64):
                    moves.append(king_tile + i)
        else:
            for i in directions:
                if king_tile + i in range(0, 64):
                    moves.append(king_tile + i)
        return moves

    def apply_fen(self, fen_str):
        """
        Applies real FEN to the board
        Changes its castling options, en passant
        Changes dictionary of pieces
        """
        pieces_symbols = {"k": "king", "q": "queen", "b": "bishop",
                          "n": "knight", "r": "rook", "p": "pawn"}
        board_str = fen_str.split(" ")[0]
        x = 0
        y = 7
        # board
        for i in range(64):
            self.board[i] = 0
        for char in board_str:
            if char == "/":
                x = 0
                y -= 1
            else:
                if char in "12345678":
                    x += eval(char)
                else:
                    if char.islower():
                        color = "black"
                    else:
                        color = "white"
                    character = char.lower()
                    piece = Piece(color, 8 * y + x, pieces_symbols[character])
                    self.board[8 * y + x] = piece
                    x += 1
                    self.pieces[piece.piece_type][color].append(8 * y + x - 1)
        string = fen_str.split(" ")
        if string[1] == "w":
            self.to_move = "white"
        else:
            self.to_move = "black"
        self.castling = string[2]
        letters = "abcdefgh"
        if string[3] == "-":
            self.en_passant = None
        else:
            a = letters.index(string[3][0])
            b = int(string[3][1]) - 1
            self.en_passant = a + b * 8
        self.half_moves = int(string[4])
        self.full_moves = int(string[5])

    def get_fen(self):
        """
        Returns FEN usable on real online chess
        based on position of pieces, en_passant and castling
        """
        piece_dic = ["k", "q", "b", "r", "n", "p"]
        fen_string = ""
        empty_num = 0
        # piece positions
        for i in range(0, 64):
            j = i // 8 * 8 + 7 - (i % 8)
            if i % 8 == 0 and i != 0:
                if empty_num != 0:
                    fen_string += str(empty_num)
                    empty_num = 0
                fen_string += "/"
            elif i == 63 and self.board[j] == 0:  # if tile is empty
                empty_num += 1
                fen_string += str(empty_num)
            if self.board[j] != 0:  # adding letter to string
                if self.board[j].color == "white":
                    letter = piece_dic[self.board[j].piece_types.index(self.board[j].piece_type)].upper()
                else:
                    letter = piece_dic[self.board[j].piece_types.index(self.board[j].piece_type)]
                if empty_num == 0:
                    fen_string += letter
                else:
                    fen_string += str(empty_num)
                    fen_string += letter
                    empty_num = 0
            else:
                empty_num += 1
        # reverses the string
        fen_string = fen_string[::-1]
        if fen_string[0] == "/":
            fen_string = fen_string[::-1]
            fen_string += "8"
            fen_string = fen_string[::-1]
        fen_string += " "
        fen_string += self.to_move[0]
        # castling
        fen_string += " "
        fen_string += self.castling
        # en passants
        fen_string += " "
        if not self.en_passant:
            fen_string += "-"
        else:
            letters = "abcdefgh"
            fen_string += f"{letters[self.en_passant % 8]}{self.en_passant // 8 + 1}"
        # halfmoves
        fen_string += " "
        fen_string += f"{self.half_moves}"
        # full moves
        fen_string += " "
        fen_string += f"{self.full_moves}"

        return fen_string

    def knight_moves(self, tile):
        """
        Returns all moves doable by a knight on tile
        """
        moves = []
        directions = [15, -15, 17, -17, 6, -6, 10, -10]
        col = tile % 8
        row = tile // 8
        if row == 7:
            if 15 in directions:
                directions.remove(15)
            if 17 in directions:
                directions.remove(17)
            if 6 in directions:
                directions.remove(6)
            if 10 in directions:
                directions.remove(10)
        if row == 6:
            if 15 in directions:
                directions.remove(15)
            if 17 in directions:
                directions.remove(17)
        if row == 0:
            if -15 in directions:
                directions.remove(-15)
            if -17 in directions:
                directions.remove(-17)
            if -6 in directions:
                directions.remove(-6)
            if -10 in directions:
                directions.remove(-10)
        if row == 1:
            if -15 in directions:
                directions.remove(-15)
            if -17 in directions:
                directions.remove(-17)
        if col == 7:
            if 17 in directions:
                directions.remove(17)
            if 10 in directions:
                directions.remove(10)
            if -6 in directions:
                directions.remove(-6)
            if -15 in directions:
                directions.remove(-15)
        if col == 6:
            if -6 in directions:
                directions.remove(-6)
            if 10 in directions:
                directions.remove(10)
        if col == 0:
            if 6 in directions:
                directions.remove(6)
            if 15 in directions:
                directions.remove(15)
            if -10 in directions:
                directions.remove(-10)
            if -17 in directions:
                directions.remove(-17)
        if col == 1:
            if 6 in directions:
                directions.remove(6)
            if -10 in directions:
                directions.remove(-10)
        for direction in directions:
            if tile + direction < 64:
                if self.board[tile + direction] != 0:
                    if self.board[tile + direction].color == self.board[tile].color:
                        continue
                moves.append((tile, tile + direction))
        return moves

    def sliding_moves(self, tile):
        """
        Diagonal and vertical and horizontal moves
        Uses different directions based on piece type
        """
        directions = np.array([8, -8, -1, 1, 7, 9, -9, -7])
        start = 0
        end = 8
        if self.board[tile].piece_type == "rook":
            end = 4
        elif self.board[tile].piece_type == "bishop":
            start = 4
        moves = []
        for i in range(start, end):
            for j in range(self.squares_to_edge_dict[tile][i]):  # while on board
                target_square = tile + directions[i] * (j + 1)  # tile in direction
                piece = self.board[target_square]
                if piece != 0:
                    if piece.color == self.board[tile].color:
                        break
                moves.append((tile, target_square))
                piece = self.board[target_square]
                if piece != 0:
                    if piece.color != self.board[tile].color:  # stops if enemy piece is on tile
                        break
        return moves

    @staticmethod
    def squares_to_edge(self):
        """
        Returns dict of distance to edge from each tile
        """
        list_offsets = {}
        for col in range(8):
            for row in range(8):
                num_top = 7 - row
                num_bot = row
                num_right = 7 - col
                num_left = col
                square_index = row * 8 + col
                list_offsets[square_index] = [num_top, num_bot, num_left, num_right, min(num_left, num_top),
                                              min(num_right, num_top), min(num_bot, num_left), min(num_bot, num_right)]
        return list_offsets

    def move(self, start, end):
        """
        Moves a piece
        and changes castling or en passant if needed
        Changes color of player to move
        """
        self.states.append(self.get_fen())
        new_passant = self.en_passant
        self.en_passant = None
        self.half_moves += 1
        if self.board[start].piece_type == "pawn" or self.board[end] != 0:
            self.half_moves = 0
        if not self.searching:
            if self.board[start].piece_type == "king":
                if self.board[start].color == "white":
                    self.castling = self.castling.replace("K", "")
                    self.castling = self.castling.replace("Q", "")
                else:
                    self.castling = self.castling.replace("k", "")
                    self.castling = self.castling.replace("q", "")
            if start == 0 or end == 0:
                self.castling = self.castling.replace("Q", "")
            if start == 7 or end == 7:
                self.castling = self.castling.replace("K", "")
            if start == 63 or end == 63:
                self.castling = self.castling.replace("k", "")
            if start == 56 or end == 56:
                self.castling = self.castling.replace("q", "")
        if self.castling == "":
            self.castling = "-"
        if self.board[start].piece_type == "king" and end == start + 2:
            self.board[end - 1] = Piece(self.board[start].color, end - 1, "rook")
            self.board[end - 1].tile = end - 1
            self.board[end + 1] = 0
        if self.board[start].piece_type == "king" and end == start - 2:
            self.board[end + 1] = Piece(self.board[start].color, end + 1, "rook")
            self.board[end + 1].tile = end + 1
            self.board[end - 2] = 0
        self.board[end] = 0
        self.board[end] = self.board[start]
        self.board[end].tile = end
        if self.board[end].piece_type == "pawn":
            if end == start + 16:
                self.en_passant = end - 8
            if end == start - 16:
                self.en_passant = end + 8
            if new_passant == end and end > start:
                self.board[end - 8] = 0
            if new_passant == end and end < start:
                self.board[end + 8] = 0
        self.board[start] = 0
        self.chosen = -1
        if self.to_move == "white":
            self.to_move = "black"
        else:
            self.to_move = "white"
        if end < 8 or end > 55:
            if self.board[end].piece_type == "pawn":
                self.board[end] = Piece(self.board[end].color, end, "queen")
        if self.to_move == "white":
            self.full_moves += 1
        fen_srt = self.get_fen()
        self.pieces = {k: {i: [] for (i, _) in v.items()} for (k, v) in self.pieces.items()}
        self.apply_fen(fen_srt)

    def pawn_attacks(self, color):
        """
        Returns all tiles under attack of pawns of a color
        """
        attacks = []
        for i in self.pieces["pawn"][color]:
            if color == "white":
                if i % 8 != 0:
                    attacks.append(i + 7)
                if i % 8 != 7:
                    attacks.append(i + 9)
            else:
                if i % 8 != 0:
                    attacks.append(i - 9)
                if i % 8 != 7:
                    attacks.append(i - 7)
        return attacks

    def attacked_squares(self, color):
        """
        Returns all squares that are under attack
        by the color
        """
        attacked_tiles = []
        tiles = []
        for i in ["queen", "rook", "bishop", "knight"]:
            if self.pieces[i][color]:
                for tile in self.pieces[i][color]:
                    attacked_tiles.extend(self.moves(tile))
        p_attacks = self.pawn_attacks(color)
        for i in attacked_tiles:
            tiles.append(i[1])
        tiles.extend(p_attacks)
        tiles.extend(self.simple_king_moves(color))
        return tiles

    @staticmethod
    def get_some_range(self, king_tile, attack_tile):
        """
        Returns list of tiles between two tiles
        if they can be moved from and to each other by sliding piece
        """
        if king_tile > attack_tile:
            if king_tile % 8 == attack_tile % 8:
                return list(range(attack_tile, king_tile, 8))
            if king_tile // 8 == attack_tile // 8:
                return list(range(attack_tile, king_tile))
            if king_tile % 8 - attack_tile % 8 == king_tile // 8 - attack_tile // 8:
                return list(range(attack_tile, king_tile, 9))
            if king_tile % 8 - attack_tile % 8 == -(king_tile // 8 - attack_tile // 8):
                return list(range(attack_tile, king_tile, 7))
        else:
            if king_tile % 8 == attack_tile % 8:
                return list(range(king_tile, attack_tile + 1, 8))[1:]
            if king_tile // 8 == attack_tile // 8:
                return list(range(king_tile + 1, attack_tile + 1))
            if attack_tile % 8 - king_tile % 8 == attack_tile // 8 - king_tile // 8:
                return list(range(king_tile, attack_tile + 1, 9))[1:]
            if attack_tile % 8 - king_tile % 8 == king_tile // 8 - attack_tile // 8:
                return list(range(king_tile, attack_tile + 1, 7))[1:]
        return []

    def pinned_pieces(self, color):
        """
        Finds positions of all pieces of the color that are pinned (first return value)
        and the pieces that are pinning them (third return value)
        Finds how many checks there are (second return value)
        Finds pieces that are causing the checks (fourth return value)
        """
        pinned_tiles = []
        directions = np.array([8, -8, -1, 1, 7, 9, -9, -7])
        colors = ["white", "black"]
        opponent_color = colors[colors.index(color) - 1]
        if not self.pieces["king"][color]:
            return [], 0, [], []
        king_pos = self.pieces["king"][color][0]
        checks = 0
        pinning_tiles = []
        checking_squares = []
        for i in range(8):
            direction = directions[i]
            piece_in_dir = False
            pinned_piece = None
            for j in range(self.squares_to_edge_dict[king_pos][i]):
                square = king_pos + direction * (j + 1)
                if self.board[square] != 0:
                    if self.board[square].color == color:
                        if not piece_in_dir:
                            pinned_piece = square
                            piece_in_dir = True
                        else:
                            break
                    elif (self.board[square].piece_type in ["rook", "queen"] and i < 4) or \
                            (self.board[square].piece_type in ["bishop", "queen"] and i > 3):
                        if piece_in_dir:
                            pinned_tiles.append(pinned_piece)
                            pinning_tiles.append(square)
                        else:
                            checks += 1
                            checking_squares.append(square)
                        if checks >= 2:
                            return pinned_tiles, checks, pinning_tiles, checking_squares
                        break
                    else:
                        break
        for i in self.pieces["knight"][opponent_color]:
            for move in self.moves(i):
                if move[1] == king_pos:
                    checks += 1
                    checking_squares.append(i)
        for i in self.pieces["pawn"][opponent_color]:
            for move in self.moves(i):
                if move[1] == king_pos:
                    checks += 1
                    checking_squares.append(i)
        # returns pieces that are pinned; number of checks; tiles where the pinning pieces are;
        # tiles where are pieces that
        # are attacking the king
        return pinned_tiles, checks, pinning_tiles, checking_squares

    def all_moves(self, color):
        """
        Returns all legal moves of one color
        """
        colors = ["white", "black"]
        opponent_color = colors[colors.index(color) - 1]
        if not self.pieces["king"][color]:
            return []
        king_tile = self.pieces["king"][color][0]
        new_moves = [self.moves(king_tile)][0]
        pinned = self.pinned_pieces(color)
        if pinned[1] >= 2:
            return new_moves
        elif pinned[1] == 1:
            checking = pinned[3][0]
            if checking in self.pieces["knight"][opponent_color] or checking in self.pieces["pawn"][opponent_color]:
                for k in self.pieces.keys():
                    for i in self.pieces[k][color]:
                        if i not in pinned[0]:
                            for move in self.moves(i):
                                if checking == move[1]:
                                    new_moves.append(move)
                return new_moves
            sq_to_rem_check = self.get_some_range(self, king_tile, checking)
            for k in self.pieces.keys():
                for i in self.pieces[k][color]:
                    if i in pinned[0]:
                        pinning = pinned[2][pinned[0].index(i)]
                        if checking in self.get_some_range(self, king_tile, pinning):
                            new_moves.append((i, checking))
                    else:
                        for move in self.moves(i):
                            if move[1] in sq_to_rem_check:
                                new_moves.append(move)
            return new_moves
        else:
            new_moves = []
            for k in self.pieces.keys():
                for i in self.pieces[k][color]:
                    if i in pinned[0]:
                        for move in self.moves(i):
                            if move[1] in self.get_some_range(self, king_tile, pinned[2][pinned[0].index(i)]):
                                new_moves.append(move)
                    else:
                        for move in self.moves(i):
                            new_moves.append(move)
        return new_moves

    def eval_board(self):
        """
        Evaluates board based on piece positions
        the higher the value, the better for white
        negative numbers are good for black
        If game is near the end, calculates a bit differently based on endgame evaluation
        """
        white_eval = 0
        black_eval = 0
        endgame = True
        end_eval = 0
        for k in self.pieces.keys():
            if self.to_move == "white":
                if self.pieces[k]["black"] and k != "king":
                    endgame = False
            else:
                if self.pieces[k]["white"] and k != "king":
                    endgame = False
        if endgame:
            self.piece_square_tables["king"] = \
                np.array([-50, -40, -30, -20, -20, -30, -40, -50,
                          -30, 0, 0, 0, 0, 0, 0, 0,
                          -30, 0, 0, 0, 0, 0, 0, -30,
                          -30, 0, 0, 0, 0, 0, 0, -30,
                          -30, 0, 0, 0, 0, 0, 0, -30,
                          -30, 0, 0, 0, 0, 0, -0, -30,
                          -30, 0, 0, 0, 0, 0, 0, -30,
                          -50, -30, -30, -30, -30, -30, -30, -50])
            end_eval = self.endgame_eval()
        for k in self.pieces.keys():
            white_eval += self.piece_values[k] * len(self.pieces[k]["white"])
            for i in self.pieces[k]["white"]:
                white_eval += self.piece_square_tables[k][-i - 1]
            black_eval += self.piece_values[k] * len(self.pieces[k]["black"])
            for i in self.pieces[k]["black"]:
                black_eval += self.piece_square_tables[k][i // 8 * 8 + 7 - i % 8]
        if self.to_move == "white":
            return white_eval - black_eval + end_eval
        else:
            return black_eval - white_eval + end_eval

    def endgame_eval(self):
        """
        Evaluation in the case of endgame
        points assigned based on relative position of kings
        """
        end_eval = 0
        colors = ["white", "black"]
        color = self.to_move
        opponent_color = colors[colors.index(color) - 1]
        op_king_col = self.pieces["king"][opponent_color][0] % 8
        op_king_row = self.pieces["king"][opponent_color][0] // 8
        op_king_to_c_col = max(3 - op_king_col, op_king_col - 4)
        op_king_to_c_row = max(3 - op_king_row, op_king_row - 4)
        op_dist_to_centre = op_king_to_c_col + op_king_to_c_row
        end_eval += op_dist_to_centre

        fr_king_col, fr_king_row = self.pieces["king"][color][0] % 8, self.pieces["king"][color][0] // 8
        dist_bet_kings_col = abs(fr_king_col - op_king_col)
        dist_bet_kings_row = abs(fr_king_row - op_king_row)
        end_eval += (14 - dist_bet_kings_col - dist_bet_kings_row) * 1000

        return end_eval * 20


board = Board()