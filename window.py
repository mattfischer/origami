from PySide import QtCore, QtGui
from PySide.QtCore import Qt

from window_ui import Ui_MainWindow

import math

class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.canvas.paintEvent = self.on_canvas_paint_event
        self.ui.canvas.mouseReleaseEvent = self.on_canvas_mouse_release_event
        self.ui.canvas.mouseMoveEvent = self.on_canvas_mouse_move_event
        self.ui.scrollArea.resizeEvent = self.on_scroll_area_resize_event

        self.ui.actionZoomIn.triggered.connect(self.on_action_zoom_in)
        self.ui.actionZoomOut.triggered.connect(self.on_action_zoom_out)
        self.ui.actionPoints.triggered.connect(self.on_action_points)
        self.ui.actionPointPoint.triggered.connect(self.on_action_point_point)
        self.ui.actionLineLine.triggered.connect(self.on_action_line_line)

        self.ui.canvas.setMouseTracking(True)

        self.zoom = 0.9
        self.points = [(0, 0), (0, 1), (1, 1), (1, 0)]
        self.highlight_point = None
        self.selected_points = []
        self.highlight_segment = None
        self.selected_segments = []
        self.lines = []
        self.update_actions()

    def point_to_window(self, point):
        size = min(self.ui.scrollArea.width(), self.ui.scrollArea.height()) * self.zoom
        margin = 10
        return (margin + point[0] * (size - 2 * margin), margin + point[1] * (size - 2 * margin))

    def window_to_point(self, point):
        size = min(self.ui.scrollArea.width(), self.ui.scrollArea.height()) * self.zoom
        margin = 10
        return ((point[0] - margin) / (size - 2 * margin), (point[1] - margin) / (size - 2 * margin))

    def find_point_near(self, mouse_point):
        found_point = None
        size = min(self.ui.scrollArea.width(), self.ui.scrollArea.height()) * self.zoom
        threshold = 10 / size
        for point in self.points:
            dx = mouse_point[0] - point[0]
            dy = mouse_point[1] - point[1]
            distance = dx * dx + dy * dy
            if distance <= threshold * threshold:
                found_point = point
                break
        return found_point

    def find_segment_near(self, mouse_point):
        found_segment = None
        size = min(self.ui.scrollArea.width(), self.ui.scrollArea.height()) * self.zoom
        threshold = 10 / size
        last_point = self.points[-1]
        for point in self.points:
            a = last_point[1] - point[1]
            b = point[0] - last_point[0]
            c = a * point[0] + b * point[1]

            d = a * mouse_point[0] + b * mouse_point[1]
            if abs(d - c) <= threshold:
                length = a * a + b * b
                dx1 = mouse_point[0] - point[0]
                dy1 = mouse_point[1] - point[1]
                dx2 = mouse_point[0] - last_point[0]
                dy2 = mouse_point[1] - last_point[1]
                if dx1 * dx1 + dy1 * dy1 < length and dx2 * dx2 + dy2 * dy2 < length:
                    found_segment = (last_point, point)
                break
            last_point = point
        return found_segment

    def on_canvas_paint_event(self, event):
        painter = QtGui.QPainter(self.ui.canvas)
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        pen.setCosmetic(True)
        brush = QtGui.QBrush(QtGui.QColor(0xFF, 0xFF, 0x80))
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        draw_points = [QtCore.QPoint(*self.point_to_window(point)) for point in self.points]
        painter.drawPolygon(draw_points)

        if self.highlight_segment:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
            painter.setPen(pen)
            draw_points = [QtCore.QPoint(*self.point_to_window(point)) for point in self.highlight_segment]
            painter.drawLine(*draw_points)

        idx = 0
        for segment in self.selected_segments:
            colors = [(0xFF, 0x80, 0x00), (0x80, 0x40, 0x00)]
            pen = QtGui.QPen(QtGui.QColor(*colors[idx]), 3, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
            painter.setPen(pen)
            draw_points = [QtCore.QPoint(*self.point_to_window(point)) for point in segment]
            painter.drawLine(*draw_points)
            idx += 1

        if self.highlight_point:
            brush = QtGui.QBrush(QtGui.QColor(0x00, 0x00, 0x00))
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QtCore.QPoint(*self.point_to_window(self.highlight_point)), 3, 3)

        idx = 0
        for point in self.selected_points:
            colors = [(0x00, 0xFF, 0x80), (0x00, 0x80, 0x40)]
            brush = QtGui.QBrush(QtGui.QColor(*colors[idx]))
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QtCore.QPoint(*self.point_to_window(point)), 3, 3)
            idx += 1

        pen = QtGui.QPen(QtGui.QColor(0x80, 0x80, 0x80), 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        painter.setPen(pen)
        for line in self.lines:
            if abs(line[0]) > abs(line[1]):
                x0 = line[2] / line[0]
                x1 = (line[2] - line[1]) / line[0]
                points = [(x0, 0), (x1, 1)]
            else:
                y0 = line[2] / line[1]
                y1 = (line[2] - line[0]) / line[1]
                points = [(0, y0), (1, y1)]
            draw_points = [QtCore.QPoint(*self.point_to_window(point)) for point in points]
            painter.drawLine(*draw_points)

    def on_canvas_mouse_release_event(self, event):
        mouse_point = self.window_to_point((event.pos().x(), event.pos().y()))
        selected_point = self.find_point_near(mouse_point)
        if selected_point:
            if selected_point in self.selected_points:
                self.selected_points.remove(selected_point)
            else:
                if len(self.selected_points) < 2:
                    self.selected_points.append(selected_point)
                    self.highlight_point = None
        else:
            selected_segment = self.find_segment_near(mouse_point)
            if selected_segment:
                if selected_segment in self.selected_segments:
                    self.selected_segments.remove(selected_segment)
                else:
                    if len(self.selected_segments) < 2:
                        self.selected_segments.append(selected_segment)
                        self.highlight_segment = None
            else:
                self.selected_points.clear()
                self.selected_segments.clear()
        self.ui.canvas.update()
        self.update_actions()

    def on_canvas_mouse_move_event(self, event):
        mouse_point = self.window_to_point((event.pos().x(), event.pos().y()))
        highlight_point = self.find_point_near(mouse_point)
        if highlight_point in self.selected_points or len(self.selected_points) == 2:
            highlight_point = None

        if highlight_point:
            highlight_segment = None
        else:
            highlight_segment = self.find_segment_near(mouse_point)
            if highlight_segment in self.selected_segments or len(self.selected_segments) == 2:
                highlight_segment = None

        if highlight_point != self.highlight_point:
            self.highlight_point = highlight_point
            self.ui.canvas.update()

        if highlight_segment != self.highlight_segment:
            self.highlight_segment = highlight_segment
            self.ui.canvas.update()

    def on_scroll_area_resize_event(self, event):
        self.resize_canvas()

    def resize_canvas(self):
        size = min(self.ui.scrollArea.width(), self.ui.scrollArea.height()) * self.zoom

        hmax = self.ui.scrollArea.horizontalScrollBar().maximum()
        hvalue = self.ui.scrollArea.horizontalScrollBar().value()
        vmax = self.ui.scrollArea.verticalScrollBar().maximum()
        vvalue = self.ui.scrollArea.verticalScrollBar().value()

        if hmax:
            x = hvalue / hmax
        else:
            x = 0.5

        if vmax:
            y = vvalue / vmax
        else:
            y = 0.5

        self.ui.canvas.setMinimumSize(QtCore.QSize(size, size))
        self.ui.canvas.setMaximumSize(QtCore.QSize(size, size))

        hmax = self.ui.scrollArea.horizontalScrollBar().maximum()
        vmax = self.ui.scrollArea.verticalScrollBar().maximum()

        self.ui.scrollArea.horizontalScrollBar().setValue(x * hmax)
        self.ui.scrollArea.verticalScrollBar().setValue(y * vmax)

    def update_actions(self):
        self.ui.actionPoints.setEnabled(len(self.selected_points) == 2 and len(self.selected_segments) == 0)
        self.ui.actionPointPoint.setEnabled(len(self.selected_points) == 2 and len(self.selected_segments) == 0)
        self.ui.actionLineLine.setEnabled(len(self.selected_points) == 0 and len(self.selected_segments) == 2)

    def on_action_zoom_in(self):
        self.zoom *= 1.25
        self.resize_canvas()

    def on_action_zoom_out(self):
        self.zoom /= 1.25
        self.resize_canvas()

    def on_action_points(self):
        p1 = self.selected_points[0]
        p2 = self.selected_points[1]
        a = p2[1] - p1[1]
        b = p1[0] - p2[0]
        c = a * p1[0] + b * p1[1]
        self.lines.append((a, b, c))
        self.selected_points.clear()
        self.update_actions()
        self.ui.canvas.update()

    def on_action_point_point(self):
        p1 = self.selected_points[0]
        p2 = self.selected_points[1]
        a = p1[0] - p2[0]
        b = p1[1] - p2[1]
        c = (a * p1[0] + b * p1[1] + a * p2[0] + b * p2[1]) / 2
        self.lines.append((a, b, c))
        self.selected_points.clear()
        self.update_actions()
        self.ui.canvas.update()

    def on_action_line_line(self):
        l1 = self.selected_segments[0]
        a1 = l1[1][1] - l1[0][1]
        b1 = l1[0][0] - l1[1][0]
        c1 = a1 * l1[0][0] + b1 * l1[0][1]
        l2 = self.selected_segments[1]
        a2 = l2[1][1] - l2[0][1]
        b2 = l2[0][0] - l2[1][0]
        c2 = a2 * l2[0][0] + b2 * l2[0][1]

        theta1 = math.atan2(-a1, b1)
        theta2 = math.atan2(-a2, b2)
        if theta1 - theta2 > math.pi/2:
            theta2 += math.pi
        if theta2 - theta1 > math.pi/2:
            theta1 += math.pi
        theta = (theta1 + theta2) / 2

        a = -math.sin(theta)
        b = math.cos(theta)
        t1 = c1 / (a1 * a + b1 * b)
        t2 = c2 / (a2 * a + b2 * b)
        t = (t1 + t2) / 2
        c = t * (a * a + b * b)
        self.lines.append((a, b, c))
        self.selected_segments.clear()
        self.update_actions()
        self.ui.canvas.update()
