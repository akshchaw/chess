"""
This is the main driver file. It will track the current game state and user inputs
"""

import pygame as p
from src.ChessEngine import GameState, Move

HEIGHT = WIDTH = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
    """
    Initialize the global dictionary of images. This will be called once to avoid rendering lag
    """
    pieces = ["wR", "wN", "wB", "wQ", "wK", "bR", "bN", "bB", "bQ", "bK", "wp", "bp"]
    for piece in pieces:
        IMAGES[piece] = p.image.load(f"src/assets/{piece}.png")


def draw_board(screen: p.Surface | p.SurfaceType):
    """
    Draw the chess board
    :param screen: The display configured for pygame
    """
    colors = [p.Color("white"), p.Color("dark gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color_used = colors[(row + col) % 2]
            p.draw.rect(screen, color_used, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen: p.Surface | p.SurfaceType, gs: GameState):
    """
    Draw the chess pieces using the IMAGES dictionary on the position on board
    :param screen: The display configured for pygame
    :param gs: The game state of the current session
    """
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            if gs.board[row][col] != "--":
                piece = gs.board[row][col]
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_game_state(screen: p.Surface | p.SurfaceType, gs: GameState):
    """
    Draw the board and the pieces of the current game state
    """
    draw_board(screen)
    draw_pieces(screen, gs)


def main():
    """
    The main driver for our code. This will handle user input and updating the graphics
    """
    p.init()
    icon = p.image.load("src/assets/bp.png")
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_icon(icon)
    p.display.set_caption("Chess", "Chess")
    screen.fill(p.Color("white"))
    clock = p.time.Clock()

    gs = GameState()
    load_images()

    square_selected = ()
    player_clicks = []
    running = True

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            # mouse event handlers
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_location = p.mouse.get_pos()
                block_row = mouse_location[1] // SQ_SIZE
                block_col = mouse_location[0] // SQ_SIZE
                # if user previously selected the same square, don't update the information
                if square_selected == (block_row, block_col):
                    square_selected = ()
                    player_clicks = []
                else:
                    square_selected = (block_row, block_col)
                    player_clicks.append(square_selected)
                # if the user clicks the second time, need to make move
                if len(player_clicks) == 2:
                    move = Move(player_clicks[0], player_clicks[1], gs.board)
                    gs.make_move(move)
                    # reset the move information
                    square_selected = ()
                    player_clicks = []
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
