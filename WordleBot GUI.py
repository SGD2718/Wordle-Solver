# import libraries
from math import *
from tkinter import *
from tkinter import ttk
import time
import sys
import random
import os

try:
    from tkmacosx import Button
except:
    pass

class WordleBot:
    '''A Bot for a game of Wordle'''
    
    def __init__(self):
        '''WordleBot() -> WordleBot'''
        # retreive word files
        self.GUESSES = []
        self.ANSWERS = []
        self.OUTCOMES = []

        with open('guesses.txt','r') as guessfile:
            for line in guessfile:
                self.GUESSES.append(line[:5])

        with open('answers.txt','r') as answerfile:
            for line in answerfile:
                self.ANSWERS.append(line[:5])

        with open('outcomes.txt','r') as outcomefile:
            self.OUTCOMES = [list(map(int,line.split())) for line in outcomefile]

    def filter_solutions(self, guesses, outcomes, answers=list(range(2315))):
        '''WordleBot.filter_solutions(guesžesIdx, outcomes, answersIdx) -> list
        returns the indices of the remaining solutions.
            guesses: the indices of all the guesses.
            outcomes: the outcomes of those guesses
            answers: the indices of the solutions to filter through'''

        solutions = []
        
        # filter through the remaining answers
        for answer in answers:
            
            isPossible = True

            # check if it has the correct
            # outcomes with all the guesses
            for i, guess in enumerate(guesses):
                if outcomes[i] != self.OUTCOMES[answer][guess]:
                    
                    # Stop if an outcome doesn't
                    # match. We already know it's
                    # not a possible solution
                    isPossible = False
                    break

            # add answer index to the
            # list of remaining solutions
            # if eligible
            if isPossible:
                solutions.append(answer)

        # return the list of the indices
        # of the remaining solutions
        return solutions

    def get_expected_info(self, guess, answers=list(range(2315))):
        '''WordleBot.get_expected_info(guess, guesses, outcomes) -> float
        returns the expected information of a guess
            guess: the index of the guess.
            answers: the indices of the remaining solutions
        CAUTION: ASSUMES THAT ANSWERS IS ALREADY FILTERED'
            '''

        # count the number of
        # occurences of each
        # outcome
        outcomeCounts = [0] * 243

        for answer in answers:
            outcomeCounts[self.OUTCOMES[answer][guess]] += 1

        # get the expected amount of information
        expected_info = 0
        
        for outcomeCount in outcomeCounts:
            if outcomeCount:
                # 1 / p(outcome)
                pOutcome = outcomeCount / len(answers)
                # E[I] = ∑p(x) * log2(1/p(x))
                expected_info -= pOutcome * log2(pOutcome)

        # return expected info
        return expected_info

    def sort_guesses(self, guesses, outcomes, answers=list(range(2315))):
        '''WordleBot.sort_guesses(amt guesses, outcomes, answers) -> list
        sorts the possible guesses based on
        information and returns the sorted list
        CAUTION: ASSUMES THAT ANSWERS IS ALREADY FILTERED'''
        infoDict = {}

        # iterate through each word
        for guess in range(len(self.GUESSES)):
            
            # add word and its expected 
            # info to the info distribution
            
            if not guess in guesses: # reduces runtime
                infoDict[guess] = self.get_expected_info(guess, answers)

        # return the guesses in order of information
        return sorted(infoDict, key=lambda guess : infoDict[guess], reverse=True)

    def get_expected_score(self, guesses, outcomes, answers=list(range(2315)), nodes=19, cutoff=6):
        '''WordleBot.get_expected_score(guesses, outcomes, answers, alpha) -> float
        returns the expected score of a position
            guesses: the list of guesses in the current game
            outcomes: the outcomes of those guesses
            answers: the remaining possible answers
            nodes: how many different guesses the algorithm looks at
            cutoff: the maximum number of guesses it should take to solve.
        CAUTION: ASSUMES THAT ANSWERS IS ALREADY FILTERED'''

        # Works similarly to α-β pruning
        # but for a 1-player game
        
        # immediately return the expected
        # score if we are in a determinant
        # state or if we've made too many
        # guesses
        if len(answers) < 3:
            #print('branch ended')
            return len(guesses) + 2 - 1 / len(answers)
        elif len(guesses) >= cutoff:
            #print('branch terminated')
            return len(guesses)

        # get the top 'nodes' guesses
        # based on information
        # and brute-force them.
        contenders = self.sort_guesses(guesses, outcomes, answers)[:nodes]

        for guess in contenders:
            # make the guess
            newGuesses = guesses+[guess]
            
            # count the number of
            # occurences of each
            # outcome
            outcomeCounts = [0] * 243

            for answer in answers:
                outcomeCounts[self.OUTCOMES[answer][guess]] += 1

            # calculate the expected score
            # of the guess with each outcome
            eScore = 0
            
            for outcome in range(243):
                if outcomeCounts[outcome]:
                    # get the probability of the outcome
                    pOutcome = outcomeCounts[outcome] / len(answers)

                    # add the outcome to the list of
                    # outcomes and filter the solutions
                    newOutcomes = outcomes+[outcome]
                    solutions = self.filter_solutions(newGuesses,newOutcomes,answers)
                    
                    # calculate the expected score for the position
                    score = self.get_expected_score(newGuesses, newOutcomes, solutions, nodes, cutoff)

                    # add the score to the weighted sum
                    eScore += pOutcome * score

                    # prune the branch if
                    # it can't be the best
                    if eScore >= cutoff:
                        break
                    
            # set new benchmark
            if eScore < cutoff:
                cutoff = eScore

        # return the lowest expected score
        return cutoff

    def encode_guess(self, guess):
        '''WordleBot.encode_guesses(guesses) -> list
        encodes guess'''
        try:
            # put the guess in integer form
             return self.GUESSES.index(guess)
        except ValueError:
            # Only allow for valid guesses
            raise ValueError(guess + ' is not a valid guess.')

    def encode_guesses(self, guesses):
        '''WordleBot.encode_guesses(guesses) -> list
        encodes any guesses that are in string form'''

        encodedGuesses = guesses[:]
        
        for i, guess in enumerate(guesses):
            # convert any string guesses to ints
            if isinstance(guess, str):
                encodedGuesses[i] = self.encode_guess(guess)

        return encodedGuesses

    def encode_outcome(self, outcome):
        '''WordleBot.encode_outcomes(outcomes) -> list
        encodes outcome'''
        # encode the outcome
        outcomeCode = 0
        
        if len(outcome) != 5:
            return -1
        
        for i, char in enumerate(outcome.lower()):
            if char == 'y':
                outcomeCode += 3**i
            elif char == 'g':
                outcomeCode += 2*(3**i)
            elif char != 'b':
                return -1 # invalid outcome
        
        return outcomeCode
         
    def encode_outcomes(self, outcomes):
        '''WordleBot.encode_outcomes(outcomes) -> list
        encodes any outcomes that are in string form'''
        
        encodedOutcomes = outcomes[:]
        
        for i, outcome in enumerate(outcomes):
            
            # convert any string outcomes to ints
            if isinstance(outcome, str):
                
                # encode the outcome
                outcomeCode = self.encode_outcome(outcome)

                # replace the element
                if outcomeCode != -1:
                    encodedOutcomes[i] = outcomeCode
                else:
                    raise ValueError(outcome + ' is not a valid outcome.')
                
        return encodedOutcomes

    def analyze_guess(self, guess, guesses, outcomes, answers = list(range(2315)), isFiltered = False, nodes = 19):
        '''WordleBot.analyze_guess(guess, guesses, outcomes, answers, isFiltered, nodes) -> float
        returns the expected score of a guess (rather than a position)'''

        # make the guess

        newGuesses = self.encode_guesses(guesses+[guess])
        outcomes = self.encode_outcomes(outcomes)

        guess = newGuesses[-1] # encoded form of guess
        
        # count the number of
        # occurences of each
        # outcome
        outcomeCounts = [0] * 243

        # filter answers, if necessary
        if not isFiltered:
            answers = self.filter_solutions(guesses, outcomes, answers)

        for answer in answers:
            outcomeCounts[self.OUTCOMES[answer][guess]] += 1

        # calculate the expected score
        # of the guess with each outcome
        eScore = 0
        
        for outcome in range(243):
            if outcomeCounts[outcome]:
                # get the probability of the outcome
                pOutcome = outcomeCounts[outcome] / len(answers)

                # add the outcome to the list of
                # outcomes and filter the solutions
                newOutcomes = outcomes+[outcome]
                solutions = self.filter_solutions(newGuesses,newOutcomes,answers)
                
                # calculate the expected score for the position
                score = self.get_expected_score(newGuesses,newOutcomes,solutions,nodes)

                # add the score to the weighted sum
                eScore += pOutcome * score
                
        return eScore

    def get_best_guesses(self, guesses, outcomes, answers=list(range(2315)), isFiltered=False, isEnglish=False, nodes=15):
        '''WordleBot.get_best_guesses(guesses, outcomes, amt, answers, isFiltered, nodes) -> list
        returns the indices of the top n best guesses, or just returns those guesses.
            guesses: the indices of all the guesses or the guesses themselves
            outcomes: the outcomes of those guesses or the outcomes in text
            answers: the indices of the solutions to filter through
            isFiltered: if the list of possible answers has been filtered
            nodes: the number of guesses it checks for each iteration
            isEnglish: determines if the output is numerical or English'''

        # convert to integer
        # form if necessary
        guesses = self.encode_guesses(guesses)
        outcomes = self.encode_outcomes(outcomes)
        
        # the first guess literally takes
        # forever to compute so it's hardcoded
        if guesses == []:
            if isEnglish:
                return {'salet' : 3.421,
                        'reast' : 3.422,
                        'crate' : 3.424,
                        'trace' : 3.424,
                        'slate' : 3.431,
                        'crane' : 3.434}
            
            return {self.encode_guess('salet') : 3.421,
                    self.encode_guess('reast') : 3.422,
                    self.encode_guess('crate') : 3.424,
                    self.encode_guess('trace') : 3.424,
                    self.encode_guess('slate') : 3.431,
                    self.encode_guess('crane') : 3.434}
        
        # filter the answers, if necessary
        if not isFiltered:
            answers = self.filter_solutions(guesses,outcomes,answers)
            
        if not len(answers):
            return {}
        
        if len(answers) < 3:
            score = len(guesses) + 2 - 1 / len(answers)
                    
            if isEnglish:
                return {self.ANSWERS[answers[i]] : score for i in range(len(answers))}
            
            return {self.GUESSES.index(self.ANSWERS[answers[i]]) : score for i in range(len(answers))}
        
        # get the top contenders based on info
        contenders = self.sort_guesses(guesses, outcomes, answers)[:nodes]
        scoreDict = {}
        print('-' * nodes)
        # get the best guess
        for guess in contenders:
            # get the expected score of a guess
            scoreDict[guess] = self.analyze_guess(guess, guesses, outcomes, answers, True, nodes)
            print('#',end='')

        print('\n')
        scoreDict = dict(sorted(scoreDict.items(), key=lambda guess : guess[1]))

        # return the guesses in order of expected score
        if (isEnglish):        
            return {self.GUESSES[key] : scoreDict[key] for key in scoreDict.keys()}
        
        return scoreDict

