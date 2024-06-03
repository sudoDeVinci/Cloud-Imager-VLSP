from numpy import log2
from _structs import *


def linear_regression(x: list[float], y: list[float]) -> Tuple[float, float, float]:
    """
    Calculate and return the slope, intercept and linear regression coefficient
    from the x and y values passed in.
    """
    
    n = len(x)
    
    x_bar = sum(x)/n
    y_bar = sum(y)/n

    slope = sum((xi - x_bar) * (yi - y_bar) for xi, yi in zip(x,y)) / sum((xi - x_bar)**2 for xi in x)

    intercept = y_bar - slope*x_bar

    sum_xy = sum(xi*yi for xi, yi in zip(x,y))
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_sq = sum(xi**2 for xi in x)
    sum_y_sq = sum(yi**2 for yi in y)

    r_numer = n*sum_xy - sum_x*sum_y
    r_denom = ((n*sum_x_sq - sum_x**2) * (n*sum_y_sq - sum_y**2))**0.5
    r_value = r_numer/r_denom if r_denom>0 else 0
    
    
    return slope, intercept, r_value

def power_law(x: List[float], y: List[float]) -> LogEq:
    """
    Calculate power-law eqn for a given set of x and y values.
    Return in the form [slope, intercept, coefficient]
    """
    log_x = log2(x)
    log_y = log2(y)

    slope, intercept, r_value = linear_regression(log_x, log_y)

    return slope, 2**intercept, r_value


def generate_expected_data(slope: float, intercept:float, x: List[float], plot_type:PlotType, eq: str, size: int) -> Plot:
    """
    Generate expected values for a given list of values for an indepedent variable
    accordintg the the type of plot.
    """
    plot:Plot = None

    match plot_type:
        case PlotType.LINEAR:
            plot = Plot(label = f"Linear Approx. {eq}",
                        x = x,
                        type = PlotType.LINE,
                        size = size)
            plot["y"] = [(slope*x_val)+intercept for x_val in x]
            plot["approximation"] = None

        case PlotType.EXPONENTIAL:
            plot = Plot(label = f"Exp. Approx. {eq}",
                        x = x,
                        type = PlotType.LINE,
                        size = size)
            plot["y"] = [intercept*(x_val**slope) for x_val in x]
            plot["approximation"] = None

        case PlotType.LOGARITHMIC:
            plot = Plot(label = f"Log. Approx. {eq}",
                        x = x,
                        type = PlotType.LINE,
                        size = size)
            plot["y"] = [intercept*(x_val**slope) for x_val in x]
            plot["approximation"] = None

        case _:
            plot = None

    return plot