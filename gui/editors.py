import os
import sys
import matplotlib


from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QLineEdit,
    QHBoxLayout, QLabel, QGroupBox, QComboBox, QVBoxLayout,
    QWidget, QCheckBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir
))
sys.path.append(DIR)

matplotlib.use('Qt5Agg')


from windows import WINDOWS
from spectral import SPECTRAL_ANALYSIS as SPECTRAL, SOUND_ANALYSIS as SOUND
from gui.widgets import *
from models import Input, InputSignals


SIZE = QSize(128, 24)


class NameEdit(QDialog):

    def __init__(self, parent = None, f = Qt.WindowType.Dialog) -> None:
        super().__init__(parent, f)

        self.setWindowTitle('Signal Name')
        self.setFixedSize(QSize(312, 72))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        layout = QGridLayout()

        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.name = QLineEdit()
        self.name.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel('Input signal name'))
        line_layout.addWidget(self.name)

        layout.addLayout(line_layout, 0, 0)
        layout.addWidget(buttonBox, 1, 0)
        self.setLayout(layout)

    @Slot()
    def accept(self):
        self.name = self.name.text() if self.name else None
        return super().accept()
    
    @Slot()
    def reject(self):
        self.name = None
        return super().reject()


class MpCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot()
        self.axes.grid(True)
        super(MpCanvas, self).__init__(self.fig)


