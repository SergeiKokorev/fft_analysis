import os
import sys
import math
import matplotlib


from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QLineEdit,
    QHBoxLayout, QLabel, QGroupBox, QComboBox, QVBoxLayout,
    QWidget, QSizePolicy, QLayout, QDoubleSpinBox, QSlider
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir
))
sys.path.append(DIR)

matplotlib.use('Qt5Agg')


from const import WINDOWS
from gui.widgets import DoubleSlider


SIZE = QSize(128, 24)






class SliderEdit(DoubleSlider):

    def __init__(self, decimals=3, *args, **kwargs):
        super().__init__(decimals, *args, **kwargs)
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setFixedSize(QSize(112, 24))

    def setupSlider(self, **settings):
        
        if max_val := settings.get('max_val', None):
            self.setMaximum(max_val)
        if min_val := settings.get('min_val', None):
            self.setMinimum(min_val)
        if slot := settings.get('slot', None):
            self.doubleValueChanged.connect(slot)
        if single_step := settings.get('single_step', None):
            self.setSingleStep(single_step)
    
    @classmethod
    def getDecimals(self, step):
        end = True
        n = 0
        while end:
            if math.floor(step * 10 ** n):
                end = False
            else:
                n += 1
        return n

class NameEdit(QDialog):

    def __init__(self, parent = None, f = Qt.WindowType.Dialog) -> None:
        super().__init__(parent, f)

        self.setWindowTitle('Signal Name')
        self.setFixedSize(QSize(312, 72))
        layout = QGridLayout()

        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.name = QLineEdit()
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


class InputSignal(QDialog):
    
    def __init__(self, parent = None, f = Qt.WindowType.Dialog, **kwargs) -> None:
        super().__init__(parent, f)
        self._model = kwargs.get('model', None)

        self.mlayout = QGridLayout()
        self.setWindowTitle('Input Signal Settings')
        self.setLayout(self.mlayout)

        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)    
        buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        buttonBox.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)

        self.output_signal = MpCanvas(self, width=5, height=4, dpi=100)


        out_layout = QHBoxLayout()
        out_layout.addWidget(self.output_signal)
        out_group = QGroupBox('FFT Signal')
        out_group.setLayout(out_layout)

        self.__init_input__()

        self.mlayout.addWidget(out_group, 1, 0)
        self.mlayout.addWidget(buttonBox, 2, 0)
        self.setLayout(self.mlayout)

    def __init_input__(self):
        in_layout = QGridLayout()
        in_group = QGroupBox('Input Signal')
        
        self.input_signal = MpCanvas(self, width=5, height=4, dpi=100)



        self.window_fun = QComboBox(self)
        self.window_fun.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.window_fun.setFixedSize(QSize(128, 24))
        self.window_fun.addItem('None')
        self.window_fun.addItems(WINDOWS.keys())
        vlayout = QVBoxLayout()

        self.in_xlabel = QLineEdit(self)
        self.in_xlabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.in_xlabel.setFixedSize(QSize(128, 24))
        lbl = QLabel('X Axis')
        vlayout.addWidget(lbl)
        vlayout.addWidget(self.in_xlabel)
        lbl = QLabel('Y Axis')

        self.in_ylabel = QLineEdit(self)
        self.in_ylabel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.in_ylabel.setFixedSize(QSize(128, 24))
        vlayout.addWidget(lbl)
        vlayout.addWidget(self.in_ylabel)

        crop_gruop = QGroupBox('Crop Signal')
        crop_gruop.setFixedSize(QSize(128, 128))
        crop_layout = QVBoxLayout()
        xmin_lbl = QLabel('xmin:')
        xmax_lbl = QLabel('xmax:')
        tmin = self._model.input[0,0]
        tmax = self._model.input[-1,0]

        dt = self._model.dt
        decimals = SliderEdit.getDecimals(dt)
        self.xmin = SliderEdit(decimals=decimals)
        self.xmax = SliderEdit(decimals=decimals)
        self.xmin.setupSlider(
            max_val=tmax, min_val=tmin,
            slot=lambda: self.tickChanged(xmin_lbl, decimals, self.xmin.value()),
            single_step=dt
        )
        self.xmax.setupSlider(
            max_val=tmax, min_val=tmin,
            slot=lambda: self.tickChanged(xmax_lbl, decimals, self.xmax.value()),
            single_step=dt
        )
        self.xmin.setSliderPosition(tmin)
        self.xmax.setSliderPosition(tmax)
        crop_layout.addWidget(xmin_lbl)
        crop_layout.addWidget(self.xmin)
        crop_layout.addWidget(xmax_lbl)
        crop_layout.addWidget(self.xmax)
        crop_gruop.setLayout(crop_layout)

        in_layout.addWidget(self.input_signal, 0, 0, 4, 1)
        in_layout.addWidget(self.window_fun, 0, 1)
        in_layout.addLayout(vlayout, 1, 1)
        in_layout.addWidget(crop_gruop, 2, 1)

        in_layout.addWidget(QWidget(), 3, 1)
        in_layout.setRowStretch(3, 1)

        in_group.setLayout(in_layout)
        self.mlayout.addWidget(in_group)

    def plot(self):
        x, y = self._model.input[:,0], self._model.input[:,1]
        xlabel, ylabel = self._model.xlabel, self._model.ylabel
        self.input_signal.axes.plot(x, y)
        self.input_signal.axes.set_xlabel(xlabel)
        self.input_signal.axes.set_ylabel(ylabel)
        amp, freq = self._model.amplitude, self._model.frequency
        self.output_signal.axes.plot(freq, amp)
        self.output_signal.axes.set_xlabel('Frequency [Hz]')
        self.output_signal.axes.set_ylabel(f'Amplitude fft({ylabel})')

    @Slot()
    def apply(self):
        print('apply')
    
    def tickChanged(self, lbl: QLabel, decimals, values):
        txt = lbl.text().split(':')[0]
        lbl.setText(f'{txt}: {round(values, decimals + 3)}')
