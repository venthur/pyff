
import random

from FeedbackBase import PygameFeedback


def stroop_iterator(classes):
    last_elem = classes[0]
    while True:
        elem = random.choice(classes)
        while elem[0] == last_elem[0]:
            elem = random.choice(classes)
        last_elem = elem
        yield elem


class StroopFeedback(PygameFeedback.PygameFeedback):

    def init(self):
        PygameFeedback.PygameFeedback.init(self)

        # all possible colors
        colors = ["red", "blue", "green", "brown", "purple"]
        self.colors = {"red" : [255,0,0],
                       "green" : [0, 191, 0],
                       "blue" : [0,0,255],
                       "brown" : [150, 75, 0],
                       "purple" : [128, 0, 128]}

        # all possible combinations of [color1, color2] where color1 != color2
        # color1 is the printed word, color2 the actual color
        classes = [[i,j] for i in colors for j in colors if i != j]

        self.si = stroop_iterator(classes)
        self.timer = 0
        self.current = self.si.next()


    def play_tick(self):
        self.do_print(self.current[0], self.colors[self.current[1]], 200, superimpose=False)
        self.timer += self.elapsed
        if self.timer > 1000:
            self.timer = 0
            self.current = self.si.next()


    def pause_tick(self):
        self.do_print("pause", (128,128,128), 100)


if __name__ == "__main__":
    fb = StroopFeedback()
    fb.on_init()
    fb.on_play()

