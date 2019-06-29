from random import choices
from collections import Counter

# define classes


class Code:
    """
    Represents an ordered set of four pegs, each being one of six colors (duplicates allowed)
    """

    CODE_PEG_COLORS = {1, 2, 3, 4, 5, 6}

    def __init__(self, peg_array: list) -> None:
        """
        :param peg_array: int values corresponding to colors of pegs in the code
        """
        if all(elt in Code.CODE_PEG_COLORS for elt in peg_array) and len(peg_array) == 4:
            self._peg1 = peg_array[0]
            self._peg2 = peg_array[1]
            self._peg3 = peg_array[2]
            self._peg4 = peg_array[3]
        else:
            raise Exception('Code must be initialized with a list of four code peg colors')

    def __eq__(self, other):
        """
        :param other: code to be compared to self
        :return: True if self and other are equivalent, False otherwise
        """
        return type(other) == type(self) and self.to_number() == other.to_number()

    def __hash__(self):
        return hash((self._peg1, self._peg2, self._peg3, self._peg4))

    def to_number(self):
        """
        Used to break ties in minimax algorithm
        :return: numerical representation of a code's peg colors, e.g. 3562
        """
        return self._peg1 * 1000 + self._peg2 * 100 + self._peg3 * 10 + self._peg4

    @staticmethod
    def generateRandom():
        """
        :return: code instance with randomly colored pegs
        """
        return Code(choices(list(Code.CODE_PEG_COLORS), k=4))

    @staticmethod
    def get_full_code_set():
        """
        :return: set of all possible codes
        """
        codes = set([])

        for p1 in Code.CODE_PEG_COLORS:
            for p2 in Code.CODE_PEG_COLORS:
                for p3 in Code.CODE_PEG_COLORS:
                    for p4 in Code.CODE_PEG_COLORS:
                        codes.add(Code([p1, p2, p3, p4]))

        return codes


class PegScore:
    """
    Represents a collection of up to four key pegs which collectively indicate the accuracy of a guessed code relative
    to the solution code - a red peg represents a correct code peg in both position and color, while a white peg represents

    """

    KEY_PEG_COLORS = {'red', 'white'}

    def __init__(self, num_red: int = 0, num_white: int = 0):
        if num_red + num_white > 4 or num_red + num_white < 0 or num_red > 4 or num_red < 0 or num_white > 4 or num_white < 0:
            raise Exception('Invalid peg score')
        self._num_red = num_red
        self._num_white = num_white

    def __eq__(self, other):
        return type(self) == type(other) and self._num_red == other._num_red and self._num_white == other._num_white

    def __hash__(self):
        return hash((self._num_red, self._num_white))

    def __str__(self):
        return f'{self._num_red} red, {self._num_white} white'


def get_next_guess(solution_candidates: set, unguessed: set):
    """
    :param solution_candidates: set of codes that could potentially be the solution
    :param unguessed: set of codes that have not been guessed yet
    :return: the best possible code to make next, based on Knuth's minimax algorithm, and the worst-case number of codes
             that this guess would eliminate from the solution candidates
    """
    if len(unguessed) == 0:
        raise Exception('Ran out of unguessed codes')

    best_code = unguessed.pop() # start with random guess
    max_min_eliminated = get_min_eliminated(best_code, solution_candidates)

    for u in unguessed:
        min_eliminated = get_min_eliminated(u, solution_candidates)
        if min_eliminated > max_min_eliminated:
            best_code = u
            max_min_eliminated = min_eliminated
            continue

        # Adopt Knuth's tiebreaking convention: guess a code in the set of solution candidates whenever possible; if all
        # else equal, select guess with lower numerical value
        if min_eliminated == max_min_eliminated:
            if best_code in solution_candidates and u not in solution_candidates:
                continue
            if best_code not in solution_candidates and u in solution_candidates:
                best_code = u
            elif u.to_number() < best_code.to_number():
                best_code = u

    return best_code, max_min_eliminated


def get_min_eliminated(code: Code, solution_candidates: set):
    """
    Get the hitcounts of the resulting peg scores with guess `code` and all possible solutions in `solution_candidates`;
    subtract the max hitcount from the length of `solution_candidates` to get the minimum (worst-case) number of potential
    solutions that would be eliminated as a result of guessing `code`; this represents the minimax score of `code` against
    solution set `solution_candidates`
    :param code: a potential guess
    :param solution_candidates: the set of possible solutions at this point in the game
    :return: minimum number of potential solutions that would be eliminated after guessing `code`
    """
    peg_scores = [] # keep track of peg scores for each solution candidate

    for soln in solution_candidates:
        result = get_peg_score(code, soln)
        peg_scores.append(result)

    ctr = Counter(peg_scores)
    max_hit_ct = ctr.most_common(1)[0][1] # number of occurrences of the most prevalent peg score
    min_eliminated = len(solution_candidates) - max_hit_ct

    return min_eliminated


