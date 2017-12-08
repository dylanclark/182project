from blackjack import main as runBlackjack
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from pprint import pprint
import sys
import numpy as np

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SCRIPT TO RUN BLACKJACK MANY TIMES WITH DIFF ARGS AND GENERATE GRAPHS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

folder = "../imgs/"
numTraining = 10000
numTesting  = 100000
startingMoney = 100000000


"""
GET ARGS TO RUN BLACKJACK 
"""
def getRandomArgs(n_test = numTesting):
    return "-a random -n {} -s {}".format(n_test, startingMoney).split(" ")

def getOptimalArgs(n_test = numTesting):
    return "-a optimal -n {} -s {}".format(n_test, startingMoney).split(" ")

def getExpectiArgs(n_test = numTesting):
    return "-a expectimax -n {} -s {}".format(n_test, startingMoney).split(" ")

def getQLearningArgs(n_train = numTraining, n_test = numTesting):
    return "-a qlearning -t {} -n {} -s {}".format(n_train, n_test, startingMoney).split(" ")


"""
Make a graph of win state ratios for each alg type, grouped by win state
"""
def makeInversePercentageAlgPlots(optimal_stats, random_stats, expecti_stats, q_stats):
    opt_pct = [optimal_stats['percentages']['WIN'], optimal_stats['percentages']['LOSE'], optimal_stats['percentages']['PUSH'], optimal_stats['percentages']['BLACKJACK']]

    ran_pct = [random_stats['percentages']['WIN'], random_stats['percentages']['LOSE'], random_stats['percentages']['PUSH'], random_stats['percentages']['BLACKJACK']]
    
    exp_pct = [expecti_stats['percentages']['WIN'], expecti_stats['percentages']['LOSE'], expecti_stats['percentages']['PUSH'], expecti_stats['percentages']['BLACKJACK']]

    q_pct   = [q_stats['percentages']['WIN'], q_stats['percentages']['LOSE'], q_stats['percentages']['PUSH'], q_stats['percentages']['BLACKJACK']]

    allPct = [ran_pct, exp_pct, q_pct, opt_pct]

    n_types = 4

    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, 1.02*height,"{:.1%}".format(height), ha='center', va='bottom')
 
    index = np.arange(n_types)

    bar_width = .2

    opacity = .7

    win_bar = ax.bar(index - bar_width, opt_pct, bar_width, alpha=opacity, color='b', label='Opt')
    lose_bar = ax.bar(index, q_pct, bar_width, alpha=opacity, color='r', label='Q')
    push_bar = ax.bar(index + bar_width, exp_pct, bar_width, alpha=opacity, color='y', label='Expectimax')
    bj_bar = ax.bar(index + 2*bar_width, ran_pct, bar_width, alpha=opacity, color='g', label='Random')

    plt.xlabel('Outcome')
    plt.ylabel('Ratio of outcome')
    plt.title('Outcome by algorithm')
    autolabel(win_bar)
    autolabel(lose_bar)

    autolabel(push_bar)
    autolabel(bj_bar)
    plt.xticks(index + bar_width / float(2), ('Wins', 'Losses', 'Pushes', 'Blackjacks'))
    plt.legend()
    plt.savefig(folder + 'alg_outcomes_unclustered')

