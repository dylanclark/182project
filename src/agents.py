from util import raiseNotDefined
from util import raiseErrorAtLoc
import random
from actions import Actions
from diskIO import readPolicy

class Agent():
    """
    Base Agent class that all dealers and players inherit from
    they all implement getAction
    """
    # Return action that happens
    def getAction(self, gameState):
        raiseNotDefined()



class Dealer(Agent):
    """ Dealer agent for blackjack games """
    def getAction(self, gameState):
        """
        Return action dealer must take based on rules
        input: gameState of current game
        return: action the dealer takes in the state
        """
        dealerHand = gameState.getDealerHand()
        if dealerHand.getHandValue() >= 17:
            return Actions.STAND
        else:
            return Actions.HIT


class Player(Agent):
    """
    Base player class that all player types inherit fromt
    """
    def __init__(self, startingMoney):
        """ Set the players amount of money and bet amount """
        self.money = int(startingMoney)
        self.betAmt = 10
        self.wins = 0
        self.loses = 0

    def getMoney(self):
        """ return: (int) amount of money left """
        return self.money

    def getBetAmt(self):
        """ return: (int) amount of money to bet """
        return self.betAmt

    def payout(self, amount):
        """
        Apply payout to player
        input: (int) amount to add (or remove if lose)
        returns: nothing
        """
        self.money += amount

    def getAllActions(self):
        """
        return: (list) of all possible Actions
        """
        return [Actions.HIT, Actions.STAND, Actions.DOUBLE_DOWN, Actions.SPLIT]

    def getValidActions(self, gameState):
        """
        Get valid actions based on gamestate
        input: gameState of hand
        returns: list of valid actions the player can take
        """
        validActions = []
        # Player may have split and have multiple hands, get current one
        # from the gameState
        try:
            playerHand = gameState.getCurrentPlayableHand()
        except IndexError as e:
            return []

        if playerHand.isBlackjack():
            return [Actions.STAND]

        if Actions.isHitValid(playerHand):
            validActions.append(Actions.HIT)

        if Actions.isStandValid(playerHand):
            validActions.append(Actions.STAND)

        if Actions.isDoubleDownValid(playerHand, gameState):
            validActions.append(Actions.DOUBLE_DOWN)

        if Actions.isSplitValid(playerHand, gameState):
            validActions.append(Actions.SPLIT)

        return validActions

    def bet(self, gameState):
        """
        Bet either self.betAmt or the max money you have if you have less than that
        returns: (int) amount of the bet
        returns: (int) amount for player to bet
        """
        if self.money < self.betAmt:
            return self.money
        else:
            return self.betAmt

class Random(Player):
    """
    A Random blackjack player
    Chooses randomly from valid actions at every state
    """
    def __init__(self, startingMoney):
        super().__init__(startingMoney)

    def getAction(self, gameState):
        return random.choice(self.getValidActions(gameState))

class UserPlayer(Player):
    """
    User player agent for command line playing of blackjack
    """
    def __init__(self, startingMoney):
        super().__init__(startingMoney)

    def getAction(self, gameState):
        """
        GetAction for UserPlayer prints valid actions and asks for input for the action to take
        input: gameState of current game
        returns: action to take
        """
        dealerHand = gameState.getDealerHand()
        playerHand = gameState.getCurrentPlayableHand()

        # Get and display valid actions
        actions = self.getValidActions(gameState)
        print("Your move!\n You may choose one of {}".format(", ".join(actions)))
        help_string = "HIT: 'h' or 'hit', STAND: 's' or 'stand', SPLIT: 'sp' or 'split', DOUBLE DOWN: 'd' or 'double'\n"

        # Receive user input for action to take
        while(True):
            actionStr = input('---> ')

            if Actions.HIT in actions and (actionStr == 'h' or actionStr == 'hit'):
                return Actions.HIT
            elif Actions.STAND in actions and (actionStr == 's' or actionStr =='stand'):
                return Actions.STAND
            elif Actions.SPLIT in actions and (actionStr == 'sp' or actionStr =='split'):
                return Actions.SPLIT
            elif Actions.DOUBLE_DOWN in actions and (actionStr == 'd' or actionStr =='double'):
                return Actions.DOUBLE_DOWN
            else:
                print("Unrecognized or invalid action, please try again\n {}".format(help_string))

