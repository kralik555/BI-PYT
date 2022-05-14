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

TILE_SIZE = tkinter.Tk().winfo_screenheight() // 9.5
game_display = pygame.display.set_mode((8.4 * TILE_SIZE, 8.4 * TILE_SIZE))
pygame.display.set_caption("Chess")
player_color = "black"
ai_color = "white"
# overlay surfaces
showed_move = pygame.Surface((TILE_SIZE, TILE_SIZE))
showed_move.set_alpha(64)
showed_move.fill((255, 0, 0))
button_surface = pygame.Surface((2 * TILE_SIZE, TILE_SIZE))
button_surface.set_alpha(64)
button_surface.fill((100, 100, 100))
ai_difficulty = 3
piece_values = {"pawn": 100, "queen": 900, "rook": 500, "bishop": 300, "knight": 300, "king": 100000}
big_font = pygame.font.SysFont("arialblack", int(0.4 * TILE_SIZE), bold=False, italic=False)


def check_mate():  # display "check mate" and returns to menu after 3 seconds
    ts = TILE_SIZE
    if not board.searching:
        tw, th = big_font.size("check mate")
        gui.display_text("check mate", big_font, 4 * ts - tw/2, 4 * ts - th/2, (0, 255, 0))
        pygame.display.update()
        time.sleep(3)
        menu()


def stale_mate():  # displays "stale mate" and returns to menu
    ts = TILE_SIZE
    if not board.searching:
        tw, th = big_font.size("stale mate")
        gui.display_text("stale mate", big_font, 4 * ts - tw/2, 4 * ts - th/2, (0, 0, 255))
        pygame.display.update()
        time.sleep(3)
        menu()


def ai_play():  # how ai plays based on set difficulty
    if not board.all_moves(ai_color):
        if board.pinned_pieces(board.to_move)[1]:
            check_mate()
        else:
            stale_mate()
    move0 = random.choice(board.all_moves(ai_color))
    board.move(move0[0], move0[1])
    board.searching = False


def play():  # main game loop
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
                if player_color == "black":
                    tile = int(y // ts * 8 + x // ts)
                else:
                    tile = int((7 - y // ts) * 8 + x // ts)
                if board.chosen != -1:  # moves piece if a piece is chosen and clicked tile in piece's moves
                    if (board.chosen, tile) in board.all_moves(player_color) and board.to_move == player_color:
                        board.move(board.chosen, tile)
                    elif board.board[tile] == 0:
                        board.chosen = -1
                    elif board.board[tile].color == player_color:
                        board.chosen = tile
                elif board.board[tile] != 0:  # chooses a new piece if none is chosen and one is clicked
                    if board.to_move == player_color and board.board[tile].color == player_color:
                        board.chosen = tile
                else:  # no piece is chosen if clicked on an empty square
                    board.chosen = -1
        gui.display_board()
        board.display_pieces()
        if board.chosen != -1:  # displays all possible moves for chosen piece
            for i in board.moves(board.chosen):
                if i in board.all_moves(player_color):
                    if player_color == "black":
                        game_display.blit(showed_move, (i[1] % 8 * ts, i[1] // 8 * ts, ts, ts))
                    else:
                        game_display.blit(showed_move, (i[1] % 8 * ts, (7 - i[1] // 8) * ts, ts, ts))
        pygame.display.update()
        if board.to_move == ai_color:  # ai plays
            ai_play()
            board.to_move = player_color
        pygame.display.update()


# code for menu here
def make_quit():  # quit the app
    pygame.quit()
    quit()
    return True


# changing color of player
def to_white():  # swaps player color to white
    global player_color
    global ai_color
    board.player_color = "white"
    board.ai_color = "black"
    player_color = "white"
    ai_color = "black"


def to_black():  # swaps player color to black
    global player_color
    global ai_color
    board.player_color = "black"
    board.ai_color = "white"
    player_color = "black"
    ai_color = "white"


def to_random():  # randomly chooses player color
    global player_color
    global ai_color
    player_color = random.choice(["white", "black"])
    if player_color == "white":
        board.player_color = "white"
        board.ai_color = "black"
        ai_color = "black"
    else:
        board.player_color = "black"
        board.ai_color = "white"
        ai_color = "white"


# sets the ai difficulty
def easy():
    global ai_difficulty
    ai_difficulty = 1


def medium():
    global ai_difficulty
    ai_difficulty = 2


def hard():
    global ai_difficulty
    ai_difficulty = 3


def menu():  # displays menu
    ts = TILE_SIZE
    # all the buttons in menu
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
    while True:  # checking for events and displaying buttons
        game_display.fill((150, 150, 150))  # grey
        for button in buttons:
            button.display()
        if chosen_x:  # to see which button has been clicked
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


menu()