"""
Make a graph of win state ratios for each alg type, grouped by algorithm
"""
def makePercentageVsAlgPlots(optimal_stats, random_stats, expecti_stats, q_stats):
    opt_pct = optimal_stats['percentages']
    ran_pct = random_stats['percentages']
    exp_pct = expecti_stats['percentages']
    q_pct   = q_stats['percentages']

    allPct = [ran_pct, exp_pct, q_pct, opt_pct]

    wins = [d['WIN'] for d in allPct]
    losses = [d['LOSE'] for d in allPct]
    pushes = [d['PUSH'] for d in allPct]
    bjs = [d['BLACKJACK'] for d in allPct]

    n_types = 4

    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, 1.02*height,"{:.1%}".format(height), ha='center', va='bottom')
 
    index = np.arange(n_types)

    bar_width = .2

    opacity = .7

    win_bar = ax.bar(index - bar_width, wins, bar_width, alpha=opacity, color='b', label='Wins')
    lose_bar = ax.bar(index, losses, bar_width, alpha=opacity, color='r', label='Losses')
    push_bar = ax.bar(index + bar_width, pushes, bar_width, alpha=opacity, color='y', label='Pushes')
    bj_bar = ax.bar(index + 2*bar_width, bjs, bar_width, alpha=opacity, color='g', label='Blackjacks')

    plt.xlabel('Outcome')
    plt.ylabel('Ratio of outcome')
    plt.title('Outcome by algorithm')
    autolabel(win_bar)
    autolabel(lose_bar)

    autolabel(push_bar)
    autolabel(bj_bar)
    plt.xticks(index + bar_width / 2, ('Random', 'Expectimax', 'Q-Learning', 'Optimal'))
    plt.legend()

    plt.savefig(folder + 'alg_outcomes_clustered')

def graphQLearningPerformanceVsTrainingHands_SMALLER():
    max_training = 70000 
    max_loops = 70
    n_trainings = [int((i / max_loops) * max_training) for i in range(1, max_loops + 1)]
    n_testing = 100000 
    
    n_trainings.insert(0,750)
    n_trainings.insert(0,500)
    n_trainings.insert(0,250)
    n_trainings.insert(0,1)
    print(n_trainings)
    q_stats = []

    num_trials_other = 5
    print("-- STAT ENGINE RUNNING RANDOM  AGENT --")
    r_stats = [runBlackjack(getRandomArgs(70000)) for i in range (num_trials_other)]
    print("-- STAT ENGINE RUNNINGEXPECTIMAX AGENT --")
    e_stats = [runBlackjack(getExpectiArgs(70000)) for i in range(num_trials_other)]
    print("-- STAT ENGINE RUNNING OPTIMAL AGENT --")
    o_stats = [runBlackjack(getOptimalArgs(70000)) for i in range(num_trials_other)]
     
    for idx, training in enumerate(n_trainings):
        print("\n--- STAT ENGINE EVALUATING ALGORITHMS VS {} TRAININGS FOR Q-LEARNING ---\n".format(training))
    
        print("-- STAT ENGINE RUNNING OPTIMAL AGENT --")
        q_stats.append(runBlackjack(getQLearningArgs(training, n_testing)))
             
    q_edge = list(map(lambda d: 100 * d['houseEdge'], q_stats))
    r_edge = list(map(lambda d: 100 * d['houseEdge'], r_stats))
    e_edge = list(map(lambda d: 100 * d['houseEdge'], e_stats))
    o_edge = list(map(lambda d: 100 * d['houseEdge'], o_stats))

    fig, ax = plt.subplots()
    ax.axhline(y =sum(r_edge) / num_trials_other, color='b', alpha=.3, ls='-', label = 'Random Avg')
    ax.axhline(y = sum(e_edge) / num_trials_other, color='g', alpha=.3, ls='-', label= 'Expectimax Avg')
    ax.axhline(y = sum(o_edge) / num_trials_other, color='k', alpha=.3, ls='-', label = 'Optimal Avg')
    ax.plot(n_trainings, q_edge, 'r-.', label="Q-Learning")
    
    
    plt.ylabel("House edge after {} testing hands (%)".format(n_testing))
    plt.xlabel("Q-Learning Training Hands (int)")
    plt.title("Relateive Q-Learning Performance vs. Amount of Training")
    legend = ax.legend()

    
    majorLocator = MultipleLocator(5)
    majorFormatter = FormatStrFormatter('%.0f')
    minorLocator = MultipleLocator(1)
    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)
    ax.yaxis.set_minor_locator(minorLocator)

    plt.savefig(folder + 'qlearn_training_fewer.png')