class OptimalPlayer(Player):
    """
    An 'optimal' blackjack player based on strategy found at https://wizardofodds.com/game/blackjack/strategy/8-decks
    Policy is hardcoded in a csv, read into memory, and player acts determinsitically based on the policy
    """
    def __init__(self, startingMoney):
        """ Init parent and load the policy from disk """
        super().__init__(startingMoney)
        self.loadPolicy()

    def loadPolicy(self):
        """ Use diskIO module to load policy from disk """
        self.policy = readPolicy("../policy/optimal.csv")


    def getHandType(self, playerHand):
        """ Type of hand for dictionary lookups """
        playerHand.getHandValue()
        if playerHand.isDoubles():
            return 'double'
        elif playerHand.isHard():
            return 'hard'
        else:
            return 'soft'

    def getPlayerVal(self, playerHand, handType):
        """
        Get the playerVal key in the policy dictionary
        in the policy, key for a double is not the value of both of them but just the card that's doubled
        For soft and hard hands, though, the key is the value of the hand
        """
        if handType == 'double':
            cards = playerHand.getCards()
            card = cards[0]
            value = card.getValue()
            # normal card, non ace
            if type(value) is int:
                return value
            # else its an ace, so its an 11 in our csv
            else:
                return 11
        else:
            return playerHand.getHandValue()

    def getDealerVal(self, dealerHand):
        """ Return dealer hand value """
        return dealerHand.getHandValue()

    def getAction(self, gameState):
        """
        Get the features of the hand and lookup in policy which action to return
        """
        dealerHand = gameState.getDealerHand()
        playerHand = gameState.getCurrentPlayableHand()

        legalActions = self.getValidActions(gameState)

        # params for policy.getActionsFromPolicy
        handType = self.getHandType(playerHand)

        # If split not allowed (after a previous split in same hand), the hand is no longer
        # considered a doubles but is hard or soft
        if (handType == 'double' and Actions.SPLIT not in legalActions):
            handType = 'hard' if playerHand.isHard() else 'soft'

        playerVal = self.getPlayerVal(playerHand, handType)
        dealerVal = self.getDealerVal(dealerHand)

        actionList = self.policy.getActionsFromPolicy(handType, playerVal, dealerVal)
        
        # Return legal action from policy
        for action in actionList:
            if action in legalActions:
                return action

class Expectimax(Player):
    """
    Player that implements an expectimax policy for choosing actions
    """
    def __init__(self, startingMoney):
        # Init player parent
        super().__init__(startingMoney)
        self.avgVal = float(4*(1+2+3+4+5+6+7+8+9+10+10+10+10))/float(52)

    def getAction(self, gameState):
        """
        GetAction for UserPlayer prints valid actions and asks for input for the action to take
        input: gameState of current game
        returns: action to take
        """

        """
        Get the expected dealer hand value using the dealers current hand and
        the average value of a deck
        """
        averageValue = self.avgVal
        dVal = gameState.dealerHand.getHandValue()
        while dVal < 17:
            dVal += averageValue
        hand = gameState.getCurrentPlayableHand()
        handVal = hand.getHandValue()
        splitPossible = hand.isDoubles()

        # Overall function that tests for an end state and returns a score
        def overall(self, state, agent, pStand, dealerVal, bet):
            if pStand or state > 21:
                pBust = state > 21
                if pBust:
                    return [-bet]
                elif dealerVal > 21:
                    return [bet]
                elif dealerVal > state:
                    return [-bet]
                elif state > dealerVal:
                    return [bet]
                else:
                    return [0]

            if agent == 0:
                return maxVal(self, state, agent, pStand, dealerVal, bet)
            else:
                return expVal(self, state, agent, pStand, dealerVal, bet)

        # if its the agents turn, then take the maximum of the possible actions
        def maxVal(self, state, agent, pStand, dealerVal, bet):

            # initialize a highschore (in a list so we can add optimal action)
            highScore = [float('-inf')]

            # get possible actions for first turn
            if splitPossible:
                actions = [Actions.HIT, Actions.STAND, Actions.DOUBLE_DOWN, Actions.SPLIT]
            else:
                actions = [Actions.HIT, Actions.STAND, Actions.DOUBLE_DOWN]

            # keep the max action score of the actions
            for action in actions:
                if action == Actions.SPLIT:
                    score1 = overall(self, state/2, 1, False, dealerVal, bet)
                    score2 = overall(self, state/2, 1, False, dealerVal, bet)
                    if score1[0] + score2[0] >= highScore[0]:
                        highScore = [score1[0] + score2[0], action]
                else:
                    nS = generateSuccessor(state, pStand, bet, action)
                    score = overall(self, nS[0], 1, nS[1], dealerVal, nS[2])
                    if score[0] >= highScore[0]:
                        highScore = [score[0], action]
            return highScore

        # for all subsequent turns, take the expected val of possible actions
        def expVal(self, state, agent, pStand, dealerVal, bet):

            highScore = [0]
            actions = [Actions.HIT, Actions.STAND]

            # accumulate expected val of actions
            for action in actions:
                nS = generateSuccessor(state, pStand, bet, action)
                score = overall(self, nS[0], 1, nS[1], dealerVal, nS[2])
                highScore[0] += float(score[0])/float(len(actions))
                # print(state.getPlayerHands() == og, '****')
            return highScore

        # depending on the action, update the card val, stand status, and bet
        def generateSuccessor(state, pStand, bet, action):
            averageValue = self.avgVal
            if action == Actions.HIT:
                newState = state + averageValue
                newStand = pStand
                newBet = bet
            if action == Actions.STAND:
                newStand = True
                newState = state
                newBet = bet
            if action == Actions.DOUBLE_DOWN:
                newBet = bet*2
                newState = state + averageValue
                newStand = True
            return [newState, newStand, newBet]

        return overall(self, handVal, 0, False, dVal, gameState.bets[gameState.playerHandIdx])[1]


