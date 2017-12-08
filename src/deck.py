import random

class Face:
    """ Face of a card class """
    ACE = 'Ace'
    KING = 'King'
    QUEEN = 'Queen'
    JACK = 'Jack'
    TEN = 'Ten'
    NINE = 'Nine'
    EIGHT = 'Eight'
    SEVEN = 'Seven'
    SIX = 'Six'
    FIVE = 'Five'
    FOUR = 'Four'
    THREE = 'Three'
    TWO = 'Two'
    
    # Mapping from face to short hand for printing hands
    shortStrMapping = {
        ACE : 'A',
        KING : 'K',
        QUEEN : 'Q',
        JACK : 'J',
        TEN : '10',
        NINE : '9',
        EIGHT : '8',
        SEVEN : '7',
        SIX : '6',
        FIVE : '5',
        FOUR : '4',
        THREE : '3',
        TWO : '2'
    }

    # Mapping from face to value
    valueMapping = {
        ACE : [11, 1],
        QUEEN : [10],
        KING : [10],
        JACK : [10],
        TEN : [10],
        NINE : [9],
        EIGHT : [8],
        SEVEN : [7],
        SIX : [6],
        FIVE : [5],
        FOUR : [4],
        THREE : [3],
        TWO : [2]
    }

class Suit:
    """ Suit class for each card """
    SPADES = 'Spades'
    CLUBS = 'Clubs'
    DIAMONDS = 'Diamonds'
    HEARTS = 'Hearts'

class Card():
    """ Card class wraps a face and a suit and provides methods for printing and getting value """
    def __init__(self, face, suit):
        """ Init card with face and suit """
        self.face = face
        self.suit = suit

    def __eq__(self, card):
        """ Consider cards equal if faces match, not suits
        input: card to compare
        returns: (bool) if they're same face or not
        """
        return self.face == card.face

    def getFace(self):
        return self.face

    def getStr(self):
        """ return long-hand string of the card """
        return "{} of {}".format(self.face, self.suit)

    def getPrettyStr(self):
        """ return short-hand string of the card """
        clubs =  '\u2663'
        spades = "\u2660"
        diamonds = "\u2666"
        hearts = "\u2665"

        if self.suit == Suit.SPADES:
            suit = spades
        elif self.suit == Suit.CLUBS:
            suit = clubs
        elif self.suit == Suit.DIAMONDS:
            suit = diamonds
        else:
            suit = hearts
        
        return "{}{}".format(Face.shortStrMapping[self.face], suit)

    def getValue(self):
        """ Get value of the card
        returns: (int) value of card if not an ace
                or (list) possible values of aces
        """
        values = Face.valueMapping[self.face]
        if len(values) == 1:
            return values[0]
        else:
            return values 

class Deck():
    """ Deck of cards class
    Decks in this game are infinite. All 52 cards are initialized and dealt with replacement
    """
    def __init__(self):
        self.cards = []

        for face in [Face.ACE, Face.KING, Face.QUEEN, Face.JACK, Face.TEN, Face.NINE, Face.EIGHT, Face.SEVEN, Face.SIX, Face.FIVE, Face.FOUR, Face.THREE, Face.TWO]:
            for suit in [Suit.SPADES, Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS]:
                self.cards.append( Card(face, suit) )

    def getRandomCard(self):
        """ Get a random card from the deck
        returns: a card from the list of 52 cards 
        """
        return random.choice(self.cards)

class Hand():
    """ Hand class for player and dealer hands """
    def __init__(self):
        self.hand = []
        self.nCards = 0
        
        # Soft hand when an ace is demoted to 1 b/c 11 would bust
        self.hard = True
   
    """ Determine if hand is soft or hard """
    def isHard(self):
        return self.hard
    def isSoft(self):
        return not self.hard

    def getNumCards(self):
        """ Return how many cards are in hand"""
        return self.nCards

    def getCards(self):
        """ Return list of cards in hand"""
        return self.hand

    def strFromHand(self):
        """ return string representation of hand """
        cards = self.hand[0].getPrettyStr()
        for card in self.hand[1:]:
            cards += ", {}".format(card.getPrettyStr())

        value = self.getHandValue()

        return "Cards: {}\n Value: {} ({})\n".format(cards, value, "hard" if self.isHard() else "soft")

    def receiveCard(self, card):
        """ Add a card to hand
        input: a new card
        returns: nothing
        """
        self.hand.append(card)
        self.nCards += 1
        # to set if hand is hard or soft
        self.getHandValue()

    def getHandValue(self):
        """ Return the value of the hand
        Determines the value of hard and soft aces, defaults to soft ace unless it'd be a bust
        Returns: (int) value of hand
        """
        nAces = 0
        hardValue = 0
        softValue = 0
        for card in self.hand:
            value = card.getValue()
            if type(value) is int:
                hardValue += value
                softValue += value
            # Else its a [11,1] list for values for ace
            else:
                # First ace can be 11 (soft hand) or 1 (hard hand)
                if nAces == 0:
                    # ace is 11
                    softValue += value[0]
                    # ace is 1
                    hardValue += value[1]
                # Any more aces are 1
                else:
                    softValue += value[1]
                    hardValue += value[1]
                nAces += 1
        # Determine if hand is soft or hard (hard is default, soft only if ace and the value < 21)
        if softValue > hardValue and softValue <= 21:
            self.hard = False
        else:
            self.hard = True
        
        return hardValue if self.hard else softValue

    def isDoubles(self):
        """ Determine if hand is doubles or not
        return: (bool) True if 2 cards that have same value
        """
        if len(self.hand) != 2:
            return False
        else:
            return self.hand[0] == self.hand[1]

   
    def isBlackjack(self):
        """ determines if hand is blackjack or not
        blackjack is limited toa 2 card hand of value 21
        returns: (bool) whether or not hand is blackjack
        """
        if len(self.hand) > 2:
            return False
        if self.hand[0].face == Face.ACE:
            if self.hand[1].face in [Face.KING, Face.QUEEN, Face.JACK, Face.TEN]:
                return True
        if self.hand[1].face == Face.ACE:
            if self.hand[0].face in [Face.KING, Face.QUEEN, Face.JACK, Face.TEN]:
                return True
        return False

    def isBust(self):
        """ Return true if hand is a busted hand """
        return self.getHandValue() > 21







