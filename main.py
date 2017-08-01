import sys
from PyQt5.QtWidgets import *
from MainWindow import *

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: SaveCheckDialog(controller_interface).exec())
    controller_interface = MainWindow()
    controller_interface.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
