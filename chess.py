import pygame
import sys
import os
##
# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
PIECES = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']
IMAGES = {}

# Colors
WHITE = (255, 255, 255)
BLACK = (64, 64, 64)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_YELLOW = (255, 255, 153)

# Set up the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

def load_images():
    for piece in PIECES:
        IMAGES[piece] = pygame.image.load(os.path.join('images', f'{piece}.png'))

def draw_board(win):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                pygame.draw.rect(win, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(win, board, in_check):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != '--':
                win.blit(IMAGES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))
            if in_check.get('w') and piece == 'wk':
                pygame.draw.rect(win, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
            elif in_check.get('b') and piece == 'bk':
                pygame.draw.rect(win, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def get_square_under_mouse(board):
    mouse_pos = pygame.mouse.get_pos()
    col = mouse_pos[0] // SQUARE_SIZE
    row = mouse_pos[1] // SQUARE_SIZE
    if 0 <= col < COLS and 0 <= row < ROWS:
        return board[row][col], row, col
    return None, None, None

def get_pawn_moves(piece, row, col, board):
    moves = []
    direction = -1 if piece[0] == 'w' else 1
    start_row = 6 if piece[0] == 'w' else 1
    if board[row + direction][col] == '--':
        moves.append((row + direction, col))
        if row == start_row and board[row + 2 * direction][col] == '--':
            moves.append((row + 2 * direction, col))
    if col - 1 >= 0 and board[row + direction][col - 1][0] != piece[0] and board[row + direction][col - 1] != '--':
        moves.append((row + direction, col - 1))
    if col + 1 < COLS and board[row + direction][col + 1][0] != piece[0] and board[row + direction][col + 1] != '--':
        moves.append((row + direction, col + 1))
    return moves

def get_rook_moves(row, col, board, color):
    moves = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for direction in directions:
        for i in range(1, 8):
            r = row + direction[0] * i
            c = col + direction[1] * i
            if 0 <= r < ROWS and 0 <= c < COLS:
                if board[r][c] == '--':
                    moves.append((r, c))
                elif board[r][c][0] != color:
                    moves.append((r, c))
                    break
                else:
                    break
            else:
                break
    return moves

def get_knight_moves(row, col, board, color):
    moves = []
    directions = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for direction in directions:
        r = row + direction[0]
        c = col + direction[1]
        if 0 <= r < ROWS and 0 <= c < COLS:
            if board[r][c] == '--' or board[r][c][0] != color:
                moves.append((r, c))
    return moves

def get_bishop_moves(row, col, board, color):
    moves = []
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for direction in directions:
        for i in range(1, 8):
            r = row + direction[0] * i
            c = col + direction[1] * i
            if 0 <= r < ROWS and 0 <= c < COLS:
                if board[r][c] == '--':
                    moves.append((r, c))
                elif board[r][c][0] != color:
                    moves.append((r, c))
                    break
                else:
                    break
            else:
                break
    return moves

def get_queen_moves(row, col, board, color):
    return get_rook_moves(row, col, board, color) + get_bishop_moves(row, col, board, color)

def get_king_moves(row, col, board, color):
    moves = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for direction in directions:
        r = row + direction[0]
        c = col + direction[1]
        if 0 <= r < ROWS and 0 <= c < COLS:
            if board[r][c] == '--' or board[r][c][0] != color:
                moves.append((r, c))
    return moves

def get_valid_moves(piece, row, col, board, check_king=True):
    moves = []
    color = piece[0]
    if piece[1] == 'p':  # Pawn
        moves.extend(get_pawn_moves(piece, row, col, board))
    elif piece[1] == 'r':  # Rook
        moves.extend(get_rook_moves(row, col, board, color))
    elif piece[1] == 'n':  # Knight
        moves.extend(get_knight_moves(row, col, board, color))
    elif piece[1] == 'b':  # Bishop
        moves.extend(get_bishop_moves(row, col, board, color))
    elif piece[1] == 'q':  # Queen
        moves.extend(get_queen_moves(row, col, board, color))
    elif piece[1] == 'k':  # King
        moves.extend(get_king_moves(row, col, board, color))

    if check_king:
        # Filter out moves that put the king in check
        valid_moves = []
        for move in moves:
            new_board = [r[:] for r in board]
            new_board[move[0]][move[1]] = new_board[row][col]
            new_board[row][col] = '--'
            if not is_in_check(new_board, color):
                valid_moves.append(move)
        return valid_moves
    return moves

def is_in_check(board, color):
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == color + 'k':
                king_pos = (row, col)
                break
        if king_pos:
            break
    if not king_pos:
        return False

    opponent_color = 'b' if color == 'w' else 'w'
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col][0] == opponent_color:
                piece = board[row][col]
                moves = get_valid_moves(piece, row, col, board, check_king=False)
                if king_pos in moves:
                    return True
    return False

def has_legal_moves(board, color):
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col][0] == color:
                moves = get_valid_moves(board[row][col], row, col, board)
                for move in moves:
                    new_board = [r[:] for r in board]
                    new_board[move[0]][move[1]] = new_board[row][col]
                    new_board[row][col] = '--'
                    if not is_in_check(new_board, color):
                        return True
    return False

