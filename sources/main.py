import pygame
import time
import random
import math
import tkinter
import numpy as np
import gui
from gui import Button
from board import board, Piece

pygame.init()

"""
Setting up global variables like pygame surfaces etc.
"""
TILE_SIZE = tkinter.Tk().winfo_screenheight() // 9.5
# overlay surfaces
showed_move = pygame.Surface((TILE_SIZE, TILE_SIZE))
showed_move.set_alpha(64)
showed_move.fill((255, 0, 0))
button_surface = pygame.Surface((2 * TILE_SIZE, TILE_SIZE))
button_surface.set_alpha(64)
button_surface.fill((100, 100, 100))
ai_difficulty = 3
big_font = pygame.font.SysFont("arialblack", int(0.4 * TILE_SIZE), bold=False, italic=False)


def check_mate():
    """
    Displays information about being check mated or
    giving check mate to opponent
    then sends user back to menu
    """
    ts = TILE_SIZE
    if not board.searching:
        tw, th = big_font.size("check mate")
        gui.display_text("check mate", big_font, 4 * ts - tw/2, 4 * ts - th/2, (0, 255, 0))
        pygame.display.update()
        time.sleep(3)
        menu()


def stale_mate():
    """
    Displays information about reaching stale mate
    and sends user to menu
    """
    ts = TILE_SIZE
    if not board.searching:
        tw, th = big_font.size("stale mate")
        gui.display_text("stale mate", big_font, 4 * ts - tw/2, 4 * ts - th/2, (0, 0, 255))
        pygame.display.update()
        time.sleep(3)
        menu()


# move order for minimax search
def move_ordering(moves):
    """
    Orders moves for the minimax algorithm based on how likely they are to be good
    Moves where player caútures are very good, moves where his pieces are captured are very bad
    """
    colors = ["white", "black"]
    opponent_color = colors[colors.index(board.to_move) - 1]
    move_scores = {}
    multiplier = 10
    for i in range(len(moves)):
        score = 0
        if board.board[moves[i][1]] != 0:  # first capturing moves
            score = multiplier * board.piece_values[board.board[moves[i][1]].piece_type] \
                    - board.piece_values[board.board[moves[i][0]].piece_type]
        if board.board[moves[i][0]].piece_type == "pawn":  # then moves with pawns
            if moves[i][1] in range(8) or moves[i][1] in range(56, 64):
                score += 900
        else:
            if moves[i][1] in board.pawn_attacks(opponent_color):
                # lesser value of move if getting into attack of enemy pawn
                score -= 350
        move_scores[i] = score
    # sort moves
    for i in range(len(moves)-1):
        for j in range(1, i+1):
            swap_index = j - 1
            if move_scores[swap_index] < move_scores[j]:
                moves[j], moves[swap_index] = moves[swap_index], moves[j]
                move_scores[j], move_scores[swap_index] = move_scores[swap_index], move_scores[j]
    return moves


# continuation of minimax algorithm in case captures are possible
def capture_search(alpha, beta):
    """
    Based on minimax algorithm with alpha beta pruning
    Evaluates board till there are possible capture moves
    Returns the evaluation of board in the position in which it starts
    """
    eval = board.eval_board()
    if not board.all_moves(board.to_move):
        if board.pinned_pieces(board.to_move)[1]:
            return -math.inf
        else:
            return 0
    if eval >= beta:
        return beta
    if eval > alpha:
        alpha = eval
    for mov in board.all_moves(board.to_move):
        if board.board[mov[1]] != 0:
            board.move(mov[0], mov[1])
            eval = -capture_search(-beta, -alpha)
            board.apply_fen(board.states[-1])
            board.states.pop()
            if eval >= beta:
                return beta
            if eval > alpha:
                alpha = eval

    return alpha


def minimax(depth, alpha, beta):
    """
    Recursively calls itself until depth is reached
    At the end of recursion calculates value of board
    and goes back to find out which move in the current
    position is the best
    If the difficulty is set to hard, evaluates based on capture search as well
    """
    board.searching = True
    moves = move_ordering(board.all_moves(board.to_move))
    best_move = None
    if not moves:  # check mate or stale mate
        if board.pinned_pieces(board.to_move)[1]:
            return -math.inf
        else:
            return 0
    if depth == 0:  # max depth, just evaluates
        if ai_difficulty == 3:
            eval = capture_search(alpha, beta)
            return eval
        return board.eval_board()
    for mov in moves:  # searches all possible moves in position, prunes with alpha beta
        board.move(mov[0], mov[1])
        evaluate = -minimax(depth - 1, -beta, -alpha)
        board.pieces = {k: {i: [] for (i, _) in v.items()} for (k, v) in board.pieces.items()}
        board.apply_fen(board.states[-1])
        board.states.pop()
        if evaluate > beta:
            return beta
        if evaluate > alpha:
            alpha = evaluate
            best_move = mov
    if depth == 2:
        return best_move
    return alpha


def ai_play():
    """
    Does moves for the computer
    If the difficulty is chosen to be easy, plays a random move
    If the difficulty is medium or hard, plays based on the minimax algorithm
    """
    if ai_difficulty == 1:
        if not board.all_moves(board.ai_color):
            if board.pinned_pieces(board.to_move)[1]:
                check_mate()
            else:
                stale_mate()
        move0 = random.choice(board.all_moves(board.ai_color))
        board.move(move0[0], move0[1])
        board.searching = False
    elif ai_difficulty == 2 or ai_difficulty == 3:  # sees one full move into the future
        mov = minimax(2, -math.inf, math.inf)
        board.searching = False
        if not mov or type(mov) == int:
            if board.pinned_pieces(board.to_move)[1]:
                check_mate()
            else:
                stale_mate()
        board.move(mov[0], mov[1])


