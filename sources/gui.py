import pygame
import tkinter
import time

pygame.init()


TILE_SIZE = tkinter.Tk().winfo_screenheight() // 9.5
game_display = pygame.display.set_mode((8.4 * TILE_SIZE, 8.4 * TILE_SIZE))
pygame.display.set_caption("Chess")

big_font = pygame.font.SysFont("arialblack", int(0.4 * TILE_SIZE), bold=False, italic=False)
help_font = pygame.font.SysFont("arialblack", int(0.3 * TILE_SIZE), bold=False, italic=False)


def display_board():  # display rectangles for board
    ts = TILE_SIZE
    for i in range(8):
        for j in range(8):
            if (i+j) % 2 == 0:
                pygame.draw.rect(game_display, (255, 255, 255), (j * ts, i * ts, ts, ts))
            else:
                pygame.draw.rect(game_display, (150, 150, 150), (j * ts, i * ts, ts, ts))


def display_piece(player_color, sprite, tile):
    ts = TILE_SIZE
    sprite = pygame.transform.scale(sprite, (ts, ts))
    if player_color == "black":
        game_display.blit(sprite, (tile % 8 * ts, tile // 8 * ts))
    else:
        game_display.blit(sprite, (tile % 8 * ts, (7 - tile // 8) * ts))


class Button:
    def __init__(self, color, x, y, width, height, text, func):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.func = func

    def display(self):  # displays the button with text in the middle based on x, y, height and width of the button
        pygame.draw.rect(game_display, self.color, (self.x, self.y, self.width, self.height))
        tw, th = big_font.size(self.text)
        display_text(self.text, big_font, self.x + self.width / 2 - tw / 2,
                     self.y + self.height / 2 - th / 2, (255, 255, 255))


def display_text(text, font, x, y, color):  # display text to the screen
    displayed_text = font.render(text, True, color)
    game_display.blit(displayed_text, (x, y))


def help_screen():
    ts = TILE_SIZE
    # displayed text in help
    texts = ["To quit the app press Q or click QUIT in menu.",
             "To return to the menu, press any other key.",
             "In the menu, choose difficulty and your color",
             "by clicking on the buttons.",
             "To move a piece in the game, click on it and",
             "then click on the tile you want it to move to.",
             "To return a move, press Z.",
             "If Z doesn't work, press Y.",
             "The hard difficulty opponent may take",
             "a bit more time to move sometimes, ",
             "so just wait for the response."]
    while True:  # checking for events and displays text
        game_display.fill((150, 150, 150))
        # displays some advice on how to work with the app
        for i, text in enumerate(texts):
            tw, th = help_font.size(text)
            display_text(text, help_font, 4 * ts - tw / 2, 0.5 * ts * (i + 1) - 0.1 * ts - th / 2, (0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                else:
                    return None
        pygame.display.update()
