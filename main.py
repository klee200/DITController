import sys
from PyQt5.QtWidgets import *
from MainWindow import *
from SignalHandler import *
import pdb

def main():
    app = QApplication(sys.argv)
    # app.aboutToQuit.connect(lambda: SaveCheckDialog(controller_interface).exec())
    mainWindow = MainWindow()
    signalHandler = SignalHandler(mainWindow)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

