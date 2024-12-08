# Wordle-Solver
A Brute Force Wordle-Solver

Here are the instructions for setting up and running your Wordle bot in Python:

# Wordle Solver Bot

## How to Download and Run

### 1. Clone the Repository
Start by cloning the repository from GitHub to your local machine:

git clone https://github.com/SGD2718/Wordle-Solver.git
cd Wordle-Solver

---

### 2. Dependencies
Ensure you have Python installed on your system. The program relies on the following built-in Python libraries, so no additional installations should be necessary:

- `math`
- `tkinter` (for GUI support)
- `concurrent.futures`
- `time`
- `os`

To verify that Python is installed, run the following command:

python –version

If Python is not installed, download and install it from https://www.python.org/downloads/

---

### 3. File Structure
The repository includes the following files:

- `Wordle Outcome Generator.py`: Script for generating Wordle outcomes.
- `WordleBot GUI.py`: The main GUI interface for the solver.
- `answers.txt`: A list of valid Wordle answers.
- `guesses.txt`: A list of valid Wordle guesses.

---

### 4. Running the Wordle Bot
Follow these steps to run the bot:

1. Run the GUI script:

python “WordleBot GUI.py”

2. A graphical interface will open, allowing you to interact with the bot.

---

### 5. Notes
- The bot requires the `answers.txt` and `guesses.txt` files to be in the same directory as the Python scripts. Ensure these files are not moved or deleted.
- If you encounter any issues, ensure that you are using Python 3.6 or later.

Feel free to tweak this to match your exact preferences or needs!

## Usage:
You can type the guesses that you made, just like in Wordle (note that the return/enter key does nothing). All guesses must be valid words, or else you will not be able to click the 'Calculate' button (which calculates the best guess).

For valid guesses, you can click on the tiles to cycle their color between black, yellow, and green.

If it seems to be taking forever (longer than 2 minutes) to calculate the best guess, it may be the case that you made an objectively terrible guess, or you just got unlucky and ended up eliminating very few words.

Note that all the contenders for the best guess are calculated at once (using threads), so you may have to wait over a minute for that progress bar to stop displaying 0% (which usually happens when the hint revealed is ⬛️⬛️⬛️⬛️⬛️).
