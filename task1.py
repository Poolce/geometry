from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQGLViewer import *
from OpenGL.GL import *

from math import sin, cos, sqrt, pi
import numpy as np

from utils import Point


class VertexGenerator:
    @staticmethod
    def get_vertex() -> list[Point]:
        pass


class CubeVertexGenerator(VertexGenerator):
    @staticmethod
    def get_vertex() -> list[Point]:
        stride = 0.33
        n_ = int(1 / stride) + 1
        res = list()
        for x in range(n_):
            for y in range(n_):
                for z in range(n_):
                    res.append(Point(stride * x,
                                     stride * y,
                                     stride * z))
        return res


class FillCubeVertexGenerator(VertexGenerator):
    @staticmethod
    def get_vertex() -> list[Point]:
        res = list()
        n = 20000
        l = 1
        for i in range(n):
            x = np.random.uniform(0, l)
            y = np.random.uniform(0, l)
            z = np.random.uniform(0, l)
            res.append(Point(x, y, z))
        return res

class FillSphereVertexGenerator(VertexGenerator):
    @staticmethod
    def get_vertex() -> list[Point]:
        res = list()
        n = 20000
        r = 1
        for i in range(n):
            r = np.random.uniform(0, r) ** (1 / 3)
            phi = np.random.uniform(0, np.pi)
            theta = np.random.uniform(0, 2 * np.pi)
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            res.append(Point(x, y, z))
        return res

class SphereVertexGenerator(VertexGenerator):
    @staticmethod
    def get_vertex() -> list[Point]:
        n = 1000
        phi = (1 + sqrt(5)) / 2
        res = list()
        for i in range(n):
            theta = 2 * pi * i / phi
            z = 1 - (2 * i) / (n - 1)
            r = sqrt(1 - z ** 2)
            x = r * cos(theta)
            y = r * sin(theta)
            res.append(Point(x, y, z))
        return res


class Viewer(QGLViewer):
    def __init__(self, parent = None):
        QGLViewer.__init__(self,parent)
        self.points = []
        self.point_size = 5
        self.figure_id = -1
        self.figures = [CubeVertexGenerator,
                        SphereVertexGenerator,
                        FillCubeVertexGenerator,
                        FillSphereVertexGenerator]

    def draw(self):
        glPointSize(self.point_size)
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.0 , 0.0)
        for p_ in self.points:
            glVertex3f(p_.x, p_.y, p_.z)
        glEnd()

    def keyPressEvent(self, e):
        modifiers = e.modifiers()
        if (e.key() == Qt.Key_C):
            self.clear()
        elif (e.key() == Qt.Key_N):
            self.change_figure()


    def change_figure(self):
        if self.figure_id == len(self.figures) - 1:
            self.figure_id = 0
        else:
            self.figure_id += 1
        self.points = self.figures[self.figure_id].get_vertex()
        self.update()

    def clear(self):
        self.points = list()
        self.update()
        self.figure_id = -1





def main():
    qapp = QApplication([])
    viewer = Viewer()
    viewer.show()
    qapp.exec_()

if __name__ == '__main__':
    main()