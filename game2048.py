from tkinter import *
from tkinter import messagebox
from tkinter.simpledialog import askstring
from random import choice

from time import time_ns


def timeit(func):
    """
    Обертка для дебага, посмотреть время выполнения функции.
    """

    def wrap(*args, **kwargs):
        start = time_ns()
        result = func(*args, **kwargs)
        finish = time_ns()
        print(f"{func.__name__} completes in {(finish - start) / 1000000}ms")
        return result

    return wrap


class Block:
    """
    Блок на доске.
    """
    def __init__(self, val=2):
        self.val = val

    def __repr__(self):
        return f"Block({self.val})"

    def __str__(self):
        return str(self.val)

    def __eq__(self, other):
        if other is None:
            return False
        return self.val == other.val

    def __lt__(self, other):
        return self.val < other.val

    def __gt__(self, other):
        return self.val > other.val

    def __add__(self, other):
        if other is None:
            return self
        if self == other:
            return self.__class__(self.val + other.val)
        else:
            raise ValueError(f"Нельзя складывать блоки разных размеров.")


class Board:
    """
    Доска
    """
    def __init__(self, size: int) -> None:
        self.current_score = 0
        self.size = size
        self.board: list[list[Block | None]] = [[None for _ in range(self.size)] for _ in range(self.size)]

    def __repr__(self) -> str:
        """
        Печатает матрицу.
        """
        return "\n".join(map(str, self.board))

    def __copy_board(self):
        return [line.copy() for line in self.board]

    def no_more_moves(self) -> bool:
        """
        Если движение в любую из сторон не изменило доску, значит ходов больше нет.
        """
        return all([
            self.board == self._shift_up(self.__copy_board()),
            self.board == self._shift_left(self.__copy_board()),
            self.board == self._shift_right(self.__copy_board()),
            self.board == self._shift_down(self.__copy_board()),
        ])

    def is_have_free_cells(self) -> bool:
        """
        Есть пустые блоки в матрице?
        """
        return not all([all(row) for row in self.board])

    def get_free_cell_coords(self) -> list[tuple[int, int]]:
        """
        Возвращяет список с координатами пустых блоков.
        """
        return [(row, col) for col in range(self.size) for row in range(self.size) if self.board[row][col] is None]

    def put_block(self) -> None:
        """
        Если есть пустые блоки, то рандомно выберает один из них и устанавливает туда новый блок.
        """
        if self.is_have_free_cells():
            x, y = choice(self.get_free_cell_coords())
            self.board[x][y] = Block()

    @staticmethod
    def __clean(blocks_line: list[int or None]) -> list[int]:
        """
        Удаляет пустые блоки.
        """
        while None in blocks_line:
            blocks_line.remove(None)
        return blocks_line

    def __sum_equal(self, blocks_line: list[int | None]) -> list[int | None]:
        """
        Для одной строки, удаляет пустые блоки, складывает одинаковые блоки слева на право,
        добавляет вконце пустые блоки.
        """
        tmp = blocks_line.copy()
        blocks_line.clear()
        tmp = self.__clean(tmp)

        while len(tmp) > 1:
            one = tmp.pop(0)
            two = tmp.pop(0)

            if one == two:
                blocks_line.append(one + two)
                self.current_score += 1
            else:
                blocks_line.append(one)
                tmp.insert(0, two)

        if len(tmp) == 1:
            blocks_line.append(tmp.pop(0))

        while len(blocks_line) < self.size:
            blocks_line.append(None)

        return blocks_line

    def __cols_to_lines(self, board: list[list[int | None]]) -> list[list[int | None]]:
        """
        Переворачивает матрицу, колонки становятся строками
        """
        return [[line[index] for line in board] for index in range(self.size)]

    def __left(self, blocks_line: list[int or None]):
        """
        Сдвигает одну линию блоков влево и суммирует одинаковые блоки
        [Block(2), None, Block(2), None] ==> [Block(4), None, None, None]
        """
        return self.__sum_equal(blocks_line)

    def __right(self, blocks_line: list[int or None]):
        """
        Сдвигает одну линию блоков вправо и суммирует одинаковые блоки.
        [Block(2), None, Block(2), None] ==> [None, None, None, Block(4)]
        """
        blocks_line.reverse()
        blocks_line = self.__sum_equal(blocks_line)
        blocks_line.reverse()
        return blocks_line

    def _shift_up(self, board: list[list[int | None]]) -> list[list[int | None]]:
        """
        Сдвигает все блоки, в полученной матрице, вверх и суммирует одинаковые блоки.
        Возвращяет сдвинутую матрицу
        """
        board = self.__cols_to_lines(board)
        for index, line in enumerate(board):
            board[index] = self.__left(line)
        board = self.__cols_to_lines(board)
        return board

    def _shift_right(self, board: list[list[int | None]]):
        """
        Сдвигает все блоки, в полученной матрице, вправо и суммирует одинаковые блоки.
        Возвращяет сдвинутую матрицу
        """
        for index, line in enumerate(board):
            board[index] = self.__right(line)
        return board

    def _shift_down(self, board: list[list[int | None]]) -> list[list[int | None]]:
        """
        Сдвигает все блоки, в полученной матрице, вниз и суммирует одинаковые блоки.
        Возвращяет сдвинутую матрицу
        """
        board = self.__cols_to_lines(board)
        for index, line in enumerate(board):
            board[index] = self.__right(line)
        board = self.__cols_to_lines(board)
        return board

    def _shift_left(self, board: list[list[int | None]]) -> list[list[int | None]]:
        """
        Сдвигает все блоки, в полученной матрице, влево и суммирует одинаковые блоки.
        Возвращяет сдвинутую матрицу
        """
        for index, line in enumerate(board):
            board[index] = self.__left(line)
        return board

    def shift_up(self) -> None:
        """Сдыинуть собственную матрицу вверх"""
        self.board = self._shift_up(self.board)

    def shift_right(self) -> None:
        """Сдыинуть собственную матрицу вправо"""
        self.board = self._shift_right(self.board)

    def shift_down(self) -> None:
        """Сдыинуть собственную матрицу вниз"""
        self.board = self._shift_down(self.board)

    def shift_left(self) -> None:
        """Сдыинуть собственную матрицу влево"""
        self.board = self._shift_left(self.board)


