from typing import Any, Sequence


from PySide6.QtCore import (
    QObject, Qt, QAbstractListModel, Signal
)
from PySide6.QtWidgets import (
    QPushButton, QButtonGroup, QLayout,
    QSlider
)


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
    

class SignalModel(QAbstractListModel):

    def __init__(self, data) -> None:
        super().__init__()
        self._data = data

    def data(self, index, role) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if not index.isValid() : return None
            if not 0 <= index.row() <= len(self._data.data()) : return None
            return str(self._data.get(index.row()))

    def rowCount(self, index) -> int:
        return len(self._data.view())
