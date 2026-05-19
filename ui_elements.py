from pyglet import text
from pyglet import image
from pyglet.sprite import Sprite

# contains pyglet ui labels and drawing functions
# separated from machine learning logic for cleaner structure

class TrainerUI:
    def __init__(self):
        self.title = text.Label(
            "Fitness Trainer",
            font_size=28,
            x=40,
            y=550,
            color=(0, 0, 0, 255)
        )

        self.activity = text.Label(
            "Current activity: waiting...",
            font_size=20,
            x=40,
            y=450,
            color=(0, 0, 0, 255)
        )

        self.accuracy = text.Label(
            "Model accuracy: -",
            font_size=16,
            x=40,
            y=400,
            color=(0, 0, 0, 255)
        )

        self.hint = text.Label(
            "Try: running / rowing / lifting / jumpingjacks",
            x=40,
            y=120,
            color=(0, 0, 0, 255)
        )

        # load activity images
        self.activity_images = {
            "running": [
                image.load("img/running_1.png"),
                image.load("img/running_2.png")
            ],

            "rowing": [
                image.load("img/rowing_1.png"),
                image.load("img/rowing_2.png")
            ],

            "lifting": [
                image.load("img/lifting_1.png"),
                image.load("img/lifting_2.png")
            ],

            "jumpingjacks": [
                image.load("img/jumpingjack_1.png"),
                image.load("img/jumpingjack_2.png")
            ]
        }

        self.current_frame = 0
        self.animation_counter = 0

        # default image shown at startup
        self.current_sprite = None

    # update activity text and animation based on predicted activity
    def set_activity(self, activity):

        self.activity.text = f"Current activity: {activity}"

        # image animation logic created with AI assistance
        if activity in self.activity_images:

            self.animation_counter += 1

            if self.animation_counter % 15 == 0:
                self.current_frame = 1 - self.current_frame

            # create sprite first time
            if self.current_sprite is None:

                self.current_sprite = Sprite(
                    self.activity_images[activity][self.current_frame],
                    x=500,
                    y=120
                )

            else:
                self.current_sprite.image = self.activity_images[activity][self.current_frame]

            # I adjust rowing images position because it's bigger than the others
            if activity == "rowing":
                self.current_sprite.x = 420
                self.current_sprite.y = 120
                self.current_sprite.scale = 0.65
            else:
                self.current_sprite.x = 500
                self.current_sprite.y = 120
                self.current_sprite.scale = 1.0

    def draw(self):
        self.title.draw()
        self.activity.draw()
        self.hint.draw()
        self.accuracy.draw()
        if self.current_sprite:
            self.current_sprite.draw()