def get_peg_score(guess: Code, soln: Code):
    """
    :param guess:
    :param soln:
    :return: resulting peg score from a guess of `guess` and a solution of `soln`
    """
    red_ct = (guess._peg1 == soln._peg1) + (guess._peg2 == soln._peg2) + (guess._peg3 == soln._peg3) + \
                    (guess._peg4 == soln._peg4)

    # calculate white count: for each unique color in `guess`, sum the min of `guess` occurrences and `soln` occurrences
    # for each unique color, subtract red_ct from this sum, as these are already accounted for as red pegs
    colors = set([guess._peg1, guess._peg2, guess._peg3, guess._peg4])
    white_ct = 0
    for c in colors:
        guess_occ = Counter([guess._peg1, guess._peg2, guess._peg3, guess._peg4])[c]
        soln_occ = Counter([soln._peg1, soln._peg2, soln._peg3, soln._peg4])[c]
        white_ct += min(guess_occ, soln_occ)
    white_ct -= red_ct

    return PegScore(num_red=red_ct, num_white=white_ct)


def run_game_cpu_cpu():
    """
    Executes a single game with a cpu codemaker and a cpu codebreaker, selecting a random solution code and using
    the minimax algorithm to make guesses
    :return: the number of guesses required to guess the solution code
    """
    soln = Code.generateRandom()
    print(f'Solution: {soln.to_number()}\n')

    solution_candidates = Code.get_full_code_set()
    unguessed = solution_candidates
    guess_num = 1
    recommended_guess = Code([1, 1, 2, 2]) # optimal starting guess
    for i in range(1296): # worst case - unguessed contains all possible codes
        print(f'Guess #{guess_num}: {recommended_guess.to_number()}')
        unguessed.remove(recommended_guess)
        peg_score = get_peg_score(recommended_guess, soln)
        print(f'Peg score: {peg_score}')
        if recommended_guess == soln:
            print(f'VICTORY in {guess_num} guesses!\n\n')
            return guess_num
        solution_candidates = set([s for s in solution_candidates if get_peg_score(recommended_guess, s) == peg_score])
        recommended_guess = get_next_guess(solution_candidates, unguessed)[0]
        guess_num += 1

    raise Exception('Timeout')


def get_guess_input(suggested: Code):
    """
    Receive code guess from stdin with the given suggested guess
    :param suggested: guess determined by minimax algorithm
    :return: code instance representing player's guess
    """
    print(f'Suggested guess: {suggested.to_number()}')
    guess = None
    while guess == None:
        guess_digits = input('Enter your guess as a 4-digit number, or press enter to use the suggested guess: ')
        try:
            if guess_digits == '':
                guess = suggested
            else:
                guess = Code([int(i) for i in str(guess_digits)])
        except:
            print('Guess must be a number containing exactly 4 digits 1-6')

    return guess


def get_peg_score_input():
    """
    Receive peg score from stdin
    :return: peg score instance representing resulting peg score
    """
    peg_score = None
    while peg_score == None:
        num_red = input('Enter the number of red pegs in the resulting peg score: ')
        num_white = input('Enter the number of white pegs in the resulting peg score: ')
        try:
            num_red = int(num_red)
            num_white = int(num_white)
            peg_score = PegScore(num_red=num_red, num_white=num_white)
        except:
            print('Peg score must be two numbers adding to 0-4')

    return peg_score


def run_game_human_human():
    """
    Executes a single game with a human codemaker and a human codebreaker, using the minimax algorithm to make
    suggestions based on peg scores
    :return: the number of guesses required to guess the solution code
    """
    solution_candidates = Code.get_full_code_set()
    unguessed = solution_candidates
    recommended_guess = Code([1, 1, 2, 2])
    peg_score = PegScore(num_red=0, num_white=0)
    guess_num = 0  # incremented at least once

    while peg_score != PegScore(num_red=4, num_white=0):
        # get player's guess
        guess = get_guess_input(recommended_guess)
        unguessed.remove(guess)

        # get resulting peg score
        peg_score = get_peg_score_input()

        solution_candidates = set([s for s in solution_candidates if get_peg_score(recommended_guess, s) == peg_score])

        recommended_guess = get_next_guess(solution_candidates, unguessed)[0]
        guess_num += 1

    print(f'VICTORY in {guess_num} moves')

    return guess_num


def run_game_cpu_human():
    """
    Executes a single game with a cpu codemaker and a human codebreaker, using the minimax algorithm to make
    suggestions based on peg scores
    :return: the number of guesses required to guess the solution code
    """
    soln = Code.generateRandom()
    solution_candidates = Code.get_full_code_set()
    unguessed = solution_candidates
    recommended_guess = Code([1, 1, 2, 2])
    peg_score = PegScore(num_red=0, num_white=0)
    guess_num = 0  # incremented at least once

    while peg_score != PegScore(num_red=4, num_white=0):
        # get player's guess
        guess = get_guess_input(recommended_guess)
        unguessed.remove(guess)

        # get resulting peg score
        peg_score = get_peg_score(guess, soln)
        print(f'Peg score: {peg_score}')

        solution_candidates = set([s for s in solution_candidates if get_peg_score(recommended_guess, s) == peg_score])

        recommended_guess = get_next_guess(solution_candidates, unguessed)[0]
        guess_num += 1

    print(f'VICTORY in {guess_num} moves')

    return guess_num


def run_simulation():
    """
    Run 100 automated cpu vs. cpu games and print the counts of number of guesses required to guess the solution in each game
    :return:
    """
    guess_cts = []
    for i in range(100):
        num_guesses = run_game_cpu_cpu()
        guess_cts.append(num_guesses)

    print(f'Guess counts: {Counter(guess_cts)}')


if __name__ == '__main__':
    # run_simulation()
    run_game_human_human()
