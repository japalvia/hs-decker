#!/usr/bin/env python3

import hscollection as hs

import sys

from PyQt5.QtWidgets import (QApplication, QWidget,
    QPushButton, QGridLayout, QVBoxLayout, QScrollArea, QLabel, QLineEdit)
from PyQt5.QtCore import (QCoreApplication, Qt)
from PyQt5.QtGui import (QPixmap, QValidator, QPalette)

'''
class DeckValidator(QValidator):
    def __init__(self):
        super().__init__()

    def validate(self, string, pos):
        if len(string) < 10:
            return QValidator.Invalid
        else:
            return QValidator.Acceptable
'''

class CardGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self)

class HSGui(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.collection = hs.HSCollection('data/cards.collectible.json',
                                          'data/mycollection.json')

    def init_ui(self):

        # self.grid = QGridLayout(self)
        # self.grid.setSpacing(10)
        vbox = QVBoxLayout()
        # vbox.addStretch(1)
        self.setLayout(vbox)

        self.decklabel = QLabel()
        # self.grid.addWidget(self.decklabel, 0, 0)
        vbox.addWidget(self.decklabel)
        self.reset_decklabel()

        self.textedit = QLineEdit()
        # self.grid.addWidget(self.textedit)
        vbox.addWidget(self.textedit)
        self.textedit.returnPressed.connect(self.load_deck)

        '''
        button_quit = QPushButton('Quit', self)
        button_quit.clicked.connect(QCoreApplication.instance().quit)
        button_quit.resize(button_quit.sizeHint())
        # self.grid.addWidget(button_quit)
        vbox.addWidget(button_quit)
        '''

        # self.setLayout(self.grid)

        self.setWindowTitle('HSCollection')
        self.show()

    def reset_decklabel(self):
        self.decklabel.setText('Copy-paste deck string and press Enter!')

    def load_deck(self):
        found, missing = self.collection.load_deckstring(self.textedit.text())
        if not found or not missing:
            self.decklabel.setText('Invalid deck string, try again')
            return
        self.reset_decklabel()

        #grid = QGridLayout()

        cardGrid = CardGrid()
        grid = cardGrid.layout()

        image_dir = '/home/palvja/repos/hearthstone-card-images/rel'
        col, row = 0, 0 # we start filling cards from grid pos (0,1)
        for i, card in enumerate(found):
            path = image_dir + '/' + str(card['dbfId']) + '.png'
            pixmap = QPixmap(path)
            label = QLabel()
            label.setPixmap(pixmap)
            col = i % 5
            if col == 0:
                row += 1
            print("{} ({},{})".format(card['name'], row, col))
            grid.addWidget(label, row, col)

        for i, card in enumerate(missing):
            path = image_dir + '/' + str(card['dbfId']) + '.png'
            pixmap = QPixmap(path)
            label = QLabel()
            label.setPixmap(pixmap)
            col = i % 5
            if col == 0:
                row += 1
            print("{} ({},{})".format(card['name'], row, col))
            grid.addWidget(label, row, col)

        scrollArea = QScrollArea()
        scrollArea.setBackgroundRole(QPalette.Shadow)
        scrollArea.setWidget(cardGrid)
        vbox = self.layout()
        vbox.addWidget(scrollArea)


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    gui = HSGui()
    sys.exit(app.exec_())
