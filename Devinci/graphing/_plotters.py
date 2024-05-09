from matplotlib.axes import Axes
from _plotmath import *

def get_graph_data(inPlot: Plot) -> Plot|None:
    """
    Get the approximate function and Plot for a set off data as a tuple.
    """

    equation:Equation = None
    x_coords = inPlot["x"]
    y_coords = inPlot["y"]
    type = inPlot["type"]
    
    match type:
        case PlotType.LINEAR:
            slope, intercept, r_value = linear_regression(x_coords, y_coords)
            equation = LineEq(r_value, intercept, slope)

        case PlotType.EXPONENTIAL:
            slope, intercept, r_value = power_law(x_coords, y_coords)
            equation = ExpEq(r_value, intercept, slope)
            
        case PlotType.LOGARITHMIC:
            slope, intercept, r_value = power_law(x_coords,y_coords)
            equation = LogEq(r_value, intercept, slope)

        case _:
            equation = None
            slope = None
            intercept = None

    # Generate expected values
    expected_data = generate_expected_data(equation.slope, equation.intercept, x_coords, type, equation.equation, inPlot['size']//10) if equation is not None else None
    
    return expected_data

def get_plotter(plot:Plot) -> Callable:
    """
    Return the plotting function corresponding to the graph type.
    """
    plotFunc:Callable

    match plot['type']:
        case PlotType.LINEAR | PlotType.LOGARITHMIC | PlotType.EXPONENTIAL:
            plotFunc = _approximated
        case PlotType.LINE:
            plotFunc = _line
        case PlotType.SCATTER:
            plotFunc = _scatter
        case PlotType.NONE:
            plotFunc = _do_nothing
    
    return plotFunc


def _line(ax: Axes, plot: Plot) -> None:
    """
    Plot a line and give it a label.
    """
    l:str = f"{plot['label']}" if plot['label'] != "None" else f"Plot data"
    ax.plot(plot['x'], plot['y'], label = l, linewidth = str(plot['size']))


def _scatter(ax: Axes,plot: Plot) -> None:
    """
    Plot a scatter plot and give it a label.
    """
    
    l:str = f"{plot['label']}" if plot['label'] != "None" else f"Plot data"
    ax.scatter(plot['x'], plot['y'], s = plot['size']*2, alpha = 0.8, label = l)


def _approximated(ax: Axes,plot: Plot) -> None:
    """
    Plot scatterpoints, then find and plot the approximated equation of them.
    """

    expected_plot = get_graph_data(plot)

    _scatter(ax, plot)
    if expected_plot is not None:
        expected_plot["label"] = f"{plot['label']} {expected_plot['label']}"
        _line(ax, expected_plot)

def _do_nothing(ax: Axes, plot: Plot) -> None:
    """
    Do absolutely nothing.
    """
    pass