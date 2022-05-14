from board import Board
import main
import pytest


# test simple usage of fen and then getting current fen representation of board
def test_fen_first():
    board = Board()
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    assert(board.pieces == {'pawn': {'white': [8, 9, 10, 11, 12, 13, 14, 15],
                                     'black': [48, 49, 50, 51, 52, 53, 54, 55]},
                            'bishop': {'white': [2, 5], 'black': [58, 61]},
                            'knight': {'white': [1, 6], 'black': [57, 62]},
                            'rook': {'white': [0, 7], 'black': [56, 63]},
                            'queen': {'white': [3], 'black': [59]},
                            'king': {'white': [4], 'black': [60]}})
    assert(board.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")


def test_fen_second():
    board = Board()
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.board[2] = 0
    board.board[58] = 0  # removed a bishop from each color
    assert (board.get_fen() == "rn1qkbnr/pppppppp/8/8/8/8/PPPPPPPP/RN1QKBNR w KQkq - 0 1")


# test moving ========================================================
# basic move
def test_move_one():
    # basic move test
    board = Board()
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.move(6, 21)
    board.move(62, 45)
    assert(board.get_fen() == "rnbqkb1r/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 2 2")


# en passant
def test_move_two():
    # tests en passant
    board = Board()
    board.apply_fen("rnbqkbnr/pppppppp/8/6P1/8/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1")
    board.move(1, 18)
    assert(board.get_fen() == "rnbqkbnr/pppppppp/8/6P1/8/2N5/PPPPP1PP/R1BQKBNR b KQkq - 1 1")
    assert(board.en_passant is None)
    board.move(55, 39)
    assert(board.get_fen() == "rnbqkbnr/ppppppp1/8/6Pp/8/2N5/PPPPP1PP/R1BQKBNR w KQkq h6 0 2")
    assert(board.en_passant == 47)
    board.move(38, 47)
    assert(board.get_fen() == "rnbqkbnr/ppppppp1/7P/8/8/2N5/PPPPP1PP/R1BQKBNR b KQkq - 0 2")


# castling on both sides
def test_move_three():
    # tests castling
    board = Board()
    board.apply_fen("r3kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 4")
    board.move(4, 6)
    assert (board.get_fen() == "r3kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1RK1 b kq - 1 4")
    board.move(60, 58)
    assert(board.get_fen() == "2kr1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1RK1 w - - 2 5")


# change pawn to queen, remove castle options on king side
def test_move_four():
    board = Board()
    board.apply_fen("rnbqkbnr/6P1/8/8/8/8/6p1/RNBQKBNR w KQkq - 0 6")
    board.move(54, 63)
    board.move(14, 7)
    assert(board.get_fen() == "rnbqkbnQ/8/8/8/8/8/8/RNBQKBNq w Qq - 0 7")


# test finding moves from position ==================================
# basic moves, no capturing
def test_moves_one():
    board = Board()
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.squares_to_edge_dict = board.squares_to_edge(board)
    assert(board.moves(3) == board.moves(63) == [])
    assert(board.moves(1) == [(1, 16), (1, 18)])


# en passant in moves
def test_moves_two():
    board = Board()
    board.apply_fen("rnbqkbnr/ppppppp1/8/6Pp/8/2N5/PPPPP1PP/R1BQKBNR w KQkq h6 0 2")
    board.squares_to_edge_dict = board.squares_to_edge(board)
    assert(board.board[47] == 0)
    assert((38, 47) in board.moves(38))


# castling, also check if rook taken or rook moves
def test_moves_three():
    board = Board()
    board.apply_fen("r3k2r/p1pq1ppp/1pnp1n2/1N2p1B1/2BbP1b1/1P1P1N2/P1PQ1PPP/R3K2R w KQkq - 4 10")
    board.squares_to_edge_dict = board.squares_to_edge(board)
    assert((4, 6) in board.moves(4))
    assert((4, 2) in board.moves(4))
    board.move(7, 6)
    assert((60, 62) in board.moves(60))
    assert((60, 58) in board.moves(60))
    board.move(27, 0)
    assert((4, 2) not in board.moves(4))
    assert((4, 6) not in board.moves(4))


# queen moves and pawn capture
def test_moves_four():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("rnb1kbnr/ppp1pppp/3q4/3p4/4P1Q1/8/PPPP1PPP/RNB1KBNR w KQkq - 2 3")
    assert(len(board.moves(30)) == 15)
    assert(len(board.moves(43)) == 16)
    assert((28, 36) in board.moves(28) and (28, 35) in board.moves(28))


# pawn double move
def test_moves_five():
    board = Board()
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.squares_to_edge_dict = board.squares_to_edge(board)
    assert((8, 16), (8, 17) in board.moves(8))
    assert((51, 43), (51, 35) in board.moves(51))


# test getting checked and pinned ===================================
def test_pin_one():
    board = Board()
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.squares_to_edge_dict = board.squares_to_edge(board)
    assert(board.pinned_pieces("white") == [], 0, [], [])


def test_pin_two():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("rnb1kbnr/ppp1pppp/3q4/1B1p4/4P1Q1/8/PPPP1PPP/RNB1K1NR b KQkq - 2 3")
    assert(board.pinned_pieces("black")[1] == 1)
    assert (board.pinned_pieces("black")[3] == [33])
    board.move(50, 42)
    assert(board.pinned_pieces("black") == [42], 0, [33], [])


def test_pin_three():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("rnb1kbnr/ppp1p1pp/3q4/1B1p3Q/4P3/8/PPPP1PPP/RNB1K1NR b KQkq - 2 3")
    assert(board.pinned_pieces("black")[1] == 2)
    assert(board.pinned_pieces("black")[3] == [33, 39])


def test_pin_four():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("rnb1k3/ppp1p1pp/4r3/3P1n2/1qB4b/8/PPPP1QPP/RNB1K1NR w KQq - 2 3")
    assert(board.pinned_pieces("white") == [10, 12], 1, [25, 31], [44])


def test_pin_five():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("rnb1k3/ppp1p1pp/4r3/3P4/1qB4b/3n4/PPPP1QPP/RNB1K1NR w KQq - 2 3")
    assert (board.pinned_pieces("white") == [10, 12], 2, [25, 31], [19, 44])


def test_pin_six():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("rnb1k3/ppp1p2p/4r3/3P4/1qB4b/3n4/PPPp1QPP/RNB1K1NR w KQq - 2 3")
    assert (board.pinned_pieces("white") == [12], 3, [31], [11, 19, 44])


# test finding all moves =============================================
def test_all_moves_one():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    assert(len(board.all_moves("white")) == 20)


# check mate
def test_all_moves_two():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("7k/5K2/8/8/8/6Q1/8/8 b - - 2 18")
    assert(board.all_moves("black") == [(63, 55)])
    board.move(63, 55)
    board.move(22, 23)
    assert(not board.all_moves("black"))


def test_all_moves_three():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("6Rk/8/4Q3/8/2K5/8/8/8 b - - 2 3")
    assert((63, 62) not in board.all_moves("black"))


def test_all_moves_four():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("8/5k2/8/1R1Q4/2K5/8/8/8 b - - 2 3")
    assert(board.all_moves("black"))
    assert((53, 62) not in board.all_moves("black"))
    assert((53, 44) not in board.all_moves("black"))
    assert((53, 52) in board.all_moves("black"))


def test_all_moves_five():
    board = Board()
    board.squares_to_edge_dict = board.squares_to_edge(board)
    board.apply_fen("6k1/1R6/4b3/8/8/1Q6/2K5/8 b - - 2 15")
    assert((44, 53) in board.all_moves("black"))
    assert((44, 51) not in board.all_moves("black"))
    assert((44, 17) in board.all_moves("black"))
    assert((62, 61) in board.all_moves("black"))
    assert((62, 54) not in board.all_moves("black"))


if __name__ == "__main__":
    pass
