"""
A module to represent a model for the hecks game, for engines to be able to use.
"""

import collections

RED = "R"
BLUE = "B"

HTP_PASS = "pass"
HTP_RESIGN = "resign"


# A move is an immutable collection of color and HTP vertex string.
Move = collections.namedtuple("Move", ["color", "vertex"])


class Game(object):
    """
    The basic representation of a game. use Game.play() to add a move to the board, and Game.is_legal(move) to check
    the move's legality. Additional methods to access the current state of the board also exist.

    A distinction should me made between vertex and vertex_tuple. All interaction with the class is expected to take
    place using vertices, as defined in the HTP. Nevertheless, some of the class's methods are exposed for convenience,
    and these methods use the class's inner representation of the game and the moves, which is based on vertex_tuple -
    an integer tuple representation of the vertices. Therefore when using the class's methods, read the docs and make
    sure you understand exactly which type of vertex you need. The static method Game.to_vertex_tuple can be used to
    make the conversion when necessary.

    As a general rule of thumb, methods using Move objects will always require the move vertex to use HTP vertices,
    while moves requiring just the vertex, will usually use a tuple_notation vertex.

    THIS CLASS IS NOT THREAD SAFE.
    """

    # Dictionaries used for memoization, to reduce some calculations.
    __conversion_dict = {}
    __neighbors_dict = {}

    def __init__(self):
        """ Create a new object with an empty board. """
        self.board = collections.defaultdict(lambda: None)
        self.movelist = []
        self.current_player = BLUE

    def count_liberties_of(self, vertex_tuple):
        """ Return the number of free liberties of the group with a stone located at given vertex_tuple. """

        color = self.board[vertex_tuple]
        if not color:
            raise ValueError("Can't count liberties of empty space.")

        liberties = 0

        queue = collections.deque() # Just because lists work O(1)
        queue.append(vertex_tuple)
        expanded = {}

        while queue:
            visiting = queue.popleft()
            if visiting in expanded:
                continue
            expanded[visiting] = True

            for neighbor in self.get_neighbors(visiting):
                if self.board[neighbor] is None:
                    liberties += 1
                elif self.board[neighbor] == color:
                    queue.append(neighbor)

        return liberties

    def is_legal(self, move):
        """ Return True if given Move is legal. """
        if self.current_player == move.color:
            if move.vertex in (HTP_PASS, HTP_RESIGN):
                return True

            try:
                vertex_tuple = self.to_vertex_tuple(move.vertex)
            except ValueError:
                print("error")
                return False

            if self.board[vertex_tuple] is None and self.is_not_suicide(move):
                return True
        return False

    def is_not_suicide(self, move):
        """ Return True if playing given move will not result in a suicide. """
        vertex_tuple = self.to_vertex_tuple(move.vertex)
        if self.board[vertex_tuple] is not None:
            raise ValueError("Non-empty coordinate passed to is_not_suicide")
        self.board[vertex_tuple] = move.color
        liberty_count = self.count_liberties_of(vertex_tuple)
        self.board[vertex_tuple] = None
        return liberty_count != 0

    def play(self, move):
        """ Play a move on the board if it's legal. Raise ValueError otherwise. """
        if self.is_legal(move):
            self.board[move.vertex] = move.color
            self.movelist.append(move)
            self.current_player = RED if self.current_player == BLUE else BLUE
        else:
            raise ValueError("Illegal move given to play")

    def pprint(self):
        """ Attempt to prettily print the current state of the board."""
        for y in range(10, 0, -1):
            row_length = self.length_of_row(y)
            top_row = chr(ord('a') + y - 1) + " " * ((19 - row_length) // 2)
            bottom_row = chr(ord('a') + y - 1) + " " * ((19 - row_length) // 2)
            for x in range(1, row_length + 1):
                dot = self.board[(y, x)]
                if not dot:
                    dot = "."
                if (y >= 6 and x % 2 == 0) or (y <= 5 and x % 2 == 1):
                    top_row += dot
                    bottom_row += " "
                else:
                    bottom_row += dot
                    top_row += " "

            print(top_row)
            print(bottom_row)

    @staticmethod
    def length_of_row(row):
        """ Return the number of vertices in a given row. Accepts both integer and alphabetical notation. """
        if isinstance(row, str) and row.isalpha():
            row = ord(row.lower()) - ord('a') + 1
        try:
            row = int(row)
        except ValueError:
            raise ValueError('Invalid literal for length_of_row(): {}'.format(repr(row)))

        if 1 <= row <= 5:
            return 9 + 2 * row
        elif 6 <= row <= 10:
            return 9 + 2 * (11 - row)
        else:
            raise ValueError('Invalid literal for length_of_row(): {}'.format(repr(row)))

    @staticmethod
    def get_neighbors(vertex_tuple):
        """ Return a list of integer tuple vertices neighboring given integer tuple vertex. (Assumes valid vertex) """
        if vertex_tuple in Game.__neighbors_dict:
            return Game.__neighbors_dict[vertex_tuple]

        y, x = vertex_tuple

        max_x = Game.length_of_row(y)

        neighbors = ()
        if x > 1:
            neighbors += (y, x - 1),
        if x < max_x:
            neighbors += (y, x + 1),

        if y <= 5:
            if y >= 2 and x % 2 == 0:
                neighbors += (y - 1, x - 1),
            elif x % 2 == 1:
                if y < 5:
                    neighbors += (y + 1, x + 1),
                else:
                    neighbors += (y + 1, x),
        else:
            if y <= 9 and x % 2 == 0:
                neighbors += (y + 1, x - 1),
            elif x % 2 == 1:
                if y > 6:
                    neighbors += (y - 1, x + 1),
                else:
                    neighbors += (y - 1, x),
        Game.__neighbors_dict[vertex_tuple] = neighbors
        return neighbors

    @staticmethod
    def to_vertex_tuple(vertex):
        """
        Return an integer tuple representing the vertex string.

        Raise ValueError in case of illegal formatting or moves not placed on the board,
        but doesn't check for legality of moves. Will also raise ValueError for "pass" and "resign".

        i.e. "a1" will be converted to (1,1), and "B100" will be converted to (2, 100)

        :param vertex: HTP string representing a vertex
        :return: integer tuple representing the vertex
        """
        if vertex in Game.__conversion_dict:
            return Game.__conversion_dict[vertex]

        if 2 <= len(vertex) <= 3:
            row, col = vertex[0], vertex[1:]
            if row.isalpha() and 'a' <= row.lower() <= 'j' and col.isdigit():

                row_val = ord(row.lower()) - ord('a') + 1
                col = int(col)

                max_col = Game.length_of_row(row)

                if 1 <= int(col) <= max_col:
                    Game.__conversion_dict[vertex] = (row_val, col)
                    return row_val, col

        raise ValueError("Invalid vertex to to_tuple_vertex {}".format(vertex))

if __name__ == "__main__":
    # Test Move immutability
    a = Move(3, 3)
    assert a.color == 3
    try:
        a.color = 2
    except AttributeError:
        pass
    assert a.color == 3

    # Test Game.length_of_row
    for value, expected in (("a", 11), ("b", 13), ("c", 15), ("D", 17), ("e", 19), ("F", 19), ("g", 17), ("h", 15), ("i", 13), ("J", 11),
                            (1, 11), (2, 13), (3, 15), (4, 17), (5, 19), ("6", 19), ("7", 17), ("8", 15), ("9", 13), ("10", 11)):
        got = Game.length_of_row(value)
        print(value, expected, got)
        assert expected == got

    # Test Game.to_vertex_tuple
    for value, expected in (("a1", (1,1)), ("h3", (8,3)), ("a11", (1,11)), ("j11", (10,11)), ("e19", (5,19)),
                            ("f19", (6,19))):
        got = Game.to_vertex_tuple(value)
        print(value, got, expected)
        assert got == expected

    for value in ("a20", "11", "f-2", "e0", "a12", "b14", "c16", "d18", "e20", "a", "4a"):
        print(value, "Expecting ValueError")
        try:
            got = Game.to_vertex_tuple(value)
            print(got)
            assert False
        except ValueError:
            pass

    # Test Game.get_neighbors
    for value, expected in (((1, 2), ((1,1), (1,3))), ((1, 2), ((1,1), (1,3))), ((5,5), ((5,4), (5,6), (6,5))),
                            ((1,1), ((1,2), (2,2))), ((10,11), ((10,10), (9, 12)))):
        got = Game.get_neighbors(value)
        print(value, ":", repr(got), "=", repr(expected))
        assert got == expected

    # Test game.count_liberties_of
    def test_liberties_scenario(moves, target, expected):
        game = Game()
        for move in moves:
            game.board[game.to_vertex_tuple(move.vertex)] = move.color
        game.pprint()
        got = game.count_liberties_of(target)
        print(target, got, expected)
        assert got == expected
    scenarios = [
        ([Move(BLUE, "a1"), Move(BLUE, "b2")],
         (1,1), 3),
        ([Move(BLUE, "a1"), Move(BLUE, "b2")],
         (2,2), 3),
        ([Move(BLUE, "a1"), Move(RED, "b2")],
         (1,1), 1),
        ([Move(BLUE, "a1"), Move(RED, "b2")],
         (2,2), 2),
        ([Move(BLUE, "a1"), Move(RED, "b2"), Move(RED, "a2")],
         (1,1), 0),
        ([Move(BLUE, "e9")],
         (5, 9), 3),
        ([Move(BLUE, "e9"), Move(BLUE, "e11"), Move(RED, "e7")],
         (5, 9), 3),
        ([Move(BLUE, "e9"), Move(BLUE, "f9")],
         (5, 9), 4),
        ([Move(BLUE, "e9"), Move(RED, "f9"), Move(BLUE, "F8")],
         (5, 9), 2)
    ]
    for scenario in scenarios:
        test_liberties_scenario(*scenario)

    # Test game.is_legal
    game = Game()
    game.current_player = BLUE
    assert game.is_legal(Move(RED, "a1")) is False

    game = Game()
    game.current_player = RED
    assert game.is_legal(Move(BLUE, "a1")) is False

    def test_is_legal_scenario(moves, target, expected):
        game = Game()
        game.current_player = target.color
        for move in moves:
            game.board[game.to_vertex_tuple(move.vertex)] = move.color
        game.pprint()
        got = game.is_legal(target)
        print(target, got, expected)
        assert got == expected


    scenarios = [
        ([Move(BLUE, "a1"), Move(BLUE, "b2")],
         Move(BLUE, "a2"), True),
        ([Move(BLUE, "a1"), Move(BLUE, "b2")],
         Move(BLUE, "a1"), False),
        ([Move(BLUE, "a1"), Move(BLUE, "b1"), Move(BLUE, "b3")],
         Move(RED, "b2"), False),
        ([Move(BLUE, "a1"), Move(BLUE, "b1"), Move(BLUE, "b3")],
         Move(BLUE, "b2"), True),
        ([Move(BLUE, "a1"), Move(BLUE, "b1"), Move(BLUE, "b3"), Move(RED, "A2"), Move(RED, "B4"), Move(RED, "c2"), Move(RED, "c4")],
         Move(BLUE, "b2"), False),
        ([Move(BLUE, "a1"), Move(BLUE, "b1"), Move(BLUE, "b3"), Move(RED, "A2"), Move(RED, "B4"), Move(RED, "c2"),
          Move(RED, "c4")],
         Move(RED, "b2"), False)
    ]
    for scenario in scenarios:
        test_is_legal_scenario(*scenario)
