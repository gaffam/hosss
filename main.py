from PyQt5.QtWidgets import QApplication
import sys

from musica.gui import MusicaProOmnibusGUI

app = QApplication(sys.argv)
window = MusicaProOmnibusGUI()
window.show()
app.exec_()
