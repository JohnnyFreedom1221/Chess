import os
from abc import ABC, abstractmethod


class ChessPiece(ABC):
    """Класс шахматных фигур.

    Attributes:
        color (str): Цвет фигуры ('white' или 'black').
        location (str): Текущая позиция на доске (например, 'e2').
        symbol (str): Символ для отображения на доске.
        replacement (str): Какую фигуру заменяет (для новых фигур, по умолчанию None).
    """
    def __init__(self, color, location):
        """Инициализация фигуры.

        Args:
            color (str): Цвет фигуры ('white' или 'black').
            location (str): Начальная позиция (например, 'e2').
        """
        self.color = color
        self.location = location
        self.symbol = ''
        self.replacement = None

    @abstractmethod
    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для фигуры.

        Args:
            board (ChessBoard): Текущая доска.

        Returns:
            list: Список возможных ходов в формате ['a1', 'b2', ...].
        """
        pass

    def move(self, new_location, board):
        """Перемещает фигуру на новую позицию, если ход допустим.

        Args:
            new_location (str): Целевая позиция.
            board (ChessBoard): Текущая доска.

        Returns:
            bool: True, если ход успешен, иначе False.
        """
        if new_location in self.get_possible_moves(board):
            board.make_move(self.location + '-' + new_location)
            return True
        return False


# Класс пешек (будь он не ладен)
class Pawn(ChessPiece):
    """Класс для пешки."""
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'P' if color == 'white' else 'p'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для пешки."""
        moves = []
        row, col = board.pos_to_indices(self.position)
        direction = 1 if self.color == 'white' else -1
        start_row = 1 if self.color == 'white' else 6

        # Здесь реализован обыкновыенный ход вперёд
        new_row = row + direction
        if 0 <= new_row < 8 and board.board[new_row][col] is None:
            moves.append(board.indices_to_pos(new_row, col))
            if row == start_row and board.board[new_row + direction][col] is None:
                moves.append(board.indices_to_pos(new_row + direction, col))

        # Здесь представлено взятие по диагонали
        for dc in [-1, 1]:
            if 0 <= col + dc < 8 and 0 <= new_row < 8:
                target = board.board[new_row][col + dc]
                if target and target.color != self.color:
                    moves.append(board.indices_to_pos(new_row, col + dc))

        # Пресловутое взятие на проходе.
        if self.color == 'white' and self.position[1] == '5':
            for dc in [-1, 1]:
                col_adj = col + dc
                if 0 <= col_adj < 8:
                    adjacent_piece = board.board[row][col_adj]
                    if adjacent_piece and adjacent_piece.color == 'black' and isinstance(adjacent_piece, Pawn):
                        last_move = board.move_history[-1] if board.move_history else None
                        if last_move and last_move.piece == adjacent_piece and last_move.start_pos[1] == '7' and last_move.end_pos[1] == '5':
                            moves.append(board.indices_to_pos(row + 1, col_adj))
        elif self.color == 'black' and self.position[1] == '4':
            for dc in [-1, 1]:
                col_adj = col + dc
                if 0 <= col_adj < 8:
                    adjacent_piece = board.board[row][col_adj]
                    if adjacent_piece and adjacent_piece.color == 'white' and isinstance(adjacent_piece, Pawn):
                        last_move = board.move_history[-1] if board.move_history else None
                        if last_move and last_move.piece == adjacent_piece and last_move.start_pos[1] == '2' and last_move.end_pos[1] == '4':
                            moves.append(board.indices_to_pos(row - 1, col_adj))
        return moves


class Rook(ChessPiece):
    """Класс ладей."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'R' if color == 'white' else 'r'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для ладьи."""
        return board.get_straight_moves(self.location, self.color)


class Knight(ChessPiece):
    """Класс коней."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'N' if color == 'white' else 'n'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для коня."""
        moves = []
        row, col = board.pos_to_indices(self.location)
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.board[new_row][new_col]
                if target is None or target.color != self.color:
                    moves.append(board.indices_to_pos(new_row, new_col))
        return moves