def draw_popup(win, text):
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    popup_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(win, LIGHT_YELLOW, popup_rect)
    win.blit(text_surface, text_rect)

def reset_game(board):
    return [
        ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
        ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['--', '--', '--', '--', '--', '--', '--', '--'],
        ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
    ]

def main():
    clock = pygame.time.Clock()
    load_images()
    run = True

    # Initial board setup
    board = reset_game(None)

    selected_piece = None
    selected_row = None
    selected_col = None
    valid_moves = []
    turn = 'w'
    in_check = {'w': False, 'b': False}
    game_over = False

    while run:
        clock.tick(60)  # 60 frames per second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                piece, row, col = get_square_under_mouse(board)
                if selected_piece:
                    if (row, col) in valid_moves:
                        board[selected_row][selected_col] = '--'
                        board[row][col] = selected_piece
                        in_check[turn] = is_in_check(board, turn)
                        opponent_color = 'b' if turn == 'w' else 'w'
                        if is_in_check(board, opponent_color):
                            in_check[opponent_color] = True
                        else:
                            in_check[opponent_color] = False
                        if is_in_check(board, opponent_color) and not has_legal_moves(board, opponent_color):
                            game_over = True
                            while game_over:
                                draw_board(WIN)
                                draw_pieces(WIN, board, in_check)
                                draw_popup(WIN, f"Checkmate! {turn.upper()} wins. Press 'R' to reset.")
                                pygame.display.flip()
                                for event in pygame.event.get():
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_r:
                                            board = reset_game(board)
                                            selected_piece = None
                                            selected_row = None
                                            selected_col = None
                                            valid_moves = []
                                            turn = 'w'
                                            in_check = {'w': False, 'b': False}
                                            game_over = False
                                            break
                                    elif event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                        elif not is_in_check(board, opponent_color) and not has_legal_moves(board, opponent_color):
                            game_over = True
                            while game_over:
                                draw_board(WIN)
                                draw_pieces(WIN, board, in_check)
                                draw_popup(WIN, "Stalemate! Press 'R' to reset.")
                                pygame.display.flip()
                                for event in pygame.event.get():
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_r:
                                            board = reset_game(board)
                                            selected_piece = None
                                            selected_row = None
                                            selected_col = None
                                            valid_moves = []
                                            turn = 'w'
                                            in_check = {'w': False, 'b': False}
                                            game_over = False
                                            break
                                    elif event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                        turn = 'b' if turn == 'w' else 'w'
                    selected_piece = None
                    valid_moves = []
                else:
                    if piece != '--' and piece[0] == turn:
                        selected_piece = piece
                        selected_row = row
                        selected_col = col
                        valid_moves = get_valid_moves(piece, row, col, board)

        draw_board(WIN)
        draw_pieces(WIN, board, in_check)

        if selected_piece:
            pygame.draw.rect(WIN, GREEN, (selected_col * SQUARE_SIZE, selected_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
            for move in valid_moves:
                pygame.draw.circle(WIN, BLUE, (move[1] * SQUARE_SIZE + SQUARE_SIZE // 2, move[0] * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 4)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()