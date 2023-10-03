#!/usr/bin/env python3
"""
This file contains the functions to parse a parameter file and
to color-highlight differences between the parameters in the file.
"""

import argparse as ap


def main():
    """
    Main function working as a driver for the program.
    """

    # Parse the command line arguments
    parser = ap.ArgumentParser(
        description="Color-highlight differences in parameter files."
    )
    parser.add_argument(
        "--file", help="The parameter file to be parsed.", type=str, required=True
    )
    args = parser.parse_args()

    # Parse the parameter file
    elements, elements_lineno = parse_line_numbers(args.file)

    for i, element in enumerate(elements):
        print(element, elements_lineno[i])


def parse_line_numbers(file_path) -> tuple[list, list]:
    """
    Parses a parameter file and returns a dictionary with the parameters.
    """
    with open(file_path, encoding="UTF-8") as file:
        lines = file.readlines()

    elements = []
    element_line_numbers = []

    k = 0
    for line in lines:
        content = line.strip().split()
        # if the line starts with an integer, it is the start of a new parameter
        isint = False
        isfloat = False
        try:
            intval = int(content[0])
            if str(intval) == content[0]:
                isint = True
        except ValueError:
            try:
                float(content[0])
                isfloat = True
            except ValueError:
                pass
        if isint:
            k += 1
            elements.append(int(content[0]))
            element_line_numbers.append(lines.index(line))
        # Else if the line contains a float (and not an integer!), just continue
        elif isfloat:
            continue
        # Else if the line is completely empty, it is the end of the file
        elif content[0] == "":
            break
        else:
            print(content)
            raise ValueError("Error. The line does not start with an integer or float.")

    return elements, element_line_numbers


if __name__ == "__main__":
    main()
