from deck import Hand

class Actions:
    """ Actions that a player and delaer can take """
    HIT = 'HIT'
    STAND = 'STAND'
    DOUBLE_DOWN = 'DOUBLE DOWN'
    SPLIT = 'SPLIT'

    allActs = [HIT, STAND, DOUBLE_DOWN, SPLIT]

    def isHitValid(hand):
        """ Returns: (bool) True if agent can hit, else false """
        return hand.getHandValue() < 21

    def isStandValid(hand):
        """ Returns: (bool) True if agent can stand, else false (they can always stand) """
        return True

    def isSplitValid(hand, gameState):
        """ Returns: (bool) True if agent can split their hand, else false
        Can only split a two card hand, isDoubles ensures only 2 cards
        Can only split up to 2 hands!
        """
        return hand.isDoubles()  and gameState.getNumPlayerHands() == 1

    def isDoubleDownValid(hand, gameState):
        """ Returns: (bool) True if agent can double down, else false
        Can't double down after a split, so ensure just one hand and that
        the action is being taken after initial deal """
        return gameState.getNumPlayerHands() == 1 and gameState.getCurrentPlayableHand().getNumCards() == 2
