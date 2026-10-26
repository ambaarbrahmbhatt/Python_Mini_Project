"""Typing Speed Tester
Concepts used: strings, functions and a tkinter GUI.
Run with:  python typing_speed_tester.py
"""
import math
import random
import time
import tkinter as tk
from tkinter import font as tkfont

SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Practice makes a person faster and more accurate.",
    "Python is a simple language that is easy to learn.",
    "A good programmer writes code that other people can read.",
    "Typing without looking at the keyboard saves a lot of time.",
    "Every small bug teaches us something new about the program.",
    "The library was quiet except for the sound of keyboards.",
    "Learning to code takes patience, practice and curiosity.",
    "Rain tapped on the window while the kettle slowly came to a boil.",
    "She folded the map twice and decided to trust her sense of direction.",
    "A steady rhythm matters more than raw speed when you are typing.",
    "The bakery on the corner opens before the sun is up.",
    "He kept a notebook of small ideas that never seemed to run out.",
    "Good habits are built one ordinary day at a time.",
    "The train pulled away just as we reached the platform.",
    "Fresh snow covered the hills and made the whole valley seem quiet.",
    "Take a deep breath, relax your shoulders and keep your eyes on the words.",
    "The old clock in the hall has been running five minutes fast for years.",
    "We spent the afternoon planting herbs along the sunny wall.",
    "A short walk after lunch can clear your head better than coffee.",
    "The museum was almost empty, so we took our time in every room.",
    "Mistakes are fine as long as you notice them and move on.",
    "Wind carried the smell of pine across the lake.",
    "Her handwriting was messy, but every letter had a purpose.",
    "The recipe called for two lemons, a pinch of salt and plenty of patience.",
    "Before the meeting started, someone opened a window to let in the breeze.",
    "A new keyboard feels strange for the first few days.",
    "They argued about the best route and then took the long way anyway.",
    "The garden looked wild, yet every plant seemed to be in its place.",
    "Once you stop thinking about each key, your fingers start to find them.",
    "The ferry horn sounded twice and the harbour began to wake up.",
    "It is easier to learn a skill when you enjoy the small wins.",
    "Late at night the city hums quietly like a refrigerator.",
    "He wrapped the parcel in brown paper and tied it with green string.",
    "A cup of tea and a quiet corner were all she needed.",
    "The final chapter surprised everyone, including the person who wrote it.",
    "Keep your wrists level and let your fingers do the work.",
    "On Sunday mornings the market smells of bread, flowers and fresh coffee.",
]

DURATIONS = [60, 180, 300]          # seconds: 1, 3 and 5 minutes

# ---------- Colours ----------
BG = "#d4c1ec"          # lilac
SURFACE = "#f1e9fb"     # paler lilac for the text areas
EDGE = "#b9a0dd"        # border of the text areas
INK = "#2b1b45"         # main text
MUTED = "#55436e"       # secondary text
ACCENT = "#3a2761"      # selected option and buttons
ACCENT_HOVER = "#4d3680"
PILL = "#c3abe4"        # unselected option
PILL_HOVER = "#b79adb"
GOOD = "#17704a"
BAD = "#b0213f"


# ---------- Functions (the logic of the program) ----------

def pick_sentence(deck, previous=""):
    """Take the next sentence from the deck. The deck is refilled and shuffled
    when it runs out, so sentences do not repeat until all have been used."""
    if not deck:
        deck.extend(SENTENCES)
        random.shuffle(deck)
        if len(deck) > 1 and deck[-1] == previous:
            deck[0], deck[-1] = deck[-1], deck[0]
    return deck.pop()


def count_errors(target, typed):
    """Count wrong characters. Missing or extra characters count as errors."""
    errors = abs(len(target) - len(typed))
    for correct, written in zip(target, typed):
        if correct != written:
            errors += 1
    return errors


def score_attempt(target, typed, unfinished=False):
    """Return (errors, characters checked) for one sentence.
    An unfinished sentence is only compared with the part that was reached."""
    if unfinished:
        target = target[:len(typed)]
    return count_errors(target, typed), max(len(target), len(typed))


def calculate_accuracy(errors, checked):
    """Accuracy as a percentage (0 to 100)."""
    if checked <= 0:
        return 0.0
    return max(0.0, (checked - errors) / checked * 100)


def calculate_wpm(characters, seconds):
    """Words per minute. One 'word' is 5 characters (standard rule)."""
    if seconds <= 0:
        return 0.0
    return (characters / 5) / (seconds / 60)


def get_rating(wpm, accuracy):
    """Return a short comment based on speed and accuracy."""
    if accuracy < 80:
        return "Slow down and focus on accuracy."
    if wpm < 25:
        return "Beginner. Keep practising!"
    if wpm < 45:
        return "Good speed."
    if wpm < 65:
        return "Very good!"
    return "Excellent typist!"


