from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainterPath, QPen, QColor, QBrush


class TimelineWidget(QGraphicsView):
    """Basic sequencer timeline for arranging clips."""

    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setFixedHeight(120)
        self.setDragMode(self.ScrollHandDrag)

    def clear_clips(self):
        self.scene().clear()

    def add_waveform(self, waveform, start):
        path = QPainterPath()
        for i, v in enumerate(waveform):
            x = start * 50 + i
            y = -v * 30
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        self.scene().addPath(path, QPen(QColor('#00ffaa')))


class PianoRollWidget(QGraphicsView):
    """Basic piano roll widget."""

    step_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setFixedHeight(200)
        self.setDragMode(self.ScrollHandDrag)

    def mousePressEvent(self, event):
        step = int(event.pos().x() / 10)
        self.step_clicked.emit(step)
        super().mousePressEvent(event)


class AutomationEditor(QGraphicsView):
    """Simple automation curve editor."""

    point_added = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setFixedHeight(100)
        self.setDragMode(self.ScrollHandDrag)

    def mousePressEvent(self, event):
        time = event.pos().x() / 50
        value = 1.0 - (event.pos().y() / self.height())
        self.scene().addEllipse(
            event.pos().x() - 2,
            event.pos().y() - 2,
            4,
            4,
            QPen(Qt.red),
            QBrush(QColor(Qt.red)),
        )
        self.point_added.emit(time, max(0.0, min(1.0, value)))
        super().mousePressEvent(event)
