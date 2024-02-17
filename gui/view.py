import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QPushButton,
    QVBoxLayout,QLabel, QGroupBox, QHBoxLayout, 
    QFileDialog, QListView
)
from PySide6.QtCore import Qt


from gui.editors import SignalEditor, NameEdit
from gui.widgets import SignalList, ButtonGroup
from tools import get_data
from models import InputSignals, Input


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

        self.__cdir = os.sep

        buttons = [
            {'text': 'Add Files', 'name': 'add_file', 'enable': True},
            {'text': 'Modify Input Signal', 'name': 'input_signal', 'enable': False},
            {'text': 'Modify Output Signal', 'name': 'output_signal', 'enable': False},
            {'text': 'Graph', 'name': 'graph', 'enable': False}
        ]

        layout = QGridLayout()

        self.data = InputSignals()
        self.input_model = SignalList(self.data)
        self.signalView = QListView()
        self.signalView.clicked.connect(self.update_info)
        self.signalView.setModel(self.input_model)

        # Settings group
        settings_grp = QGroupBox('Settings')
        btn_layout = QVBoxLayout()
        self.button_group = ButtonGroup(self, btn_layout)
        self.button_group.addPushButton(*buttons)
        self.button_group.buttonClicked.connect(self.click_btn)
        btn_layout.addWidget(QWidget(), 1)

        files_layout = QVBoxLayout()
        files_layout.addWidget(self.signalView)

        settings_layout = QHBoxLayout()
        settings_layout.addLayout(btn_layout)
        settings_layout.addLayout(files_layout)
    
        settings_grp.setLayout(settings_layout)

        # Info group
        self.info = QLabel(INFO)
        info_grp = QGroupBox('Info')
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.info)
        info_grp.setLayout(info_layout)

        layout.addWidget(settings_grp, 0, 0)
        layout.addWidget(info_grp, 1, 0)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

    def click_btn(self, btn: QPushButton):
        
        match btn.objectName():
            case 'add_file':
                self.add_file()
            case 'input_signal':
                self.modify_input_signal()

    def add_file(self):

        file = QFileDialog.getOpenFileName(
            self, 'Open Input Signal File', self.__cdir,
            'Excel File (*.xlsx *.xls);; CSV (*.csv)'
        )[0]
        
        if file:
            name_edit = NameEdit(self)
            name_edit.show()
            name_edit.exec()
            name = name_edit.name if name_edit.name else os.path.split(file)[1]
            x, y = get_data(file)
            signal = Input(x, y, file=file, name=name)
            self.input_model.add(signal)
            self.button_group.enable(self.button_group.buttons()[1:])
            self.input_model.layoutChanged.emit()
            self.__cdir = os.path.split(file)[0]

    def modify_input_signal(self):
        idx = self.signalView.currentIndex().row()
        input_signal: Input = self.data.signals[idx]
        signal_editor = SignalEditor(self, input=input_signal)
        signal_editor.show()
        signal_editor.exec()

    def update_info(self, signal):
        self.info.setText(self.data.signals[signal.row()].info)
