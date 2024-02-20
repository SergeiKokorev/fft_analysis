import os
import sys
import matplotlib
import numpy as np


from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QLineEdit,
    QHBoxLayout, QLabel, QGroupBox, QComboBox,
    QWidget, QCheckBox, QFormLayout
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir
))
sys.path.append(DIR)

matplotlib.use('Qt5Agg')


from windows import WINDOWS
from analysis import SPECTRAL_ANALYSIS as SPECTRAL, SOUND_ANALYSIS as SOUND
from gui.widgets import *
from models import Input, InputSignals


SIZE = QSize(128, 24)
TMP = '.tmp'


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
        self.ax = self.fig.add_subplot()
        self.ax.grid(True)
        super(MpCanvas, self).__init__(self.fig)

    def plot(self, x, y, *, 
             xlim=None, ylim=None, 
             xlabel=None, ylabel=None, 
             xtick=None, ytick=None,
             title=None):
        
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.grid(True)
        self.ax.set_title(title if title else 'Graph')
        if xlim:
            self.ax.set_xlim(xlim)
        if ylim:
            self.ax.set_ylim(ylim)
        if xtick:
            self.ax.set_xticks(xtick)
        if ytick:
            self.ax.set_yticks(ytick)
        self.ax.set_xlabel(xlabel if xlabel else 'X')
        self.ax.set_ylabel(ylabel if ylabel else 'Y')
        self.fig.canvas.draw()
        self.flush_events()

    def save_fig(self, fname, dpi=300):
        self.fig.savefig(fname, dpi=dpi)


class InputLayout(QFormLayout):

    def __init__(self, model: Input, parent: QWidget | None = None) -> None:
        super().__init__()

        self.setSpacing(25)
        self.setContentsMargins(5, 5, 5, 5)

        self.__model = model
        size = QSize(196, 28)

        self._windows = QComboBox()
        self._windows.addItems(list(WINDOWS.keys()) + ['None'])
        self._windows.setFixedSize(size)

        self._xlabel = QLineEdit()
        self._xlabel.setPlaceholderText('Enter X label name')
        self._xlabel.setFixedSize(size)

        self._ylabel = QLineEdit()
        self._ylabel.setPlaceholderText('Enter Y label name')
        self._ylabel.setFixedSize(size)

        self._xmax = DoubleSlider(decimals=DoubleSlider.getDecimals(self.__model.dt))
        self._xmin = DoubleSlider(decimals=DoubleSlider.getDecimals(self.__model.dt))
        self._xmax.setObjectName('xmax')
        self._xmin.setObjectName('xmin')
        self._xmax.setMaximum(self.__model._xlim[1])
        self._xmax.setMinimum(self.__model._xlim[0])
        self._xmin.setMaximum(self.__model._xlim[1])
        self._xmin.setMinimum(self.__model._xlim[0])
        self._xmax.setSingleStep(self.__model.dt)
        self._xmin.setSingleStep(self.__model.dt)
        self._xmax.setSliderPosition(self.__model._xlim[1])
        self._xmin.setSliderPosition(self.__model._xlim[0])
        self._xmin.setOrientation(Qt.Orientation.Horizontal)
        self._xmax.setOrientation(Qt.Orientation.Horizontal)
        self._xmin.setFixedSize(size)
        self._xmax.setFixedSize(size)
        
        self._sub_mean = QCheckBox()
        self._sub_mean.setCheckState(Qt.CheckState.Unchecked)

        self.addRow('Windows', self._windows)
        self.addRow('X label', self._xlabel)
        self.addRow('Y label', self._ylabel)
        self._xmaxlb = QLabel(f'Xmax: {self._xmax.value()}')
        self._xminlb = QLabel(f'Xmin: {self._xmin.value()}')
        self._xmax.doubleValueChanged.connect(self.sliderValueChanged)
        self._xmin.doubleValueChanged.connect(self.sliderValueChanged)
        self.addRow(self._xmaxlb, self._xmax)
        self.addRow(self._xminlb, self._xmin)
        self.addRow('Subtrackt mean', self._sub_mean)

    def sliderValueChanged(self, value):
        objectName = self.sender().objectName()
        if objectName == 'xmax':
            self._xmaxlb.setText(f'Xmax: {value}')
        elif objectName == 'xmin':
            self._xminlb.setText(f'Xmin: {value}')

    def data(self) -> dict:
        xlabel = 'X' if not self._xlabel.text() else self._xlabel.text()
        ylabel = 'Y' if not self._ylabel.text() else self._ylabel.text()
        if xlabel == ylabel:
            xlabel = 'X'
            ylabel = 'Y'
        return {
            'window': self._windows.currentText(),
            'xlabel': xlabel,
            'ylabel': ylabel,
            'xlim': (self._xmin.value(), self._xmax.value()),
            'sub_mean': self._sub_mean.isChecked()
        }

    def update(self):
        self.__model.update(**self.data())


