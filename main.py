import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
# import pdb

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.dataWindow.move(app.screens()[-1].geometry().topLeft())
    mainWindow.dataWindow.showMaximized()
    # mainWindow.dataWindow.setGeometry(app.screens()[-1].geometry().x() + 10, app.screens()[-1].geometry().y() + 50, app.screens()[-1].geometry().width() - 20, app.screens()[-1].geometry().height() - 100)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