""" 
Graph qlearning performance based on varying training hand numbers, include 
averge performance for the other three algorithms
"""
def graphQLearningPerformanceVsTrainingHands():
    max_training = 200000 
    max_loops = 50
    n_trainings = [int((i / max_loops) * max_training) for i in range(1, max_loops + 1)]
    n_trainings.insert(0,1)
    n_trainings.insert(1, 500)
    n_trainings.insert(2, 1000)
    n_trainings.insert(3, 1500)
    n_trainings.insert(4, 2000)
    n_trainings.insert(5, 2750)
    n_trainings.insert(6, 3500)
    n_testing = 40000 

    q_stats = []

    num_trials_other = 5
    print("-- STAT ENGINE RUNNING RANDOM  AGENT --")
    r_stats = [runBlackjack(getRandomArgs(50000)) for i in range (num_trials_other)]
    print("-- STAT ENGINE RUNNINGEXPECTIMAX AGENT --")
    e_stats = [runBlackjack(getExpectiArgs(50000)) for i in range(num_trials_other)]
    print("-- STAT ENGINE RUNNING OPTIMAL AGENT --")
    o_stats = [runBlackjack(getOptimalArgs(50000)) for i in range(num_trials_other)]
     
    for idx, training in enumerate(n_trainings):
        print("\n--- STAT ENGINE EVALUATING ALGORITHMS VS {} TRAININGS FOR Q-LEARNING ---\n".format(training))
    
        print("-- STAT ENGINE RUNNING OPTIMAL AGENT --")
        q_stats.append(runBlackjack(getQLearningArgs(training, n_testing)))
             
    q_edge = list(map(lambda d: 100 * d['houseEdge'], q_stats))
    r_edge = list(map(lambda d: 100 * d['houseEdge'], r_stats))
    e_edge = list(map(lambda d: 100 * d['houseEdge'], e_stats))
    o_edge = list(map(lambda d: 100 * d['houseEdge'], o_stats))

    fig, ax = plt.subplots()
    ax.axhline(y =sum(r_edge) / num_trials_other, color='b', alpha=.3, ls='-', label = 'Random Avg')
    ax.axhline(y = sum(e_edge) / num_trials_other, color='g', alpha=.3, ls='-', label= 'Expectimax Avg')
    ax.axhline(y = sum(o_edge) / num_trials_other, color='k', alpha=.3, ls='-', label = 'Optimal Avg')
    ax.plot(n_trainings, q_edge, 'r-.', label="Q-Learning")
    
    
    plt.ylabel("House edge after {} testing hands (%)".format(n_testing))
    plt.xlabel("Q-Learning Training Hands (int)")
    plt.title("Relateive Q-Learning Performance vs. Amount of Training")
    legend = ax.legend()

    
    majorLocator = MultipleLocator(5)
    majorFormatter = FormatStrFormatter('%.0f')
    minorLocator = MultipleLocator(1)
    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)
    ax.yaxis.set_minor_locator(minorLocator)

    plt.savefig(folder + 'qlearn_training.png')
def graphAllPerformance():
    
    print("-- STAT ENGINE RUNNING OPTIMAL AGENT --")
    optimal_stats = runBlackjack(getOptimalArgs(100000))
    
    print("-- STAT ENGINE RUNNING RANDOM AGENT --")
    random_stats = runBlackjack(getRandomArgs(100000))
    
    print("-- STAT ENGINE RUNNING EXPECTIMAX AGENT --")
    expecti_stats = runBlackjack(getExpectiArgs(100000))

    print("-- STAT ENGINE RUNNING QLEARNING AGENT --")
    q_stats = runBlackjack(getQLearningArgs(500000,100000))

    makePercentageVsAlgPlots(optimal_stats, random_stats, expecti_stats, q_stats)
    makeInversePercentageAlgPlots(optimal_stats, random_stats, expecti_stats, q_stats)
    graphQLearningPerformanceVsTrainingHands()
    graphQLearningPerformanceVsTrainingHands_SMALLER()

def main():
    from os import makedirs
    makedirs(folder, exist_ok=True)
    graphAllPerformance()

if __name__ == '__main__':
    sys.exit(main())
