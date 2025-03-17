class ChessPiece:
    SYMBOLS = {'P': 'P', 'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K'}

    def __init__(self, color, piece_type):
        self.color = color  # 'white' or 'black'
        self.piece_type = piece_type  # 'P', 'R', 'N', 'B', 'Q', 'K'
        self.symbol = self.SYMBOLS[piece_type] if color == 'white' else self.SYMBOLS[piece_type].lower()

    def is_valid_move(self, board, start, end):
        raise NotImplementedError("This method should be implemented in subclasses")

    def __str__(self):
        return self.symbol


class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'P')

    def is_valid_move(self, board, start, end):
        sx, sy = start
        ex, ey = end
        direction = -1 if self.color == 'white' else 1

        if sy == ey and ((ex == sx + direction and not board[ex][ey]) or
                         (ex == sx + 2 * direction and sx in (1, 6) and not board[ex][ey] and not board[sx + direction][ey])):
            return True

        if abs(sy - ey) == 1 and ex == sx + direction and board[ex][ey] and board[ex][ey].color != self.color:
            return True

        return False


class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'R')

    def is_valid_move(self, board, start, end):
        sx, sy = start
        ex, ey = end

        if sx == ex or sy == ey:
            step_x = 0 if sx == ex else (1 if ex > sx else -1)
            step_y = 0 if sy == ey else (1 if ey > sy else -1)

            x, y = sx + step_x, sy + step_y
            while (x, y) != (ex, ey):
                if board[x][y]:
                    return False
                x += step_x
                y += step_y

            return not board[ex][ey] or board[ex][ey].color != self.color

        return False


class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'N')

    def is_valid_move(self, board, start, end):
        sx, sy = start
        ex, ey = end
        return (abs(sx - ex), abs(sy - ey)) in [(2, 1), (1, 2)] and (not board[ex][ey] or board[ex][ey].color != self.color)


class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'B')

    def is_valid_move(self, board, start, end):
        sx, sy = start
        ex, ey = end

        if abs(sx - ex) == abs(sy - ey):
            step_x = 1 if ex > sx else -1
            step_y = 1 if ey > sy else -1

            x, y = sx + step_x, sy + step_y
            while (x, y) != (ex, ey):
                if board[x][y]:
                    return False
                x += step_x
                y += step_y

            return not board[ex][ey] or board[ex][ey].color != self.color

        return False


class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'Q')

    def is_valid_move(self, board, start, end):
        return Rook(self.color).is_valid_move(board, start, end) or Bishop(self.color).is_valid_move(board, start, end)


class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'K')

    def is_valid_move(self, board, start, end):
        sx, sy = start
        ex, ey = end
        return max(abs(sx - ex), abs(sy - ey)) == 1 and (not board[ex][ey] or board[ex][ey].color != self.color)


class ChessBoard:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.setup_pieces()
        self.move_count = 0

    def setup_pieces(self):
        for _ in range(8):
            self.board[1][_] = Pawn('black')
            self.board[6][_] = Pawn('white')

        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for _, piece in enumerate(pieces):
            self.board[0][_] = piece('black')
            self.board[7][_] = piece('white')

    def display(self):
        print("  a b c d e f g h")
        print(" +----------------")
        for i in range(8):
            print(f"{8-i}|", end=" ")
            for j in range(8):
                print(self.board[i][j] or ".", end=" ")
            print()

    def move(self, start, end, color):
        sx, sy = start
        ex, ey = end
        piece = self.board[sx][sy]

        if piece and piece.color == color and piece.is_valid_move(self.board, start, end):
            self.board[ex][ey] = piece
            self.board[sx][sy] = None
            self.move_count += 1
            return True
        return False


class ChessGame:
    def __init__(self):
        self.board = ChessBoard()
        self.current_player = 'white'

    def parse_input(self, move):
        try:
            return 8 - int(move[1]), ord(move[0]) - ord('a')
        except:
            return None

    def play(self):
        while True:
            self.board.display()
            print(f"Ход {self.current_player} ({self.board.move_count}): ")
            move = input("Введите ход (например, e2 e4): ").strip().split()
            if len(move) != 2:
                print("Неверный ввод!")
                continue

            start, end = self.parse_input(move[0]), self.parse_input(move[1])
            if start and end and self.board.move(start, end, self.current_player):
                self.current_player = 'black' if self.current_player == 'white' else 'white'
            else:
                print("Недопустимый ход!")


if __name__ == "__main__":
    game = ChessGame()
    game.play()