class FFTLayout(QFormLayout):

    def __init__(self, model: Input, parent: QWidget | None = None) -> None:
        super().__init__()

        self.setSpacing(25)
        self.setContentsMargins(5, 5, 5, 5)

        self.__model = model
        size = QSize(196, 28)

        self._analysis = QComboBox()
        self._analysis.addItems(list(SPECTRAL.keys()) + list(SOUND.keys()))
        self._analysis.setFixedSize(size)

        self._xlabel = QLineEdit()
        self._xlabel.setPlaceholderText('Enter X axis name')
        self._xlabel.setFixedSize(size)

        self._ylabel = QLineEdit()
        self._ylabel.setPlaceholderText('Enter Y axis name')
        self._ylabel.setFixedSize(size)

        freq = Input.get_frequency(self.__model.N, self.__model.dt)
        beam = freq[1] - freq[0]
        self._xmax = DoubleSlider(decimals=DoubleSlider.getDecimals(1 / self.__model.dt))
        self._xmax.setMaximum(freq[-1])
        self._xmax.setMinimum(freq[0])
        self._xmax.setSingleStep(beam)
        self._xmax.setSliderPosition(freq[-1])
        self._xmax.setOrientation(Qt.Orientation.Horizontal)
        self._xmax.setFixedSize(size)
        self._xmax.setObjectName('xmax')
        self._xmax.doubleValueChanged.connect(self.sliderValueChanged)

        self._xmin = DoubleSlider(decimals=DoubleSlider.getDecimals(1 / self.__model.dt))
        self._xmin.setMaximum(freq[-1])
        self._xmin.setMinimum(freq[0])
        self._xmin.setSingleStep(beam)
        self._xmin.setSliderPosition(freq[0])
        self._xmin.setOrientation(Qt.Orientation.Horizontal)
        self._xmin.setFixedSize(size)
        self._xmin.setObjectName('xmin')
        self._xmin.doubleValueChanged.connect(self.sliderValueChanged)

        self._ref_pressure = QLineEdit()
        self._ref_pressure.setValidator(QRegularExpressionValidator(QRegularExpression(r'[0-9]*e?-?.?[0-9]+')))
        self._ref_pressure.setText(str(2e-5))
        self._ref_pressure.setFixedSize(QSize(96, 28))

        self.addRow('Plot', self._analysis)
        self.addRow('X label', self._xlabel)
        self.addRow('Y label', self._ylabel)
        self._xmaxlb = QLabel(f'Xmax: {self._xmax.value()}')
        self._xminlb = QLabel(f'Xmax: {self._xmin.value()}')
        self.addRow(self._xmaxlb, self._xmax)
        self.addRow(self._xminlb, self._xmin)
        self.addRow('Reference Pressure', self._ref_pressure)

    @Slot(float)
    def sliderValueChanged(self, value):
        objectName = self.sender().objectName()
        if objectName == 'xmax':
            self._xmaxlb.setText(f'Xmax: {value}')
        elif objectName == 'xmin':
            self._xminlb.setText(f'Xmin: {value}')

    def data(self):
        xlabel = 'X' if not self._xlabel.text() else self._xlabel.text()
        ylabel = 'Y' if not self._ylabel.text() else self._ylabel.text()
        if xlabel == ylabel:
            xlabel = 'X'
            ylabel = 'Y'
        return {
            'plot': self._analysis.currentText(),
            'xlabel': xlabel,
            'ylabel': ylabel,
            'xlim': (self._xmin.value(), self._xmax.value()),
            'pref': self._ref_pressure.text()
        }


