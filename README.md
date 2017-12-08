## CS 182 BLACKJACK
#### Dylan Clark, Lana Gorlinski, Nathan Ondracek
#### CS182 Final Project 2017

### What is this?

For our final project we are modeling blackjack as a game for Artificial Intelligence agents to learn, and to test those agents performance against established 'optimal' strategies found online. We aim to implement an expectimax agent, a q-learning agent, a random agent, and maybe more. Additionally, a user can try their own hand by playing the dealer via a command-line interface

### Usage

The game is written in Python 3. Make sure you have Python 3 installed!

##### Basic game-playing

To play against the dealer, simply run `python3 blackjack.py`, and the game will guide you from there!

##### Using command-line arguments

- `-a`, `--agent_type` : Option for a string representing the type of agent to play
	- One of 'user' (default), 'expectimax', 'random', 'q-learning', 'optimal'

- `-n`, `--hands` : Option for an integer for the maximum number of hands to play (doesn't apply for user agents)
	- Default to 0, should be specified every time

- `-s`, `--starting_money` : Option for an integer for how much money the player starts off with
	- Default to 1000

- `-v`, `--verbose` : Option for a boolean for the game to be played with verbosity
	- Default to false for all agents other than the user agent, which needs verbosity to play
	- Verbosity will print every deal, every action, etc, and shouldn't be used for playing many hands with an artificial agent unless you want endless text output
	- One of 'True' or 'False'

###### Examples
- Play blackjack on your own with 100 dollars to start
	- `python3 blackjack.py -s 100`
- Have the 'optimal' agent (hardcoded strategy from online) play blackjack for 10,000 hands with $1 million to start
	- `python3 blackjack.py -a optimal -n 10000 -s 1000000

##### Casino Rules (due to change but these seem common enough)
- No doubling down after splitting
- Splitting after splitting OK
	- Can re-split aces
- Allowed to split aces like a normal split
- Splits must be same card, not same value
	- Some would let you split Jack, Queen. We can only split Jack, Jack
- Dealer stands on soft 17

Online calc says this would make house edge in 8 deck blackjack just .502, and -.06 for 1 deck game. 
