"""
Main file for running the A-Maze-ing maze generator.
"""

import sys
from mazegen import Config, MazeGenerator, InputError, Pallets, Cell
from os import system
from typing import Generator
import random


def get_coord(coord: str) -> tuple[int, int]:
    """
    Converts a string in the format 'x,y' into a tuple of integers.

    Args:
        coord (str): String with coordinates separated by a comma.
    Returns:
        tuple[int, int]: Tuple with integer coordinates.
    """
    coord_list: list[str] = coord.split(",")
    try:
        return (int(coord_list[0]), int(coord_list[1]))
    except (IndexError):
        raise IndexError("Invalid coordinates syntax")


def get_mazegen(file_name: str) -> MazeGenerator:
    """
    Reads the configuration file and returns a Config object.

    Args:
        file_name (str): Name of the configuration file.
    Returns:
        Config: Filled configuration object.
    Raises:
        FileNotFoundError: If the file does not exist.
        KeyError: If there is an error in the configurations.
    """

    config_dict: dict[str, str] = {}

    try:
        with open(file_name, "r") as file:
            for line in file:
                if not line.startswith("#"):
                    key: str = line.split("=")[0]
                    value: str = line.strip().split("=")[1]
                    config_dict.update({key: value})

    except FileNotFoundError:
        raise FileNotFoundError("Error: Invalid file!")

    except KeyError:
        raise KeyError(f"Error: Invalid configurations in {file_name}!")

    try:
        if (config_dict["PERFECT"].upper() in ["TRUE", "FALSE"]):
            perfect: bool = config_dict["PERFECT"].upper() == "TRUE"
        if ("SEED" in config_dict):
            seed: int | None = int(config_dict["SEED"])
        else:
            seed = None
        return MazeGenerator(int(config_dict["WIDTH"]),
                             int(config_dict["HEIGHT"]),
                             get_coord(config_dict["ENTRY"]),
                             get_coord(config_dict["EXIT"]),
                             config_dict["OUTPUT_FILE"],
                             perfect,
                             seed)

    except (KeyError, ValueError) as err:
        raise KeyError(f"{err}")


def display_maze(generator: MazeGenerator) -> None:
    """
    Print the maze to the terminal.

    Raises:
        MazeError: If there is no maze to display.
    """
    if (not generator.grid):
        raise Exception("There's no maze to display.")
    ret: str = ""
    for y in range(generator.configs.height):
        line_1: str = f"{generator.configs.color.wall_h}"
        line_2: str = ""
        for x in range(generator.configs.width):
            cell: Cell = generator.grid[y][x]
            if cell.is_pattern:
                line_1 += f"{generator.configs.color.wall_t}"
                line_2 += f"{generator.configs.color.wall_h}"
                line_2 += f"{generator.configs.color.fourty_two_v}"
            elif cell.is_path and generator.show_path:
                if cell.walls["north"] == 1:
                    line_1 += f"{generator.configs.color.wall_t}"
                else:
                    if generator.grid[y-1][x].is_path:
                        line_1 += f"{generator.configs.color.path_v}\
{generator.configs.color.wall_h}"
                    else:
                        line_1 += f"{generator.configs.color.bg_v}\
{generator.configs.color.wall_h}"
                if cell.walls["west"] == 1:
                    line_2 += f"{generator.configs.color.wall_h}"
                else:
                    if generator.grid[y][x-1].is_path:
                        line_2 += f"{generator.configs.color.path_h}"
                    else:
                        line_2 += f"{generator.configs.color.bg_h}"
                if not cell.exit and not cell.entry:
                    line_2 += f"{generator.configs.color.path_v}"
                elif cell.entry:
                    line_2 += f"{generator.configs.color.entry}"
                else:
                    line_2 += f"{generator.configs.color.exit}"

            else:
                if (cell.walls["north"] == 1):
                    line_1 += f"{generator.configs.color.wall_tw}"
                else:
                    line_1 += f"{generator.configs.color.bg_v}"
                if (cell.walls["west"] == 1):
                    line_2 += f"{generator.configs.color.wall_h}"
                else:
                    line_2 += f"{generator.configs.color.bg_h}"
                if (cell.exit):
                    line_2 += f"{generator.configs.color.exit}"
                elif (cell.entry):
                    line_2 += f"{generator.configs.color.entry}"
                else:
                    line_2 += f"{generator.configs.color.bg_v}"
                line_1 += f"{generator.configs.color.wall_h}"
        line_2 += f"{generator.configs.color.wall_h}"
        ret = ret + line_1 + "\n" + line_2 + "\n"
    bottom_line: str = ""
    for x in range(generator.configs.width):
        bottom_line += f"{generator.configs.color.wall_t}"
    bottom_line += f"{generator.configs.color.wall_h}"
    ret += bottom_line
    print(ret)


