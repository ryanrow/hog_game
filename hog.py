"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'

    total, exit = 0, 0
    while num_rolls > 0:
        n, num_rolls = dice(), num_rolls - 1
        if n > 1:
            total = total + n
        else:
            exit = 1

    if exit:
        return exit
    else:
        return total

def free_bacon(opponent_score):
    """ Helper function to reduce redundancy.  Returns the number of points the
       current player would receive for rolling 0 dice.
    """
    return 1 + abs(opponent_score%10 - opponent_score//10)


def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    
    if num_rolls > 0:
        return roll_dice(num_rolls, dice)
    elif num_rolls == 0:
        return free_bacon(opponent_score)


def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """

    if (score + opponent_score) % 7 == 0:
        return four_sided
    else:
        return six_sided


def bid_for_start(bid0, bid1, goal=GOAL_SCORE):
    """Given the bids BID0 and BID1 of each player, returns three values:

    - the starting score of player 0
    - the starting score of player 1
    - the number of the player who rolls first (0 or 1)
    """
    assert bid0 >= 0 and bid1 >= 0, "Bids should be non-negative!"
    assert type(bid0) == int and type(bid1) == int, "Bids should be integers!"

    # The buggy code is below:
    if bid0 == bid1:
        return goal,goal, 0
    if bid0 == bid1 - 5:
        return 0, 10, 1
    if bid1 == bid0 - 5:
        return 10, 0, 0
    if bid1 > bid0:
        return bid1, bid0, 1
    else:
        return bid1, bid0, 0


def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def swine_swap(score0,score1):
    """ Helper function to reduce redundancy.  This function implements the
        swine swap special rule.
    """
    if score0 == 2 * score1 or score1 == 2 * score0:
        return score1, score0
    else:
        return score0, score1


def play(strategy0, strategy1, score0=0, score1=0, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first
    strategy1:  The strategy function for Player 1, who plays second
    score0   :  The starting score for Player 0
    score1   :  The starting score for Player 1
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)

    score0, score1 = 0,0

    while score0 < goal and score1 < goal:
        if who == 0:
            score0 = score0 + take_turn(strategy0(score0,score1),score1, select_dice(score0,score1))
        elif who == 1:
            score1 = score1 + take_turn(strategy1(score1,score0),score0, select_dice(score1,score0))
        who = other(who)
    return swine_swap(score0,score1)  # You may want to change this line.



#######################
# Phase 2: Strategies #
#######################

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=10000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """

    def average_value(*args):
        total = 0
        counter = num_samples

        while counter:
            result = fn(*args)
            total = total + result
            counter = counter - 1

        return total/num_samples
            
    return average_value

def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    10
    """
    
    x, maximum = 10, 0

    while x > 0:
        average = make_averaged(roll_dice,10000)(x,dice)
        if average > maximum:
            maximum = average
            num_dice = x
        x = x - 1

    return num_dice

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if True: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    
    if free_bacon(opponent_score) >= margin:
        return 0
    else:
        return num_rolls

def swap_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least MARGIN points and rolls
    NUM_ROLLS otherwise.
    """
    
    if 2*(free_bacon(opponent_score) + score) == opponent_score:
        return 0
    if (free_bacon(opponent_score) + score) == 2*opponent_score:
        return num_rolls

    return bacon_strategy(score, opponent_score, margin, num_rolls)

def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.

    *** 1. If rolling zero will win, roll zero.
        2. If hogged, roll zero if it returns 6 or greater points, otherwise, roll three.
        3. If losing, try to cause a positive swine swap, roll zero when 8 or more points are returned, or play more aggressively.
        4. If winning, prevent a negative swine swap, roll zero when 8 or more point are returned, or play more conservatively.
     ***
    """

    if GOAL_SCORE - free_bacon(opponent_score) + score <= 0: # 1.
        return 0

    if (score + opponent_score) % 7 == 0: # 2.
        if free_bacon(opponent_score) >= 6:
            return 0
        return 3


    if opponent_score > score:  # 3.
        if opponent_score - score >= 8:
            if .5 * opponent_score == score + 1:
                return 10
            if .5 * opponent_score == free_bacon(opponent_score) + score:
                return 0
        if free_bacon(opponent_score) >= 8:
            return 0
        if opponent_score - score >= 40:
            return 7
        if opponent_score - score >= 25:
            return 6


    if score > opponent_score:   # 4.
        if score + 1 == 2*opponent_score:
            if free_bacon(opponent_score) >= 2:
                return 0
            if free_bacon(opponent_score) + score == 2*opponent_score:
                return 4
        if free_bacon(opponent_score) >= 8:
            return 0
        if score - opponent_score >=30:
            return 4

    return 5


##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
