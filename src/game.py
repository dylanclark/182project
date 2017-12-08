from deck import Deck
from deck import Card
from deck import Face
from deck import Suit
from deck import Hand
from agents import Dealer
from agents import UserPlayer
from agents import OptimalPlayer
from agents import Expectimax
from agents import QLearning
from agents import Random
from actions import Actions
from util import vPrint
from util import raiseErrorAtLoc
from gameState import WinStates
from gameState import GameState
from diskIO import QDictIO

from time import sleep
from functools import reduce
# PLAYER IS IDX 0, TURN 0
# DEALER IS IDX 1, TURN 1

class Game():
    """
    Game class instantiates dealer and player and the initial game state. It plays the game by playing
    a sequence of hands until the player bustso or until the nHands value is reached (nHands should be used
    when not using a user-agent so if the agent keeps winning the game doesnt go on forever)
    """
    def __init__(self, verbose, agentType, nHands, startingMoney, nTraining):
        """
        Initialize the game! Create dealer and player objects and an initial gameState
        input: verbose
            whether or not to print each step as agents play
        input: agentType
            string representing the type of agent to instantiate
        input: nHands
            number of hands to play at max if agent never busts
        input: startingMoney
            the amount of money the agent gets to start with
        input: nTraining
            the number of training hands to do for a qlearning player
        returns: nothing
        """
        self.verbose = verbose
        self.agentType = agentType
        self.nHands = int(nHands) + int(nTraining)
        self.nStartingHands = int(nHands) + int(nTraining)
        print("{} test {} train {} total".format(nHands, nTraining, self.nHands))
        self.startingMoney = startingMoney
        self.nTraining = int(nTraining)
        self.dealer = Dealer()
        self.player = self.createAgent(self.agentType, self.startingMoney, nTraining)

        self.agents = [self.player, self.dealer]

        # Clean slate
        dealerHand = Hand()
        playerHand = Hand()
        deck = Deck()

        # list because player can split
        playerHands = [playerHand]
        if self.player:
            initialBets = [self.player.getBetAmt()]
            # Create initial game state
            self.gameState = GameState(verbose, self.dealer, dealerHand, self.player, playerHands, deck, initialBets)

        self.q = self.agentType == 'qlearning'

    def isValidGame(self):
        """ Make sure we created the player correctly """
        if self.player is None:
            return False
        return True

    def createAgent(self, agentType, startingMoney, nTraining):
        """ Create an agent of the right type
        input: string agentType
            type of agent to create
        input: int startingMoney
            how much money the agent starts off with

        returns: An instantiated agent with startingMoney, or None if agent not supported yet
        """
        if (agentType == 'user'):
            return UserPlayer(startingMoney)
        elif (agentType == 'optimal'):
            return OptimalPlayer(startingMoney)
        elif (agentType == 'expectimax'):
            return Expectimax(startingMoney)
        elif (agentType == 'q-learning' or agentType == 'qlearning'):
            return QLearning(startingMoney, nTraining)
        elif (agentType == 'random'):
            return Random(startingMoney)
        else:
            print("Can't create other agent types at this point\n")
            return None


    def reportPerformance(self, aggregateOutcomes, payout, totalBet,  moneyLeft, maxAmtHad, minAmtHad):
        """
        Take the values from the playGame loop and output a summary of player performance over the hands 
        Return the stats to the game so they can be passed to statEngine
        """
        nHandsPlayed = sum(aggregateOutcomes.values())
        aggregatePercentages = {k : float(v) / float(nHandsPlayed) for k, v in aggregateOutcomes.items()}
        
        totalWinnings = payout
        houseEdge = - totalWinnings / float(totalBet)

        print("Counting all splits as two hands, there were {} hands played by the agent who started with ${}\n".format(nHandsPlayed, self.startingMoney))
        print("Most money ever had: {}\t Least money ever had: {}\n".format(maxAmtHad, minAmtHad))
        print("Money remaining after all hands:  ${}\n".format(moneyLeft))
        print("Total winnings {} on total bets of {} for a house edge of {:.1%}".format(totalWinnings, totalBet,  houseEdge))
        for state, number in aggregateOutcomes.items():
            print("{} : {} ({:.1%})\n".format(state, number, aggregatePercentages[state]))

        stats = {
                'nHands' : nHandsPlayed,
                'outcomes' : aggregateOutcomes,
                'percentages' : aggregatePercentages,
                'totalWinnings' : payout,
                'totalBet' : totalBet,
                'houseEdge' : houseEdge,
                }

        return stats
    def playGame(self):
        """ Loop through playing hands until agent out of money or we reach self.nHands
        input: none
        returns: stat dictionary with summary of performance

        """
        if(self.verbose):
            print("**** Welcome to CS182 Blackjack! ****\n\n\nNew game:\nYour starting money: {}\n".format(self.startingMoney))

        # Performance bookkeeping
        aggregateOutcomes = {
            WinStates.WIN : 0,
            WinStates.PUSH : 0,
            WinStates.BLACKJACK : 0,
            WinStates.LOSE: 0,
        }
        aggregatePayout = 0
        aggregateBet = 0
        minVal = int(self.startingMoney)
        maxVal = int(self.startingMoney)
        stats = None 
        # Game loop
        while(True):
            if self.nHands % 10000 == 0:
                print(self.nHands)

            # Play hand
            winStateList, payout, betAmount = self.playHand()

            # Performance tracking. Only track performance for Q-learner if it's out of training
            bookkeep = True
            if self.q:
                if((self.nStartingHands - self.nHands) < (self.nTraining)):
                    bookkeep = False
       
            if bookkeep:
                # Bookkeeping on performance
                for winState in winStateList:
                    aggregateOutcomes[winState] += 1
                aggregatePayout += payout
                aggregateBet += betAmount
    
                curMoney = self.gameState.player.getMoney()
                if curMoney > maxVal:
                    maxVal = curMoney
                if curMoney < minVal:
                    minVal = curMoney

            # Reset hands 
            self.gameState.resetHands()
            
            # if user player, ask if wants to play more
            if self.agentType == 'user' :
                sleep(2)
                cont = input("Another hand? y/n ---> ")
                if cont == "n" or cont == "N" or cont == "no":
                    break

            # Out of money or game over
            if self.nHands == 0 or self.gameState.player.getMoney() <= 0:
                stats = self.reportPerformance(aggregateOutcomes, aggregatePayout, aggregateBet, curMoney, maxVal, minVal)
                
                # If qlearner, write the policy to disk
                if self.q:
                    diskIO = QDictIO(self.player.QValues)
                    diskIO.write()
                break
        
        return stats


    def playHand(self):
        """
        Play a hand! deal to the player and dealer, get players actions, change gameState, get dealer's actions,
        determine winner, etc

        input: none
        returns: Return winsState list for all hands, the payout across all hands, and the amount bet
        (multiple hands mentioned in case fo split)
        """

        vPrint("\n\n*************** NEW HAND ***************\n\n", self.verbose)

        self.nHands -= 1

        # Place bet and deal
        self.gameState.initialDeal()

        vPrint("New hand: Player bet: {}\tPlayer money: {}\n".format(self.player.getBetAmt(), self.player.getMoney()), self.verbose)
        vPrint("...Dealing...\n", self.verbose)
    
        # for storing last actions of each hand for qlearning updates
        lastActions = []
        lastNewStates = []
        lastPrevStates = []
        
        # Hand loop
        while not self.gameState.isTerminal():
            # Player turn
            if self.gameState.isPlayerTurn():
                vPrint("***** Player's turn *****\n\n", self.verbose)
                for idx, hand in enumerate(self.gameState.getPlayerHands()):
                    vPrint("Player hand {}: {}\n".format(idx, hand.strFromHand()), self.verbose)

                vPrint("Player is currently playing hand {}\n".format(self.gameState.getPlayerHandIdx()), self.verbose)
                vPrint("Dealer's shown card: {}\n".format(self.gameState.dealerHand.strFromHand()), self.verbose)


                # Get action player takes in this state (will make sure its action for the hand they're playing)
                playerAction = self.player.getAction(self.gameState)

                vPrint("Player action is {}\n".format(playerAction), self.verbose)

                # Take the action
                newGameState = self.gameState.generatePlayerSuccessor(playerAction)

                # If Q learner player, update them or store their last action to update after the dealer plays
                if self.q:
                    # Still player turn, give a zero reward if playing same hand (didnt bust)
                    if newGameState.isPlayerTurn():
                        if newGameState.getPlayerHandIdx() == self.gameState.getPlayerHandIdx():
                            reward = 0
                            newGameState.player.update(self.gameState, playerAction, newGameState, reward)
                        else:
                            # Playing another hand, store the last action of this hand to update with hand rewards after eval
                            lastActions.append(playerAction)
                            lastPrevStates.append(self.gameState)
                            lastNewStates.append(newGameState)
                    # Its dealer turn, append the last action to update after hand eval
                    else:
                        lastActions.append(playerAction)
                        lastPrevStates.append(self.gameState)
                        lastNewStates.append(newGameState)

                # Update the gamestate
                self.gameState = newGameState
       
            # Dealer turn
            else:
                vPrint("***** Dealer's turn ****** \n\n", self.verbose)
                for idx, hand in enumerate(self.gameState.getPlayerHands()):
                    vPrint("Player hand {}: {}\n".format(idx, hand.strFromHand()), self.verbose)
                vPrint("Dealer's shown card: {}\n".format(self.gameState.dealerHand.strFromHand()), self.verbose)

                # Get dealers action
                dealerAction = self.dealer.getAction(self.gameState)

                vPrint("Dealer action is {}\n".format(dealerAction), self.verbose)

                # Take the action
                self.gameState = self.gameState.generateDealerSuccessor(dealerAction)

        # Evaluate who won
        winStates = self.gameState.getWinState()
        totalBet = sum(self.gameState.getBets())
        payouts = [self.gameState.getPayout(winState, handIdx) for handIdx, winState in enumerate(winStates)]

        # Update the qlearner with payouts based on their last actions
        if self.q:
            # Blackjack dealt so no actions, no update
            if len(lastActions) != len(payouts):
                    pass
            else:
                # send an update for each tuple of (s,a,r,s')
                for i in range(len(payouts)):
                    reward = payouts[i]
                    action =  lastActions[i]
                    orig_state = lastPrevStates[i]
                    new_state = lastNewStates[i]
                    self.gameState.player.update(orig_state, action, new_state, reward)
            # Reset the lists of update items
            lastActions = []
            lastPrevStates = []
            lastNewStates = []

        # Get the total payout and apply it, return the results to the game loop
        payout = reduce(lambda p1, p2: p1 + p2, payouts)

        # vPrint the results of each hand and total payout
        for idx, hand in enumerate(self.gameState.getPlayerHands()):
            vPrint("=============\n\nHand {}:\nPlayer has {}, dealer has {}\n\nResult of hand is a {} for the player, payout is {}\n\n=============\n\n".format(idx, hand.getHandValue(), self.gameState.dealerHand.getHandValue(), winStates[idx], payouts[idx]), self.verbose)
        vPrint("Total payout across all hands is {}\n".format(payout), self.verbose)

        self.gameState = self.gameState.applyPayout(payout)

        return (winStates, payout, totalBet)
