from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QPushButton,
    QButtonGroup, QVBoxLayout, QListWidget, QLabel,
    QGroupBox, QHBoxLayout
)
from PySide6.QtCore import Qt


from gui.widgets import *


INFO = '''

What is Lorem Ipsum?

Lorem Ipsum is simply dummy text of the printing and typesetting 
industry. Lorem Ipsum has been the industry's standard dummy 
text ever since the 1500s, when an unknown printer took a galley 
of type and scrambled it to make a type specimen book. It has 
survived not only five centuries, but also the leap into electronic 
typesetting, remaining essentially unchanged. It was popularised in 
the 1960s with the release of Letraset sheets containing Lorem 
Ipsum passages, and more recently with desktop publishing 
software like Aldus PageMaker including versions of Lorem Ipsum.

'''


class View(QMainWindow):

    def __init__(self, parent=None, flag=Qt.WindowType.Window):
        super().__init__(parent, flag)
        self.setWindowTitle('Fourier Transform')

        layout = QGridLayout()

        self.files_list = QListWidget()
        self.info = QLabel(INFO)

        btns = (
            QPushButton('Add File'),
            QPushButton('Modify Input Signal'),
            QPushButton('Modify Output Signal'),
            QPushButton('Show Graph')
        )

        self.btn_grp = QButtonGroup()
        for btn in btns:
            self.btn_grp.addButton(btn)
        
        btn_layout = QVBoxLayout()
        for btn in btns:
            btn_layout.addWidget(btn)

        files_layout = QVBoxLayout()
        files_layout.addWidget(self.files_list)

        settings_grp = QGroupBox('Settings')
        settings_layout = QHBoxLayout()
        settings_layout.addLayout(btn_layout)
        settings_layout.addLayout(files_layout)
        settings_grp.setLayout(settings_layout)

        layout.addWidget(settings_grp, 0, 0)
        layout.addWidget(self.info, 1, 0, 1, 2)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

