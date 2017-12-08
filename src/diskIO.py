from actions import Actions
from pprint import pprint
from util import raiseErrorAtLoc
import csv

policyActionMap = {
    0 : [Actions.HIT],
    1 : [Actions.STAND],
    2 : [Actions.DOUBLE_DOWN],
    3 : [Actions.SPLIT],
    4 : [Actions.DOUBLE_DOWN, Actions.HIT], # Double if allowed, else stand
    5 : [Actions.DOUBLE_DOWN, Actions.STAND] # Double if allowed, else stand
}

class Policy():
    """
    Policy is hard-coded optimal policy read in from a CSV


    dictionary lookup for hands to get list of actions

    main dict
        keys: hard, soft, or double
        values: player hand dictionaries

        player hand dicts:
            keys: value of hand (for hard, soft) or the val of double card (for doubles)
            values: dealer hand dictionaries

            dealer hand dictionaries:
                keys: dealer's card
                values: list of actions to take (list because lets say q-learning says to double,
                but you've just split and so now can't double. need a backup

    """
    def __init__(self):
        """ Init the nested dictionaries """ 
        playerHandHard = {}
        playerHandSoft = {}
        playerHandDouble = {}
        for i in range (4, 22):
            playerHandHard[i] = self.initDealerCardDict()
            playerHandSoft[i] = self.initDealerCardDict()
        for i in range(2,12):
            playerHandDouble[i] = self.initDealerCardDict()

        self.policy = {
            'hard' : playerHandHard,
            'soft' : playerHandSoft,
            'double' : playerHandDouble
        }

    def initDealerCardDict(self):
        """ Init a subdict for policy """
        dealerCardDict = {}
        for i in range(2,12):
            dealerCardDict[i] = None
        return dealerCardDict

    def insertActions(self, action, hand_type, player_val, dealer_val):
        """ Associate the action with the handtype, dealer val, player val of the hand """
        try:
            self.policy[hand_type][player_val][dealer_val] = action
        except Exception as e:
            print("Error inserting into policy dictionary! {}\n".format(e))

    def getActionsFromPolicy(self, hand_type, player_val, dealer_val):
        """ Given hand type, player value, delaer value, return the
        action policy dictates (or actions if more than one) """

        actions = None
        try:
            actions = self.policy[hand_type][player_val][dealer_val]
        except Exception as e:
            print("Error getting policy from dictionary! {}\n".format(e))
        return actions

def readPolicy(fname):
    """
    Read the policy csv stored at fname into a policy class and return the object
    The csv format is pretty super duper rigid and hardcoded so this is messy 
    """
    policy = Policy()
    dealerValueList = [i for i in range(2,12)]

    with open(fname, 'r') as f:
        lines = f.read().splitlines()
        for line_no, line in enumerate(lines):
            if line_no == 0:
                pass
            else:
                elems = line.split(',')
                player_val = int(elems[0]) # first col is player hand
                player_type = elems[1] # second col is type of hand (soft, hard, double)

                actions = elems[2:]
                listActionLists = list(map(lambda val :policyActionMap[int(val)], actions))

                for idx, actions in enumerate(listActionLists):
                    dealerValue = dealerValueList[idx] #map 0-9 to 2-11 for what dealer has

                    policy.insertActions(actions, player_type, player_val, dealerValue)
    return policy 

class QDictIO():
    """ A class to write a Q dictionary of form Q[state][action] = Q(s,a) to the disk for analyzing """
    def __init__(self, QDict):
        """ 
        Take a Q(s,a) dictionary from QLearning player to write to disk
        """
        self.Q = QDict

    def write(self):
        """ Write the Q dictionary to disk at Q.csv """
        with open("../Q.csv", 'w+') as f:
            
            fieldnames = ['pv','dv','hard','policy', 'stand','hit','split','double']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            sortByPV = sorted(self.Q.keys(), key = lambda state: state.playerVal)
            for state in sortByPV:
                pv = state.playerVal
                dv = state.dealerVal
                hard = state.hard
                actionD = self.Q[state]
                hit = actionD[Actions.HIT]
                split = actionD[Actions.SPLIT] if Actions.SPLIT in actionD else None
                double = actionD[Actions.DOUBLE_DOWN]
                stand = actionD[Actions.STAND]
                bestAction = None 
                bestVal = float('-inf')
                sortedActions = sorted(actionD.keys(), key = lambda action: self.Q[state][action])
                sortedActions.reverse()
               
                writeDict = {
                    'pv' : pv,
                    'dv' : dv,
                    'hard': hard,
                    'policy' : '-'.join(sortedActions[:3]),
                    'stand' : stand,
                    'double' : double,
                    'hit' : hit,
                    'split' : split
                }
                writer.writerow(writeDict)

