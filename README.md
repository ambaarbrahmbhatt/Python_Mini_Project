# Typing Speed Tester (Python + tkinter)

A simple desktop app with a countdown timer. Pick 1, 3 or 5 minutes, then type the
sentences that appear. Press Enter after each one to get a new sentence. When the
time runs out you get your speed (WPM), accuracy and number of errors.

## Concepts used
- **Strings** - comparing the typed text with the target sentence, character by character
- **Functions** - `pick_sentence`, `count_errors`, `score_attempt`, `calculate_accuracy`, `calculate_wpm`, `get_rating`, `format_time`
- **GUI** - tkinter widgets (Label, Text, Frame), events and `after()` for the live countdown

## How to run
tkinter comes with Python, so nothing needs to be installed.
```
python typing_speed_tester.py
```

## How to use
1. Choose 1, 3 or 5 minutes under the timer.
2. Start typing in the lower box. The clock starts with your first key.
3. Press **Enter** to finish a sentence and get the next one. This goes on until the timer reaches 0:00.
4. Your result appears when time is up. Click **Restart** (or another length) to go again.

Correct letters turn green and wrong letters turn red while you type.
The timer turns red for the last 10 seconds.

## Formulas
- WPM = (total characters typed / 5) / minutes
- Errors = wrong characters + missing or extra characters
- Accuracy = (characters checked - errors) / characters checked x 100
- A sentence you were still typing when time ran out is only checked up to where you got to.
