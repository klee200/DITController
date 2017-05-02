import sys
from PyQt5.QtWidgets import *
from MainWindow import *

def main():
    app = QApplication(sys.argv)
    controller_interface = MainWindow()
    controller_interface.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
