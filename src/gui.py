#!/usr/bin/env python3

import hscollection as hs

import argparse
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

    def addCard(self, card_tuple, row, col):
        card = card_tuple[0]
        found = card_tuple[1]
        missing = card_tuple[2]
        image_dir = '/home/palvja/repos/hearthstone-card-images/rel'
        path = image_dir + '/' + str(card['dbfId']) + '.png'
        pixmap = QPixmap(path)

        image = QLabel(self)
        image.setPixmap(pixmap)

        cardWidget = CardWidget()
        cardWidget.layout().addWidget(image)

        count_str = '{}'.format(str(found+missing))
        if missing:
            count_str = '{}/{}'.format(str(found), count_str)
        countLabel = QLabel(count_str, self)
        countLabel.setAlignment(Qt.AlignHCenter)
        countLabel.setStyleSheet("font-family: URW Bookman; font-style: Light;"
                                 "font-size: 50px; color: black");
        cardWidget.layout().addWidget(countLabel)

        self.grid.addWidget(cardWidget, row, col)

class HSGui(QWidget):
    def __init__(self, args):
        super().__init__()
        self.init_ui()
        self.collection = hs.HSCollection(args.collectible, args.mycollection)

    def init_ui(self):
        self.cardGrid = None
        self.scrollArea = None

        vbox = QVBoxLayout(self)
        self.setLayout(vbox)

        self.decklabel = QLabel(self)
        vbox.addWidget(self.decklabel)
        self.reset_decklabel()

        self.textedit = QLineEdit(self)
        vbox.addWidget(self.textedit)
        self.textedit.returnPressed.connect(self.load_deck)

        self.setWindowTitle('HSCollection')
        self.show()

    def reset_decklabel(self):
        self.decklabel.setText('Copy-paste deck string and press Enter!')

    def load_deck(self):
        cards_tuple = self.collection.load_deckstring(self.textedit.text())
        if not cards_tuple:
            self.decklabel.setText('Invalid deck string, try again')
            return
        self.reset_decklabel()

        if self.cardGrid:
            self.layout().removeWidget(self.cardGrid)
            self.cardGrid.hide()
            self.cardGrid = None
        self.cardGrid = CardGrid()

        col, row = 0, 0 # we start filling cards from grid pos (0,1)
        for i, card_tuple in enumerate(cards_tuple):
            col = i % 5
            if col == 0:
                row += 1
            self.cardGrid.addCard(card_tuple, row, col)

        if self.scrollArea:
            self.layout().removeWidget(self.scrollArea)
            self.scrollArea = None

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setBackgroundRole(QPalette.Shadow)
        self.scrollArea.setWidget(self.cardGrid)
        self.layout().addWidget(self.scrollArea)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('-c', '--collectible', required=True,
                        help='cards.collectible.json')
    parser.add_argument('-m', '--mycollection', required=True,
                        help='mycollection.json')
    parser.add_argument('-i', '--images', required=True,
                        help='path to card image directory')
    parser.add_argument('-d', '--deck', help='deck string')

    args = parser.parse_args()

    app = QApplication(sys.argv)
    gui = HSGui(args)
    sys.exit(app.exec_())