"""                                             """
"""                    Q-LEARNING               """
"""                                             """

class QState():
    """
    A reduced state space containing only vital info
    needed for the Q-learner, with overriden hash and eq
    methods to determine state equality in dictionary
    """
    def __init__(self, gameState):
        dealerHand = gameState.getDealerHand()
        playerHand = gameState.getCurrentPlayableHand()

        self.dealerVal = dealerHand.getHandValue()
        self.playerVal = playerHand.getHandValue()
        self.hard = playerHand.isHard()

    def __eq__(self, other):
        """ Two QStates equal IFF dealervalue, playervalue, and hand hardness are same """
        inst = isinstance(other, QState)
        dv = self.dealerVal == other.dealerVal
        pv = self.playerVal == other.playerVal
        h = self.hard == other.hard
        return inst and dv and pv and h

    def __hash__(self):
        """ Keys in dictionary based only on these features,
        not other instance features
        """
        return hash( (self.dealerVal, self.playerVal, self.hard) )


class QLearning(Player):
    """
    Implements a QLearning algorithm for policy improvement to play blackjack
    """
    
    def __init__(self, startingMoney, numTraining, discount=.3):
        """
        Init parent, init Q dictionary and N dictionary, 
        and varaibles to keep track of training vs testing 
        """
        super().__init__(startingMoney)
        self.discount = float(discount)
        self.numTraining = int(numTraining)
        self.QValues = {}                   # Q(s,a) nested dictionary, value of a state is QValues[<Qstate>][<action>]
        self.NVisited = {}                  # N(s,a) nested dictionary, number of updates to QValues is NVisited[<Qstate>][<action>]
        self.omega = .97                    # Used in hyperharmonic alpha calculation
        self.episodeNumber = 0

    def isTraining(self):
        """ Is agent training or testing """
        return self.episodeNumber < self.numTraining

    def isTesting(self):
        """ Is agent training or testing """
        return not self.isTraining()

    def getEpsilon(self):
        """
        Get epsilon value for Q value updates
        While training, bias towards high randomness
        When testing, epsilon is 0 for determinsitic action 
        """
        fracPlayed = self.episodeNumber / float(self.numTraining)
        if fracPlayed < .9:
            return .9
        elif fracPlayed < 1:
            return .5
        else:
            return 0.0

    def getAlpha(self, state, action):
        """ 
        Get the learning rate for a state, action pair
        Uses hyperharmonic strategy to have higher learning rate 
        for states that havent been visited as much
        alpha = 1 / (N(s,a) ^ omega)
        """
        qstate = QState(state)
        if qstate not in self.NVisited:
            self.NVisited[qstate] = {
                Actions.HIT : 0,
                Actions.STAND : 0,
                Actions.DOUBLE_DOWN : 0,
                Actions.SPLIT : 0
            }
        self.NVisited[qstate][action] += 1
        return 1 / float(self.NVisited[qstate][action] ** self.omega)

    def getQValue(self, gameState, action):
        """ Return Q(s,a) """
        qstate = QState(gameState)

        if qstate not in self.QValues:
            # if state is a bust, the value is just -100
            if qstate.playerVal > 21 and qstate.dealerVal <= 21:
                if qstate.dealerVal <= 21:
                    return -100.0
                else:
                    return 0
            else:
                # Insert new state into dict if never visted
                self.QValues[qstate] = {
                    Actions.HIT: 0.0,
                    Actions.STAND: 0.0,
                    Actions.DOUBLE_DOWN: 0.0,
                }
                # no split unless even number
                if (qstate.playerVal % 2 == 0):
                    self.QValues[qstate][Actions.SPLIT] = 0.0

        return self.QValues[qstate][action]

    def getValue(self, state):
        '''
        Returns max_action Q(state, action)
        '''
        if not self.getValidActions(state):
            return 0.0

        else:
            return self.getQValue(state, self.computeActionFromQValues(state))

    def computeActionFromQValues(self, state):
        '''
        Computes best action to take in a state
        '''

        #initializes max value, action
        max_value = -float("inf")
        max_action = None

        # iterates through possible actions and their values, returning argmax
        for action in self.getValidActions(state):
            value = self.getQValue(state, action)
            if value > max_value:
                max_value = value
                max_action = action
            elif value == max_value:
                max_action = random.choice((action, max_action))

        return max_action

    def getAction(self, state):
        """ Get action from state using epsilon-greedy strategy """
        legalActions = self.getValidActions(state)
        action = None
        self.episodeNumber += 1
        if random.uniform(0,1) < self.getEpsilon():
            return random.choice(legalActions)
        else:
            return self.computeActionFromQValues(state)

    def update(self, state, action, nextState, reward):
        """
        Apply update rule update(s,a,r,s') 
        Q(s,a) += alpha [r + discount * max_a Q(s',a) - Q(s,a)]
        """
        qOriginal = self.getQValue(state, action)
        error = self.getAlpha(state, action) * (reward + self.discount * self.getValue(nextState) - qOriginal)
        legalActions = self.getValidActions(state)
        qState = QState(state)
        self.QValues[qState][action] = qOriginal + error

