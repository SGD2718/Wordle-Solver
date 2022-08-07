# Wordle-Solver
A Brute Force Wordle-Solver

## Pre-Usage:
Before you can run the program, you need to run `Wordle Outcome Generator.py`. It will create a file containing encoded forms of the outcomes/colors for all of the possible guess-answer pairs. (The file will be about 66 MB, too big to upload directly to the repository).

If you use Windows, then you can remove the code
```py
try:
    from tkmacosx import Button
except:
    pass
```
from `WordleBot GUI.py` (lines 10-13).

## Using the Solver:
You can type the guesses that you made, just like in Wordle (note that the return/enter key does nothing). All guesses must be valid words, or else you will not be able to click the 'Calculate' button (which calculates the best guess).

For valid guesses, you can click on the tiles to cycle their color between black, yellow, and green.

If it seems to be taking forever (longer than 2 minutes) to calculate the best guess, it may be the case that you made an objectively terrible guess, or you just got unlucky and ended up eliminating very few words.

Note that all the contenders for the best guess are calculated at once (using threads) so you may have to wait over a minute for that progress bar to stop displaying 0% (which usually happens when the hint revealed is ⬛️⬛️⬛️⬛️⬛️).
