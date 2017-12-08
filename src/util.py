import sys, inspect, random

def raiseNotDefined():
    """ Raise not defined: Print the error location and exit if function hasn't been defined """
    filename = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("Method not implemented: {} at line {} in file {}".format(method, line, filename))
    sys.exit(1)

def raiseErrorAtLoc():
    filename = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("Method has error: {} at line {} in file {}".format(method, line, filename))
    sys.exit(1)


def vPrint(string, verbosity):
    """ Print string IF verbosity 
    Used for printing within gameState, game classes instead of lots of checks for verbosity 
    """
    if verbosity:
        print(string)

