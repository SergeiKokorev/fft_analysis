from PySide6.QtWidgets import (
    QWidget, QTabBar, QTabWidget
)


class TabWidget(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)


class TabBar(QTabBar):

    def __init__(self, parent=None, **settings):
        super().__init__(parent)

        actions = settings.get('actions', None)
        tabs = settings.get('tabs', None)

        if actions: self.addActions(actions)
        if tabs: 
            for tab in tabs:
                self.addTab(tab)
                
