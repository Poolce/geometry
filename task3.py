from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQGLViewer import *
from OpenGL.GL import *

import numpy as np

from CGAL.CGAL_Kernel import Point_2, Point_3
from CGAL import CGAL_Convex_hull_2, CGAL_Convex_hull_3
from CGAL.CGAL_Polyhedron_3 import Polyhedron_3

from utils import Line, Point, gen_random_points

from dataclasses import dataclass

def clamp(value, minval, maxval):
    return max(minval, min(value, maxval))

class BSpline:
    def __init__(self, reference_points, discrete_num = 10, closed = True , is_2_degree = True):
        self.points = reference_points
        self.d_num = int(discrete_num)
        self.closed = closed
        self.is_2_degree = is_2_degree

        self.coefs = []
        for i in range(self.d_num):
            if self.is_2_degree:
                spline_segm_coef = self.calc_spline2_coef(i/self.d_num)
            else:
                spline_segm_coef = self.calc_spline3_coef(i/self.d_num)
            self.coefs.append(spline_segm_coef)

    def calc_spline3_coef(self, t):
        coefs = [0,0,0,0]
        coefs[0] = (1 - t)**3 / 6
        coefs[1] = (3*t**3 - 6*t**2 + 4) / 6
        coefs[2] = (-3.0*t**3 + 3*t**2 + 3*t + 1) / 6
        coefs[3] = t**3 / 6
        return coefs

    def calc_spline2_coef(self, t):
        coefs = [0,0,0]
        coefs[0] = (1 - t)**2 / 2
        coefs[1] = (-2*t**2+2*t+1) / 2
        coefs[2] = (t**2) / 2
        return coefs
    
    def draw_spline_curve(self):
        if not self.closed:     
            segmentsCount = len(self.points) - 1
        else:
            segmentsCount = len(self.points)
        res_points = []
        for i in range(segmentsCount):
            if self.is_2_degree:
                res_points.extend(self.draw_glvertex_for_one_segment_of_spline2(i))
            else:
                res_points.extend(self.draw_glvertex_for_one_segment_of_spline3(i))
        return res_points
            
    def draw_glvertex_for_one_segment_of_spline3(self, segment_id):
        pNum = len(self.points)
        if not self.closed:
            p0 = clamp(segment_id - 1, 0, pNum - 1)
            p1 = clamp(segment_id, 0, pNum - 1)
            p2 = clamp(segment_id + 1, 0, pNum - 1)
            p3 = clamp(segment_id + 2, 0, pNum - 1)
        else:
            p0 = (segment_id - 1 + pNum) % pNum
            p1 = (segment_id + pNum) % pNum
            p2 = (segment_id + 1 + pNum) % pNum
            p3 = (segment_id + 2 + pNum) % pNum
        res = []
        for i in range(self.d_num):
            x = self.coefs[i][0] * self.points[p0].x   \
                + self.coefs[i][1] * self.points[p1].x \
                + self.coefs[i][2] * self.points[p2].x \
                + self.coefs[i][3] * self.points[p3].x 
            y = self.coefs[i][0] * self.points[p0].y   \
                + self.coefs[i][1] * self.points[p1].y \
                + self.coefs[i][2] * self.points[p2].y \
                + self.coefs[i][3] * self.points[p3].y
            z = self.coefs[i][0] * self.points[p0].z   \
                + self.coefs[i][1] * self.points[p1].z \
                + self.coefs[i][2] * self.points[p2].z \
                + self.coefs[i][3] * self.points[p3].z
            res.append(Point(x,y,z))
        return res

    def draw_glvertex_for_one_segment_of_spline2(self, segment_id):
        pNum = len(self.points)
        if not self.closed:
            p0 = clamp(segment_id - 1, 0, pNum - 1)
            p1 = clamp(segment_id, 0, pNum - 1)
            p2 = clamp(segment_id + 1, 0, pNum - 1)
        else:
            p0 = (segment_id - 1 + pNum) % pNum
            p1 = (segment_id + pNum) % pNum
            p2 = (segment_id + 1 + pNum) % pNum
        
        res = []
        for i in range(self.d_num):
            x = self.coefs[i][0] *   self.points[p0].x \
                + self.coefs[i][1] * self.points[p1].x \
                + self.coefs[i][2] * self.points[p2].x
            y = self.coefs[i][0] *   self.points[p0].y \
                + self.coefs[i][1] * self.points[p1].y \
                + self.coefs[i][2] * self.points[p2].y
            z = self.coefs[i][0] *   self.points[p0].z \
                + self.coefs[i][1] * self.points[p1].z \
                + self.coefs[i][2] * self.points[p2].z 
            res.append(Point(x,y,z))
        return res

