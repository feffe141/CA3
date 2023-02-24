#Imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
from PyQt5 import QtCore
import sys

from cardsmodel import HandModel
from cardsmodel import CardsModel
from cardsmodel import TableModel


class TableScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.tile = QPixmap('cards/table.png')
        self.setBackgroundBrush(QBrush(self.tile))

class CardItem(QGraphicsSvgItem):
    """ A simple overloaded QGraphicsSvgItem that also stores the card position """
    def __init__(self, renderer, position):
        super().__init__()
        self.setSharedRenderer(renderer)
        self.position = position

def read_cards():
    """
    Reads all the 52 cards from files.
    :return: Dictionary of SVG renderers
    """
    all_cards = dict()  # Dictionaries let us have convenient mappings between cards and their images
    for suit_file, suit in zip('CDHS', range(4)):
        for value_file, value in zip(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'], range(2, 15)):
            file = value_file + suit_file
            key = (value, suit)  # I'm choosing this tuple to be the key for this dictionary
            all_cards[key] = QSvgRenderer('cards/' + file + '.svg')
    return all_cards

class CardsView(QGraphicsView):
    """ A View widget that represents the table area displaying a players cards. """
    # We read all the card graphics as static class variables
    back_card = QSvgRenderer('cards/Red_Back_2.svg')
    all_cards = read_cards()

    def __init__(self, cards_model: CardsModel, card_spacing: int = 250, padding: int = ()):
        """
        Initializes the view to display the content of the given model
        :param cards_model: A model that represents a set of cards. Needs to support the CardsModel interface.
        :param card_spacing: Spacing between the visualized cards.
        :param padding: Padding of table area around the visualized cards.
        """
        self.scene = TableScene()
        super().__init__(self.scene)

        self.card_spacing = card_spacing
        self.padding = padding

        # Note that this viewer doesn't care about whether this is Hand, or a "Table" or a "Deck".
        # It only knows how to display a set of cards
        self.model = cards_model
        # Whenever this window should update, it should call the "__change_cards" method.
        # This can, for example, be done by connecting it to a signal.
        # The view can listen to changes:
        self.model.new_cards.connect(self.__change_cards)

        # Add the cards the first time around to represent the initial state.
        self.__change_cards()

    def __change_cards(self):  # the double underscore is used to indicate that this is a private method.
        # Add the cards from scratch
        self.scene.clear()
        for i, card in enumerate(self.model):
            # The ID of the card in the dictionary of images is a tuple with (value, suit), both integers
            graphics_key = (card.get_value(), card.suit)
            renderer = self.back_card if self.model.flipped() else self.all_cards[graphics_key]
            c = CardItem(renderer, i)

            # Shadow effects
            shadow = QGraphicsDropShadowEffect(c)
            shadow.setBlurRadius(10.)
            shadow.setOffset(10, 10)
            shadow.setColor(QColor(0, 0, 0, 180))  # Semi-transparent black!
            c.setGraphicsEffect(shadow)

            # Place the cards on the default positions
            c.setPos(c.position * self.card_spacing, 0)
            self.scene.addItem(c)

        self.update_view()

    def update_view(self):
        scale = (self.viewport().height()-2*self.padding)/(313*1.25)
        self.resetTransform()
        self.scale(scale, scale)

    def resizeEvent(self, painter):
        # This method is called when the window is resized.
        self.update_view()
        super().resizeEvent(painter)


class MyTableView(QGroupBox):
    def __init__(self):
        super().__init__('Table')

        table_layout = QVBoxLayout()
        self.setLayout(table_layout)
        table_layout.addWidget(TableContent(player1_bet, player2_bet))
        table_layout.addWidget(CardsView(tablecards, card_spacing=250,padding=10))

class TableContent(QGroupBox):
    def __init__(self, player1_bet, player2_bet):
        super().__init__()
        tablecontent_layout = QVBoxLayout()
        self.setLayout(tablecontent_layout)

        #Total pot
        totalpot_layout = QHBoxLayout()
        total_pot = QLabel(f"Total pot: x sek")

        totalpot_layout.addWidget(total_pot)
        totalpot_layout.setAlignment(Qt.AlignCenter)

        #Player bets
        playerbets_layout = QHBoxLayout()
        p1bet_label = QLabel(f"Player 1's total bets: {player1_bet}")
        p2bet_label = QLabel(f"Player 2's total bets: {player2_bet}")
        playerbets_layout.addWidget(p1bet_label)
        playerbets_layout.addWidget(p2bet_label)
        playerbets_layout.setAlignment(Qt.AlignCenter)

        # Adding total pot- and player bets layouts togheter
        tablecontent_layout.addLayout(totalpot_layout)
        tablecontent_layout.addLayout(playerbets_layout)



class PlayersActionView(QGroupBox):
    def __init__(self):
        super().__init__('Players')

        playeraction_layout = QHBoxLayout()
        self.setLayout(playeraction_layout)

        playeraction_layout.addWidget(PlayerView(1, player1_balance, player1_hand, active_player))
        playeraction_layout.addWidget(ActionView(['Call', 'Raise', 'Fold']))
        playeraction_layout.addWidget(PlayerView(2, player2_balance, player2_hand, active_player))


class ActionView(QGroupBox):
    def __init__(self, action_names):
        super().__init__('Action Buttons')

        action_layout = QVBoxLayout()
        self.setLayout(action_layout)

        # Call/Raise/Fold Action Section
        for name in action_names:
            button = QPushButton(f"{name}")
            button.setFixedSize(QtCore.QSize(200, 140))
            action_layout.addWidget(button)
            action_layout.setAlignment(Qt.AlignCenter)


class PlayerView(QGroupBox):
    def __init__(self, whichplayer, player_balance, player_hand, active_player):
        super().__init__(f"Player {whichplayer}")

        player_view_layout = QHBoxLayout()
        self.setLayout(player_view_layout)

        #Active player/Balance/Bet-amount layout
        balancebet_layout = QVBoxLayout()

        if whichplayer == active_player:     #Shows the active player
            active_playerlabel = QLabel("Your turn")
            balancebet_layout.addWidget(active_playerlabel)

        # Balance
        balance_label = QLabel(f"Balance: {player_balance} sek")

        # Bet amount
        bet_box = QSpinBox()
        bet_box.setMinimum(0)
        bet_box.setMaximum(player_balance)
        bet_box.setPrefix("Bet: ")
        bet_box.setSuffix("SEK")
        bet_box.setFixedSize(QtCore.QSize(250, 90))

        # Adds to layout
        balancebet_layout.addWidget(balance_label)
        balancebet_layout.addWidget(bet_box)
        balancebet_layout.setAlignment(Qt.AlignBottom)


        # Cards/Flip
        cardsflip_layout = QVBoxLayout()

        # Flip button
        button = QPushButton("Hide/Show Cards")
        button.clicked.connect(player_hand.flip)
        cardsflip_layout.addWidget(button)

        # Cards on hand
        cards_on_hand = CardsView(player_hand, card_spacing=250, padding=10)
        cardsflip_layout.addWidget(cards_on_hand)


        # Adding layouts together
        player_view_layout.addLayout(balancebet_layout)
        player_view_layout.addLayout(cardsflip_layout)

class TexasHoldemView(QWidget):
    def __init__(self, tablecards):
        super().__init__()

        vbox = QVBoxLayout()
        vbox.addWidget(MyTableView())
        vbox.addWidget(PlayersActionView())

        self.setLayout(vbox)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle("Daves Dunkers: Texas hold'em")


# Global variabels (Placeholder values, imported from model later) and Execution

active_player = 2
player1_bet = 1000
player2_bet = 2000
whichplayer = [1, 2]
player1_balance = 15000
player2_balance = 360000

tablecards = TableModel()
player1_hand = HandModel()
player2_hand = HandModel()

qt_app = QApplication(sys.argv)
view = TexasHoldemView(tablecards)
view.show()
qt_app.exec_()


