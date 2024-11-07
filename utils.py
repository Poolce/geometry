import numpy as np

from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

@dataclass
class Line:
    start: Point
    end: Point

@dataclass
class Triangle:
    p1: Point
    p2: Point
    p3: Point

def gen_random_points(n: int, is_2d_: bool = False) -> list[Point]:
    res = list()
    for i in range(n):
        x = np.random.uniform(-0.5, 0.5)
        y = np.random.uniform(-0.5, 0.5)
        z = np.random.uniform(-0.5, 0.5)
        if is_2d_:
            z = 0
        res.append(Point(x, y, z))
    return res