@dataclass
class PointHandler:
    _id : int
    label : int
    sliderx : int
    slidery : int
    sliderz : int
    remover : int

class InputDialog(QDialog):
    def __init__(self, points, parent=None):
        super(InputDialog, self).__init__(parent)
        self.setWindowTitle("Controll Mode")
        self.setGeometry(100, 100, 500, 800)
        self.point_wigets = []
        self.layout = QVBoxLayout(self)

        for i in points:
            id = len(self.point_wigets)
            label = QLabel(f"point_{id}:", self)
            sliderx = self.get_slider(i.x * 100)
            slidery = self.get_slider(i.y * 100)
            sliderz = self.get_slider(i.z * 100)
            remover = QPushButton("Remove point", self)
            remover.clicked.connect(lambda _:self.remove_point(id))
            self.point_wigets.append(PointHandler(id,
                                                  label,
                                                  sliderx,
                                                  slidery,
                                                  sliderz,
                                                  remover))
        self.draw()


    def draw(self):
        self.remove_all_widgets()
        self.add = QPushButton("Add point", self)
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
        
        self.add.clicked.connect(self.add_point)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)
        for p in self.point_wigets:
            self.layout.addWidget(p.label)
            self.layout.addWidget(p.sliderx)
            self.layout.addWidget(p.slidery)
            self.layout.addWidget(p.sliderz)
            self.layout.addWidget(p.remover)

        self.layout.addWidget(self.add)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.cancel_button)


    def add_point(self):
        id = len(self.point_wigets)
        label = QLabel(f"point_{id}:", self)
        sliderx = self.get_slider()
        slidery = self.get_slider()
        sliderz = self.get_slider()
        remover = QPushButton("Remove point", self)
        remover.clicked.connect(lambda : self.remove_point(id))
        self.point_wigets.append(PointHandler(id, label, sliderx, slidery, sliderz, remover))
        self.draw()

    def get_slider(self, default = 0):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(-50)
        slider.setMaximum(50)
        slider.setValue(default)
        return slider

    def remove_all_widgets(self):
        for i in reversed(range(self.layout.count())): 
            widgetToRemove = self.layout.itemAt(i).widget()
            self.layout.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)

    def get_points(self):
        return [Point(i.sliderx.value() / 100, 
                      i.slidery.value() / 100,
                      i.sliderz.value() / 100,)
                      for i in self.point_wigets]

    def remove_point(self, e):
        print(e)
        self.point_wigets = list(filter(lambda x : x._id != e, self.point_wigets))
        self.draw()


class Viewer(QGLViewer):
    def __init__(self, parent = None):
        QGLViewer.__init__(self, parent)
        self.setWindowTitle("2d spline")
        self.points = []
        self.spline_points = []
        self.point_size = 5
        self.closed_mode = True
        self.degree_mode = True

    def draw(self):
        glPointSize(self.point_size)
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.0 , 0.0)
        for p_ in self.points:
            glVertex3f(p_.x, p_.y, p_.z)
        glEnd()

        if not self.closed_mode:     
            glBegin(GL_LINE_STRIP)
        else:
            glBegin(GL_LINE_LOOP)
        for p_ in self.spline_points:
            glVertex3f(p_.x, p_.y, p_.z)
        glEnd()
    
    def controll_mode(self):
        dialog = InputDialog(self.points)
        if dialog.exec_() == QDialog.Accepted:
            self.points = dialog.get_points()

    def draw_spline(self):
        spline = BSpline(self.points, 10, self.closed_mode, self.degree_mode)
        self.spline_points = spline.draw_spline_curve()

    def keyPressEvent(self, e):
        modifiers = e.modifiers()
        if (e.key() == Qt.Key_C):
            self.clear()
        if (e.key() == Qt.Key_R):
            self.points = gen_random_points(5, False)
        if (e.key() == Qt.Key_X):
            self.clear_spline()
        if (e.key() == Qt.Key_P):
            self.controll_mode()
        if (e.key() == Qt.Key_D):
            self.degree_mode = not self.degree_mode
            if self.degree_mode:
                self.setWindowTitle("2d spline")
            else:
                self.setWindowTitle("3d spline")
        if (e.key() == Qt.Key_S):
            self.closed_mode = not self.closed_mode
        self.draw_spline()
        self.update()

    def clear(self):
        self.spline_points = list()
        self.points = list()

    def clear_spline(self):
        self.spline_points = list()



def main():
    qapp = QApplication([])
    viewer = Viewer()
    viewer.show()
    qapp.exec_()

if __name__ == '__main__':
    main()