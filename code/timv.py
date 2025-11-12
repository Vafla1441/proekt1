from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QCheckBox,
                             QLabel, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal


class TaskItemWidget(QWidget):
    taskDeleted = pyqtSignal(int)
    taskToggled = pyqtSignal(int, bool)

    def __init__(self, task_id, task_text, completed=False,
                 category_name="Общие", category_color="#95a5a6", parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.init_Ui(task_text, completed, category_name, category_color)

    def init_Ui(self, task_text, completed, category_name, category_color):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(completed)
        self.checkbox.stateChanged.connect(self.checkboxchange)
        layout.addWidget(self.checkbox)
        self.task_label = QLabel(task_text)
        self.task_label.setWordWrap(True)
        layout.addWidget(self.task_label, 1)
        self.category_label = QLabel(category_name)
        self.category_label.setFixedWidth(80)
        layout.addWidget(self.category_label)
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(25, 25)
        self.delete_btn.clicked.connect(self.deltask)
        layout.addWidget(self.delete_btn)

        self.setLayout(layout)

    def checkboxchange(self, state):
        completed = state == Qt.CheckState.Checked.value
        self.taskToggled.emit(self.task_id, completed)

    def deltask(self):
        self.taskDeleted.emit(self.task_id)
