import math


from typing import Any, Sequence


from PySide6.QtCore import (
    QObject, Qt, QAbstractListModel, Signal, QSize,
    Slot
)
from PySide6.QtWidgets import (
    QPushButton, QButtonGroup, QLayout,
    QSlider, QGroupBox, QLabel, QVBoxLayout,
    QHBoxLayout, QComboBox, QLineEdit, QWidget,
    QCheckBox
)


def groupBuilder(title, widgets, orientation='vertical', size=QSize(128, 64)) -> QGroupBox:
    
    layout = QHBoxLayout() if orientation == 'horizontal' else QVBoxLayout()
    for w in widgets:
        if isinstance(w, QWidget):
            layout.addWidget(w)
        elif isinstance(w, QLayout):
            layout.addLayout(w)
    group = QGroupBox(title=title)
    group.setLayout(layout)
    group.setFixedSize(size)

    return group


class CheckBox(QCheckBox):

    def __init__(self, *, check_state=True, obj_name='CheckBox', label='CheckBox', **settings):
        super().__init__()

        if size:=settings.get('fixed_size', None):
            self.setFixedSize(size)
        if size:=settings.get('base_size', None):
            self.setBaseSize(size)
        
        self.setText(label)
        self.setCheckState(Qt.CheckState.Checked if check_state else Qt.CheckState.Unchecked)
        self.setObjectName(obj_name)


class LineEdit:
    
    def __init__(self, parent=None, label="Edit line", obj_name='LineEdit', **settings) -> None:
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel(label))
        self.editor = QLineEdit()
        self.editor.setParent(parent)
        if size:=settings.get('fixed_size', None):
            self.editor.setFixedSize(size)
        if size:=settings.get('base_size', None):
            self.editor.setBaseSize(size)
        if placeholder:=settings.get('placeholder', None):
            self.editor.setPlaceholderText(placeholder)
        self.editor.setObjectName(obj_name)
        self.layout.addWidget(self.editor)

    def text(self):
        return self.editor.text()


class ComboBox(QComboBox):

    def __init__(self, parent=None, items=[], obj_name='ComboBox', **settings) -> None:
        super().__init__(parent)
        if size:=settings.get('fixed_size', None):
            self.setFixedSize(size)
        if size:=settings.get('base_size', None):
            self.setBaseSize(size)
        self.addItems(items)
        self.setObjectName(obj_name)


class DoubleSlider(QSlider):
    
    doubleValueChanged = Signal(float)

    def __init__(self, decimals=3, *args, **kwargs):
        super(DoubleSlider, self).__init__(*args, **kwargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi
    
    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self._multi)
    
    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def setSliderPosition(self, value) -> None:
        return super(DoubleSlider, self).setSliderPosition(value * self._multi)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)
    
    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi
    
    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))

    @classmethod
    def getDecimals(cls, step):
        end = True
        n = 0
        while end:
            if math.floor(step * 10 ** n):
                end = False
            else:
                n += 1
        return n


class CropSignal(QVBoxLayout):

    def __init__(self, decimals=3, label: str='', obj_name='Slider'):
        super().__init__()
        self.label = QLabel(label)
        self.slider = DoubleSlider(decimals=decimals)
        self.slider.setObjectName(obj_name)
        self.slider.doubleValueChanged.connect(self.sliderChanged)
        self.addWidget(self.label)
        self.addWidget(self.slider)

    def sliderSetup(
            self, xmin: float, xmax: float, step: float, *,
            size: QSize = QSize(124, 28), 
            orientation: Qt.Orientation = Qt.Orientation.Horizontal,
            pos: float=None
        ) -> None:

        self.slider.setMinimum(xmin)
        self.slider.setMaximum(xmax)
        self.slider.setSingleStep(step)
        pos = pos if pos else xmin
        self.slider.setSliderPosition(pos)
        self.slider.setFixedSize(size)
        self.slider.setOrientation(orientation)

    @Slot(float)
    def sliderChanged(self, value) -> None:
        text = self.label.text().split(':')
        self.label.setText(f'{text[0]}:{value}')


class PushButton(QPushButton):

    def setButton(self, **settings) -> None:
        self.setText(settings.get('text', 'Button'))
        self.setObjectName(settings.get('name', 'button'))
        self.setEnabled(settings.get('enable', True))


class ButtonGroup(QButtonGroup):

    def __init__(self, parent: QObject | None = None, layout: QLayout | None = None) -> None:
        super().__init__(parent)
        self.layout = layout

    def addButtons(self, buttons: Sequence[QPushButton]) -> None:
        for (i, button) in enumerate(buttons):
            self.addButton(button, i)
            if self.layout: self.layout.addWidget(button)

    def addPushButton(self, *buttons) -> None:

        for idx, button in enumerate(buttons):
            btn = PushButton()
            btn.setButton(**button)
            self.addButton(btn, idx)
            if self.layout: self.layout.addWidget(btn)
            
    def enable(self, buttons: Sequence[PushButton]):
        for btn in buttons:
            btn.setEnabled(True)
    
    def disable(self, buttons: Sequence[PushButton]):
        for btn in buttons:
            btn.setEnabled(False)
    

class SignalList(QAbstractListModel):

    def __init__(self, data) -> None:
        super().__init__()
        self._data = data

    def data(self, index, role) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if not index.isValid() : return None
            if not 0 <= index.row() <= len(self._data.signals) : return None
            return str(self._data.get(index.row()))

    def add(self, signal):
        return self._data.add(signal)
    
    def insert(self, idx, signal):
        return self._data.insert(signal, idx)

    def delete(self, idx):
        return self._data.delete(idx)
    
    def rowCount(self, index) -> int:
        return len(self._data.signals)
