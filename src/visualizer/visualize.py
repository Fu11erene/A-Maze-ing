from sys import exit
from src.mazegen import MazeGenerator


def visualize(maze_gen: MazeGenerator) -> None:
    maze_gen.generate_data()
    maze_gen.print_board()
    maze_gen.generate_output()

    while True:
        print("===A-maze_gen-ing ===")
        print("1. Re-generate a new maze_gen")
        print("2. Show / Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Quit")
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
            raise ValueError("Invalid input")
