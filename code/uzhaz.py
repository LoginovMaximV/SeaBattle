from random import randint

class Color:
    yellow2 = '\033[1;35m'
    reset = '\033[0m'
    blue = '\033[0;34m'
    yellow = '\033[1;93m'
    red = '\033[1;31m'
    miss = '\033[0;37m'


def set_color(text, color):
    return color + text + Color.reset


class Cell(object):
    empty_cell = set_color(' ', Color.yellow2)
    ship_cell = set_color('■', Color.blue)
    damaged_ship = set_color('X', Color.red)
    miss_cell = set_color('•', Color.miss)

class Dot:

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f'({self.x}, {self.y})'


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self) -> str:
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self) -> str:
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


class Ship:

    def __init__(self, bow_of_ship, length: int, orientation: int) -> None:
        self.bow_of_ship = bow_of_ship
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self) -> list:
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow_of_ship.x
            cur_y = self.bow_of_ship.y

            if self.orientation == 0:
                cur_x += i

            if self.orientation == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot) -> bool:
        return shot in self.dots

class Board:

    def __init__(self, hid=False, size=6) -> None:
        self.hid = hid
        self.size = size

        self.count = 0

        self.field = [[Cell.empty_cell for i in range(size)] for i in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self) -> str:
        res = ""
        res += "  | 0 | 1 | 2 | 3 | 4 | 5 |"
        for i, row in enumerate(self.field):
            res += f"\n{i} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace(Cell.ship_cell, Cell.empty_cell)
        return res

    def out(self, dot) -> bool:
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, verb=False) -> None:
        near = [
            (-1, 1), (0, 1), (1, 1),
            (-1, 0), (0, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]
        for dot in ship.dots:
            for dot_x, dot_y in near:
                cur = Dot(dot.x + dot_x, dot.y + dot_y)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = Cell.miss_cell
                    self.busy.append(cur)

    def add_ship(self, ship):

        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = Cell.ship_cell
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.busy:
            raise BoardUsedException()

        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.x][dot.y] = Cell.damaged_ship
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = Cell.miss_cell
        print("Мимо")
        return False

    def begin(self):
        self.busy = []

class Player:

    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def action(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):

    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {dot.x} {dot.y}')
        return dot

class User(Player):
    def ask(self):
        while True:
            coordinations = input("Ваш ход: ").split()

            if len(coordinations) != 2:
                print("Введите 2 координаты! ")
                continue

            x, y = coordinations
            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x, y)

class Game:

    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.user = User(pl, co)

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def upload_board(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.user.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)

    def loop(self):
        num = 0
        while True:
            self.upload_board()
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.user.action()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.action()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                self.upload_board()
                break

            if self.user.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                self.upload_board()
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
