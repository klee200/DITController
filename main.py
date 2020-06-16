import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
# import pdb

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.move(app.screens()[0].geometry().topLeft())
    mainWindow.showMaximized()
    mainWindow.dataWindow.move(app.screens()[-1].geometry().topLeft())
    mainWindow.dataWindow.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

