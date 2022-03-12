"""
Homework 01 - Game of life.

Your task is to implement a kind of cellular automaton called "Game of life".
The automaton is a 2D simulation where each cell on the grid is either dead
or alive.

The state of each cell is updated in every iteration based state of neighbouring cells.
Cell neighbours are cells that are horizontally, vertically, or diagonally adjacent.

Rules for the update are as follows:

1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
2. Any live cell with two or three live neighbours lives on to the next generation.
3. Any live cell with more than three live neighbours dies, as if by overpopulation.
4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.


Our implementation uses the coordinate system with grid coordinates starting
from (0, 0) - upper left corner. The first coordinate is a row, and the second
is a column.

Do not use wrap-around (toroid) when reaching the edge of the board.

For more details about Game of Life, see Wikipedia:
https://en.wikipedia.org/…ife
"""


# row, then column
def get_neighbors(pos, size, alive):
    n = 0
    row, col = pos
    height, width = size
    if row:
        if (row - 1, col) in alive:
            n += 1
        if col:
            if (row - 1, col - 1) in alive:
                n += 1
        if col != width - 1:
            if (row - 1, col + 1) in alive:
                n += 1
    if col:
        if (row, col - 1) in alive:
            n += 1
    if row != height - 1:
        if (row + 1, col) in alive:
            n += 1
        if col:
            if (row + 1, col - 1) in alive:
                n += 1
        if col != width - 1:
            if (row + 1, col + 1) in alive:
                n += 1
    if col != width - 1:
        if (row, col + 1) in alive:
            n += 1
    return n


def update(alive: set, size: (int, int), iter_n: int) -> set:
    """
    Perform iter_n iterations.

    Args
    ----
        alive (set):
            A set of cell coordinates marked as alive, can be empty.
        size (int, int):
            The size of simulation grid as a tuple of two ints.
        iter_n (int):
            A number of iterations to perform.

    Returns
    -------
        _  (set):
            A set of coordinates of alive cells after iter_n iterations.
    """

    # TODO: Implement update rules.
    new_alive = list(alive)
    height, width = size
    for _ in range(0, iter_n):
        nextalive = []
        for row in range(height):
            for col in range(width):
                neighbors = get_neighbors((row, col), size, new_alive)
                if (row, col) in alive:
                    if neighbors < 2 or neighbors > 3:
                        # nextalive.remove((row, col))
                        pass
                    else:
                        nextalive.append((row, col))
                else:
                    if neighbors == 3:
                        nextalive.append((row, col))
        new_alive = nextalive

    return set(new_alive)


def draw(alive: set, size: (int, int)) -> str:
    """
    Draw a game board.

    Args
    ----
        alive (set):
            A set of cell coordinates marked as alive, can be empty.
        size (int, int):
            The size of simulation grid as a tuple of two ints.

    Returns
    -------
        _  (string):
           A string showing the board state with alive cells marked with X.
    """
    # TODO: implement board drawing logic and return it as output
    # Don't call print in this method, just return board string as output.
    # Example of 3x3 board with 1 alive cell at coordinates (0, 2):
    # +---+
    # |  X|
    # |   |
    # |   |
    # +---+
    height, width = size
    board = """+"""
    for _ in range(width):
        board += "-"
    board += "+\n"
    for row in range(height):
        board += "|"
        for col in range(width):
            if (row, col) in alive:
                board += "X"
            else:
                board += " "
        board += "|\n"
    board += "+"
    for _ in range(width):
        board += "-"
    board += "+"
    return board


if __name__ == "__main__":
    t = {(0, 1), (1, 1), (2, 1)}
    print(draw(t, (3, 3)))
    print(update(t, (3, 3), 2))
