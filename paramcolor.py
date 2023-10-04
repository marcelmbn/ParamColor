#!/usr/bin/env python3
"""
This file contains the functions to parse a parameter file and
to color-highlight differences between the parameters in the file.
"""

import argparse as ap
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# from typing import Dict, List

cm = 1.0 / 2.54


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
    # parser.add_argument(
    #     "--delmaxdev",
    #     help="Delete the highest <int> deviations from the plot.",
    #     type=int,
    #     required=False,
    #     default=0,
    # )
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
    plot_difference(parameters, args.thresh)  # , args.delmaxdev


def parse_line_numbers(file_path: str) -> Tuple[Dict, int]:
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

    # DEPRECATED: max_vals is not used anymore
    # max_vals = []

    # divide each parameter entry of the first parameter array by the
    # corresponding entry of the second parameter array
    # set up a for loop to iterate over the rows
    print("Damped ratio of the parameters:")
    for i in range(rows):
        for j in range(max_floats):
            if parameters[keys[0]][i, j] == 0.0 or parameters[keys[1]][i, j] == 0.0:
                div[i, j] = np.nan
            elif (
                abs(parameters[keys[0]][i, j]) < thresh
                or abs(parameters[keys[1]][i, j]) < thresh
            ):
                if parameters[keys[0]][i, j] < parameters[keys[1]][i, j]:
                    div[i, j] = (
                        parameters[keys[0]][i, j] - parameters[keys[1]][i, j]
                    ) - thresh / (
                        abs(parameters[keys[0]][i, j])
                        + abs(parameters[keys[1]][i, j] + thresh)
                    )
                else:
                    div[i, j] = (
                        parameters[keys[0]][i, j] - parameters[keys[1]][i, j]
                    ) + thresh / (
                        abs(parameters[keys[0]][i, j])
                        + abs(parameters[keys[1]][i, j] + thresh)
                    )
            else:
                div[i, j] = (parameters[keys[0]][i, j] - parameters[keys[1]][i, j]) / (
                    abs(parameters[keys[0]][i, j]) + abs(parameters[keys[1]][i, j])
                )
            div[i, j] = div[i, j] * 100.0
            # DEPRECATED: max_vals is not used anymore
            # max_vals.append([div[i, j], i, j])
            print(f"{div[i, j]:10.4f}", end=" ")
        print()

    try:
        div[0, 8] = np.nan
    except IndexError:
        print("WARNING: No increment parameter found. Skipping increment parameter.")

    # DEPRECATED: max_vals is not used anymore
    # sort max_vals by the absolute value of each first element of the list
    # max_vals.sort(key=lambda x: abs(x[0]), reverse=True)
    # if delmaxdev is not zero, set the highest <int> deviations to zero
    # if delmaxdev != 0:
    #     for i in range(delmaxdev):
    #         div[max_vals[i][1], max_vals[i][2]] = 0.0

    # plot the ratio of the parameters as a heatmap
    plt.figure("Parameter difference", figsize=(20 * cm, 10 * cm), dpi=300)
    rdgn = sns.diverging_palette(h_neg=270, h_pos=10, s=100, l=40, sep=1, as_cmap=True)
    sns.heatmap(
        div,
        cmap=rdgn,
        center=0.00,
        annot=True,
        fmt=".1f",
        linewidths=1,
        linecolor="black",
        cbar=True,
        vmax=75,
        vmin=-75,
    )

    # set ticks such that they start from 1 and end at the number of rows and columns
    plt.xticks(np.arange(0.5, max_floats, 1), np.arange(1, max_floats + 1, 1))
    plt.yticks(np.arange(0.5, rows, 1), np.arange(1, rows + 1, 1))

    plt.title(
        "Ratio of the parameters for elements "
        + str(keys[0])
        + " and "
        + str(keys[1])
        + " in % [ "
        + str(keys[0])
        + " / "
        + str(keys[1])
        + "; 0 % => equal]",
    )

    plt.show()


if __name__ == "__main__":
    main()
