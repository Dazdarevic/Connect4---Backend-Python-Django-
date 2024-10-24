# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

ROWS = 6
COLS = 7
AI1 = 1
AI2 = 2
EMPTY = 0

def check_winner(board, player):
    # Horizontal check
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] == player and board[r][c+1] == player and \
               board[r][c+2] == player and board[r][c+3] == player:
                return True

    # Vertical check
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] == player and board[r+1][c] == player and \
               board[r+2][c] == player and board[r+3][c] == player:
                return True

    # Diagonal checks
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] == player and board[r+1][c+1] == player and \
               board[r+2][c+2] == player and board[r+3][c+3] == player:
                return True
            if board[r+3][c] == player and board[r+2][c+1] == player and \
               board[r+1][c+2] == player and board[r][c+3] == player:
                return True

    return False

def get_valid_locations(board):
    return [col for col in range(COLS) if board[0][col] == EMPTY]

def evaluate_window(window, player):
    opponent = AI1 if player == AI2 else AI2
    score = 0

    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def score_position(board, player):
    score = 0
    WINDOW_LENGTH = 4

    # Score center column
    center_array = [board[r][COLS//2] for r in range(ROWS)]
    center_count = center_array.count(player)
    score += center_count * 1

    # Score Horizontal
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, player)

    # Score Vertical
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, player)

    # Score positive sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, player)

    # Score negative sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, player)

    return score

def is_terminal_node(board):
    return check_winner(board, AI1) or check_winner(board, AI2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if check_winner(board, AI2):
                return (None, 1000)
            elif check_winner(board, AI1):
                return (None, -1000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI2))
    
    if maximizing_player:
        value = float('-inf')
        column = valid_locations[0]
        for col in valid_locations:
            temp_board = [row[:] for row in board]
            for r in range(ROWS-1, -1, -1):
                if temp_board[r][col] == EMPTY:
                    temp_board[r][col] = AI2
                    break
            new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = float('inf')
        column = valid_locations[0]
        for col in valid_locations:
            temp_board = [row[:] for row in board]
            for r in range(ROWS-1, -1, -1):
                if temp_board[r][col] == EMPTY:
                    temp_board[r][col] = AI1
                    break
            new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

@csrf_exempt
def get_best_move(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        board = data['board']
        player = data['player']
        is_first_move = data.get('isFirstMove', False)
        depth = data.get('depth', 1)  # Default depth je 0 ako nije prosleđeno

        if is_first_move:
            valid_locations = get_valid_locations(board)
            import random
            best_col = random.choice(valid_locations)
        else:
            valid_locations = get_valid_locations(board)
            best_score = float('-inf') if player == AI2 else float('inf')
            best_col = valid_locations[0]

            for col in valid_locations:
                temp_board = [row[:] for row in board]
                for r in range(ROWS-1, -1, -1):
                    if temp_board[r][col] == EMPTY:
                        temp_board[r][col] = player
                        break
                score = minimax(temp_board, depth, float('-inf'), float('inf'), player == AI2)[1]
                if player == AI2:
                    if score > best_score:
                        best_score = score
                        best_col = col
                else:
                    if score < best_score:
                        best_score = score
                        best_col = col

        return JsonResponse({'bestMove': best_col})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)