import sys
from PyQt5.QtWidgets import *
from MainWindow import *
from SignalHandler import *
import pdb

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.dataWindow.move(app.screens()[1].geometry().topLeft())
    signalHandler = SignalHandler(mainWindow)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

