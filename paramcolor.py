#!/usr/bin/env python3
"""
This file contains the functions to parse a parameter file and
to color-highlight differences between the parameters in the file.
"""

import argparse as ap

# from typing import Dict, List


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
    parser.add_argument(
        "--elements",
        help="The elements to be compared.",
        nargs="+",
        type=int,
        required=True,
    )
    args = parser.parse_args()

    # Parse the parameter file
    elements, max_floats = parse_line_numbers(args.file)

    # for key, value in elements.items():
    #     print (key, value)

    # Parse the parameters
    for el in args.elements:
        parse_parameters(args.file, el, elements, max_floats)


def parse_line_numbers(file_path) -> tuple[dict, int]:
    """
    Parses a parameter file and returns a dictionary with the parameters.
    """
    with open(file_path, encoding="UTF-8") as file:
        lines = file.readlines()

    elements = {}
    max_floats = 0
    glob_var = True
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
                glob_var = False
        except ValueError:
            try:
                float(content[0])
                isfloat = True
            except ValueError:
                pass
        if isint:
            k += 1
            elements[int(content[0])] = lines.index(line)
        # Else if the line contains a float (and not an integer!), just continue
        elif isfloat:
            # count the number of floats in the line
            if not glob_var:
                nfloats = len(content)
                if nfloats > max_floats:
                    max_floats = nfloats
            continue
        # Else if the line is completely empty, it is the end of the file
        elif content[0] == "":
            break
        else:
            print(content)
            raise ValueError("Error. The line does not start with an integer or float.")

    return elements, max_floats


def parse_parameters(file_path, el, elements, max_floats):
    """
    Parses a parameter file and returns a dictionary with the parameters.
    """

    try:
        lowerbound = elements[el] + 1
        upperbound = elements[el + 1] - 1
    except IndexError as exc:
        raise IndexError("Error. The element is not in the parameter file.") from exc

    with open(file_path, encoding="UTF-8") as file:
        for i in range(lowerbound):
            next(file)
        lines = []
        for i in range(upperbound + 1 - lowerbound):
            lines.append(next(file))

    print(lines)

    return None


if __name__ == "__main__":
    main()