class Game2048(Tk):
    def __init__(self, size=4):
        super().__init__()
        self.size = size
        self.board = None
        self.geometry(f"{self.size * 70}x{(self.size * 70) + 100}")

        self.colors = {}
        self.set_colors()

        self.bind('<Up>', self.up_key)
        self.bind('<Left>', self.left_key)
        self.bind('<Down>', self.down_key)
        self.bind('<Right>', self.right_key)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        for i in range(self.size + 1):
            self.columnconfigure(index=i, weight=1)
            self.rowconfigure(index=i, weight=1)

        self.best_score = None
        self.best_player = None
        self.get_best_score()

        self.player_name = None
        self.get_player_name()
        self.title(f"Game 2048 - {self.player_name if self.player_name else 'Noname'}")

        self.new_game()

    def set_colors(self):
        """
        Создает словарь с цветами для блоков, где ключ вес блока, а значение цвет в 16-ричной кодировке.
        """
        start_color = int("FFFF00", 16)
        color_step = int("2000", 16)
        i = 2
        while i <= 2 ** 24:
            current_color = start_color - color_step
            self.colors[i] = f"#{current_color:x}"
            start_color = current_color
            i *= 2

    def new_game(self):
        """
        Новая игра.
        Создает новую доску, поиещяет туда два первых блока.
        """
        self.board = Board(self.size)
        self.board.put_block()
        self.board.put_block()
        self.update_board()

    def get_player_name(self):
        """
        Запрашивает имя игрока и устанавливает его.
        """
        player_name = askstring('Name', 'What is your name?')
        self.player_name = player_name if player_name else "Noname"

    def get_best_score(self):
        """
        Считывает из файла `data` лучший ризультат и имя игрока.
        """
        try:
            with open("data", "r") as file:
                self.best_player, self.best_score = file.read().split('@')
        except FileNotFoundError:
            self.best_score = 0

    def is_best_score(self):
        """
        Текущий счет лучше сохраненного?
        """
        return self.board.current_score > int(self.best_score)

    def set_best_score(self):
        """
        Записывает имя игрока и его результат в файл `data`.
        """
        try:
            with open("data", "w") as file:
                file.write(f"{self.player_name}@{self.board.current_score}")
        except:
            pass

    def on_closing(self):
        """
        При закрытии спросить, сохранить результат, если он лучший.
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.is_best_score():
                self.set_best_score()
            self.destroy()

    def when_losing(self):
        """
        Сообщить о проигрыше, сохранить результат, если он лучший.
        """
        if messagebox.askokcancel("Losing", "Do you want to start again?"):
            if self.is_best_score():
                self.set_best_score()
            self.new_game()

    def update_board(self):
        """
        Обновить доску согласно текущей матрице.
        """
        curr_score = Label(self, text=f"Score: {self.board.current_score}")
        best_score = Label(self, text=f"Best: {self.best_score} by {self.best_player}")

        for r in range(self.size):
            for c in range(self.size):
                block = self.board.board[r][c]
                if block:
                    btn = Label(
                        text=f"{block.val}",
                        background=self.colors.get(block.val),
                        anchor="center",
                        relief="groove",
                    )
                else:
                    btn = Label(
                        text="",
                        background=f"#ffffff",
                        relief="sunken",
                    )

                btn.grid(row=r, column=c, ipadx=30, ipady=30, padx=4, pady=4, sticky=NSEW)

        curr_score.grid(row=self.size + 1, column=0, columnspan=self.size, ipadx=20, ipady=3, padx=4, pady=4,
                        sticky=NSEW)
        best_score.grid(row=self.size + 2, column=0, columnspan=self.size, ipadx=20, ipady=3, padx=4, pady=4,
                        sticky=NSEW)

    def game_is_over(self):
        """
        Игра проиграна, если ходов больше нет.
        """
        return self.board.no_more_moves()

    def __after_move(self):
        """
        Всякие обновления после любого нажатия.
        """
        self.update_board()
        self.board.put_block()
        self.update_board()
        if self.game_is_over():
            self.when_losing()

    def up_key(self, event):
        """
        Выполняется если нажата стрелка вверх.
        """
        self.board.shift_up()
        self.__after_move()

    def left_key(self, event):
        """
        Выполняется если нажата стрелка влево.
        """
        self.board.shift_left()
        self.__after_move()

    def down_key(self, event):
        """
        Выполняется если нажата стрелка вниз.
        """
        self.board.shift_down()
        self.__after_move()

    def right_key(self, event):
        """
        Выполняется если нажата стрелка вправо.
        """
        self.board.shift_right()
        self.__after_move()

    def start(self):
        """
        Запуск игры.
        """
        self.new_game()
        self.mainloop()


if __name__ == '__main__':
    g = Game2048()
    g.start()
