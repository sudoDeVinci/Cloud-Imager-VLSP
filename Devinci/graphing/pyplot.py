import sys
import json
import toml
import argparse
from os import path
from _plotters import *


def _load_json(file_path: str) -> Dict[str , Any] | None:
    """
    Attempt to load JSON file data as a dictionary.
    """
    data = None
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if not data:
                return None
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
        return None
    
    return data

def _load_toml(file_path:str) -> Dict[str , Any] | None:
    """ 
    Attempt to load a toml file as a dictionary.
    """
    toml_data = None
    try:
        with open(file_path, 'r') as file:
            toml_data = toml.load(file)
            if not toml_data:
                return None
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except toml.TomlDecodeError as e:
        print(f"Error decoding TOML file: {e}")
        return None

    return toml_data


def __same_dimensions(list1: List|object, list2: List|object) -> bool:
    """
    Recursively check if passed in lists have the same dimensionality.
    """
    if isinstance(list1, list) and isinstance(list2, list):
        try:
            if len(list1) != len(list2): return False
        except Exception as e:
            print(f"Couldn't check dimensionality: {e}")
            return False
        for sublist1, sublist2 in zip(list1, list2):
            if not __same_dimensions(sublist1, sublist2):
                return False
        return True
    
    else:
        return False

def _json_to_Plot(plot: dict) -> Plot:
    """
    Convert a graph plot dictionary to a Plot object.
    """
    return Plot(label = plot['label'],
                x = plot['x'],
                y = plot['y'],
                type = PlotType.match(plot['type']),
                size = plot['size']
            )

def _json_to_Graph(graph: dict) -> Graph:
    """
    Convert the graph data Dictionary to a Graph object.
    """
    outGraph = Graph(name = graph['name'],
                    title = graph['title'],
                    x_label = graph['x_label'],
                    y_label = graph['y_label'],
                    fontsize=graph['fontsize'])
    
    outGraph['plots'] = [_json_to_Plot(graph['plots'][index]) for index in range(len(graph['plots']))]
    return outGraph

def graph(graph: Graph, graph_path: str = "src/graphs/test.png") -> None:
    """
    Renders and saves a graph based on the provided Graph object and path.

    This function takes a Graph object containing all necessary data for plotting,
    including labels, titles, and plot data. It then renders the graph using matplotlib
    and saves it to the specified path. The fontsize for the graph elements is adjusted
    based on the Graph object's fontsize attribute, with a default and minimum value set to 10.

    Parameters:
    - graph: Graph object containing the data and settings for the graph to be plotted.
    - graph_path: str, optional. The file path where the graph image will be saved. Defaults to "src/graphs/test.png".

    Returns:
    - None. The graph is saved to the specified file path.
    """
    # Set the fontsize, ensuring it is not below 10
    fs = graph['fontsize'] if graph['fontsize'] is not None else 10
    fs = graph['fontsize'] if graph['fontsize'] >= 10 else 10
    
    # Initialize the figure and axis for the plot
    fig, ax  = plt.subplots()
    fig.set_figheight(fs)
    fig.set_figwidth(fs*1.5)

    # Plot each plot in the graph
    for plot in graph["plots"]:
        plotFunc = get_plotter(plot)
        plotFunc(ax, plot)
    
    # Set the labels and title with the specified fontsize
    plt.xlabel(f"\n{graph['x_label']}\n", fontsize = fs)
    plt.ylabel(f"{graph['y_label']}\n", fontsize = fs)
    plt.title(f"{graph['title']}\n", fontsize = fs*1.50)
    plt.xticks(fontsize = fs)
    plt.yticks(fontsize = fs)
    
    # Configure and display the legend
    ax.legend(loc='upper left',
          fancybox=True, shadow=True, ncol=2, fontsize= (fs-2) if fs >= 12 else 8)

    # Save the rendered graph to the specified path
    plt.savefig(graph_path)
