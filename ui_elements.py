from pyglet import text

# contains pyglet ui labels and drawing functions
# separated from machine learning logic for cleaner structure

class TrainerUI:
    def __init__(self):
        self.title = text.Label(
            "Fitness Trainer",
            font_size=28,
            x=40,
            y=550
        )

        self.activity = text.Label(
            "Current activity: waiting...",
            font_size=20,
            x=40,
            y=450
        )

        self.accuracy = text.Label(
            "Model accuracy: -",
            font_size=16,
            x=40,
            y=400
        )

        self.hint = text.Label(
            "Try: running / rowing / lifting / jumpingjacks",
            x=40,
            y=120
        )

    def set_activity(self, activity):
        self.activity.text = f"Current activity: {activity}"

    def draw(self):
        self.title.draw()
        self.activity.draw()
        self.hint.draw()
        self.accuracy.draw()