from deck import Deck
from deck import Card
from deck import Face
from deck import Suit
from deck import Hand
from agents import Dealer
from agents import UserPlayer
from actions import Actions
from util import vPrint
from util import raiseErrorAtLoc

from copy import deepcopy
from time import sleep
from functools import reduce
# PLAYER IS IDX 0, TURN 0
# DEALER IS IDX 1, TURN 1


"""
The outcomes of a hand. Win pays 1.0, blackjack pays 1.5, push pays even, lose loses bet
"""
class WinStates:
    WIN = 'WIN'
    BLACKJACK = 'BLACKJACK'
    PUSH = 'PUSH'
    LOSE = 'LOSE'

class GameState():
    """
    GameState class gets dealer, player, hands, tracks turns, and takes actions
    """
    def __init__(self, verbose, dealer, dealerHand, player, playerHands, deck, bets = None,playerHandIdx = 0, turn = 0):
        self.verbose = verbose
        self.turn = turn
        self.dealer = dealer
        self.player = player
        self.deck = deck
        self.dealerHand = dealerHand
        # List because player can split
        self.playerHands = playerHands
        # Bets is list of bets passed in or if none, its an initial bet for one hand
        # There will be a bet for each hand in this list, ordered same wasy as playerHands
        self.bets = bets if bets is not None else [self.player.getBetAmt()]
        self.playerHandIdx = playerHandIdx
    
    def getBets(self):
        return self.bets

    def copy(self):
        """ A copy of a state is the same state but we need to do a deep copy of each hand to ensure altering hands in the 
            copied state doesn't affect the original state
        """
        copyDealerHand = deepcopy(self.dealerHand)
        copyPlayerHands = [deepcopy(hand) for hand in self.playerHands]
        
        return GameState(self.verbose, self.dealer, copyDealerHand, self.player, copyPlayerHands, self.deck, self.bets,  self.playerHandIdx, self.turn)
 
        
    ########### OBSERVING INFO ABOUT STATE ###############
    def getNumPlayerHands(self):
        """ Return the number of hands player has (up to 4 allows w/ multiple splits) """
        return len(self.playerHands)

    def getCurrentPlayableHand(self):
        """ Return the hand in playerHands corresponding to playerHandIdx """
        return self.playerHands[self.playerHandIdx]

    def getPlayerHandIdx(self):
        """ Return the index in list self.playerHands corresponding to which hand
        the player is playing """
        return self.playerHandIdx

    def getPlayerHands(self):
        """
        Returns player's hand list
        """
        return self.playerHands

    def getDealerHand(self):
        """
        Return dealer's hand
        """
        return self.dealerHand

    def isPlayerTurn(self):
        """
        Returns: True if players turn, else False
        """
        return self.turn == 0
    def isDealerTurn(self):
        """
        Returns: True if dealer's turn, else False
        """
        return not self.isPlayerTurn()

    def isTerminal(self):
        """
        GameState terminal if player busts on last hand, dealer done with his turn, or player gets blackjack
        Returns: True if terminal, else False
        """
        playerBust = self.playerHands[len(self.playerHands) -1].isBust()
        #reduce(lambda a, b: a and b, [hand.getHandValue() > 21 for hand in self.playerHands])
        playerBlackjack = len(self.playerHands) == 1 and self.playerHands[0].isBlackjack()
        dealerDone = self.dealerHand.getHandValue() >= 17
        return playerBust or playerBlackjack or dealerDone


    def getWinState(self):
        """
        Returns: List of WinState objects corresponding to a terminal GameState for each player hand
        """
        # No win state if hand not done
        if not self.isTerminal():
            return None

        winStatesForHands = []
        for hand in self.playerHands:
            # Player has blackjack
            if hand.isBlackjack():
                # it's a push if dealer also has blackjack,
                # so deal the dealer's second card and see
                if self.dealerHand.nCards == 1:
                    self.dealDealerCard()
                if self.dealerHand.isBlackjack():
                    winStatesForHands.append(WinStates.PUSH)
                else:
                    winStatesForHands.append(WinStates.BLACKJACK)

            # Player has higher hand total, win if player didn't bust, else lose
            elif hand.getHandValue() > self.dealerHand.getHandValue():
                if hand.isBust():
                    winStatesForHands.append(WinStates.LOSE)
                else:
                    winStatesForHands.append(WinStates.WIN)

            # Player has lower hand total, win if dealer busted, else lose
            elif hand.getHandValue() < self.dealerHand.getHandValue():
                if self.dealerHand.isBust():
                    winStatesForHands.append(WinStates.WIN)
                else:
                    winStatesForHands.append(WinStates.LOSE)

            # Equal hand totals, push as long as player didn't bust
            elif hand.getHandValue() == self.dealerHand.getHandValue():
                if hand.isBust():
                    winStatesForHands.append(WinStates.LOSE)
                else:
                    winStatesForHands.append(WinStates.PUSH)

            else:
                raiseErrorAtLoc()

        return winStatesForHands

    def getPayout(self, winState, handIdx):
        """
        Calculate the payout from a WinState
        returns: (int) amount to payout to player
        """
        if winState == WinStates.WIN:
            return self.bets[handIdx]
        elif winState == WinStates.BLACKJACK:
            return 1.5 * self.bets[handIdx]
        elif winState == WinStates.PUSH:
            return 0
        else:
            return -1 * self.bets[handIdx]

    ################## DEALING METHODS #####################

    def dealCard(self):
        """
        Deal a card
        returns: a Card object from deck
        """
        return self.deck.getRandomCard()

    def dealPlayerCard(self, handIdx = 0):
        """
        Deal a card to player by adding a dealt card to their hand
        input: (int) handIdx the index in playerHands list corresponding to hand to deal to
        returns: nothing
        """
        newCard = self.dealCard()
        vPrint("Player dealt {}".format(newCard.getPrettyStr()), self.verbose)
        self.playerHands[handIdx].receiveCard(newCard)

    def dealDealerCard(self):
        """
        Deal a card to dealer by adding a dealt card to their hand
        returns: nothing
        """
        newCard = self.dealCard()
        if self.verbose:
            vPrint("Dealer dealt {}".format(newCard.getPrettyStr()), self.verbose)
        self.dealerHand.receiveCard(newCard)

    def initialDeal(self):
        """
        Deal an initial hand of 2 cards to player and one to dealer
        returns: nothing
        """
        for i in range(2):
            self.dealPlayerCard()
        self.dealDealerCard()

    ################## ALTERING STATES ###################

    def applyPayout(self, payout):
        """
        Apply a payout to the player
        input: payout amount
        returns: new gameState with the payout applied, turn reset to 0, hand reset to first, and default bet for one hand
        """
        newState = GameState(self.verbose, self.dealer, self.dealerHand, self.player, self.playerHands, self.deck)
        newState.player.payout(payout)
        return newState

    def makeDealerTurn(self):
        """
        Make it the dealers turn, after a playre stands or busts
        """
        if self.isDealerTurn():
            raiseErrorAtLoc()
        else:
            self.turn = 1

    def resetHands(self):
        """
        Reset the hands to empty hands for a new deal
        returns: nothing
        """
        self.playerHands = [Hand()]
        self.dealerHand = Hand()

    def splitPlayableHand(self):
        """
        Split the hand corresponding to player hand idx
        Create two hands, each with one of the cards and one newly dealt one and add them to playerHands list
        returns: nothing
        """
        # Get the hand to split and remove it from the list
        handBeingSplit = self.playerHands.pop(self.playerHandIdx)

        if not handBeingSplit.isDoubles():
            raiseErrorAtLoc()

        # Create a new hand, give it the second card from original and remove from original
        newHand = Hand()
        newHand.receiveCard(handBeingSplit.hand.pop(1))

        # Deal each one a new card
        handBeingSplit.receiveCard(self.dealCard())
        newHand.receiveCard(self.dealCard())

        # Insert new hands back into the list where original was
        self.playerHands.insert(self.playerHandIdx, handBeingSplit)
        self.playerHands.insert(self.playerHandIdx + 1, newHand)

        # Apply the bet to new hand
        self.bets.insert(self.playerHandIdx + 1, self.player.getBetAmt())
    
    ##################### THE ACTION #####################

    def generatePlayerSuccessor(self, action):
        """
        Generate the successor gamestate after the player action
        input: (Action) player's action
        returns: (GameState) new gameState object after the action has been taken
        """
        # copy gamestate
        newState = self.copy()

        if action == Actions.HIT:
            # Deal a card to player
            newState.dealPlayerCard(newState.playerHandIdx)

            # If current played hand is now busted, move on to next one in the new state
            # (if it's the last one, game will determine all player hands are busted and will break the
            # game loop, so no worries about the index going over the number of hands)
            if newState.getCurrentPlayableHand().isBust():
                newState.playerHandIdx += 1
            if newState.playerHandIdx == len(self.playerHands):
                newState.makeDealerTurn()

        elif action == Actions.STAND:
            # If standing on a hand, either move play to the next hand player has or to dealer
            # if player has played all hands
            if self.playerHandIdx == len(self.playerHands) - 1:
                newState.makeDealerTurn()
            else:
                newState.playerHandIdx += 1

        elif action == Actions.SPLIT:
            vPrint("Splitting player's hand...\nPlayer adding bet to new hand...\n", self.verbose)
            newState.splitPlayableHand()

        elif action == Actions.DOUBLE_DOWN:
            vPrint("Doubling down the bet on the hand...\nReceiving final card...\n", self.verbose)
            newState.dealPlayerCard()
            newState.bets[self.playerHandIdx] += self.player.getBetAmt()
            newState.makeDealerTurn()
        return newState

    def generateDealerSuccessor(self, action):
        """
        Generate the successor gamestate after the dealer action
        input: (Action) dealer's action
        returns: (GameState) new gameState object after the action has been taken
        """
        # copy game state
        newState = self.copy() 

        if action == Actions.HIT:
            newState.dealDealerCard()
        elif action == Actions.STAND:
            pass
        else:
            print("Dealer cant {}!\n".format(action))

        return newState