class Tile:
    '''a tile for the Wordle GUI'''
    
    def __init__(self, master, letter, color, x, y):
        '''Tile(master, letter, color, row, col) -> Tile'''
        
        self.color = color
        self.letter = letter

        self.colors = ['#3A3A3C','#B1A04C','#618C55']
        
        frame = Frame(master)
        frame.grid(column=x,row=y+1)
        
        self.tile = Button(frame,width=100,height=100,          \
                           bg=self.colors[color],fg='white',    \
                           activebackground=self.colors[color], \
                           bd=0,command=self.next_color,        \
                           text=letter,padx=40,pady=40,         \
                           justify=CENTER,                      \
                           font=('clear sans','55','bold'),     \
                           disabledbackground='#121214',        \
                           disabledforeground='white')
        self.tile.pack()
        
        self.set_letter(letter,True)
        
    def next_color(self):
        '''Updates the tile's color'''
        self.color = (self.color + 1) % 3
        self.tile['bg'] = self.colors[self.color]
        self.tile['activebackground'] = self.colors[self.color]

    def get_color(self):
        '''Tile.get_color() -> int
        returns the tile's color'''
        return self.color
    
    def get_letter(self):
        '''Tile.get_letter() -> str
        returns the tile's letter'''
        return self.letter

    def set_letter(self,letter, autoLock=False):
        '''Tile.set_letter(letter, autoLock) -> None
        updates the tile's letter and state'''
        
        self.letter = letter
        self.tile['text'] = letter

        # update color and lock/unlock tile
        if self.letter == ' ':
            self.color = 0
            self.tile['bg'] = self.colors[self.color]
            self.tile['activebackground'] = self.colors[self.color]
            if autoLock:
                self.tile['state'] = DISABLED
        else:
            self.color = 0
            self.tile['bg'] == self.colors[self.color]
            
            if autoLock:
                self.tile['state'] = NORMAL

    def unlock(self, keepColor=False):
        '''Tile.unlock() -> None
        unlocks the tile button'''

        # reset color
        if not keepColor:
            self.color = 0
            self.tile['bg'] == self.colors[self.color]
            
        # enable tile
        self.tile['state'] = NORMAL

    def lock(self, keepColor=False):
        '''Tile.lock() -> None
        locks the tile button'''

        # reset color
        if not keepColor:
            self.color = 0
            self.tile['bg'] = self.colors[self.color]
            self.tile['activebackground'] = self.colors[self.color]
            
        self.tile['state'] = DISABLED

        # fix color
        if keepColor:
            self.tile['bg'] = self.colors[self.color]
            self.tile['activebackground'] = self.colors[self.color]
    