def display_options(generator: MazeGenerator,
                    color: Generator[Pallets.Pallet, None, None]) -> None:
    """
    Displays the options menu for the user to interact with the maze.

    Args:
        generator (MazeGenerator): Maze generator.
        color (Generator[Pallets.Pallet]): Color pallet generator.
    """
    print("\n==A-Maze-In==")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate colors")
    print("4. Quit")
    try:
        answer: str = input("Choice? (1-4): ")
        if (answer in ["1", "2", "3", "4", "67"]):
            match answer:
                case "1":
                    system(f"rm -rf {generator.configs.output_file}")
                    system("clear")
                    display_interface(generator, color)
                case "2":
                    system("clear")
                    if generator.show_path:
                        generator.show_path = False
                    else:
                        generator.show_path = True
                    display_maze(generator)
                    display_options(generator, color)
                case "3":
                    generator.configs.color = next(color)
                    system("clear")
                    display_maze(generator)
                    display_options(generator, color)
                case "4":
                    exit(0)
                case "67":
                    system("clear")
                    generator.build_grid()
                    random.seed(generator.configs.seed)
                    try:
                        generator.insert_67()
                    except Exception as e:
                        print(e)
                    generator.make_maze(generator.grid[0][0], [])
                    if (not generator.configs.perfect):
                        generator.unperfectify()
                    generator.get_output_file()
                    display_maze(generator)
                    display_options(generator, color)

        raise InputError("Choose a number 1-4!")
    except InputError as e:
        print(e)
        display_options(generator, color)


def choose_color() -> Generator[Pallets.Pallet, None, None]:
    """
    Infinitely generates the available color pallets.

    Returns:
        Generator[Pallets.Pallet, None, None]: Pallet generator.
    """
    colors: list[Pallets.Pallet] = [Pallets.VSCode(),
                                    Pallets.CandyStore(),
                                    Pallets.Quaquaval(),
                                    Pallets.SSalazzle(),
                                    Pallets.Brits(),
                                    Pallets.HomemDeFerro(),
                                    Pallets.Default()]
    while True:
        for color in colors:
            yield (color)


def display_interface(maze_generator: MazeGenerator, color:
                      Generator[Pallets.Pallet, None, None]) -> None:
    """
    Builds and displays the maze, and calls the options menu.

    Args:
        maze_generator (MazeGenerator): Maze generator.
        color (Generator[Pallets.Pallet]): Color pallet generator.
    """
    maze_generator.build_grid()
    start: Cell = maze_generator.grid[0][0]
    path: list[Cell] = []
    random.seed(maze_generator.configs.seed)
    maze_generator.insert_42()
    maze_generator.make_maze(start, path)
    if (not maze_generator.configs.perfect):
        maze_generator.unperfectify()
    maze_generator.get_output_file()
    display_maze(maze_generator)
    display_options(maze_generator, color)


def main(file_name: str) -> None:
    """
    Runs the main program.

    Args:
        file_name (str): Name of the configuration file.
    """
    try:
        generator: MazeGenerator = get_mazegen(file_name)
        colors: Generator[Pallets.Pallet, None, None] = choose_color()
        display_interface(generator, colors)
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Error: missing configuration file")
