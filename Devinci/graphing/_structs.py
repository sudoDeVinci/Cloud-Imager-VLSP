from typing import List, Sequence, Tuple, TypedDict, Dict, NamedTuple, Any, Iterable, TypeVar, TypeAlias, Optional, Self, Callable
from numpy import log2
from abc import ABC, abstractmethod
from enum import Enum
from matplotlib import pyplot as plt
import functools

"""
Tuple of colour-marker pairs for graphing.
"""
COLOUR_MARKERS:Tuple[Tuple[str,str]] = (
    ('b', 'o'),  # blue, circle
    ('g', '^'),  # green, triangle up
    ('r', 's'),  # red, square
    ('c', 'D'),  # cyan, diamond
    ('m', 'p'),  # magenta, pentagon
    ('y', '*'),  # yellow, star
    ('k', 'x'),  # black, x
    ('#FFA07A', 'H'),  # LightSalmon, hexagon1
    ('#20B2AA', 'v'),  # LightSeaGreen, triangle down
    ('#8A2BE2', '8'),  # BlueViolet, octagon
    ('#7FFF00', 'D'),  # Chartreuse, diamond
    ('#FF4500', 'h'),  # OrangeRed, hexagon2
    ('#9932CC', 'p'),  # DarkOrchid, pentagon
    ('#3CB371', 'X'),  # MediumSeaGreen, x
    ('#40E0D0', 'd'),  # Turquoise, thin_diamond
    ('#FFD700', '+'),  # Gold, plus
    ('#DC143C', '|'),  # Crimson, vline
    ('#800080', '_')   # Purple, hline
)


class PlotType(Enum):
    """
    Graph typing enum, will return NONE if non-present type passed in.
    """
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    SCATTER  = "scatter"
    LINE = "line"
    NONE = "None"

    @classmethod
    @functools.lru_cache(maxsize=None)
    def __contains__(cls, value: Self):
        if cls.match(value) is cls.NONE: return False
        return True
    
    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, graph:str):
        """
        Match input string to PlotType.
        """
        graph = graph.lower()
        for _, PlotType in cls.__members__.items():
            if graph == PlotType.value: return PlotType
        return cls.NONE
    @classmethod
    def _missing_(cls, value: Any):
        return cls.NONE



class Equation(ABC):
    """
    Representation of an equation of an line or curve given by the 
    slope, intercept and r-value.
    """
    __slots__ = ('_slope', '_intercept', '_r_value','_equation')
    _equation: str
    _r_value: float
    _intercept: float
    _slope: float

    def __init__(self, r_value, intercept, slope) -> None:
        self._r_value = r_value
        self._intercept = intercept
        self._slope = slope
        self._get_eq()

    @abstractmethod
    def _get_eq(self) -> Self:
        ...
    
    @property
    def equation(self) -> str:
        return self._equation
    
    @property
    def r_value(self) -> float:
        return self._r_value
    
    @property
    def intercept(self) -> float:
        return self._intercept
    
    @property
    def slope(self) -> float:
        return self._slope
    
    def __repr__(self) -> str:
        return self._equation

class LineEq(Equation):
    """
    Representation of the equation of a line.
    """
    def _get_eq(self):
        self._equation = fr'$y={self._slope:.4f} \cdot x + {self._intercept:.4f}$' + '\n' + f'r: {self._r_value:.3f}'

class ExpEq(Equation):
    """
    Representation of the equation of an exponential.
    """
    def _get_eq(self):
        self._equation = fr'$y={self._intercept:.4f} \cdot x^{{ {self._slope:.4f} }}$' + '\n' + f'r: {self._r_value:.3f}\n'

class LogEq(Equation):
    """
    Representation of the equation of a Logarithm.
    """
    def _get_eq(self):
        self._equation =  fr'$y={self._intercept:.4f} \cdot \log_2({self._slope:.4f} \cdot x)$' + '\n' + f'r: {self._r_value:.3f}\n'


class Plot(TypedDict, total = False):
    """
    Representation of a labelled plot.
    """
    label: str
    x: List[float]
    y: List[float]
    type: PlotType
    size: int
    approximation: Optional[Equation]

class Graph(TypedDict, total = False):
    """
    Representation of a named graph containing many plots.
    """
    name: str
    title: str
    x_label: str
    y_label: str
    fontsize: int
    plots: List[Plot]
