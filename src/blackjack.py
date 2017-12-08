
import argparse
import sys
from os import chdir, getcwd

from game import Game

def set_args(arguments):
    """ Set the command line args """
    global args
    parser = argparse.ArgumentParser( description="Blackjack Arguments", formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-a', '--agent_type', default='user', help="Agent type for blackjack: One of 'user', 'expectimax', 'q-learning'")
    parser.add_argument('-n', '--hands', default=0, help="Number of hands to play (if not a user agent)")
    parser.add_argument('-s', '--starting_money', default = 1000, help="Amount player starts with")
    parser.add_argument('-v', '--verbose', default = False, help="Print each step if verbose, user_agent is automatically verbose")
    parser.add_argument('-t', '--training', default=0, help="Number of qlearning training rounds")

    args = parser.parse_args(arguments)

def main(arguments):
    global args
    set_args(arguments)

    if args.agent_type == 'user':
        verbose = True
    else:
        if not args.verbose or args.verbose == 'False' or args.verbose == 'F' or args.verbose == 'f':
            verbose = False
        elif args.verbose or args.verbose == 'True' or args.verbose == 'T' or args.verbose == 't':
            verbose = True
        else:
            print("Error: Options for verbose are 'True','T','t','False','F','f'")
            return 1

    # Initialize the game
    game = Game(verbose, args.agent_type, int(args.hands), args.starting_money, args.training)

    if not game.isValidGame():
        print("Invalid game setup, please try again")
        return 1

    # Play the game
    results = game.playGame()

    if __name__ != '__main__':
        return results

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
