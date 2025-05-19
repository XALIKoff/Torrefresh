import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QSpinBox, QHBoxLayout, QLabel,
    QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
import pywinstyles

from main import run_update_logic


class UpdateThread(QThread):
    log_signal = pyqtSignal(str)

    def run(self):
        try:
            run_update_logic(print_fn=self.log_signal.emit)
        except Exception as e:
            self.log_signal.emit(f"Ошибка: {e}")


class TorrentUpdaterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("Torrefresh")
        self.setGeometry(100, 100, 600, 400)

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #333333;
                border: 1px solid #555555;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #555555;
            }
            QSpinBox {
                background-color: #222222;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px 4px;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QLabel {
                color: #cccccc;
            }
        """)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Кнопка обновления
        self.update_button = QPushButton("Обновить сейчас")
        self.update_button.clicked.connect(self.run_update)
        self.layout.addWidget(self.update_button)

        # Интервал автообновления (минуты)
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Интервал автообновления (мин):")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 1440)
        self.interval_spinbox.setValue(60)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        self.layout.addLayout(interval_layout)

        # Кнопка автообновления (чекбокс)
        self.auto_update_button = QPushButton("Запустить автообновление")
        self.auto_update_button.setCheckable(True)
        self.auto_update_button.clicked.connect(self.toggle_auto_update)
        self.layout.addWidget(self.auto_update_button)

        # Поле лога
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)

        # Таймер автообновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_update)

        # Трей
        self.tray_icon = QSystemTrayIcon(QIcon("icon.ico"), self)
        tray_menu = QMenu()

        restore_action = QAction("Открыть", self)
        restore_action.triggered.connect(self.show_normal_from_tray)
        tray_menu.addAction(restore_action)

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def show_normal_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # ЛКМ по иконке
            self.show_normal_from_tray()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.show()
        self.tray_icon.showMessage(
            "Torrefresh",
            "Свернуто в трей. Нажмите на иконку для открытия.",
            QSystemTrayIcon.Information,
            3000
        )

    def log(self, message):
        self.log_output.append(message)

    def run_update(self):
        self.update_button.setEnabled(False)
        self.interval_spinbox.clearFocus()
        self.log("Запуск обновления...")
        self.thread = UpdateThread()
        self.thread.log_signal.connect(self.log)
        self.thread.finished.connect(lambda: self.update_button.setEnabled(True))
        self.thread.start()

    def toggle_auto_update(self):
        if self.auto_update_button.isChecked():
            interval_minutes = self.interval_spinbox.value()
            self.timer.start(interval_minutes * 60 * 1000)
            self.run_update()
            self.log(f"Автообновление включено. Интервал: {interval_minutes} мин.")
            self.auto_update_button.setText("Остановить автообновление")
        else:
            self.timer.stop()
            self.log("Автообновление остановлено.")
            self.auto_update_button.setText("Запустить автообновление")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TorrentUpdaterGUI()

    pywinstyles.apply_style(window, "dark")
    window.show()
    sys.exit(app.exec_())