class SignalEditor(QDialog):
    
    def __init__(self, parent = None, f = Qt.WindowType.Dialog, **kwargs) -> None:
        super().__init__(parent, f)
        self._input: Input = kwargs.get('input', None)
        self.input = MpCanvas(self, width=5, height=4, dpi=100)
        self.fft= MpCanvas(self, width=5, height=4, dpi=100)

        layout = QGridLayout()
        self.setLayout(layout)
        self.setWindowTitle('Plot settings')
        self.setMinimumSize(QSize(1024, 728))
        self.setWindowModality(Qt.WindowModality.WindowModal)

        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)    
        buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        buttonBox.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)

        in_group = QGroupBox(self)
        fft_group = QGroupBox(self)
        in_group.setTitle('Input Signal')
        fft_group.setTitle('FFT Signal')
        in_group.setLayout(self.__init_signal__())
        fft_group.setLayout(self.__fft_signal__())

        layout.addWidget(in_group)
        layout.addWidget(fft_group, 1, 0)
        layout.addWidget(buttonBox, 2, 0)

    def __init_signal__(self) -> QGridLayout:
        
        layout = QGridLayout()
        settings_layout = QVBoxLayout()

        items = list(WINDOWS.keys()) + ['None']
        cmb_win = ComboBox(self, items, 'window', fixed_size=QSize(168, 28))
        
        xlabel = LineEdit(self, 'X label', 'xlabel', fixed_size=QSize(128, 28), placeholder='Input X label name')
        ylabel = LineEdit(self, 'Y label', 'ylabel', fixed_size=QSize(128, 28), placeholder='Input Y abel name')

        dec = DoubleSlider.getDecimals(self._input.dt)
        xmax = CropSignal(dec, 'Xmax', 'xmax')
        xmin = CropSignal(dec, 'Xmin', 'xmin')
        xmax.sliderSetup(
            self._input._x[0], self._input._x[-1], self._input.dt,
            size=QSize(168, 28), pos=self._input._xlimits[1]
        )
        xmin.sliderSetup(
            self._input._x[0], self._input._x[-1], self._input.dt,
            size=QSize(168, 28), pos=self._input._xlimits[0]
        )
        subtrack_mean = CheckBox(check_state=True, obj_name='sub_mean', label='Subtrackt mean', fixed_size=QSize(196, 32))

        settings_layout.addWidget(groupBuilder('Window', [cmb_win], size=QSize(196, 64)))
        settings_layout.addWidget(groupBuilder('Labels', [xlabel.layout, ylabel.layout], size=QSize(196, 96)))
        settings_layout.addWidget(groupBuilder('Limits', [xmin, xmax], size=QSize(196, 164)))
        settings_layout.addWidget(subtrack_mean)
        settings_layout.addWidget(QWidget(), 1)

        layout.addLayout(settings_layout, 0, 1)
        layout.addWidget(self.input, 0, 0)

        return layout

    def __fft_signal__(self) -> QGridLayout:

        layout = QGridLayout()
        settings_layout = QVBoxLayout()

        items = SPECTRAL.keys()
        cmb_plot = ComboBox(self, items, 'spectral', fixed_size=QSize(168, 28))

        xlabel = LineEdit(self, 'X label', 'xlabel_fft',fixed_size=QSize(128, 28), placeholder='Input X label')
        ylabel = LineEdit(self, 'Y label', 'ylabel_fft',fixed_size=QSize(128, 28), placeholder='Input Y label')

        dec = DoubleSlider.getDecimals(1 / self._input.dt)
        xmax = CropSignal(dec, 'Xmax', 'xmax_fft')
        xmin = CropSignal(dec, 'Xmin', 'xmin_fft')
        freq = Input.get_frequency(self._input.x.size, self._input.dt)
        xmax.sliderSetup(
            freq[0], freq[-1], 1 / self._input.dt,
            size=QSize(168, 28), pos=freq[-1]
        )
        xmin.sliderSetup(
            freq[0], freq[-1], 1 / self._input.dt,
            size=QSize(168, 28), pos=freq[0]
        )

        settings_layout.addWidget(groupBuilder('Plot', [cmb_plot], size=QSize(196, 64)))
        settings_layout.addWidget(groupBuilder('Labels', [xlabel.layout, ylabel.layout], size=QSize(196, 96)))
        settings_layout.addWidget(groupBuilder('Limits', [xmin, xmax], size=QSize(196, 164)))
        settings_layout.addWidget(QWidget(), 1)

        layout.addLayout(settings_layout, 0, 1)
        layout.addWidget(self.fft, 0, 0)

        return layout

    def plot(self, /, canvas: MpCanvas , x, y, xlabel, ylabel, name, xlimits, method=None) -> None:
        canvas.axes.clear()
        if method == 'bar':
            canvas.axes.bar(x, y)
        elif method == 'scatter':
            canvas.axes.scatter(x, y)
        else:
            canvas.axes.plot(x, y)
        canvas.axes.grid(True)
        print(xlimits)
        canvas.axes.set_xlim(xlimits)
        canvas.fig.suptitle(name)
        canvas.axes.set_xlabel(xlabel)
        canvas.axes.set_ylabel(ylabel)
        canvas.fig.canvas.draw()
        canvas.flush_events()

    def input_data(self) -> dict:
        data = {}
        data['window'] = None if not self.findChild(QComboBox, 'window') else self.findChild(QComboBox, 'window').currentText()
        data['xlabel'] = None if not self.findChild(QLineEdit, 'xlabel') else self.findChild(QLineEdit, 'xlabel').text()
        data['ylabel'] = None if not self.findChild(QLineEdit, 'ylabel') else self.findChild(QLineEdit, 'ylabel').text()
        xmax = None if not self.findChild(QSlider, 'xmax') else self.findChild(QSlider, 'xmax').value()
        xmin = None if not self.findChild(QSlider, 'xmin') else self.findChild(QSlider, 'xmin').value()
        data['xlimits'] = (xmin, xmax)
        data['sub_mean'] = False if not self.findChild(QCheckBox, 'sub_mean') else self.findChild(QCheckBox, 'sub_mean').isChecked()
        return data

    def output_data(self) -> dict:
        data = {}
        data['spectral'] = list(SPECTRAL.keys())[0] if not self.findChild(QComboBox, 'spectral') else self.findChild(QComboBox, 'spectral').currentText()
        data['xlabel'] = 'Frequency [Hz]' if not self.findChild(QLineEdit, 'xlabel_fft') else self.findChild(QLineEdit, 'xlabel_fft').text()
        data['ylabel'] = f'Amplitude {self._input.ylabel}' if not self.findChild(QLineEdit, 'ylabel_fft') else self.findChild(QLineEdit, 'ylabel_fft').text()
        xmax = None if not self.findChild(QSlider, 'xmax_fft') else self.findChild(QSlider, 'xmax_fft').value()
        xmin = None if not self.findChild(QSlider, 'xmin_fft') else self.findChild(QSlider, 'xmin_fft').value()        
        data['xlimits'] = (xmin, xmax)
        return data

    @Slot()
    def apply(self):
        input = self.input_data()
        self._input.update(xlabel=input['xlabel'], ylabel=input['ylabel'], xlimits=input['xlimits'])
        x = self._input.x
        y = self._input.y if not input['sub_mean'] else Input.subtrackt_mean(self._input.y)
        y = y if input['window'] == 'None' else Input.window(y, input['window'])
        self.plot(self.input, x, y, self._input.xlabel, self._input.ylabel, self._input.name, self._input.xlimits)

        fft = self.output_data()
        x = Input.get_frequency(self._input.x.size, self._input.dt)
        if (spectral := fft['spectral']) in SPECTRAL.keys():
            y = SPECTRAL[spectral](self._input.y)
        elif (spectral := fft['spectral']) in SOUND.keys():
            y = SOUND[spectral](self._input.y)
        self.plot(self.fft, x, y, xlabel=fft['xlabel'], ylabel=fft['ylabel'], name=f'{spectral} {self._input.name}', xlimits=fft['xlimits'], method='bar')
