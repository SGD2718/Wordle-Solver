def reveal(guess, answer):
    outcome = 0
    green = ['_'] * 5
    yellow = ['_'] * 5
    
    for i in range(5):
        if guess[i] == answer[i]:
            green[i] = guess[i]
            outcome += 2*(3**i)
    for i, letter in enumerate(guess):
        if green[i] == '_' and answer.count(letter)-green.count(letter)-yellow.count(letter):
            yellow[i] = letter
            outcome += 3**i
    return outcome

guesses = []
answers = []
outcomes = []

with open('guesses.txt','r') as guessfile:
    for line in guessfile:
        guesses.append(line[:5])

with open('answers.txt','r') as answerfile:
    for line in answerfile:
        answers.append(line[:5])

if input('recreate outcomes? (y / n)') == 'y':
    with open('outcomes.txt','w') as outcomefile:
        for answer in answers:
            line = ''
            for guess in guesses:
                line += str(reveal(guess, answer))+' '
            outcomefile.write(line[:-1]+'\n')
