from sys import exit
from src.mazegen import MazeGenerator


def _print_operations() -> None:
    print("1. Re-generate a new maze")
    print("2. Show / Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Quit")


def visualize(maze_gen: MazeGenerator) -> None:
    """
    迷路の表示や表示の切り替えなどをするUI
    """
    maze_gen.generate_data()
    maze_gen.print_board()
    maze_gen.generate_output()

    print("===A-maze-ing ===")
    _print_operations()
    while True:
        try:
            choise = input("Choise? (1-4): ")
        except KeyboardInterrupt:
            raise ValueError("\nKeyboard interrupted")
        if choise == "1":
            maze_gen.generate_data()
            maze_gen.print_board()
            maze_gen.generate_output()
        elif choise == "2":
            continue
        elif choise == "3":
            maze_gen.rotate_wall_colour()
        elif choise == "4":
            exit(0)
        else:
            print("Invalid input. Try again.")
            continue
        _print_operations()