class WordleGUI(WordleBot,Frame):
    '''a GUI for the Wordle Bot'''
    
    def __init__(self, master):
        WordleBot.__init__(self)
        Frame.__init__(self,master)
        self.grid()

        self.guesses = []
        self.outcomes = []

        self.isCalculating = False
        self.canType = True

        # create the interface
        Label(self,text='Wordle Bot',font=('clear sans',60,'bold'),anchor=CENTER).grid(columnspan=5)
        self.gameState = [[Tile(self,' ',0,i,j) for i in range(5)] for j in range(6)]
        self.calculateButton = Button(self,
                                      width=150,
                                      height=35,
                                      text='Calculate',
                                      command=self.calculate,
                                      bg='#618C55',
                                      font=('clear sans',20,'bold'),
                                      fg='white',
                                      activebackground='#91B487',
                                      disabledbackground='#808080',
                                      disabledforeground='white')
        
        self.calculateButton.grid(row=1,column=6,columnspan=3,sticky=N)
        Label(self,text='\t').grid(column=5)
        
        Label(self,text='Guesses:\n',font=('clear sans',13,'bold')).grid(row=1,column=6,sticky=S)
        Label(self,text='Guesses\nRemaining:',font=('clear sans',13,'bold')).grid(row=1,column=8,sticky=S)
        
        self.bestGuessList = Listbox(self,
                                     font=('clear sans',20),
                                     bg='#2B2B2B',
                                     bd=0,
                                     height=15,
                                     highlightthickness=0,
                                     selectbackground='#3A3A3C',
                                     width=5)
        
        self.bestScoreList = Listbox(self,
                                     font=('clear sans',20),
                                     bg='#2B2B2B',
                                     bd=0,
                                     height=15,
                                     highlightthickness=0,
                                     selectbackground='#3A3A3C',
                                     width=5)
        Label(self,text='\t').grid(column=9)
        self.bestGuessList.grid(row=2,column=6,rowspan=4,sticky=N)
        Label(self,text='  ').grid(column=7)
        self.bestScoreList.grid(row=2,column=8,rowspan=4,sticky=N)

        # allow user to type stuff
        self.keyRow = 0
        self.keyCol = 0
        master.bind("<BackSpace>", self.delete)
        master.bind("<KeyPress>", self.keydown)
        
    def keydown(self,event):
        '''When the user types something'''
        if event.char.isalpha() and self.canType and not (self.keyRow == 6 or self.isCalculating):

            # "type" the letter
            self.gameState[self.keyRow][self.keyCol].set_letter(event.char.upper())

            # update cursor position
            self.keyCol = (self.keyCol+1) % 5

            # add guess to list and unlock row
            if self.keyCol == 0:
                guess = self.read_guess(self.keyRow)

                if guess in self.GUESSES:
                    self.canType = True
                    for col in range(5):
                        # allow the player to change the colors
                        self.gameState[self.keyRow][col].unlock()
                        
                    self.calculateButton['state'] = NORMAL
                else:
                    self.canType = False
                    self.calculateButton['state'] = DISABLED
            else:
                self.calculateButton['state'] = DISABLED
                    
            # update cursor position
            self.keyRow += not self.keyCol

    def delete(self, event):
        '''When the user presses delete'''
        if not self.isCalculating:
            if self.keyRow or self.keyCol:
                self.keyRow -= not self.keyCol
                self.keyCol = (self.keyCol-1) % 5
                self.gameState[self.keyRow][self.keyCol].set_letter(' ', True)

            # let user type
            self.canType = True

            # lock the tiles if necessary
            if self.keyCol == 4:
                for col in range(5):
                    self.gameState[self.keyRow][col].lock()
                    
            if self.keyCol:
                self.calculateButton['state'] = DISABLED
            else:
                self.calculateButton['state'] = NORMAL

    def read_guess(self, row):
        '''WordleGUI.read_guess(row) -> str
        returns the guess on row'''
        return ''.join([self.gameState[row][col].get_letter() for col in range(5)]).lower()

    def read_guesses(self):
        '''WordleGUI.read_guess(row) -> list
        returns the guesses the user made'''
        self.guesses = []
                       
        for row in range(6):
            guess = self.read_guess(row)
            if ' ' in guess:
                print(guess)
                break
            else:
                self.guesses.append(guess)

        return self.guesses
        
    def read_outcome(self, row):
        '''WordleGUI.read_outcome(row) -> int
        returns the outome on row'''
        outcome = 0
        for col in range(5):
            outcome += self.gameState[row][col].get_color()*(3**col)
        return outcome

    def read_outcomes(self):
        '''WordleGUI.read_outcomes() -> list
        returns the outomes of the user's guesses.'''
        self.outcomes = []
        
        for row in range(len(self.guesses)):
            self.outcomes.append(self.read_outcome(row))

        return self.outcomes

    def calculate(self):
        '''WordleGUI.calculate() -> dict
        calculates the best guesses for
        the current game state'''
        self.read_guesses()
        self.read_outcomes()
        self.isCalculating = True
        self.calculateButton['state'] = DISABLED

        # lock tiles to prevent changing colors
        for row in range(len(self.guesses)):
            for col in range(5):
                self.gameState[row][col].lock(True)
            
        bestGuesses = self.get_best_guesses(self.guesses, self.outcomes, isEnglish=True)

        # unlock tiles
        for row in range(len(self.guesses)):
            for col in range(5):
                self.gameState[row][col].unlock(True)
        
        self.calculateButton['state'] = NORMAL
        self.isCalculating = False

        self.bestGuessList.delete(0,END) # clear the list of optimal guesses
        self.bestScoreList.delete(0,END) # clear the list of scores

        # add the stuff to the list box
        numGuesses = len(self.guesses)
        for guess in bestGuesses.keys():
            self.bestGuessList.insert(END,guess)
            self.bestScoreList.insert(END,'%0.3f' % (bestGuesses[guess]-numGuesses))

# disable key repeats
os.system('xset r off') 

# main loop
root = Tk()
root.title('Wordle Solver')
main = WordleGUI(root)
root.mainloop()

# enable key repeats because we don't want to mess up the user's computer settings.
os.system('xset r on') 
