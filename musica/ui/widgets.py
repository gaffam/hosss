from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QLinearGradient
from PyQt5.QtCore import Qt, QRectF, pyqtSignal

class JogWheelWidget(QWidget):
    jog_moved = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 100)
        self.angle = 0
        self.last_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(5, 5, 90, 90)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, QColor("#003087"))
        gradient.setColorAt(1, QColor("#007bff"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.white, 1))
        painter.drawEllipse(rect)
        painter.translate(50, 50)
        painter.rotate(self.angle)
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(-3, -45, 6, 10)

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos:
            delta_x = event.pos().x() - self.last_pos.x()
            delta_y = event.pos().y() - self.last_pos.y()
            self.angle += delta_x
            value = delta_x / 100.0 if abs(delta_x) > abs(delta_y) else delta_y / 100.0
            self.jog_moved.emit(value)
            self.last_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_pos = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.jog_moved.emit(delta * 0.05)
        self.update()
