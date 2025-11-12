import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem,
                             QMessageBox, QMenu, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.uic import loadUi
from dbmv import DatabaseManager
from timv import TaskItemWidget


class Tasker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        loadUi('task.ui', self)
        self.setupaui()
        self.signal()
        self.loadctg()
        self.loadtask()

    def setupaui(self):
        self.tasks_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.tasks_list.customContextMenuRequested.connect(
            self.showconmenu)

    def signal(self):
        self.task_input.returnPressed.connect(self.addtask)
        self.add_btn.clicked.connect(self.addtask)
        self.add_category_btn.clicked.connect(self.addnewctg)
        self.delete_category_btn.clicked.connect(self.deletectg)
        self.filter_combo.currentTextChanged.connect(self.ftasks)
        self.category_filter.currentTextChanged.connect(self.ftasks)
        self.clear_completed_btn.clicked.connect(self.cctasks)
        self.refresh_btn.clicked.connect(self.loadtask)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about)

    def loadctg(self):
        self.category_combo.clear()
        categories = self.db.getctg()
        for cat_id, name, color in categories:
            self.category_combo.addItem(name, cat_id)
        self.category_filter.clear()
        self.category_filter.addItem("Все категории")
        for cat_id, name, color in categories:
            self.category_filter.addItem(name)

    def addtask(self):
        text = self.task_input.text().strip()
        if text:
            category_id = self.category_combo.currentData()
            if category_id:
                self.db.addtsk(text, category_id)
                self.task_input.clear()
                self.loadtask()

    def loadtask(self):
        self.tasks_list.clear()
        tasks = self.db.getatt()
        filter_type = self.filter_combo.currentText()
        category_filter = self.category_filter.currentText()
        for task in tasks:
            task_id, text, completed, category_name, \
                category_color, created = task
            if filter_type == "Активные" and completed:
                continue
            if filter_type == "Выполненные" and not completed:
                continue
            if category_filter != "Все категории" \
                    and category_name != category_filter:
                continue
            item = QListWidgetItem(self.tasks_list)
            widget = TaskItemWidget(
                task_id, text, completed, category_name, category_color)
            widget.taskDeleted.connect(self.deletetask)
            widget.taskToggled.connect(self.ttaskstatus)
            item.setSizeHint(widget.sizeHint())
            self.tasks_list.setItemWidget(item, widget)

    def deletetask(self, task_id):
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить эту задачу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.deltsk(task_id)
            self.loadtask()

    def ttaskstatus(self, task_id, completed):
        self.db.upts(task_id, completed)

    def ftasks(self):
        self.loadtask()

    def cctasks(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить все выполненные задачи?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clrct()
            self.loadtask()

    def showconmenu(self, position):
        item = self.tasks_list.itemAt(position)
        if item:
            menu = QMenu(self)
            mark_action = QAction("Пометить как выполнено", self)
            mark_action.triggered.connect(self.comenuaction(item, True))
            menu.addAction(mark_action)
            unmark_action = QAction("Пометить как активное", self)
            unmark_action.triggered.connect(self.cmenuaction(item, False))
            menu.addAction(unmark_action)
            menu.addSeparator()
            delete_action = QAction("Удалить задачу", self)
            delete_action.triggered.connect(self.cmenudelete(item))
            menu.addAction(delete_action)
            menu.exec(self.tasks_list.mapToGlobal(position))

    def cmenuaction(self, item, completed):
        widget = self.tasks_list.itemWidget(item)
        if widget:
            self.db.upts(widget.task_id, completed)
            self.loadtask()

    def cmenudelete(self, item):
        widget = self.tasks_list.itemWidget(item)
        if widget:
            self.deletetask(widget.task_id)

    def addnewctg(self):
        name, ok = QInputDialog.getText(
            self,
            "Новая категория",
            "Введите название категории:"
        )
        if ok and name.strip():
            category_id = self.db.addctg(name.strip())
            if category_id:
                self.loadctg()
                QMessageBox.information(self, "Успех", "Категория добавлена!")
            else:
                QMessageBox.warning(
                    self, "Ошибка",
                          "Категория с таким названием уже существует!")

    def deletectg(self):
        categories = self.db.getctg()
        if len(categories) <= 1:
            QMessageBox.warning(
                self, "Ошибка", "Должна остаться хотя бы одна категория!")
            return
        category_names = [cat[1] for cat in categories]
        category_name, ok = QInputDialog.getItem(
            self,
            "Удаление категории",
            "Выберите категорию для удаления:",
            category_names,
            0,
            False
        )
        if ok and category_name:
            category_id = next(cat[0]
                               for cat in categories
                               if cat[1] == category_name)
            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Все задачи из категории '{category_name}' \
                    будут перемещены в 'Общие'. Продолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.db.deletectg(category_id)
                self.loadctg()
                self.loadtask()
                QMessageBox.information(self, "Успех", "Категория удалена!")

    def about(self):
        QMessageBox.about(self, "О программе",
                          "Задачник\n\n"
                          "by Vafla1441")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Tasker()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
