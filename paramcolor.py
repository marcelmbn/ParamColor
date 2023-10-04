#!/usr/bin/env python3
"""
This file contains the functions to parse a parameter file and
to color-highlight differences between the parameters in the file.
"""

import argparse as ap

import numpy as np

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
    parser.add_argument(
        "--thresh",
        help="The threshold for the difference between two parameters.",
        type=float,
        required=False,
        default=0.001,
    )
    args = parser.parse_args()

    # Parse the parameter file
    elements, max_floats = parse_line_numbers(args.file)

    # sort the elements in ascending order
    # args.elements.sort() # currently commented out!

    parameters = {}

    # Parse the parameters
    for el in args.elements:
        par = parse_parameters(args.file, el, elements, max_floats)
        parameters[el] = par

        # print the parameter
        print(f"Parameter {el}:")
        for i in range(par.shape[0]):
            for j in range(par.shape[1]):
                print(f"{par[i, j]:10.4f}", end=" ")
            print()
        print()

    # Plot the difference between the parameters
    plot_difference(parameters, args.thresh)


def parse_line_numbers(file_path: str) -> tuple[dict, int]:
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


def parse_parameters(
    file_path: str, el: int, elements: dict, max_floats: int
) -> np.ndarray:
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

    # Initialize an empty NumPy array with double precision
    rows = upperbound - lowerbound + 1
    par = np.zeros((rows, max_floats), dtype=np.float64)

    # parse the parameters
    for i, line in enumerate(lines):
        content = line.strip().split()
        for j, val in enumerate(content):
            par[i, j] = np.float64(val)

    return par


def plot_difference(parameters: dict, thresh: float):
    """
    Plots the difference between two parameters.
    """

    if len(parameters) != 2:
        raise ValueError("Error. The number of parameters is not two.")

    # get the keys of the dictionary
    keys = list(parameters.keys())
    # get the number of rows and columns of the parameter arrays
    rows, max_floats = parameters[keys[0]].shape
    div = np.zeros((rows, max_floats), dtype=np.float64)
    # divide each parameter entry of the first parameter array by the
    # corresponding entry of the second parameter array

    # set up a for loop to iterate over the rows
    print("Ratio of the parameters:")
    for i in range(rows):
        for j in range(max_floats):
            div[i, j] = (parameters[keys[0]][i, j] + thresh) / (
                parameters[keys[1]][i, j] + thresh
            )
            print(f"{div[i, j]:10.4f}", end=" ")
        print()


if __name__ == "__main__":
    main()