class SignalEditor(QDialog):
    
    def __init__(self, parent = None, f = Qt.WindowType.Dialog, **kwargs) -> None:
        super().__init__(parent, f)

        self.__in_signal = None
        self.__fft_signal = None

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

        self.input_layout = InputLayout(parent=self, model=self._input)
        self.fft_layout = FFTLayout(parent=self, model=self._input)

        in_group.setTitle('Input Signal')
        fft_group.setTitle('FFT Signal')
        in_group.setLayout(self.input_layout)
        fft_group.setLayout(self.fft_layout)

        layout.addWidget(self.input, 0, 0)
        layout.addWidget(in_group, 0, 1)

        layout.addWidget(self.fft, 1, 0)
        layout.addWidget(fft_group, 1, 1)
        layout.addWidget(buttonBox, 2, 0)
        
        layout.setColumnStretch(0, 1)

    @property
    def input_signal(self):
        return self.__in_signal
    
    @property
    def fft_signal(self):
        return self.__fft_signal

    def save_csv(self, x, y, fname, header=None):
        with open(fname, 'w', newline='') as f:
            if header:
                f.write(f'{header[0]},{header[1]}\n')
            for xi, yi in zip(x, y):
                f.write(f'{xi},{yi}\n')

    @Slot()
    def apply(self):
        data = self.input_layout.data()
        self._input.update(**data)
        x = self._input.x
        y = self._input.y if not data['sub_mean'] else Input.subtrackt_mean(self._input.y)  
        y = self._input.window_signal(y, self._input.window) if self._input.window else y
        self.input.plot(x, y, xlim=data['xlim'], xlabel=data['xlabel'],
                        ylabel=data['ylabel'], title=self._input.name)
        self.__in_signal = {self._input.xlabel: x, self._input.ylabel: y}

        data = self.fft_layout.data()
        x = self._input.get_frequency(self._input.N, self._input.dt)
        if (plot:=data['plot']) in SPECTRAL.keys():
            y = SPECTRAL[plot](y)[:x.size]
        elif plot in SOUND.keys():
            y = SOUND[plot](y, float(data['pref']))[:x.size]
        self.fft.plot(x, y, xlim=data['xlim'], xlabel=data['xlabel'],
                      ylabel=data['ylabel'], title=f'{self._input.name} {plot}')
        self.__fft_signal = {data['xlabel']: x, data['ylabel']: y}

    @Slot()
    def accept(self):

        fname = os.path.splitext(os.path.split(self._input.file)[1])[0]
        self.input.save_fig(os.path.abspath(os.path.join(TMP, f'{fname}.png')))
        x, y = self.__in_signal.values()
        self.save_csv(x, y, os.path.abspath(os.path.join(TMP, f'{fname}.csv')),
                       header=tuple(self.__in_signal.keys()))

        data = self.fft_layout.data()
        x, y = self.__fft_signal.values()
        xlabel, ylabel = tuple(self.__fft_signal.keys())
        self.fft.save_fig(os.path.abspath(os.path.join(TMP, f"{data['plot']}_{fname}.png")))
        self.save_csv(x, y, os.path.abspath(os.path.join(TMP, f"{data['plot']}_{fname}.csv")),
                      header=(xlabel, ylabel))

        return super().accept()

    @Slot()
    def reject(self):
        self._input.reset()
        self.__in_signal = None
        self.__fft_signal = None
        return super().reject()
