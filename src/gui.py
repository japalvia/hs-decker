#!/usr/bin/env python3

import hscollection as hs

import sys

from PyQt5.QtWidgets import (QApplication, QWidget,
    QPushButton, QGridLayout, QVBoxLayout, QScrollArea, QLabel, QLineEdit)
from PyQt5.QtCore import (QCoreApplication, Qt)
from PyQt5.QtGui import (QPixmap, QValidator, QPalette)


class CardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vbox = QVBoxLayout(self)

class CardGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self)

    def addCard(self, card, row, col):
        image_dir = '/home/palvja/repos/hearthstone-card-images/rel'
        path = image_dir + '/' + str(card['dbfId']) + '.png'
        pixmap = QPixmap(path)

        image = QLabel(self)
        image.setPixmap(pixmap)

        cardWidget = CardWidget()
        cardWidget.layout().addWidget(image)

        countLabel = QLabel(str(card['count']))
        countLabel.setAlignment(Qt.AlignHCenter)
        countLabel.setStyleSheet("font-family: URW Bookman; font-style: Light;"
                                 "font-size: 50px; color: black");
        cardWidget.layout().addWidget(countLabel)

        self.grid.addWidget(cardWidget, row, col)

class HSGui(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.collection = hs.HSCollection('data/cards.collectible.json',
                                          'data/mycollection.json')

    def init_ui(self):

        vbox = QVBoxLayout(self)
        self.setLayout(vbox)

        self.decklabel = QLabel()
        vbox.addWidget(self.decklabel)
        self.reset_decklabel()

        self.textedit = QLineEdit()
        vbox.addWidget(self.textedit)
        self.textedit.returnPressed.connect(self.load_deck)

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

        cardGrid = CardGrid()

        col, row = 0, 0 # we start filling cards from grid pos (0,1)
        for i, card in enumerate(found):
            col = i % 5
            if col == 0:
                row += 1
            cardGrid.addCard(card, row, col)

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
