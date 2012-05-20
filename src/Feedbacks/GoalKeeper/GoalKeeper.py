#!/usr/bin/env python



# GoalKeeper.py -
# Copyright (C) 2008-2009  Simon Scholler
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""GoalKeeper BCI Feedback."""


import random
import sys
import math
import random
import os
import time
from PIL import Image

import pygame

from FeedbackBase.PygameFeedback import PygameFeedback


class GoalKeeper(PygameFeedback):


    # TRIGGER VALUES FOR THE PARALLEL PORT (MARKERS)
    START_EXP, END_EXP = 252, 253
    COUNTDOWN_START = 0
    START_TRIAL_ANIMATION = 36
    TARGET_LEFT, TARGET_RIGHT = 1, 2
    CORRECT_LEFT, CORRECT_RIGHT = 11, 12
    INCORRECT_KL_TR, INCORRECT_KR_TL = 21, 22
    HIT_LEFT, HIT_RIGHT = 41, 42
    MISS_KL_TR, MISS_KR_TL, MISS_KM = 51, 52, 53
    TOO_LATE_LEFT, TOO_LATE_RIGHT = 31, 32
    TOO_LATE_CORRECT_LEFT, TOO_LATE_CORRECT_RIGHT = 61, 62
    TOO_LATE_INCORRECT_KL_TR, TOO_LATE_INCORRECT_KR_TL = 71, 72
    END_OF_RED_CIRCLE = 80
    SHORTPAUSE_START, SHORTPAUSE_END = 249, 250


    def init(self):
        """
        Initializes variables etc., but not pygame itself.
        """
        #self.logger.debug("on_init")
        ### TESTING
        PygameFeedback.init(self)
        self.caption = 'Goal Keeper'
        self.keyboard = 1
        if __name__ == '__main__':
            self.testing = 1
            print('WARNING: Testing Option ON!')
            self.TODAY_DIR = 'C:/'
            self.keyboard = 0
            self.counter = 0  # for sinewavy mu-rhythm feedback
        else:
            self.testing = 0
        ### end ###

        self.durationPerTrial = [2000, 2000]    # time of the trial at the beginning and the end
                                                # (linear interpolation in between); unused if
                                                # self.adaptive_trial_time = True

        ### adaptation specific settings (used only if self.adaptive_trial_time = True) ###
        self.adaptive_trial_time = True
        if self.adaptive_trial_time and not self.keyboard:
            self.read_log()
        self.log_written = 0
        self.max_durationPerTrial = 2500
        self.endtimes = []          # trial endtimes for log-file
        self.stepsize = 5           # stepsize of the adaptive procedure
                                    # (in percent of the initial trial time (=self.durationPerTrial[0])
        ### end ###

        ### mu-rhythm settings (used only if mu_fb = 1) ###
        self.mu_fb = 1
        self.mu_left, self.mu_right = 1,1
        self.mu_bound_left = [0,1]
        self.mu_bound_right = [0,1]
        self.colorbar = list()
        for n in range(101):
            self.colorbar.append((int(round(255*(n/100.0))), int(round(255*(1-n/100.0))),0))
        ### end ###

        self.trials = 2
        self.pauseAfter = 20
        self.pauseDuration = 15000
        self.FPS = 40
        self.fullscreen = False
        self.screenPos = [100, 100]
        self.screenSize = [640, 480]
        self.countdownFrom = 2  # should be 7
        self.hitMissDuration = 1000
        self.timeUntilNextTrial = [500, 1000]  # randomly between the two values
        self.showGameOverDuration = 3000
        self.timeOfStartAnimation = 2000
        self.showTrialStartAnimation = True
        self.showCounter = True
        self.control = "relative"  # or "absolute"
        self.iBorder = 1.0 # maximal (&-min) value of the classifier output integration
        self.iTimeUntilThreshold = 500  # minimal integration time needed to reach threshold [in ms]
        self.timeUntilIntegration = 500  # time to wait at trial start before integrating [in ms]
        self.g_abs = 1
        self.showRedBallDuration = 500       # in ms
        self.continueAfterMiss = True
        self.playTimeAfterMiss = 1500        # in ms
        self.distanceBetweenHalfBalls = 25             # in percent of the screen width


        # Feedback state booleans
        self.shortPause = False
        self.gameover, self.hit, self.miss, self.false = False, False, False, False
        self.countdown, self.firstTickOfTrial = True, True
        self.showsShortPause = False
        self.trialStartAnimation, self.waitBeforeTrial = False, False

        self.elapsed, self.trialElapsed, self.countdownElapsed = 0, 0, 0
        self.hitMissElapsed, self.shortPauseElapsed, self.completedTrials = 0, 0, 0
        self.animationElapsed, self.continueAfterMissElapsed, self.waitBeforeTrialElapsed = 0, 0, 0
        self.showsHitMiss = False

        self.f = 0.0
        self.hitMissFalse = [0, 0, 0]
        self.resized = False
        self.barX = 0
        self.memoResize = False
        self.c = 0
        self.directionToDigit = {'left': - 1, 'middle':0, 'right':1}
        self.digitToDirection = { - 1:'left', 0:'middle', 1:'right'}
        self.X = 0
        self.Y = 1
        self.eps = 0.5


        # Colour settings
        self.backgroundColor = (50, 50, 50)
        self.fontColor = (0, 150, 150)
        self.countdownColor = (200, 80, 118)
        self.fixcrossColor = (130,130,130)

        # Keeper specifications
        self.contKeeperMotion = 750   # if 0:  jump between the three positions
                                      # if >0: move in a continuous fashion
                                      #        (self.contKeeperMotion=duration of the movement in seconds)
        self.noReturn = True          # if self.threshold of the classifier bar is passed, the keeper
                                      # will move to this direction without reacting to further changes
        self.tol = 5           # tolerance in pixels between the keeper and the midbottom x-coordinate
                               # of the ball for which the trial still counts as a 'hit'

        # Classifier threshold for keeper position change
        self.threshold = 1

        # HitMissCounter
        self.hitmissCounterColor = self.fontColor #(100, 100, 100)
        self.hitstr = ""    # "Hit: "
        self.missstr = ":"  #" Miss: "
        self.falsestr = ":" # " False: "
        self.x_transl = 0.95


    def pre_mainloop(self):
        #self.logger.debug("on_play")
        PygameFeedback.pre_mainloop(self)
        #self.load_images()  # this is done in init_graphics
        self.init_run()
        self.gameover = False


    def post_mainloop(self):
        PygameFeedback.post_mainloop()
        self.send_parallel(self.END_EXP)


    def tick(self):
        self.process_pygame_events()
        if self.keypressed:
            if self.lastkey_unicode == u"f": self.f = - 1
            elif self.lastkey_unicode == u" " : self.f = 0
            elif self.lastkey_unicode == u"j" : self.f = 1
            self.keypressed = False
        pygame.time.wait(10)
        self.elapsed = self.clock.tick(self.FPS)


    def pause_tick(self):
        self.do_print("Pause", self.fontColor, self.size / 6)


    def play_tick(self):

        if self.countdown:
            self.nt = 0
            self.countdown_tick()
        elif self.hit or self.miss or self.false:
            self.hit_miss_tick()
            self.nt = 0
        elif self.gameover:
            self.gameover_tick()
        elif self.shortPause:
            self.short_pause_tick()
        elif self.waitBeforeTrial:
            self.wait_before_trial()
        elif self.trialStartAnimation:
            if self.mu_fb:
                self.update_mu_fb()
                self.animate_trial_start()
        else:
            self.nt += 1
            self.trial_tick()


    def on_control_event(self, data):
        ##self.logger.debug("on_control_event: %s" % str(data))
        self.f, self.mu_right, self.mu_left = data["cl_output"]


    def init_run(self):
        self.countdown, self.firstTickOfTrial = True, True
        self.elapsed, self.completedTrials = 0, 0
        self.hitMissFalse = [0, 0, 0]
        self.completedTrials = 0


    def trial_tick(self):
        """
        One tick of the trial loop.
        """
        self.trialElapsed += self.elapsed

        # save old move-rectangles for efficient drawing
        self.bMR, self.kMR = self.ballMoveRect.move(0, 0), self.keeperMoveRect.move(0, 0)

        if self.firstTickOfTrial:
            self.f = 0.0
            self.init_time = time.clock()
            # initialize feedback start screen
            resized = False
            self.firstChange = True
            self.markerSent = False
            self.init_graphics()
            self.endtimes.append(int(self.trialDuration))
            self.trialElapsed = 0
            self.c = 0
            self.barX = 0;
            if not self.showTrialStartAnimation:
                pygame.time.wait(random.randint(self.timeUntilNextTrial[0], self.timeUntilNextTrial[1]))  # TODO: implement wait-method
            self.firstTickOfTrial = False
            self.keeperPos = 'middle'
            self.keeperChanged = False
            self.direction = self.digitToDirection[self.directions[self.completedTrials % self.pauseAfter]]
            if self.direction == 'left':    self.send_parallel(self.TARGET_LEFT)
            else:                           self.send_parallel(self.TARGET_RIGHT)

        stepX = self.stepX * self.directionToDigit[self.direction]

        # Change keeper position according to classifier output
        keeperPosBefore = self.keeperPos
        if not self.noReturn or self.firstChange:
            class_out = self.update_classifier_bar()
            self.keeperPos = min(1, int(abs(class_out) + (1 - self.threshold)))
            if class_out < 0:
                self.keeperPos *= - 1
            self.keeperPos = self.digitToDirection[self.keeperPos]

        if self.keeperPos != keeperPosBefore:
            if self.noReturn:
                self.firstChange = False
                if self.continueAfterMissElapsed == 0:
                    if self.direction == self.keeperPos:
                        if self.direction == 'left':
                            self.send_parallel(self.CORRECT_LEFT)
                        else:
                            self.send_parallel(self.CORRECT_RIGHT)
                    else:
                        if self.direction == 'left':
                            self.send_parallel(self.INCORRECT_KR_TL)
                        else:
                            self.send_parallel(self.INCORRECT_KL_TR)


            # it keeper position change is continuous and position has changed in the PREVIOUS STEP
            if self.contKeeperMotion:
                self.c = 0
                self.keeperPosBefore = self.keeperMoveRect.centerx
                self.keeperChanged = False
                self.keeperChange = True
            # if keeper position change is instantaneous
            else:
                self.center = self.keeperCenter[self.keeperPos]


        # if keeper is currently changing the position (only applies for continuous keeper movement)
        if self.contKeeperMotion and self.keeperChange:
            # normal keeper update block during keeper position change
            if not self.keeperChanged:
                if self.memoResize:
                    self.memoResize = False
                    self.center = self.keeperMoveRect.center
                    self.keeperPosBefore = self.keeperMoveRect.centerx
                alpha = min(1.0, 1.0 * self.c / (self.contKeeperMotion / 1000.0 * self.FPS))
                self.c += 1
                if alpha == 1:
                    self.keeperChange = False
                    self.keeperChanged = True
                if self.noReturn:
                    centerX = alpha * self.keeperCenter[self.keeperPos][self.X] + (1 - alpha) * self.keeperCenter['middle'][self.X]
                    self.center = (centerX, self.keeperCenter[self.keeperPos][self.Y])
                else:
                    centerX = alpha * self.keeperCenter[self.keeperPos][self.X] + (1 - alpha) * self.keeperPosBefore
                    self.center = (centerX, self.keeperCenter[self.keeperPos][self.Y])
        self.keeperMoveRect = self.keeper.get_rect(center=self.center, size=self.keeperSize) # update keeper position

        # if normal trial is over
        if self.totalTrialTicks == self.nt:
            self.ballMoveRect = self.ball.get_rect(midbottom=(self.ballX, self.keeperSurface))
            if self.init_time != 0:
                print 'Optimal trial time: ' + str(self.trialDuration)
                print "Actual trial time: " + str(int((time.clock()-self.init_time)*1000)) + ' ms'
                print "Ticks: " + str(self.nt)
                print "*************************************"
                self.init_time = 0
            if self.keeperMoveRect.left - self.ballX > self.tol or self.ballX - self.keeperMoveRect.right > self.tol:
                if self.keeperPos == 'middle' or self.keeperPos == self.direction:
                    self.send_parallel(self.MISS_KM)
                    if not self.continueAfterMiss:
                        self.miss = True; return
                else:
                    if self.keeperPos == 'left':
                        self.send_parallel(self.MISS_KL_TR)
                    else:
                        self.send_parallel(self.MISS_KR_TL)
                    self.ball = pygame.transform.scale(self.ball_miss, self.ballSize)
                    self.false = True; return
            else:
                if self.direction == 'left':
                    self.send_parallel(self.HIT_LEFT)
                else:
                    self.send_parallel(self.HIT_RIGHT)
                self.hit = True; return

        elif self.continueAfterMiss and self.nt > self.totalTrialTicks:
            if self.continueAfterMissElapsed == 0:
                self.ball = pygame.transform.scale(self.ball_missCircle, self.ballSize)
            self.continueAfterMissElapsed += self.elapsed

            if not self.markerSent:
                if self.keeperPos == self.direction:
                    if self.direction == 'left':
                        self.send_parallel(self.TOO_LATE_CORRECT_LEFT)
                    else:
                        self.send_parallel(self.TOO_LATE_CORRECT_RIGHT)
                    self.markerSent = True
                elif self.keeperPos != 'middle':
                    if self.direction == 'left':
                        self.send_parallel(self.TOO_LATE_INCORRECT_KR_TL)
                    else:
                        self.send_parallel(self.TOO_LATE_INCORRECT_KL_TR)
                    self.ball = pygame.transform.scale(self.ball_miss, self.ballSize)
                    self.markerSent = True

            if self.continueAfterMissElapsed > self.playTimeAfterMiss:
                if self.keeperPos != 'middle' and self.keeperPos != self.direction:
                    self.false = True
                else:
                    self.miss = True
                return
        else:
            # Calculate the new ball position
            self.ballX = self.ballX + stepX
            self.ballY = self.ballY + self.stepY
            self.ballMoveRect = self.ball.get_rect(midbottom=(self.ballX, self.ballY))

        self.draw_all()


    def short_pause_tick(self):
        """
        One tick of the short pause loop.
        """
        if self.shortPauseElapsed == 0:
            self.send_parallel(self.SHORTPAUSE_START)

        self.shortPauseElapsed += self.elapsed

        if self.shortPauseElapsed >= self.pauseDuration:
            self.shortPause = False
            self.shortPauseElapsed = 0
            self.countdown = True
            self.send_parallel(self.SHORTPAUSE_END)
            return

        self.draw_all()
        self.do_print("Short Break...", self.fontColor, self.size / 10)

    def countdown_tick(self):
        """
        One tick of the countdown loop.
        """
        if self.countdownElapsed == 0:
            self.send_parallel(self.COUNTDOWN_START)
            self.draw_initial()
        self.countdownElapsed += self.elapsed
        if self.countdownElapsed >= (self.countdownFrom) * 1000:
            if self.completedTrials == 0:
                self.send_parallel(self.START_EXP)
            self.countdown = False
            self.countdownElapsed = 0
            self.waitBeforeTrial = True
            # initialize targets for the upcoming trial block randomly (equal 'left' and 'right' trials)
            self.directions = [1] * int(self.pauseAfter)
            self.directions[0:int(self.pauseAfter / 2)] = [ - 1] * int(self.pauseAfter / 2)
            random.shuffle(self.directions)
            return
        t = ((self.countdownFrom + 1) * 1000 - self.countdownElapsed) / 1000
        self.do_print(str(t), self.countdownColor, self.size / 4)


    def gameover_tick(self):
        """
        One tick of the game over loop.
        """
        self.draw_all(False)
        self.do_print("(%i : %i : %i)" % (self.hitMissFalse[0], self.hitMissFalse[1], self.hitMissFalse[2]), self.fontColor, self.size / 10)
        pygame.time.wait(self.showGameOverDuration)
        self.send_parallel(self.END_EXP)
        if self.adaptive_trial_time and not self.keyboard and not self.log_written:
            self.write_log()

    def write_log(self):
        self.set_trial_time()
        self.endtimes.append(self.trialDuration)
        file = open(self.logfilename, 'w')
        for n in range(len(self.endtimes)):
            file.write(str(int(self.endtimes[n]))+'\n')
        self.log_written = 1

    def read_log(self):
        subdir = '/adaptive_trial_times/'
        file = 'gk_block'
        file_no = 1
        if not os.access(self.TODAY_DIR + subdir, os.F_OK):
            os.mkdir(self.TODAY_DIR + subdir)
        elif os.listdir(self.TODAY_DIR + subdir):  # if not empty
            while os.access(self.TODAY_DIR+subdir+file+str(file_no)+'.txt', os.F_OK):
                file_no += 1
            f = open(self.TODAY_DIR+subdir+file+str(file_no-1)+'.txt')
            endtimes = f.readlines()
            self.durationPerTrial = [int(endtimes[-1][:]) * 1.2]
        self.logfilename = self.TODAY_DIR + subdir + file + str(file_no) + '.txt'

    def hit_miss_tick(self):
        """
        One tick of the Hit/Miss loop.
        """
        if self.hitMissElapsed == 0:
            #if self.continueAfterMiss and self.continueAfterMissElapsed!=0:
            #    self.send_parallel(self.END_OF_RED_CIRCLE)
            self.continueAfterMissElapsed = 0
            self.completedTrials += 1;
            self.firstTickOfTrial = True
            self.keeperChange = False
            if self.hit:
                self.lastTrial = 'hit'
                self.hitMissFalse[0] += 1
            elif self.false:
                self.lastTrial = 'miss'
                self.hitMissFalse[2] += 1
            else:
                self.lastTrial = 'late'
                self.hitMissFalse[1] += 1

            print "Score: " + str(self.hitMissFalse[0]) + ":" + str(self.hitMissFalse[1]) + ":" + str(self.hitMissFalse[2])

        self.hitMissElapsed += self.elapsed

        if self.hitMissElapsed >= self.hitMissDuration:
            self.hitMissElapsed = 0
            self.hit, self.miss, self.false = False, False, False
            self.showsHitMiss = False
            self.waitBeforeTrial = True

            if self.completedTrials % self.pauseAfter == 0:
                self.shortPause = True
            if self.completedTrials >= self.trials:
                self.gameover = True
            return

        self.draw_all()
        self.showsHitMiss = True


    def calc_classifier(self):
        class_out = self.f
        if self.control == "absolute":
            class_out = self.g_abs * class_out
        elif self.control == "relative":
            if self.timeUntilIntegration <= self.trialElapsed:
                class_out = self.threshold * class_out * 1000.0 / (self.FPS * self.iTimeUntilThreshold) + self.barX
                #class_out = class_out*self.g_rel*0.1+self.barX
                self.barX = max(- self.iBorder, min(self.iBorder, class_out))
            else:
                self.barX = 0
                class_out = 0
        else:
             raise Exception("Control type unknown (know types: 'absolute' and 'relative').")
        return class_out

    def update_classifier_bar(self, update_classifier=True):
        if update_classifier:
            class_out = self.calc_classifier()
        else:
            class_out = self.barX
        (barWidth, barHeight) = self.barSize
        if class_out > 0:
            self.barAreaRect = pygame.Rect(barWidth / 2, 0, class_out * barWidth / 2, barHeight)
            self.barRect = pygame.Rect(self.barCenter[0], self.barCenter[1] - barHeight / 2, class_out * barWidth / 2, barHeight)
        else:
            self.barAreaRect = pygame.Rect((1 + class_out) * barWidth / 2, 0, - class_out * barWidth / 2, barHeight)
            self.barRect = pygame.Rect(self.barCenter[0] + class_out * barWidth / 2, self.barCenter[1] - barHeight / 2, - class_out * barWidth / 2, barHeight)
        return class_out


    def draw_all(self, drawall=False, drawhbs=False):
        """
        Draw current feedback state onto the screen.
        """
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.keeper, self.keeperMoveRect)
        self.screen.blit(self.bar, self.barRect, self.barAreaRect)
        self.screen.blit(self.frame, self.frameRect)
        self.screen.blit(self.tb1, self.tb1Rect)
        self.screen.blit(self.tb2, self.tb2Rect)
        self.screen.blit(self.fixl, self.fixlRect)
        self.screen.blit(self.fixr, self.fixrRect)
        self.screen.blit(self.fixb, self.fixbRect)
        if drawhbs:
            self.screen.blit(self.hbLeft, self.hbLeftRect)
            self.screen.blit(self.hbRight, self.hbRightRect)
        elif self.miss and self.showRedBallDuration >= self.hitMissElapsed and not self.continueAfterMiss:
            self.screen.blit(self.ball_miss, self.ballMoveRect)
        else:
            self.screen.blit(self.ball, self.ballMoveRect)
        if self.showCounter:
            s = self.hitstr + str(self.hitMissFalse[0]) + self.missstr + str(self.hitMissFalse[1]) + self.falsestr + str(self.hitMissFalse[ - 1])
            self.do_print(s, self.hitmissCounterColor, self.counterSize, self.counterCenter)
        if drawall or drawhbs:
            pygame.display.update()
        else:
            pygame.display.update([self.ballMoveRect, self.ballRect, self.barRect_init, self.keeperMoveRect, self.kMR, self.bMR, self.fixbRect])

    def wait_before_trial(self):
        if self.waitBeforeTrialElapsed == 0:
            self.init_graphics()
            self.draw_initial()
            self.waitBeforeTrialTime = random.randint(self.timeUntilNextTrial[0], self.timeUntilNextTrial[1])
        self.waitBeforeTrialElapsed += self.elapsed
        if (self.waitBeforeTrialElapsed >= self.waitBeforeTrialTime):
            self.waitBeforeTrialElapsed = 0
            self.waitBeforeTrial = False
            if self.showTrialStartAnimation:
                self.trialStartAnimation = True

    def animate_trial_start(self):
        """ animate the start of the trial. """
        if self.animationElapsed == 0:
            self.send_parallel(self.START_TRIAL_ANIMATION)
        self.animationElapsed += self.elapsed
        if self.timeOfStartAnimation < self.animationElapsed:
            self.trialStartAnimation = False
            self.reset_cursor_colors()
            self.animationElapsed = 0
            self.hbLeftRect = self.hbLeft.get_rect(midright=self.ballRect.center)
            self.hbRightRect = self.hbRight.get_rect(midleft=self.ballRect.center)
            self.draw_initial()
            return
        endpos = self.ballRect.center
        alpha = 1.0 * self.animationElapsed / self.timeOfStartAnimation
        offset = (1 - alpha) * self.hbOffset
        self.hbLeftRect = self.hbLeft.get_rect(midright=(self.ballRect.centerx - offset, self.ballRect.centery))
        self.hbRightRect = self.hbRight.get_rect(midleft=(self.ballRect.centerx + offset, self.ballRect.centery))
        self.barAreaRect = pygame.Rect(0, 0, 0, 0)
        self.draw_all(True, True)

    def do_print(self, text, color, size=None, center=None, superimpose=True):
        """
        Print the given text in the given color and size on the screen.
        """
        if not color:
            color = self.fontColor
        if not size:
            size = self.size / 10
        if not center:
            center = self.screen.get_rect().center

        font = pygame.font.Font(None, size)
        if not superimpose:
            self.screen.blit(self.background, self.backgroundRect)
        surface = font.render(text, 1, color, self.backgroundColor)
        self.screen.blit(surface, surface.get_rect(center=center))
        if superimpose:
            pygame.display.update(surface.get_rect(center=center))

    def update_mu_fb(self):
        if self.testing:
            self.counter = self.counter+1
            self.mu_left = abs(math.sin(self.counter*0.05))
            self.mu_right = abs(math.cos(self.counter*0.05))
        self.mu_left = self.normalize_mu(self.mu_left, 'left')
        self.mu_right = self.normalize_mu(self.mu_right, 'right')
        colorl = self.colorbar[int(self.mu_left*(len(self.colorbar)-1) )]
        colorr = self.colorbar[int(self.mu_right*(len(self.colorbar)-1) )]
        pygame.draw.polygon(self.fixl, colorl, self.pointlistl)
        pygame.draw.polygon(self.fixr, colorr, self.pointlistr)

    def normalize_mu(self, mu, mu_class):
        if mu_class=='left':
            bound = self.mu_bound_left
        elif mu_class=='right':
            bound = self.mu_bound_right
        if mu>bound[1]:
            mu = 1
        elif mu<bound[0]:
            mu = 0
        else:
            mu = (1/(bound[1]-bound[0])) * (mu-bound[0])
        return mu


    def reset_cursor_colors(self):
        pygame.draw.polygon(self.fixl, self.fixcrossColor, self.pointlistl)
        pygame.draw.polygon(self.fixr, self.fixcrossColor, self.pointlistr)

    def load_images(self):
        path = os.path.dirname(globals()["__file__"])
        self.keeper = pygame.image.load(os.path.join(path, 'keeper.png')).convert()
        self.frame = pygame.image.load(os.path.join(path, 'frame_blue_grad.bmp')).convert()
        self.bar = pygame.image.load(os.path.join(path, 'classifierbar.png')).convert()
        self.ball = pygame.image.load(os.path.join(path, 'ball.png')).convert()
        self.ball_miss = pygame.image.load(os.path.join(path, 'ball_miss.png')).convert()
        self.ball_missCircle = pygame.image.load(os.path.join(path, 'ball_missCircle3.png')).convert()
        self.hbLeft = pygame.image.load(os.path.join(path, 'halfball_left.png')).convert()
        self.hbRight = pygame.image.load(os.path.join(path, 'halfball_right.png')).convert()
        self.ballMemo = self.ball

    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size.
        """
        try:
            self.oldKeeperRange = self.keeperRange
            self.oldKeeperSurface = self.keeperSurface
            self.oldOffsetGap = self.offsetGap
            self.oldBallX = self.ballX
            self.oldBallY = self.ballY
        except:
            pass
        self.load_images() #sadly, this has to be done everytime, otherwise the images look crappy when resizing
        self.screen = pygame.display.get_surface()
        self.size = min(self.screen.get_height(), self.screen.get_width())
        #barWidth = int(self.screenSize[0] * 0.7)
        barHeight = int(self.screenSize[1] * 0.08)

        # init background
        self.background = pygame.Surface((self.screenSize[0], self.screenSize[1]))
        self.background = self.background.convert()
        self.backgroundRect = self.background.get_rect(center=self.screen.get_rect().center)
        self.background.fill(self.backgroundColor)

        # init keeper
        self.keeperSize = (self.screenSize[0] / 5, self.screenSize[0] / 30)
        self.offsetGap = self.screenSize[0] / 4
        gap = (self.screenSize[0] - 3 * self.keeperSize[0] - 2 * self.offsetGap) / 4
        self.keeperY = int((6.0 / 7) * self.screenSize[1])
        self.keeperCenter = {}
        keeper_pos = ['left', 'middle', 'right']
        for n in range(3):
            self.keeperCenter[keeper_pos[n]] = (self.offsetGap + gap * (n + 1) + int((0.5 + n) * self.keeperSize[0]), self.keeperY)
        self.center = self.keeperCenter['middle']
        self.keeper = pygame.transform.scale(self.keeper, self.keeperSize)
        self.keeperRect = self.keeper.get_rect(center=self.keeperCenter['middle'], size=self.keeperSize)
        self.keeperSurface = self.keeperRect.top
        self.keeperRange = (self.keeperCenter['middle'][self.X] - self.keeperCenter['left'][self.X])

        # init fixation cross
        fc = self.keeperRect.height
        d = fc/6
        self.fixl = pygame.Surface((fc, fc)) # left part
        self.fixr = pygame.Surface((fc, fc)) # right part
        self.fixb = pygame.Surface((fc, fc)) # border of fixtation cross
        self.fixlRect = self.fixl.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/3))
        self.fixrRect = self.fixr.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/3))
        self.fixbRect = self.fixb.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/3))
        self.fixl.set_colorkey((0,0,0))
        self.fixr.set_colorkey((0,0,0))
        self.fixb.set_colorkey((0,0,0))
        fc2 = fc/2
        self.pointlistl = [(fc2-d,0),(fc2-d,fc2-d),(0,fc2-d),(0,fc2+d),(fc2-d,fc2+d),(fc2-d,fc),(fc2,fc),(fc2,0)]
        self.pointlistr = [(fc2+d,0),(fc2+d,fc2-d),(fc,fc2-d),(fc,fc2+d),(fc2+d,fc2+d),(fc2+d,fc),(fc2,fc),(fc2,0)]
        pointlistb = [(fc2-d,0),(fc2-d,fc2-d),(0,fc2-d),(0,fc2+d),(fc2-d,fc2+d),(fc2-d,fc),(fc2+d,fc),(fc2+d,fc2+d),(fc,fc2+d),(fc,fc2-d),(fc2+d,fc2-d),(fc2+d,0)]
        pygame.draw.polygon(self.fixl, self.fixcrossColor, self.pointlistl)
        pygame.draw.polygon(self.fixr, self.fixcrossColor, self.pointlistr)
        pygame.draw.polygon(self.fixb, self.fixcrossColor, pointlistb, 3)

        # init classifier bar frame
        self.frameSize = (self.keeperRange * 2 + self.keeperSize[0], barHeight)
        self.barCenter = (self.screenSize[0] / 2, int(self.screenSize[1] * (6.5 / 7)))
        self.frame = pygame.transform.scale(self.frame, self.frameSize)
        self.frame.set_colorkey((255, 255, 255))
        self.frameRect = self.frame.get_rect(center=self.barCenter, size=self.frameSize)

        # init classifier bar
        self.barSize = (int(0.95 * self.frameSize[0]), int(0.7 * self.frameSize[1]))
        self.bar = pygame.transform.scale(self.bar, self.barSize)
        self.barRect_init = self.bar.get_rect(center=self.barCenter, size=self.barSize)

        # init threshold bars (left and right)
        self.tbSize = (self.frameSize[0] / 100, self.frameSize[1])
        self.tb1 = pygame.Surface(self.tbSize)
        self.tb2 = pygame.Surface(self.tbSize)
        c = (16, 174, 188)
        c = (44, 255, 255)
        self.tb1.fill(c)
        self.tb2.fill(c)
        if self.threshold > 0.9:
            self.tb1.set_colorkey(c)
            self.tb2.set_colorkey(c)
        self.tb1Rect = self.tb1.get_rect(center=(self.barCenter[0] - self.threshold * self.barSize[0] / 2, self.barCenter[1]))
        self.tb2Rect = self.tb2.get_rect(center=(self.barCenter[0] + self.threshold * self.barSize[0] / 2, self.barCenter[1]))

        # init ball
        diameter = self.keeperSize[0] / 5
        self.ballSize = (diameter, diameter)
        ballOffsetY = int(0.05 * self.screenSize[1])
        self.ball = pygame.transform.scale(self.ball, self.ballSize)
        self.ball_miss = pygame.transform.scale(self.ball_miss, self.ballSize)
        self.ballRect = self.ball.get_rect(midtop=(self.screenSize[0] / 2, ballOffsetY))
        self.ballX, self.ballY = self.ballRect.centerx, self.ballRect.bottom
        self.distBallKeeper = self.keeperRect.top - self.ballRect.bottom
        self.ball.set_colorkey((0,0,0))

        # init hbs
        if self.showTrialStartAnimation:
            self.hbSize = (diameter / 2, diameter)
            self.hbOffset = self.screenSize[0] * (self.distanceBetweenHalfBalls / 2) / 100
            self.hbLeft = pygame.transform.scale(self.hbLeft, self.hbSize)
            self.hbLeftRect = self.hbLeft.get_rect(midright=(self.ballRect.centerx - self.hbOffset, self.ballRect.centery))
            self.hbRight = pygame.transform.scale(self.hbRight, self.hbSize)
            self.hbRightRect = self.hbRight.get_rect(midleft=(self.ballRect.centerx + self.hbOffset, self.ballRect.centery))

        self.counterCenter = (self.frameRect.right * self.x_transl, self.size / 20)
        self.counterSize = self.screenSize[1] / 15

        # Calculate stepsize in x- and y-direction of the ball dependend on the ball speed
        if not self.waitBeforeTrial:
            self.set_trial_time()
        self.stepY = self.distBallKeeper / (self.trialDuration / 1000.0 * self.FPS)
        tangens = 1.0 * self.keeperRange / self.distBallKeeper
        self.stepX = tangens * self.stepY
        self.speed = math.sqrt(self.stepX ** 2 + self.stepY ** 2)
        self.totalTrialTicks = int(self.distBallKeeper / self.stepY)

        if not self.resized:
            # init helper rectangle for keeper (deep copy)
            self.ball = pygame.transform.scale(self.ballMemo, self.ballSize)
            self.keeperMoveRect = self.keeperRect.move(0, 0)
            self.ballMoveRect = self.ballRect.move(0, 0)
            self.barRect = self.barRect_init
            self.barAreaRect = None
            self.kMR, self.bMR = None, None
            self.keeperChange = False
            self.keeperChanged = False
        else:
            self.ballX = (1.0 * self.keeperRange / self.oldKeeperRange) * self.oldBallX
            self.ballY = (1.0 * self.keeperSurface / self.oldKeeperSurface) * self.oldBallY
            self.ballMoveRect = self.ball.get_rect(midbottom=(self.ballX, self.ballY))
            cX = ((1.0 * self.keeperMoveRect.centerx - self.oldOffsetGap) / (self.oldKeeperRange * 2)) * self.keeperRange * 2 + self.offsetGap
            self.keeperMoveRect = self.keeper.get_rect(center=(cX, self.keeperRect.centery))
            self.resized = False
            self.update_classifier_bar(False)
            self.memoResize = True
            if self.countdown or self.shortPause or self.trialStartAnimation:
                self.draw_all(True, True)
            else:
                self.draw_all(True)

    def set_trial_time(self):
        if self.adaptive_trial_time and self.completedTrials > 0:
            if self.lastTrial == 'hit':
                td = self.trialDuration - self.durationPerTrial[0] * (self.stepsize/100.0)
            else:
                td = self.trialDuration + self.durationPerTrial[0] * (self.stepsize/100.0)
            self.trialDuration = min(self.max_durationPerTrial, td)
        elif self.adaptive_trial_time and self.completedTrials == 0:
            self.trialDuration = self.durationPerTrial[0]
        else:
            alpha = 1.0 * self.completedTrials / self.trials
            self.trialDuration = (1 - alpha) * self.durationPerTrial[0] + alpha * self.durationPerTrial[1]

    def draw_initial(self, draw=True):
        """
        Draw initial feedback onto the screen.
        """
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.keeper, self.keeperRect)
        self.screen.blit(self.frame, self.frameRect)
        self.screen.blit(self.tb1, self.tb1Rect)
        self.screen.blit(self.tb2, self.tb2Rect)
        self.screen.blit(self.fixl, self.fixlRect)
        self.screen.blit(self.fixr, self.fixrRect)
        self.screen.blit(self.fixb, self.fixbRect)
        if self.showTrialStartAnimation:
            self.screen.blit(self.hbLeft, self.hbLeftRect)
            self.screen.blit(self.hbRight, self.hbRightRect)
        else:
            self.screen.blit(self.ball, self.ballMoveRect)
        if self.showCounter:
            s = self.hitstr + str(self.hitMissFalse[0]) + self.missstr + str(self.hitMissFalse[1]) + self.falsestr + str(self.hitMissFalse[ - 1])
            self.do_print(s, self.hitmissCounterColor, self.counterSize, self.counterCenter)
        if draw:
            pygame.display.flip()


if __name__ == '__main__':
    gk = GoalKeeper()
    gk.on_init()
    gk.on_play()
