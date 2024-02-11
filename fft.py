from PySide6.QtWidgets import QApplication

from gui.view import View



def main():
    
    fft_app = QApplication()

    mwin = View()
    mwin.show()

    fft_app.exec()



if __name__ == "__main__":

    main()
