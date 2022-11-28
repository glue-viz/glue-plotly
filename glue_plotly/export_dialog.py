
from qtpy.QtWidgets import QDialog, QLabel, QVBoxLayout
from qtpy.QtCore import QTimer, Qt


class ExportDialog(QDialog):

    max_dots = 3
    _BASE_MESSAGE = "Exporting to Plotly"

    def __init__(self, parent=None):
        super(ExportDialog, self).__init__(parent=parent, flags=Qt.FramelessWindowHint)

        self.label = QLabel()
        self.label.setText(self._BASE_MESSAGE)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        ending_spaces = " " * self.max_dots
        if not self.label.text().endswith(ending_spaces):
            self.label.setText(self.label.text() + ending_spaces)
        self.n_dots = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_update)
        self.timer.start(750)

    def _on_timer_update(self):
        self.n_dots = (self.n_dots + 1) % (self.max_dots + 1)
        text = self._BASE_MESSAGE + "." * self.n_dots
        self.label.setText(text)

    def close(self):
        super(ExportDialog, self).close()
        self.timer.stop()