def play():
    """
    Main game loop
    Checks every input from keyboard and mouse and
    selects pieces and squares to move to based on
    position of the clicks
    Makes the computer play if it is its turn
    """
    ts = TILE_SIZE
    board.states = []
    board.apply_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")  # starting board
    board.squares_to_edge_dict = board.squares_to_edge(board)
    while True:
        gui.display_board()
        board.display_pieces()
        if not board.all_moves(board.to_move):
            if board.pinned_pieces(board.to_move):
                check_mate()
            else:
                stale_mate()
        for event in pygame.event.get():  # gets events like clicking or key presses
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_y:
                    try:
                        board.apply_fen(board.states[-2])
                        board.states.pop()
                        board.states.pop()
                    except IndexError:  # if player tried to return a move at the beginning of the game
                        pass
                if event.key == pygame.K_m:
                    menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if board.player_color == "black":
                    tile = int(y // ts * 8 + x // ts)
                else:
                    tile = int((7 - y // ts) * 8 + x // ts)
                if board.chosen != -1:  # moves piece if a piece is chosen and clicked tile in piece's moves
                    if (board.chosen, tile) in board.all_moves(board.player_color) \
                            and board.to_move == board.player_color:
                        board.move(board.chosen, tile)
                    elif board.board[tile] == 0:
                        board.chosen = -1
                    elif board.board[tile].color == board.player_color:
                        board.chosen = tile
                elif board.board[tile] != 0:  # chooses a new piece if none is chosen and one is clicked
                    if board.to_move == board.player_color and board.board[tile].color == board.player_color:
                        board.chosen = tile
                else:  # no piece is chosen if clicked on an empty square
                    board.chosen = -1
        gui.display_board()
        board.display_pieces()
        if board.chosen != -1:  # displays all possible moves for chosen piece
            for i in board.moves(board.chosen):
                if i in board.all_moves(board.player_color):
                    if board.player_color == "black":
                        game_display.blit(showed_move, (i[1] % 8 * ts, i[1] // 8 * ts, ts, ts))
                    else:
                        game_display.blit(showed_move, (i[1] % 8 * ts, (7 - i[1] // 8) * ts, ts, ts))
        pygame.display.update()
        if board.to_move == board.ai_color:  # ai plays
            ai_play()
            board.to_move = board.player_color
        pygame.display.update()


# menu functions ================================
def make_quit():
    """
    Quits the game
    """
    pygame.quit()
    quit()
    return True


def to_white():
    """
    Changes the color of player to white
    and the color of computer to black
    """
    board.player_color = "white"
    board.ai_color = "black"


def to_black():
    """
    Changes the color of player to black
    and the color of computer to white
    """
    board.player_color = "black"
    board.ai_color = "white"


def to_random():
    """
    Chooses player color at random
    assigns computer the other color
    """
    board.player_color = random.choice(["white", "black"])
    if board.player_color == "white":
        board.ai_color = "black"
    else:
        board.ai_color = "white"


def easy():
    """
    Sets ai difficulty to easy
    """
    global ai_difficulty
    ai_difficulty = 1


def medium():
    """
    Sets difficulty to medium
    """
    global ai_difficulty
    ai_difficulty = 2


def hard():
    """
    Sets difficulty to hard
    """
    global ai_difficulty
    ai_difficulty = 3


def menu():
    """
    Creates all menu buttons and calls functions to display them
    Checks events for buttons being pressed
    Triggers buttons functions function on press
    """
    ts = TILE_SIZE
    chosen_x, chosen_y = None, None
    buttons = [Button((0, 0, 0), 3.2 * ts, 0.5 * ts, 2 * ts, ts, "Play", play),
               Button((0, 0, 0), 0.7 * ts, 2.1 * ts, 2 * ts, ts, "White", to_white),
               Button((0, 0, 0), 5.7 * ts, 2.1 * ts, 2 * ts, ts, "Random", to_random),
               Button((0, 0, 0), 3.2 * ts, 2.1 * ts, 2 * ts, ts, "Black", to_black),
               Button((0, 0, 0), 0.7 * ts, 3.8 * ts, 2 * ts, ts, "Easy", easy),
               Button((0, 0, 0), 3.2 * ts, 3.8 * ts, 2 * ts, ts, "Medium", medium),
               Button((0, 0, 0), 5.7 * ts, 3.8 * ts, 2 * ts, ts, "Hard", hard),
               Button((0, 0, 0), 3.2 * ts, 5.3 * ts, 2 * ts, ts, "Help", gui.help_screen),
               Button((0, 0, 0), 3.2 * ts, 6.8 * ts, 2 * ts, ts, "Quit", make_quit)]
    while True:
        game_display.fill((150, 150, 150))  # grey
        for button in buttons:
            button.display()
        if chosen_x:
            game_display.blit(button_surface, (chosen_x, chosen_y))
        gui.display_text("Choose your color", big_font, 2.2 * ts, 1.5 * ts, (0, 0, 0))
        gui.display_text("Choose difficulty", big_font, 2.33 * ts, 3.1 * ts, (0, 0, 0))
        pygame.display.update()
        for event in pygame.event.get():  # checks events
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                    return True
                else:
                    pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for button in buttons:
                    if x in range(int(button.x), int(button.x + button.width + 1))\
                            and y in range(int(button.y), int(button.y + button.height + 1)):
                        chosen_x, chosen_y = button.x, button.y
                        button.func()
            elif event.type == pygame.MOUSEBUTTONUP:
                chosen_x, chosen_y = None, None


if __name__ == "__main__":
    game_display = pygame.display.set_mode((8.4 * TILE_SIZE, 8.4 * TILE_SIZE))
    pygame.display.set_caption("Chess")
    menu()
