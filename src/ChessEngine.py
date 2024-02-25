class GameState:
    """
    This class is used for storing all the information regarding the current state of the game
    """

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

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move


class Move:
    """
    The class having the information of the piece moved
    """

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
