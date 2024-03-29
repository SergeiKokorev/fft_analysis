import os
import shutil

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QPushButton,
    QVBoxLayout,QLabel, QGroupBox, QHBoxLayout, 
    QFileDialog, QListView, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt


from gui.editors import SignalEditor, NameEdit
from gui.widgets import SignalList, ButtonGroup
from tools import get_data
from models.data import InputSignals, Input
from const import TMP


class View(QMainWindow):

    def __init__(self, parent=None, flag=Qt.WindowType.Window):
        super().__init__(parent, flag)
        self.setWindowTitle('Fourier Transform')
        self.__signals = []

        self.__cdir = os.sep

        buttons = [
            {'text': 'Add File', 'name': 'add_file', 'enable': True},
            {'text': 'FFT Analisys', 'name': 'fft_analysis', 'enable': False},
            {'text': 'Regression Analysis', 'name': 'ergression_analysis', 'enable': False},
            {'text': 'Delete file', 'name': 'delete', 'enable': False},
            {'text': 'Delete all files', 'name': 'reset', 'enable': False}
        ]

        layout = QGridLayout()

        self.data = InputSignals()
        self.data_model = SignalList(self.data)
        self.signalView = QListView()
        self.signalView.clicked.connect(self.update_info)
        self.signalView.setModel(self.data_model)

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
        self.info = QLabel()
        info_grp = QGroupBox('Info')
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.info)
        info_grp.setLayout(info_layout)

        # Standart button
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save 
                                   | QDialogButtonBox.StandardButton.Close)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        layout.addWidget(settings_grp, 0, 0)
        layout.addWidget(info_grp, 1, 0)
        layout.addWidget(btn_box, 2, 0)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

    @property
    def signals(self):
        return self.__signals

    def click_btn(self, btn: QPushButton):
        
        match btn.objectName():
            case 'add_file':
                self.add_file()
            case 'fft_analysis':
                self.fft_analysis()
            case 'regression_analysis':
                self.regression_analysis()
            case 'reset':
                self.reset()
            case 'delete':
                self.delete()

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
            try:
                x, y = get_data(file)
                signal = Input(x, y, file=file, name=name)
                self.data_model.add(signal)
                self.button_group.enable(self.button_group.buttons()[1:])
                self.data_model.layoutChanged.emit()
                self.__cdir = os.path.split(file)[0]
            except (AttributeError, IndexError, TypeError) as er:
                error = QMessageBox()
                msg = f'During importing data from the file an error ocurred.\n' \
                      f'The data file must contain numerical data in (x,y) format ' \
                      f'and must not contain empty lines.\n' \
                      f'Please try another data file.\n' \
                      f'Error: {str(er)}'
                error.critical(self, 'Data import error', msg,
                               QMessageBox.StandardButton.Ok)

    def fft_analysis(self):
        idx = self.signalView.currentIndex().row()
        input_signal: Input = self.data.signals[idx]
        signal_editor = SignalEditor(self, input=input_signal)
        signal_editor.show()
        signal_editor.exec()

        if signal_editor.input_signal:
            self.__signals.append((input_signal, signal_editor.input_signal, signal_editor.fft_signal))

    def regression_analysis(self):
        pass

    def reset(self):
        self.data.reset()
        for file in os.listdir(TMP):
            os.remove(os.path.abspath(os.path.join(TMP, file)))
        self.button_group.disable(self.button_group.buttons()[1:])

    def delete(self):
        index = self.signalView.currentIndex()
        self.data.delete(index.row())
        if len(self.data.signals) == 0:
            self.button_group.disable(self.button_group.buttons()[1:])

    def update_info(self, signal):
        self.info.setText(self.data.signals[signal.row()].info)

    def accept(self):
        save_to = QFileDialog.getExistingDirectory(
            self, 'Save Results', self.__cdir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )

        if not save_to:            
            return None
        
        save_from = os.path.abspath(TMP)
        msg = QMessageBox()

        try:

            for f in os.listdir(TMP):
                copy_from = os.path.join(save_from, f)
                copy_to = os.path.join(save_to, f)
                shutil.move(copy_from, copy_to)
            msg.information(self, 'Saving results', 
                                          'Results have been successfully saved', 
                                          QMessageBox.StandardButton.Ok)
        except shutil.Error as er:
            msg.critical(self, 'Saving resuts',
                         f'Results have not been saved. The error occurred {er}',
                         QMessageBox.StandardButton.Ok)

    def reject(self):
        self.data.reset()
        for file in os.listdir(TMP):
            os.remove(os.path.abspath(os.path.join(TMP, file)))
        return super().close()
