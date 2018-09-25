import sys
from PyQt5.QtWidgets import *
from MainWindow import *
from SignalHandler import *
import pdb

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # mainWindow.dataWindow.move(app.screens()[-1].geometry().topLeft())
    mainWindow.dataWindow.setGeometry(app.screens()[-1].geometry().x() + 10, app.screens()[-1].geometry().y() + 50, app.screens()[-1].geometry().width() - 20, app.screens()[-1].geometry().height() - 100)
    signalHandler = SignalHandler(mainWindow)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

