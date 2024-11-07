from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQGLViewer import *
from OpenGL.GL import *

import numpy as np

from CGAL.CGAL_Kernel import Point_2, Point_3
from CGAL import CGAL_Convex_hull_2, CGAL_Convex_hull_3
from CGAL.CGAL_Polyhedron_3 import Polyhedron_3

from utils import Line, Point, gen_random_points


def convex_hull_2d(points: list[Point]):
    input_ = [Point_2(p.x, p.y) for p in points]
    res = []
    CGAL_Convex_hull_2.convex_hull_2(input_, res)
    return [Point(p.x(), p.y(), 0) for p in res]

def convex_hull_3d(points: list[Point]):
    input_ = [Point_3(p.x, p.y, p.z) for p in points]
    hull = Polyhedron_3()
    CGAL_Convex_hull_3.convex_hull_3(input_, hull)
    res = list()

    for facet in hull.facets():
        halfedge = facet.halfedge()
        triangle = []
        for _ in range(3):
            vertex = halfedge.vertex()
            triangle.append(Point(vertex.point().x(),
                                  vertex.point().y(),
                                  vertex.point().z()))
            halfedge = halfedge.next()
        res.extend(triangle)
    return res


class Viewer(QGLViewer):
    def __init__(self, parent = None):
        QGLViewer.__init__(self, parent)
        self.points = []
        self.hull = []
        self.point_size = 5
        self.is_2d_mode = True

    def draw_2d_hull(self):
        glBegin(GL_LINES)
        glColor3f(0.0, 1.0 , 0.0)
        seg_length = len(self.hull)
        if seg_length < 2:
            glEnd()
            return
        p_id = 0
        while p_id < seg_length - 1:
            glVertex3f(self.hull[p_id].x, self.hull[p_id].y, self.hull[p_id].z)
            glVertex3f(self.hull[p_id + 1].x, self.hull[p_id + 1].y, self.hull[p_id + 1].z)
            p_id += 1
        glVertex3f(self.hull[p_id].x, self.hull[p_id].y, self.hull[p_id].z)
        glVertex3f(self.hull[0].x, self.hull[0].y, self.hull[0].z)
        glEnd()
    
    def draw_3d_hull(self):
        glBegin(GL_TRIANGLES)
        glColor3f(0.0, 1.0 , 0.0)
        seg_length = len(self.hull)
        if seg_length < 2:
            glEnd()
            return
        p_id = 0
        while p_id < seg_length - 2:
            glVertex3f(self.hull[p_id].x, self.hull[p_id].y, self.hull[p_id].z)
            glVertex3f(self.hull[p_id + 1].x, self.hull[p_id + 1].y, self.hull[p_id + 1].z)
            glVertex3f(self.hull[p_id + 2].x, self.hull[p_id + 2].y, self.hull[p_id + 2].z)
            p_id += 3
        glEnd()

    def draw(self):
        glPointSize(self.point_size)
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.0 , 0.0)
        for p_ in self.points:
            glVertex3f(p_.x, p_.y, p_.z)
        glEnd()

        if self.is_2d_mode:
            self.draw_2d_hull()
        else:
            self.draw_3d_hull()

    def draw_hull(self):
        if self.is_2d_mode:
            self.hull = convex_hull_2d(self.points)
        else:
            self.hull = convex_hull_3d(self.points)        

    def keyPressEvent(self, e):
        modifiers = e.modifiers()
        if (e.key() == Qt.Key_C):
            self.clear()
        if (e.key() == Qt.Key_G):
            self.hull = list()
            self.points = gen_random_points(35, self.is_2d_mode)
        if (e.key() == Qt.Key_H):
            self.draw_hull()
        if (e.key() == Qt.Key_M):
            self.is_2d_mode = not self.is_2d_mode
        self.update()


    def clear(self):
        self.points = list()
        self.hull = list()


def main():
    qapp = QApplication([])
    viewer = Viewer()
    viewer.show()
    qapp.exec_()

if __name__ == '__main__':
    main()