def format_time(seconds):
    """Turn seconds into m:ss, rounding up so the clock hits 0:00 only at the end."""
    whole = max(0, math.ceil(seconds))
    minutes, secs = divmod(whole, 60)
    return f"{minutes}:{secs:02d}"


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def pick_font(root, options, fallback):
    """Use the first font from the list that is installed on this computer."""
    installed = set(tkfont.families(root))
    for name in options:
        if name in installed:
            return name
    return fallback


# ---------- GUI ----------

class FlatButton(tk.Label):
    """A flat clickable label. Looks the same on Windows, macOS and Linux."""

    def __init__(self, parent, text, command, font, bg, fg, hover, padx=18, pady=7):
        super().__init__(parent, text=text, font=font, bg=bg, fg=fg,
                         padx=padx, pady=pady, cursor="hand2")
        self.command = command
        self.normal = bg
        self.hover = hover
        self.bind("<Button-1>", lambda event: self.command())
        self.bind("<Enter>", lambda event: self.config(bg=self.hover))
        self.bind("<Leave>", lambda event: self.config(bg=self.normal))

    def set_colours(self, bg, fg, hover):
        self.normal, self.hover = bg, hover
        self.config(bg=bg, fg=fg)


class TypingTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Tester")
        self.root.geometry("760x720")
        self.root.minsize(680, 680)
        self.root.configure(bg=BG)

        self.serif = pick_font(root, ["Palatino Linotype", "Palatino", "Book Antiqua",
                                      "Georgia", "DejaVu Serif"], "Times")
        self.sans = pick_font(root, ["Segoe UI", "Helvetica Neue", "Ubuntu",
                                     "DejaVu Sans", "Arial"], "Helvetica")

        self.duration = DURATIONS[0]
        self.deck = []
        self.target = ""
        self.start_time = None
        self.running = False
        self.after_id = None
        self.best_wpm = 0.0

        # totals for the current test
        self.sentences_done = 0
        self.total_typed = 0
        self.total_checked = 0
        self.total_errors = 0

        self.build_widgets()
        self.reset()

    def build_widgets(self):
        page = tk.Frame(self.root, bg=BG)
        page.pack(fill="both", expand=True, padx=56, pady=(26, 18))

        tk.Label(page, text="Typing speed tester", font=(self.serif, 20),
                 bg=BG, fg=INK).pack()

        # Timer, with the length options directly under it
        self.timer_label = tk.Label(page, text="1:00", font=(self.sans, 62),
                                    bg=BG, fg=INK)
        self.timer_label.pack(pady=(8, 0))

        options = tk.Frame(page, bg=BG)
        options.pack(pady=(2, 18))
        self.option_buttons = {}
        for seconds in DURATIONS:
            button = FlatButton(options, f"{seconds // 60} min",
                                lambda s=seconds: self.choose_duration(s),
                                font=(self.sans, 11), bg=PILL, fg=INK, hover=PILL_HOVER)
            button.pack(side="left", padx=5)
            self.option_buttons[seconds] = button

        # Sentence to type
        self.target_label = tk.Label(page, text="", font=(self.serif, 18), justify="left",
                                     anchor="w", height=3, bg=SURFACE, fg=INK,
                                     padx=20, pady=12)
        self.target_label.pack(fill="x")
        self.target_label.bind("<Configure>", self.fit_sentence)

        # Typing box
        self.text_box = tk.Text(page, height=3, font=(self.serif, 18), wrap="word",
                                bg=SURFACE, fg=INK, insertbackground=INK,
                                selectbackground=PILL, selectforeground=INK,
                                relief="flat", bd=0, padx=20, pady=12,
                                highlightthickness=2, highlightbackground=EDGE,
                                highlightcolor=ACCENT)
        self.text_box.pack(fill="x", pady=(10, 0))
        self.text_box.tag_configure("good", foreground=GOOD)
        self.text_box.tag_configure("bad", foreground=BAD, underline=True)
        self.text_box.bind("<KeyPress>", self.on_key_press)
        self.text_box.bind("<KeyRelease>", self.on_key_release)
        self.text_box.bind("<Return>", self.on_enter)

        # Hint and restart
        row = tk.Frame(page, bg=BG)
        row.pack(fill="x", pady=(12, 0))
        self.hint_label = tk.Label(row, text="", font=(self.sans, 10), bg=BG, fg=MUTED)
        self.hint_label.pack(side="left")
        FlatButton(row, "Restart", self.reset, font=(self.sans, 10, "bold"),
                   bg=ACCENT, fg="#f6efff", hover=ACCENT_HOVER,
                   padx=16, pady=6).pack(side="right")

        # Result
        result = tk.Frame(page, bg=BG, height=125)
        result.pack(fill="x", pady=(14, 0))
        result.pack_propagate(False)
        self.result_main = tk.Label(result, text="", font=(self.serif, 30), bg=BG, fg=INK)
        self.result_main.pack()
        self.result_detail = tk.Label(result, text="", font=(self.sans, 11), bg=BG, fg=INK)
        self.result_detail.pack(pady=(2, 0))
        self.result_rating = tk.Label(result, text="", font=(self.sans, 11), bg=BG, fg=MUTED)
        self.result_rating.pack(pady=(2, 0))

        self.best_label = tk.Label(page, text="", font=(self.sans, 10), bg=BG, fg=MUTED)
        self.best_label.pack(side="bottom")

    def fit_sentence(self, event):
        """Keep the sentence wrapped to the width of its box."""
        wrap = max(200, event.width - 44)
        if int(self.target_label.cget("wraplength")) != wrap:
            self.target_label.config(wraplength=wrap)

    # ----- test flow -----
    def choose_duration(self, seconds):
        self.reset(seconds)

    def reset(self, duration=None):
        """Start over with a fresh clock (optionally with a new length)."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if duration is not None:
            self.duration = duration

        self.running = False
        self.start_time = None
        self.sentences_done = 0
        self.total_typed = 0
        self.total_checked = 0
        self.total_errors = 0

        for seconds, button in self.option_buttons.items():
            if seconds == self.duration:
                button.set_colours(ACCENT, "#f6efff", ACCENT)
            else:
                button.set_colours(PILL, INK, PILL_HOVER)

        self.timer_label.config(text=format_time(self.duration), fg=INK)
        self.result_main.config(text="")
        self.result_detail.config(text="")
        self.result_rating.config(text="")
        self.hint_label.config(
            text="The clock starts with your first key. Press Enter for the next sentence.")

        self.text_box.config(state="normal")
        self.show_next_sentence()
        self.text_box.focus_set()

    def show_next_sentence(self):
        self.target = pick_sentence(self.deck, self.target)
        self.target_label.config(text=self.target)
        self.text_box.delete("1.0", "end")

    def on_key_press(self, event):
        # Start the clock on the first real character
        if self.start_time is None and event.char and event.char.isprintable():
            self.start_time = time.monotonic()
            self.running = True
            self.update_hint()
            self.tick()

    def on_key_release(self, event):
        if self.running:
            self.colour_text(self.get_typed())

    def on_enter(self, event):
        if self.running:
            self.submit_sentence()
        return "break"                    # never add a new line to the box

    def get_typed(self):
        return self.text_box.get("1.0", "end-1c")

    def colour_text(self, typed):
        """Green for correct characters, red for wrong ones."""
        self.text_box.tag_remove("good", "1.0", "end")
        self.text_box.tag_remove("bad", "1.0", "end")
        for i, written in enumerate(typed):
            correct = i < len(self.target) and written == self.target[i]
            tag = "good" if correct else "bad"
            self.text_box.tag_add(tag, f"1.{i}", f"1.{i + 1}")

    def submit_sentence(self):
        """Score the sentence that was just typed and show the next one."""
        typed = self.get_typed().rstrip()
        if not typed:
            return
        errors, checked = score_attempt(self.target, typed)
        self.total_errors += errors
        self.total_checked += checked
        self.total_typed += len(typed)
        self.sentences_done += 1
        self.show_next_sentence()
        self.update_hint()

    def update_hint(self):
        self.hint_label.config(
            text=f"{plural(self.sentences_done, 'sentence')} finished. "
                 f"Press Enter for the next one.")

    def tick(self):
        if not self.running:
            return
        remaining = self.duration - (time.monotonic() - self.start_time)
        if remaining <= 0:
            self.finish_test()
            return
        self.timer_label.config(text=format_time(remaining),
                                fg=BAD if remaining <= 10 else INK)
        self.after_id = self.root.after(100, self.tick)

    def finish_test(self):
        """Time is up: add the unfinished sentence and show the results."""
        self.running = False
        self.after_id = None

        unfinished = self.get_typed().rstrip()
        self.text_box.config(state="disabled")

        errors = self.total_errors
        checked = self.total_checked
        typed_chars = self.total_typed
        if unfinished:
            extra_errors, extra_checked = score_attempt(self.target, unfinished,
                                                        unfinished=True)
            errors += extra_errors
            checked += extra_checked
            typed_chars += len(unfinished)

        self.timer_label.config(text="0:00", fg=BAD)
        self.hint_label.config(text="Time is up. Restart, or pick another length.")

        if typed_chars == 0:
            self.result_main.config(text="0 WPM")
            self.result_detail.config(text="Nothing was typed this round.")
            return

        wpm = calculate_wpm(typed_chars, self.duration)
        accuracy = calculate_accuracy(errors, checked)

        if wpm > self.best_wpm and accuracy >= 80:
            self.best_wpm = wpm
            self.best_label.config(text=f"Best speed this session: {wpm:.0f} WPM")

        self.result_main.config(text=f"{wpm:.0f} WPM")
        self.result_detail.config(
            text=f"{accuracy:.0f}% accuracy, {plural(errors, 'error')}, "
                 f"{plural(self.sentences_done, 'sentence')} finished")
        self.result_rating.config(text=get_rating(wpm, accuracy))


def main():
    root = tk.Tk()
    TypingTester(root)
    root.mainloop()


if __name__ == "__main__":
    main()
