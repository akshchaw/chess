class GameState:
    """
    This class is used for storing all the information regarding the current state of the game
    """
    board: list[list[str]]
    white_to_move: bool
    move_log: list

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
        self.white_to_move = True
        self.move_log = []

    def make_move(self, move) -> None:
        """
        Make the piece move on board
        :param move: the Move object with all the details of the move
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

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

    def get_valid_moves(self):
        """
        Get all the moves considering checks
        """
        return self.get_all_possible_moves()

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
                    # if the piece is pawn
                    if piece_type == 'p':
                        self.get_pawn_moves(row, col, moves)
        return moves

    def get_pawn_moves(self, row: int, col: int, moves: list) -> None:
        """
        Get all the pawn moves
        :param row: the row at which pawn is located
        :param col: the column at which the pawn is located
        :param moves: the moves of pawn to be added to the list
        """
        pass


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