class Bishop(ChessPiece):
    """Класс слонов."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'B' if color == 'white' else 'b'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для слона."""
        return board.get_diagonal_moves(self.location, self.color)


class Queen(ChessPiece):
    """Класс ферзей."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'Q' if color == 'white' else 'q'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для ферзя."""
        return board.get_straight_moves(self.location, self.color) + \
               board.get_diagonal_moves(self.location, self.color)


class King(ChessPiece):
    """Класс королей."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'K' if color == 'white' else 'k'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для короля."""
        moves = []
        row, col = board.pos_to_indices(self.location)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = board.board[new_row][new_col]
                    if target is None or target.color != self.color:
                        moves.append(board.indices_to_pos(new_row, new_col))
        return moves


class SuperBishop(Bishop):
    """Класс Суперслонов (заменителя слонов)."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'E' if color == 'white' else 'e'
        self.replacement = 'Bishop'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для Суперслона."""
        return board.get_diagonal_moves(self.location, self.color, super_bishop=True)

    def move(self, location, board):
        """Перемещает Суперслона, съедая все фигуры на пути."""
        if new_location in self.get_possible_moves(board):
            board.make_move(self.location + '-' + new_location, super_bishop=True)
            return True
        return False


class Fence(Pawn):
    """Класс Забора (заменителя пешек)."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'F' if color == 'white' else 'f'
        self.replacement = 'Pawn'
        self.invulnerable = True

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для Забора."""
        moves = []
        row, col = board.pos_to_indices(self.location)
        direction = 1 if self.color == 'white' else -1

        # Это шажок вперёд
        new_row = row + direction
        if 0 <= new_row < 8 and board.board[new_row][col] is None:
            moves.append(board.indices_to_pos(new_row, col))

        # Это кушанье диагональное
        for dr, dc in [(direction, -1), (direction, 1), (direction, 0)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.board[new_row][new_col]
                if target and target.color != self.color and (not getattr(target, 'invulnerable', False)):
                    moves.append(board.indices_to_pos(new_row, new_col))
        return moves


class Gosha(King):
    """Класс Гоши (Заменителя короля)."""
    def __init__(self, color, location):
        super().__init__(color, location)
        self.symbol = 'G' if color == 'white' else 'g'
        self.replacement = 'King'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для Гоши."""
        moves = []
        row, col = board.pos_to_indices(self.location)
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = board.board[new_row][new_col]
                    if target is None or target.color != self.color:
                        moves.append(board.indices_to_pos(new_row, new_col))
        return moves


class Move:
    """Класс ходов.

    Attributes:
        start_pos (str): Начальная позиция.
        end_pos (str): Конечная позиция.
        piece (ChessPiece): Фигура, которая ходила.
        captured (ChessPiece): Съеденная фигура (если есть).
    """
    def __init__(self, start_pos, end_pos, piece, captured=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.piece = piece
        self.captured = captured


class ChessBoard:
    """Класс управления шахматной доской.

    Attributes:
        board (list): Двумерный список 8x8 с фигурами.
        movement_history (list): История ходов.
    """
    def __init__(self):
        """Инициализирует доску с начальной расстановкой."""
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.movement_history = []
        self.setup_board()

    def setup_board(self):
        """Устанавка начальной расстановки фигур."""
        # Пешки
        for col in range(8):
            self.board[1][col] = Pawn('white', self.indices_to_pos(1, col))
            self.board[6][col] = Pawn('black', self.indices_to_pos(6, col))
        # Ладьи
        self.board[0][0], self.board[0][7] = Rook('white', 'a1'), Rook('white', 'h1')
        self.board[7][0], self.board[7][7] = Rook('black', 'a8'), Rook('black', 'h8')
        # Кони
        self.board[0][1], self.board[0][6] = Knight('white', 'b1'), Knight('white', 'g1')
        self.board[7][1], self.board[7][6] = Knight('black', 'b8'), Knight('black', 'g8')
        # Слоны
        self.board[0][2], self.board[0][5] = Bishop('white', 'c1'), Bishop('white', 'f1')
        self.board[7][2], self.board[7][5] = Bishop('black', 'c8'), Bishop('black', 'f8')
        # Ферзи
        self.board[0][3] = Queen('white', 'd1')
        self.board[7][3] = Queen('black', 'd8')
        # Короли
        self.board[0][4] = King('white', 'e1')
        self.board[7][4] = King('black', 'e8')

    def pos_to_indices(self, pos):
        """Преобразует позицию (например, 'e2') в индексы."""
        col = ord(pos[0]) - ord('a')
        row = int(pos[1]) - 1
        return row, col

    def indices_to_pos(self, row, col):
        """Преобразует индексы в позицию."""
        return chr(ord('a') + col) + str(row + 1)

    def get_straight_moves(self, pos, color, super_bishop=False):
        """Возврат возможных ходов по прямым линиям."""
        moves = []
        row, col = self.pos_to_indices(pos)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append(self.indices_to_pos(new_row, new_col))
                elif target.color != color and not getattr(target, 'invulnerable', False):
                    moves.append(self.indices_to_pos(new_row, new_col))
                    break
                else:
                    break
        return moves

    def get_diagonal_moves(self, pos, color, super_bishop=False):
        """Возврат возможных ходов по диагоналям."""
        moves = []
        row, col = self.pos_to_indices(pos)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append(self.indices_to_pos(new_row, new_col))
                    if not super_bishop:
                        continue
                elif target.color != color and not getattr(target, 'invulnerable', False):
                    moves.append(self.indices_to_pos(new_row, new_col))
                    if not super_bishop:
                        break
                else:
                    if not super_bishop:
                        break
        return moves

    def make_move(self, move_str, super_bishop=False):
        """Выполнение хода на доске."""
        start_pos, end_pos = move_str.split('-')
        start_row, start_col = self.pos_to_indices(start_pos)
        end_row, end_col = self.pos_to_indices(end_pos)
        piece = self.board[start_row][start_col]
        captured = self.board[end_row][end_col]

        if super_bishop:
            # Суперслон съедает все фигуры на пути
            dr = -1 if start_row > end_row else 1 if start_row < end_row else 0
            dc = -1 if start_col > end_col else 1 if start_col < end_col else 0
            r, c = start_row + dr, start_col + dc
            while r != end_row or c != end_col:
                self.board[r][c] = None
                r += dr
                c += dc

        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.location = end_pos
        self.movement_history.append(Move(start_pos, end_pos, piece, captured))

    def undo_move(self):
        """Отмена последнего хода."""
        if not self.movement_history:
            return False
        move = self.movement_history.pop()
        start_row, start_col = self.pos_to_indices(move.start_pos)
        end_row, end_col = self.pos_to_indices(move.end_pos)
        self.board[start_row][start_col] = move.piece
        self.board[end_row][end_col] = move.captured
        move.piece.location = move.start_pos
        return True

    def display(self):
        """Отображение доски в консоли."""
        print('\n  a b c d e f g h')
        for i in range(7, -1, -1):
            row = f'{i+1} '
            for j in range(8):
                piece = self.board[i][j]
                row += (piece.symbol if piece else '.') + ' '
            print(row)
        print('  a b c d e f g h\n')


    def display_with_highlights(self, possible_moves):
        """Отображение доски с подсветкой возможных ходов."""
        print('\n  a b c d e f g h')
        for i in range(7, -1, -1):
            row = f'{i+1} '
            for j in range(8):
                pos = self.indices_to_pos(i, j)
                if pos in possible_moves:
                    row += '*' + ' '
                else:
                    piece = self.board[i][j]
                    row += (piece.symbol if piece else '.') + ' '
            print(row)
        print('  a b c d e f g h\n')

    def get_threatened_pieces(self, color):
        """Возврат списка фигур, находящихся под угрозой."""
        threatened = []
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for r in range(8):
                        for c in range(8):
                            opponent_piece = self.board[r][c]
                            if opponent_piece and opponent_piece.color == opponent_color:
                                if piece.position in opponent_piece.get_possible_moves(self):
                                    threatened.append(piece)
                                    break
        return threatened


class ChessGame:
    """Класс управления игрой в шахматы.

    Attributes:
        board (ChessBoard): Объект шахматной доски.
        current_player (str): Текущий игрок ('white' или 'black').
        move_count (int): Количество сделанных ходов.
        log_file (str): Путь к файлу для записи ходов.
        replacements (dict): Словарь замен фигур для каждого игрока.
    """
    def __init__(self):
        """Инициализация игры."""
        self.board = ChessBoard()
        self.current_player = 'white'
        self.move_count = 0
        self.log_file = 'chess_moves.txt'
        self.replacements = {'white': {}, 'black': {}}
        self.setup_replacements()

    def setup_replacements(self):
        """Настройка замены фигур перед началом игры."""
        for player in ['white', 'black']:
            print(f"\nНастройка для {player}:")
            if input("Хотите заменить фигуры? (y/n): ").lower() == 'y':
                print("Доступные замены: 1) Суперслон (за слонов), 2) Забор (за пешки), 3) Гоша (за короля)")
                choice = input("Введите номера замен (через пробел, например '1 3'): ").split()
                for c in choice:
                    if c == '1':
                        self.replacements[player]['Bishop'] = SuperBishop
                        for pos in (('c1', 'f1') if player == 'white' else ('c8', 'f8')):
                            r, c = self.board.pos_to_indices(pos)
                            self.board.board[r][c] = None
                    elif c == '2':
                        self.replacements[player]['Pawn'] = Fence
                        row = 1 if player == 'white' else 6
                        for col in range(8):
                            pos = self.board.indices_to_pos(row, col)
                            self.board.board[row][col] = Fence(player, pos)
                    elif c == '3':
                        self.replacements[player]['King'] = Gosha
                        pos = 'e1' if player == 'white' else 'e8'
                        r, c = self.board.pos_to_indices(pos)
                        self.board.board[r][c] = Gosha(player, pos)

    def save_move_to_file(self, move_str):
        """Запись хода в файл."""
        with open(self.log_file, 'a') as f:
            f.write(f"{self.move_count}. {move_str}\n")

    def handle_input(self):
        """Обработка ввода пользователя."""
        while True:
            self.board.display()
            self.display_threatened_pieces()
            prompt = f"Введите ход для {self.current_player} (например, 'e2-e4', 'backup' или 'show'): "
            move_str = input(prompt).strip()
            if move_str.lower() == 'backup':
                if self.board.undo_move():
                    self.current_player = 'black' if self.current_player == 'white' else 'white'
                    self.move_count -= 1
                    print("Ход отменен.")
                else:
                    print("Нет ходов для отмены.")
                continue
            elif move_str.lower() == 'show':
                self.show_possible_moves()
                continue

            if '-' not in move_str:
                print("Неверный формат. Используйте 'e2-e4'.")
                continue

            start_pos, end_pos = move_str.split('-')
            start_row, start_col = self.board.pos_to_indices(start_pos)
            piece = self.board.board[start_row][start_col]

            if not piece or piece.color != self.current_player:
                print("На этой позиции нет вашей фигуры.")
                continue

            if piece.move(end_pos, self.board):
                self.save_move_to_file(move_str)
                self.move_count += 1
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                break
            else:
                print("Недопустимый ход.")

    def display_threatened_pieces(self):
        """Вывод информации о фигурах, находящихся под угрозой."""
        threatened = self.board.get_threatened_pieces(self.current_player)
        if threatened:
            print(f"Фигуры {self.current_player}, находящиеся под угрозой:")
            for piece in threatened:
                print(f"{piece.symbol} на {piece.position}")
        else:
            print(f"Нет фигур {self.current_player}, находящихся под угрозой.")

    def show_possible_moves(self):
        """Отображение возможных (допустимых) ходов для выбранной фигуры."""
        pos = input("Введите позицию фигуры (например, 'e2'): ").strip()
        row, col = self.board.pos_to_indices(pos)
        piece = self.board.board[row][col]
        if piece and piece.color == self.current_player:
            moves = piece.get_possible_moves(self.board)
            self.board.display_with_highlights(moves)
        else:
            print("На этой позиции нет вашей фигуры.")

    def play(self):
        """Запуск основного цикла игры."""
        print(
            "Добро пожаловать в шахматы! Введите ходы в формате 'e2-e4'. Для отмены хода введите 'backup'. Для подсказки ходов введите 'show'.")
        while True:
            self.handle_input()


# Класс игрового процесса и правил (класс шашек)
class CheckersPiece(ChessPiece):
    """Класс для шашек."""
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'C' if color == 'white' else 'c'

    def get_possible_moves(self, board):
        """Возвращает список возможных ходов для шашки."""
        moves = []
        row, col = board.pos_to_indices(self.position)
        directions = [(-1, -1), (-1, 1)] if self.color == 'white' else [(1, -1), (1, 1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.board[new_row][new_col]
                if target is None:
                    moves.append(board.indices_to_pos(new_row, new_col))
                elif target.color != self.color:
                    jump_row, jump_col = new_row + dr, new_col + dc
                    if 0 <= jump_row < 8 and 0 <= jump_col < 8 and board.board[jump_row][jump_col] is None:
                        moves.append(board.indices_to_pos(jump_row, jump_col))
        return moves

# Класс доски
class CheckersBoard(ChessBoard):
    """Класс для доски шашек."""
    def setup_board(self):
        """Устанавливает начальную расстановку шашек."""
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = CheckersPiece('black', self.indices_to_pos(row, col))
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = CheckersPiece('white', self.indices_to_pos(row, col))

# Класс самой игры
class CheckersGame:
    """Класс для управления игрой в шашки."""
    def __init__(self):
        self.board = CheckersBoard()
        self.current_player = 'white'
        self.move_count = 0

    def play(self):
        """Запускает основной цикл игры в шашки."""
        print("Добро пожаловать в шашки! Введите ходы в формате 'e2-e4'.")
        while True:
            self.board.display()
            prompt = f"Введите ход для {self.current_player} (например, 'e2-e4'): "
            move_str = input(prompt).strip()
            if '-' not in move_str:
                print("Неверный формат. Используйте 'e2-e4'.")
                continue
            start_pos, end_pos = move_str.split('-')
            start_row, start_col = self.board.pos_to_indices(start_pos)
            piece = self.board.board[start_row][start_col]
            if not piece or piece.color != self.current_player:
                print("На этой позиции нет вашей шашки.")
                continue
            if piece.move(end_pos, self.board):
                self.move_count += 1
                self.current_player = 'black' if self.current_player == 'white' else 'white'
            else:
                print("Недопустимый ход.")

# Тестовый запуск игры
if os.path.exists('chess_moves.txt'):
    os.remove('chess_moves.txt') # Во избежание некорректного сохранения истории ходов и возникновения конфликтов при записи файла с ходами мы пересоздаём файл с ходами
print("Выберите игру: 1) Шахматы, 2) Шашки")
choice = input("Введите номер (1 или 2): ").strip()
if choice == '1':
    game = ChessGame()
    game.play()
elif choice == '2':
    game = CheckersGame()
    game.play()
else:
    print("Неверный выбор. Запускаются шахматы по умолчанию.")
    game = ChessGame()
    game.play()
