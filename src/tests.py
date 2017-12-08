from gameState import WinStates, GameState
from deck import Hand, Card, Deck, Suit, Face
from game import Game


def checkActions():
    game = Game(False, 'optimal', 100, 100, 0)
    gamestate = game.gameState
    hand = Hand()
    status = []

    # tests a playable hand (9,4)
    hand.receiveCard(Card(Face.NINE, Suit.CLUBS))
    hand.receiveCard(Card(Face.FOUR, Suit.CLUBS))
    gamestate.playerHands = [hand]
    actions = gamestate.player.getValidActions(gamestate)
    status.append(actions == ['HIT', 'STAND', 'DOUBLE DOWN'])

    # tests a doubles hand hand (9,9)
    hand.hand[1] = (Card(Face.NINE, Suit.HEARTS))
    gamestate.playerHands = [hand]
    actions = gamestate.player.getValidActions(gamestate)
    status.append(actions == ['HIT', 'STAND', 'DOUBLE DOWN', 'SPLIT'])

    # tests blackjack (Ace, King)
    hand.hand[0] = (Card(Face.ACE, Suit.HEARTS))
    hand.hand[1] = (Card(Face.KING, Suit.HEARTS))
    gamestate.playerHands = [hand]
    actions = gamestate.player.getValidActions(gamestate)
    status.append(actions == ['STAND'])

    # tests a soft hand hand (Ace,King, 3)
    hand.receiveCard(Card(Face.THREE, Suit.CLUBS))
    gamestate.playerHands = [hand]
    actions = gamestate.player.getValidActions(gamestate)
    status.append(actions == ['HIT','STAND'])

    # tests a bust hand (Ace, King, 3, 9)
    hand.receiveCard(Card(Face.NINE, Suit.CLUBS))
    gamestate.playerHands = [hand]
    actions = gamestate.player.getValidActions(gamestate)
    status.append(actions == ['STAND'])

    return status

def checkHand():
    status = []
    hand = Hand()

    # empyt starting hand
    status.append(hand.getNumCards() == 0)
    status.append(hand.getHandValue() == 0)

    # correctly appends card
    card1 = Card(Face.NINE, Suit.CLUBS)
    hand.receiveCard(card1)
    status.append(hand.getNumCards() == 1)
    status.append(hand.getHandValue() == 9)

    # checks for correct isDoubles call
    hand.receiveCard(card1)
    status.append(hand.isDoubles())
    hand.hand[1] = Card(Face.ACE, Suit.DIAMONDS)
    status.append(not hand.isDoubles())

    # Check for blackjack
    status.append(not hand.isBlackjack())
    hand.hand[0] = Card(Face.KING, Suit.CLUBS)
    status.append(hand.isBlackjack())

    # checks for soft and hard hands
    status.append(hand.isHard())
    status.append(not hand.isSoft())
    hand.receiveCard(Card(Face.QUEEN, Suit.HEARTS))
    status.append(hand.isHard())
    status.append(not hand.isSoft())

    # checks for bust
    status.append(not hand.isBust())
    hand.receiveCard(Card(Face.SEVEN, Suit.SPADES))
    status.append(hand.isBust())

    # checks for 4 aces corner case
    hand.hand[0] = Card(Face.ACE, Suit.DIAMONDS)
    hand.hand[2] = Card(Face.ACE, Suit.DIAMONDS)
    hand.hand[3] = Card(Face.ACE, Suit.DIAMONDS)
    status.append(hand.getHandValue() == 14)

    return status


print('Test #1: Correct Hand Functionality')
if all(test == True for test in checkHand()[:4]):
    print('Pass')
else:
    print ('Fail')

print('Test #2: Correct Blackjack Detection')
if all(test == True for test in checkHand()[6:8]):
    print('Pass')
else:
    print ('Fail')

print('Test #3: Correct Pair Detection')
if all(test == True for test in checkHand()[4:6]):
    print('Pass')
else:
    print ('Fail')

print('Test #4: Correct Hard/Soft Detection')
if all(test == True for test in checkHand()[8:12]):
    print('Pass')
else:
    print ('Fail')

print('Test #5: Correct Bust Detection')
if all(test == True for test in checkHand()[12:14]):
    print('Pass')
else:
    print ('Fail')

print('Test #6: 4 Aces Corner Case')
if checkHand()[14]:
    print('Pass')
else:
    print ('Fail')

print('Test #7: Correct Actions for Playable Hand')
if checkActions()[0]:
    print('Pass')
else:
    print ('Fail')

print('Test #8: Correct Actions for Doubles Hand')
if checkActions()[1]:
    print('Pass')
else:
    print ('Fail')

print('Test #9: Correct Actions for Blackjack Hand')
if checkActions()[2]:
    print('Pass')
else:
    print ('Fail')

print('Test #10: Correct Actions for Soft Hand')
if checkActions()[3]:
    print('Pass')
else:
    print ('Fail')

print('Test #11: Correct Actions for Bust Hand')
if checkActions()[4]:
    print('Pass')
else:
    print ('Fail')
