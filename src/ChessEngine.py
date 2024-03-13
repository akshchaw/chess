class GameState:
    """
    This class is used for storing all the information regarding the current state of the game
    """
    board: list[list[str]]
    white_to_move: bool
    move_log: list
    move_functions: dict
    white_king_location: tuple[int, int]
    black_king_location: tuple[int, int]
    in_check: bool
    pins: list
    checks: list

    def __init__(self):
        # board is 8X8 2D list, each element has 2 elements
        # first element is the color, 2nd element is the type
        # "--" represents empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []

    def make_move(self, move) -> None:
        """
        Make the piece move on board
        :param move: the Move object with all the details of the move
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # if king is moved, update the king location
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

    def undo_move(self) -> None:
        """
        Undo the last move made
        """
        # check if there is no move to undo
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # if king move is needed to be undone, update the previous location
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)

    def get_valid_moves(self):
        """
        Get all the moves considering checks
        """
        moves: list[Move] = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_in_context = self.white_king_location
        else:
            king_in_context = self.black_king_location
        if self.in_check:
            # if there is only one check, then move the king or put a piece in front of it
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                # to block the check, a piece needs to be moved between the king and the enemy piece
                check_info = self.checks[0]
                check_row = check_info[0]
                check_col = check_info[1]
                # enemy piece causing the check
                piece_check = self.board[check_row][check_col]
                # squares the pieces can move into to block the check
                valid_squares = []
                # if the enemy piece is knight, either knight can be captured or the king needs to be moved,
                # knight cant be blocked
                if piece_check[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        # check_info parameters are the check directions
                        valid_square = (king_in_context[0] + check_info[2] * i, king_in_context[1] + check_info[3] * i)
                        valid_squares.append(valid_square)
                        # remove the checks beyond the piece
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                # get rid of all the moves that aren't king or block the checks
                for move_index in range(len(moves) - 1, -1, -1):
                    if moves[move_index].piece_moved[1] != "K":
                        if not (moves[move_index].end_row, moves[move_index].end_col) in valid_squares:
                            moves.remove(moves[move_index])
            # more than one checks, only option is for king to move
            else:
                self.get_king_moves(king_in_context[0], king_in_context[1], moves)
        # no checks are there, so all moves are fine
        else:
            moves = self.get_all_possible_moves()
        return moves

    def check_for_pins_and_checks(self) -> tuple[bool, list[tuple[int, int, int, int]], list[tuple[int, int, int, int]]]:
        """
        Check if the player is in check, list of pins and list of checks
        """
        # squares where the allied pinned piece is and direction it is pinned from
        pins: list[tuple[int, int, int, int]] = []
        # squares where enemy is applying check
        checks: list[tuple[int, int, int, int]] = []
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for direction_index in range(len(directions)):
            direction = directions[direction_index]
            # reset possible pins
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    # if the piece found is allay piece
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        # first allied piece can be pinned
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        # 2nd allied piece, so no pin or check required in the direction
                        else:
                            break
                    # if the piece found is enemy piece
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        """
                        Possibilities covered in the below conditions:
                        1. orthogonally away from king and piece is rook
                        2. diagonally away from king and piece is a bishop
                        3. diagonally one square away and the piece is pawn
                        4. any direction and the piece is queen
                        5. to prevent one king move on another king, any direction one square away and the piece is king
                        """
                        if (0 <= direction_index <= 3 and piece_type == "R") or (
                                4 <= direction_index <= 7 and piece_type == "B") or (i == 1 and piece_type == "p" and (
                                (enemy_color == "w" and 6 <= direction_index <= 7) or (
                                enemy_color == "b" and 4 <= direction_index <= 5))) or (piece_type == "Q") or (
                                i == 1 and piece_type == "K"):
                            # no piece is blocking so calling check
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            # piece is blocking, so pinning the piece
                            else:
                                break
                        # enemy piece is not applying check so no pins or checks needed
                        else:
                            break
                # if the space found is off the board
                else:
                    break
        # check for knight moves
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for knight_move in knight_moves:
            end_row = start_row + knight_move[0]
            end_col = start_col + knight_move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # if knight is attacking the king
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_col, knight_move[0], knight_move[1]))
        return in_check, pins, checks

    def get_all_possible_moves(self):
        """
        Get all the moves without considering checks
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece_color = self.board[row][col][0]
                if (piece_color == 'w' and self.white_to_move) or (piece_color == 'b' and not self.white_to_move):
                    piece_type = self.board[row][col][1]
                    self.move_functions[piece_type](row, col, moves)
        return moves

    def get_pawn_moves(self, row: int, col: int, moves: list):
        """
        Get all the pawn moves
        :param row: the row at which pawn is located
        :param col: the column at which the pawn is located
        :param moves: the moves of pawn to be added to the list
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.white_to_move:
            # 1 square pawn advance
            if self.board[row - 1][col] == '--':
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    # 2 square row advance
                    if row == 6 and self.board[row - 2][col] == '--':
                        moves.append(Move((row, col), (row - 2, col), self.board))
            # enemy piece to capture on left
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
            # enemy piece to capture on right
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else:
            if self.board[row + 1][col] == '--':
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    # 2 square row advance
                    if row == 1 and self.board[row + 2][col] == '--':
                        moves.append(Move((row, col), (row + 2, col), self.board))
            # enemy piece to capture on left
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
            # enemy piece to capture on right
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))

    def get_rook_moves(self, row: int, col: int, moves: list):
        """
        Get all the rook moves
        :param row: the row at which rook is located
        :param col: the column at which the rook is located
        :param moves: the moves of pawn to be added to the list
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # cannot remove queen from pin on rook moves, only need to remove it for bishop moves
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (0, 1), (1, 0))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                # check if rook moves are on board
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        # if the space is empty, include the space and check for the further spaces in that direction
                        if end_piece == "--":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        # if the space has enemy, include the move and break (can't go beyond it)
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        # if the space has same color, don't allow the move and further moves in the same direction
                        else:
                            break
                # if the space is outside the board
                else:
                    break

    def get_knight_moves(self, row: int, col: int, moves: list):
        """
        Get all the knight moves
        :param row: the row at which knight is located
        :param col: the column at which the knight is located
        :param moves: the moves of pawn to be knight to the list
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            # check if rook moves are on board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    # if the end position has either enemy piece or is empty
                    if end_piece[0] == enemy_color or end_piece[0] == "-":
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row: int, col: int, moves: list):
        """
        Get all the bishop moves
        :param row: the row at which bishop is located
        :param col: the column at which the bishop is located
        :param moves: the moves of pawn to be added to the list
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                # check if rook moves are on board
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        # if the space is empty, include the space and check for the further spaces in that direction
                        if end_piece == "--":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        # if the space has enemy, include the move and break (can't go beyond it)
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        # if the space has same color, don't allow the move and further moves in the same direction
                        else:
                            break
                # if the space is outside the board
                else:
                    break

    def get_queen_moves(self, row: int, col: int, moves: list):
        """
        Get all the queen moves
        :param row: the row at which queen is located
        :param col: the column at which the queen is located
        :param moves: the moves of pawn to be added to the list
        """
        # it is a combination of rook and knight moves
        self.get_knight_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    def get_king_moves(self, row: int, col: int, moves: list):
        """
        Get all the king moves
        :param row: the row at which king is located
        :param col: the column at which the king is located
        :param moves: the moves of pawn to be added to the list
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # if the end_piece is opponent or empty
                if end_piece[0] != ally_color:
                    # place the king on end piece place and check for checks
                    if self.white_to_move:
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # put back the king
                    if self.white_to_move:
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)


class Move:
    """
    The class having the information of the piece moved
    """
    start_row: int
    start_col: int
    end_row: int
    end_col: int
    piece_moved: str
    piece_captured: str
    move_id: int

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square: tuple[int, int], end_square: tuple[int, int], board: list[list[str]]):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other: object) -> bool:
        """
        Overriding the equals method to make a move if it is valid
        :param other: The other object to be compared with
        """
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def chess_notation(self) -> str:
        """
        Get the location of the move made on chess board
        :return: the details of the move made on chess board
        """
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row,
                                                                                       self.end_col)

    def get_rank_file(self, row: int, col: int) -> str:
        """
        Get the chess notation of the square
        :param row: the row number of chess board
        :param col: the column number of chess board
        :return: the string of the location on the chess board
        """
        return self.cols_to_files[col] + self.rows_to_ranks[row]
