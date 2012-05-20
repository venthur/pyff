#!/usr/bin/env python


# LibetClock.py -
# Copyright (C) 2008  Simon Scholler
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

"""LibetClock Feedback."""

import random
import sys
import math
import os

import pygame

from FeedbackBase.PygameFeedback import PygameFeedback


class LibetClock(PygameFeedback):

    # TRIGGER VALUES FOR THE PARALLEL PORT (MARKERS)
    # 1st QUARTER: 9    (cf. end of 'trial_tick()')
    # 2nd QUARTER: 18   (cf. end of 'trial_tick()')
    # 3rd QUARTER: 27   (cf. end of 'trial_tick()')
    # 4th QUARTER: 36   (cf. end of 'trial_tick()')

    GAME_START, GAME_OVER = 252, 253
    COUNTDOWN_START = 30
    SHORTPAUSE_START = 249
    TRIAL_START = 40
    KEY_PRESS = 128
    # Trial end markers
    TE_VALID, TE_VALID_NOKP, TE_VALID_CLS_BEFORE_KP = 41, 42, 47
    TE_INVALID_MOREKP, TE_INVALID_TOOEARLY = 43, 44
    TE_INVALID_UNPRECISE, TE_INVALID_NOKP = 45, 46
    CLASSIFIER_MOVE = 100
    CLASSIFIER_NOMOVE = 110
    GAME_STATUS_PAUSE = 211


################################################################################


    def init(self):
        """
        Initializes the variables and stuff, but not pygame itself.
        """
        PygameFeedback.init(self)

        if __name__ == '__main__':
            self.screenPos = [200, 200, 600, 400]
        else:
            self.screenPos = [0, 0, 1280, 800] #[0, 0, 1920, 1200]

        self.TODAY_DIR = 'l:/data/bbciRaw/'
        self.writeClassifierLog = 1
        self.classifier_log = []
        self.cls_evolution_log = []

        self.revolutionTime = 4000  # time the clock hand needs for one revolution (in ms)
        self.quarterTime = self.revolutionTime/4
        self.nRev = 2               # number of clockhand revolutions per trial
        self.intertrialInterval = [2500, 3500]     # (in ms)
        self.showClassifier = 'random'   # 'none', 'random', 'feedback'
        self.cls_move_prob = 0.25  # probability that classifier is true at a target
                                  # (only applies  if self.showClassifier=='random')
        self.trials = 50
        self.pauseAfter = 10
        self.pauseDuration = 9000      # (in ms)
        self.kp_perfect_tol = 15       # (in ms)
        self.FPS = 50
        self.fullscreen =  False
        self.screenWidth =  self.screenPos[2]#900
        self.screenHeight =  self.screenPos[3]#600
        self.countdownFrom = 3
        self.threshold = 0
        self.redClockDuration = self.revolutionTime/8
        self.SADuration = 1000
        self.cls_ival = (-400, -200)
        self.keypress_tolerance = 50     # time deviation tolerate (in ms) of the keypress from
                                         # when the clockhand actually is at the target

        self.pause = False
        self.quit = True
        self.quitting = True

        self.gameover = False
        self.countdown = True
        self.hit = False
        self.miss = False
        self.shortPause = False
        self.end_of_trial = False
        self.start_animation = False
        self.firstTickOfTrial = True

        self.showsPause, self.showsShortPause = False, False
        self.showsHitMiss, self.showsGameover = False, False

        self.elapsed, self.trialElapsed, self.countdownElapsed, self.redClockElapsed = 0,0,0,0
        self.shortPauseElapsed, self.trialSAElapsed, self.endOfTrialElapsed = 0,0,0

        self.f = 0
        self.hitMiss = [0,0]
        self.it = 0

        self.backgroundColor = (64,64,100)
        self.clockColor = (50,50,200)
        self.redClockColor = (200,0,0)
        self.fontColor = (237, 100, 148)
        self.fb_color_good = (0, 180, 0)
        self.fb_color_bad = (200, 0, 0)
        self.countdownColor = (237, 100, 148)

        self.completedTrials = 0
        self.validTrials = 0
        self.infostr = ''
        self.infocolor = self.fb_color_good


    def post_mainloop(self):
        self.logger.debug("on_quit")
        self.send_parallel(self.GAME_OVER)
        PygameFeedback.post_mainloop()

    def on_control_event(self, data):
        self.f = data["cl_output"]

    def tick(self):
        self.process_pygame_events()
        if self.keypressed:
            if self.lastkey_unicode == u"j":
                if self.trialElapsed != 0:
                    self.send_parallel(self.KEY_PRESS)
                    if self.buttonPressed:
                        self.buttonPressError = True
                    else:
                        self.buttonPressed = True
                        self.buttonPressTime = self.trialElapsed
        pygame.time.wait(10)
        self.elapsed = self.cpu_clock.tick(self.FPS)


    def play_tick(self):
        """
        One tick of the main loop.

        Decides in wich state the feedback currently is and calls the apropriate
        tick method.
        """
        if self.pause:
            self.pause_tick()
        elif self.gameover:
            self.gameover_tick()
        elif self.countdown:
            self.countdown_tick()
        elif self.shortPause:
            self.short_pause_tick()
        elif self.start_animation:
            self.trial_start_animation()
        elif self.end_of_trial:
            self.end_of_trial_tick()
        else:
            self.trial_tick()

    def trial_start_animation(self):

        self.trialSAElapsed += self.elapsed

        if self.SADuration<self.trialSAElapsed:
            self.start_animation = False
            self.trialSAElapsed = 0
        else:
            angle = max(90,90+(self.arcAngle-90) * (1.0*(self.SADuration-self.trialSAElapsed)/self.SADuration))
            self.arc.fill(self.backgroundColor)
            self.arcRect.topleft = self.screen.get_rect().topleft
            pygame.draw.arc(self.arc, self.arcColor, self.arcRect, math.radians(90), math.radians(angle), self.arcWidth)
            self.arcRect.center = self.screencenter
            self.draw_all()


    def trial_tick(self):
        """
        One tick of the trial loop.
        """
        self.trialElapsed += self.elapsed

        # Teste ob erster Tick im Trial
        if self.firstTickOfTrial:
            if self.completedTrials == 0:
                self.send_parallel(self.GAME_START)  # sending this in pre_mainloop is too early for bbci_bet_apply
                                                # (cf. variable start_marker_received in bbci_bet_apply)
            print 'showClassifier: ' + str(self.showClassifier)
            print 'cls_ival: ' + str(self.cls_ival)
            print 'threshold: ' + str(self.threshold)
            self.send_parallel(self.TRIAL_START)
            self.classifier_log.append(list())
            self.cls_evolution_log.append(list())
            self.mrk_log = True
            pygame.draw.circle(self.clock, self.clockColor, (self.diameter/2,self.diameter/2), self.diameter/2)
            self.firstTickOfTrial = False
            self.redClock = False
            self.redClockElapsed = 0
            self.buttonPressError = False
            self.buttonPressed = False
            self.target = 0
            self.clockhandAngle = 0
            self.classified = False
            #self.targetTransitionTimes = []
            self.classifierTime = 0
            if self.nRev == 1:
                self.durationPerTrial = self.revolutionTime + 200
                self.currTargetAngle = (90, 180, 270, 360)
                self.TARGET_MARKER = (9, 18, 27, 36)
            else:
                self.durationPerTrial = self.revolutionTime*self.nRev
                totAn = self.nRev*360
                self.currTargetAngle = (totAn-360, totAn-270, totAn-180, totAn-90)
                self.TARGET_MARKER = (1, 9, 18, 27)
            self.nTargets = len(self.currTargetAngle)
            self.set_classification_time()

        # classifier evolution log
        self.cls_evolution_log[self.completedTrials].append(self.trialElapsed)
        self.cls_evolution_log[self.completedTrials].append(self.f)

        # Teste ob zeit fuer alten Trial abgelaufen ist
        if self.trialElapsed >= self.durationPerTrial:
                self.trialElapsed = 0
                pygame.draw.circle(self.clock, self.clockColor, (self.diameter/2,self.diameter/2), self.diameter/2)
                self.arcRect.topleft = self.screen.get_rect().topleft
                pygame.draw.arc(self.arc, self.arcColor, self.arcRect, math.radians(90), math.radians(self.arcAngle), self.arcWidth)
                self.arcRect.center = self.screencenter
                self.firstTickOfTrial = True
                self.end_of_trial = True

        # draw red 'no-move' clock
        if self.redClock:
            self.redClockElapsed += self.elapsed
            if self.redClockDuration<self.redClockElapsed:
                pygame.draw.circle(self.clock, self.clockColor, (self.diameter/2,self.diameter/2), self.diameter/2)
                self.redClockElapsed = 0
                self.redClock = False

        if self.showClassifier != 'none':
            # evalute classifier if classifier should be evalutated
            t = (self.trialElapsed%self.quarterTime)-self.quarterTime # time the clockhand needs to the next target
            if self.is_within_cls_interval(t) and not self.classified:
                self.classified = True
                if not self.buttonPressed:
                    self.classifier_log[self.completedTrials].append(self.f)
                else:
                    self.classifier_log[self.completedTrials].append('NaN')

#===============================================================================
#                if self.mrk_log:
#                    self.mrk_log = False
#                    if self.buttonPressed and self.buttonPressTime>self.revolutionTime+self.cls_ival[1]:
#                        self.marker_log[self.completedTrials][-1] = 1
#                    elif self.classifierTime!=0:
#                        self.marker_log[self.completedTrials][-1] = 2
#                    self.marker_log[self.completedTrials].append(0)
#                else:
#                    self.marker_log[self.completedTrials].append('NaN')
#===============================================================================

                if not self.buttonPressed and self.classifierTime==0:
                    if self.showClassifier == 'random':
                        p = random.random()
                        if p>(1.0-self.cls_move_prob):
                            f = self.threshold-1
                        else:
                            f = self.threshold+1
                    elif self.showClassifier == 'feedback':
                        print 'self.f: ' + str(self.f)
                        print 'self.f-threshold: ' + str(self.f-self.threshold)
                        f = self.f
                    else:
                        raise Exception('String option given by ''self.showClassifier'' unknown.')

                    if f <= self.threshold:
                        pygame.draw.circle(self.clock, self.redClockColor, (self.diameter/2,self.diameter/2), self.diameter/2)
                        self.redClock = True
                        self.send_parallel(self.CLASSIFIER_MOVE)
                        self.classifierTime = self.trialElapsed
                    else:
                        self.send_parallel(self.CLASSIFIER_NOMOVE)

        # calculate new position of the clock hand
        angle_t0 = -self.clockhandAngle-self.currTargetAngle[self.target]
        self.clockhandAngle = self.nRev * max(-360, -360 * (1.0*self.trialElapsed/(self.nRev*self.revolutionTime)))
        self.clockhand_rotated = pygame.transform.rotate(self.clockhand, self.clockhandAngle)
        self.clockhandRect_rotated = self.clockhand_rotated.get_rect(center=self.screencenter)
        self.clockhandRect_rotated.center = self.clockhandRect.center
        angle_t1 = -self.clockhandAngle-self.currTargetAngle[self.target]

        # check when the clockhand target transition actually occurs
        if angle_t0<0 and angle_t1>=0:
            self.send_parallel(self.TARGET_MARKER[self.target])
            self.classified = False
            #self.f += 1   # for 'classifier log' testing purposes
            self.set_classification_time()
            #self.targetTransitionTimes.append(self.trialElapsed)
            self.target += 1
            if self.target==4:
                self.target = 0
        self.draw_all_rotating()

    def is_within_cls_interval(self,t):
        lastRevolution = self.trialElapsed>self.revolutionTime*(self.nRev-1)-self.quarterTime
        return t>self.cls_time and self.durationPerTrial-self.quarterTime>self.trialElapsed and lastRevolution

    def end_of_trial_tick(self):
        if self.endOfTrialElapsed == 0:
            #print 'self.targetTransitionTimes: ' + str(self.targetTransitionTimes)
            print 'trial ' + str(self.completedTrials)
            print 'valid trial ' + str(self.validTrials)
            self.time_accuracy()
            endTrialTime =  [self.intertrialInterval[0]-self.SADuration, self.intertrialInterval[0]-self.SADuration]
            nu = random.random()
            self.endOfTrialDuration = nu*endTrialTime[0] + (1-nu) * endTrialTime[1]

        self.endOfTrialElapsed += self.elapsed
        if self.endOfTrialElapsed>self.endOfTrialDuration:
            self.end_of_trial = False
            self.endOfTrialElapsed = 0
            self.completedTrials += 1
            self.validTrials += 1
            if self.validTrials >= self.trials:
                self.gameover = True
            elif self.completedTrials % self.pauseAfter == 0:
                self.shortPause = True
            else:
                self.start_animation = True
        self.draw_all(False)
        center = (self.screencenter[0], self.screencenter[1]/2)
        self.do_print(self.infostr, self.infocolor, self.size/20, True)#, center)


    def time_accuracy(self):
        if self.buttonPressError:         # key was pressed more than once
            self.infocolor = self.fb_color_bad
            self.infostr = ['More than one keypress!', 'Please press only once per trial!']
            self.validTrials -= 1
            self.send_parallel(self.TE_INVALID_MOREKP)
            self.classifier_log[self.completedTrials].append(0.1)
        elif self.buttonPressed:           # calculate time difference between optimal and actual keypress
            t = self.buttonPressTime%(self.quarterTime)
            timediff = min(t, abs(t-(self.quarterTime)))
            if self.buttonPressTime <= self.durationPerTrial-self.revolutionTime-(self.quarterTime/2):
                    self.infocolor = self.fb_color_bad
                    self.infostr = ['Press key only during', 'the last revolution.']
                    self.validTrials -= 1
                    self.send_parallel(self.TE_INVALID_TOOEARLY)
                    self.classifier_log[self.completedTrials].append(0.2)
            else:
                if timediff > self.keypress_tolerance:
                    self.infocolor = self.fb_color_bad
                    str1 = 'Time of keypress to unprecise!'
                    self.validTrials -= 1
                    self.send_parallel(self.TE_INVALID_UNPRECISE)
                    self.classifier_log[self.completedTrials].append(0.3)
                else:
                    str1 = 'Time accuracy: '
                    self.infocolor = self.fb_color_good
                    if self.classifierTime!=0 and (self.buttonPressTime-self.classifierTime>500):
                        self.send_parallel(self.TE_VALID_CLS_BEFORE_KP)
                    else:
                        self.send_parallel(self.TE_VALID)
                    self.classifier_log[self.completedTrials].append(timediff)
                if timediff < self.kp_perfect_tol:
                    self.infostr = [str1, 'Perfect!']
                else:
                    if t == timediff:
                        self.infostr = [str1, str(timediff) + ' ms after target.']
                    else:
                        self.infostr = [str1, str(timediff) + ' ms before target.']
        else:
            if self.classifierTime==0:
                self.infostr = 'No button press!'
                self.infocolor = self.fb_color_bad
                self.validTrials -= 1
                self.send_parallel(self.TE_INVALID_NOKP)
                self.classifier_log[self.completedTrials].append(0.4)
            else:
                self.infostr = ''
                self.send_parallel(self.TE_VALID_NOKP)
                self.classifier_log[self.completedTrials].append(0.9)

        # save time difference between classifier keypress prediction and actual keypress
        if self.buttonPressed and self.classifierTime!=0: # both red clock and button press during trial
            self.classifier_log[self.completedTrials].append(self.buttonPressTime-self.classifierTime)
        elif not self.buttonPressed:
            self.classifier_log[self.completedTrials].append(0.2)
        else: # FN (button press and no red clock)
            self.classifier_log[self.completedTrials].append(0.3)

    def write_classifier_log(self):
        print 'Writing classifier log.'
        subdir = '/python_classifier_logs/'
        if not os.access(self.TODAY_DIR + subdir, os.F_OK):
            os.mkdir(self.TODAY_DIR + subdir)
        if self.showClassifier == 'feedback':
            file = self.TODAY_DIR + subdir + 'fb'
        else:
            file = self.TODAY_DIR + subdir + 'train'
        file_number = 1
        while os.access(file+str(file_number) + '.csv', os.F_OK):
            file_number += 1
        f = open(file + str(file_number) + '.csv', 'w')
        for trial in range(len(self.classifier_log)):
            l =len(self.classifier_log[trial])
            if l!=6:
                print 'write_classifier_log: list length in trial %i not as expected (actual length: %i, expected length: %i).', (trial, l, 6)
            for target in range(l):
                if target == l-1:
                    f.write(str(self.classifier_log[trial][target]))
                else:
                    f.write(str(self.classifier_log[trial][target]) + ',')
            f.write('\n')
        f.close()

    def write_clsev_log(self):
        print 'Writing classifier evolution log.'
        subdir = '/python_clsev_logs/'
        if not os.access(self.TODAY_DIR + subdir, os.F_OK):
            os.mkdir(self.TODAY_DIR + subdir)
        if self.showClassifier == 'feedback':
            file = self.TODAY_DIR + subdir + 'fb'
        else:
            file = self.TODAY_DIR + subdir + 'train'
        file_number = 1
        while os.access(file+str(file_number) + '.csv', os.F_OK):
            file_number += 1
        f = open(file + str(file_number) + '.csv', 'w')
        for trial in range(len(self.cls_evolution_log)):
            l =len(self.cls_evolution_log[trial])
            for target in range(l):
                if target == l-1:
                    f.write(str(self.cls_evolution_log[trial][target]))
                else:
                    f.write(str(self.cls_evolution_log[trial][target]) + ',')
            f.write('\n')
        f.close()


    def set_classification_time(self):
        nu = random.random()
        self.cls_time = nu * self.cls_ival[0] + (1-nu) * self.cls_ival[1]


    def pause_tick(self):
        """
        One tick of the pause loop.
        """
        if self.showsPause:
            return
        self.send_parallel(self.GAME_STATUS_PAUSE)
        self.do_print("Pause", self.fontColor, self.size/4)
        self.showsPause = True


    def short_pause_tick(self):
        """
        One tick of the short pause loop.
        """
        if self.shortPauseElapsed == 0:
            self.send_parallel(self.SHORTPAUSE_START)

        self.shortPauseElapsed += self.elapsed
        if self.shortPauseElapsed >= self.pauseDuration:
            self.showsShortPause = False
            self.shortPause = False
            self.shortPauseElapsed = 0
            self.countdown = True
            self.infostr = ''
            return
        if self.showsShortPause:
            return
        self.draw_all(False)
        self.do_print("Short Break", self.fontColor)
        self.showsShortPause = True


    def countdown_tick(self):
        """
        One tick of the countdown loop.
        """
        if self.countdownElapsed==0:
            self.send_parallel(self.COUNTDOWN_START)

        self.countdownElapsed += self.elapsed
        if self.countdownElapsed >= self.countdownFrom * 1000:
            self.firstTickOfTrial = True
            self.start_animation = True
            self.countdown = False
            self.countdownElapsed = 0
            return
        t = str((self.countdownFrom * 1000 - self.countdownElapsed) / 1000)
        self.draw_all(False)
        self.do_print(t, self.countdownColor, self.size/3, True)


    def gameover_tick(self):
        """
        One tick of the game over loop.
        """
        if self.showsGameover:
            return
        self.do_print("Finished!", self.fontColor, self.size/15)
        self.showsGameover = True
        if self.writeClassifierLog:
            self.write_classifier_log()
        self.write_clsev_log()
        self.send_parallel(self.GAME_OVER)


    def do_print(self, text, color=None, size=None, superimpose=False, pos=None):
        """
        Print the given text in the given color and size on the screen.
        If text is a list, multiple items will be used, one for each list entry.
        """
        if not color:
            color = self.fontColor
        if not size:
            size = self.size/10
        if not pos:
            pos = self.screencenter

        size = size*0.6
        font = pygame.font.Font(None, int(size))
        if not superimpose:
            self.draw_all()

        if type(text) is list:
            height = pygame.font.Font.get_linesize(font)
            top = -(2*len(text)-1)*height/2
            for t in range(len(text)):
                surface = font.render(text[t], 1, color)

                self.screen.blit(surface, surface.get_rect(midtop=(pos[0], pos[1]+top+t*1.5*height)))
        else:
            surface = font.render(text, 1, color)
            self.screen.blit(surface, surface.get_rect(center=pos))
        pygame.display.update()


    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size.
        """
        path = os.path.dirname( globals()["__file__"] )
        self.screen = pygame.display.get_surface()
        (self.screenWidth, self.screenHeight) = (self.screen.get_width(), self.screen.get_height())
        self.size = min(self.screen.get_height(), self.screen.get_width())
        self.screencenter = self.screen.get_rect().center

        img = pygame.image.load(os.path.join(path, 'background.jpg')).convert()
        self.background = pygame.transform.scale(img, (self.screenWidth, self.screenHeight))

        #self.background = pygame.Surface((self.screenWidth, self.screenHeight))
        self.backgroundRect = self.background.get_rect(center=self.screencenter)
        self.background.fill(self.backgroundColor)

        # init clock
        self.diameter = int(self.size/5)*2
        #img = pygame.image.load(os.path.join(path, 'clockface.bmp')).convert_alpha()
        #self.clock = pygame.Surface((self.diameter,self.diameter))
        #self.clock = pygame.transform.scale(img, (self.diameter,self.diameter))

        self.clock = pygame.Surface((self.diameter,self.diameter))
        self.clock.set_colorkey((0,0,0))
        pygame.draw.circle(self.clock, self.clockColor, (self.diameter/2,self.diameter/2), self.diameter/2)
        self.clockRect = self.clock.get_rect(center=self.screencenter, size=(self.diameter, self.diameter))

        # fixation points
        fp_dia = int(self.diameter/40)*2
        fp_color = (1,1,1)
        self.fixpoint_pos = [self.clockRect.midtop,self.clockRect.midleft,self.clockRect.midbottom,self.clockRect.midright]
        self.fixpoints = []
        self.fpRect = []
        for fp in range(len(self.fixpoint_pos)):
            self.fixpoints.append(pygame.Surface((fp_dia,fp_dia)))
            self.fixpoints[fp].set_colorkey((0,0,0))
            pygame.draw.circle(self.fixpoints[fp], fp_color, (fp_dia/2,fp_dia/2), fp_dia/2)
            self.fpRect.append(self.fixpoints[fp].get_rect(center=self.fixpoint_pos[fp], size=(fp_dia, fp_dia)))

        # init clock dial
        dialColor = (0,0,0)
        dialThickness = 2
        self.dialVertical = pygame.Surface((dialThickness, self.diameter))
        self.dialVertical.fill(dialColor)
        self.dialVerticalRect = self.dialVertical.get_rect(center=self.screencenter)
        self.dialHorizontal = pygame.Surface((self.diameter, dialThickness))
        self.dialHorizontal.fill(dialColor)
        self.dialHorizontalRect = self.dialHorizontal.get_rect(center=self.screencenter)

        # init clock hand
        img = pygame.image.load(os.path.join(path, 'clockhand_straight.bmp')).convert_alpha()
        #self.clockhand = pygame.Surface((self.diameter, self.diameter))
        self.clockhand = pygame.transform.scale(img, (self.diameter, self.diameter))
        self.clockhand =  pygame.Surface((self.diameter, self.diameter))
        self.clockhand.fill(self.backgroundColor)
        self.clockhand.set_colorkey(self.backgroundColor)
        pygame.draw.line(self.clockhand, (200,200,200), (self.diameter/2,0), (self.diameter/2, self.diameter/2), dialThickness*2)
        self.clockhandRect = self.clockhand.get_rect(center=self.screencenter)
        #self.hideRect = pygame.Rect(self.clockhandRect.midleft,(self.clockhandRect.width, self.clockhandRect.height/2))
        self.drawRect = pygame.Rect(self.clockhandRect.topleft,(self.clockhandRect.width,self.clockhandRect.height/2))

        #self.hideRect = pygame.Rect(0,0,self.clockhandRect.width, self.clockhandRect.height/2)
        #self.hideRect.midtop = self.screencenter

        # init start animation arc
        self.arcAngle = 451
        self.arcWidth = 5
        self.arcColor = (200,200,250)
        self.diarc = self.diameter+self.arcWidth*2
        self.arc = pygame.Surface((self.diarc, self.diarc))
        self.arc.set_colorkey((0,0,0))
        p = self.screen.get_rect().topleft
        self.arcRect = self.arc.get_rect(center=(p[0]+self.diarc/2,p[1]+self.diarc/2))
        pygame.draw.arc(self.arc, self.arcColor, self.arcRect, math.radians(90), math.radians(self.arcAngle), self.arcWidth)
        self.arcRect.center = self.screencenter
        self.draw_all()

    def init_pygame(self):
        """
        Set up pygame and the screen and the clock.
        """
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.screenPos[0], self.screenPos[1])
        pygame.init()
        pygame.display.set_caption('LibetClock')
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.screenPos[2], self.screenPos[3]), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screenPos[2], self.screenPos[3]), pygame.NOFRAME)
        self.w = self.screen.get_width()
        self.h = self.screen.get_height()
        pygame.mouse.set_visible(False)
        self.cpu_clock = pygame.time.Clock()


    def draw_all_rotating(self, draw=True):
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.clock, self.clockRect)
        self.screen.blit(self.dialVertical, self.dialVerticalRect)
        self.screen.blit(self.dialHorizontal, self.dialHorizontalRect)
        for fp in range(len(self.fixpoint_pos)):
            self.screen.blit(self.fixpoints[fp], self.fpRect[fp])
        self.screen.blit(self.clockhand_rotated, self.clockhandRect_rotated)
        if draw:
            pygame.display.flip()

    def draw_all(self, draw=True):
        self.screen.blit(self.background, self.backgroundRect)
        rect = pygame.Rect(self.arcRect.topleft, (self.arcRect.width*4, self.arcRect.height*4))
        self.screen.blit(self.arc, self.arcRect)
        self.screen.blit(self.clock, self.clockRect)
        self.screen.blit(self.dialVertical, self.dialVerticalRect)
        self.screen.blit(self.dialHorizontal, self.dialHorizontalRect)
        for fp in range(len(self.fixpoint_pos)):
            self.screen.blit(self.fixpoints[fp], self.fpRect[fp])
        self.screen.blit(self.clockhand, self.clockhandRect) #, self.drawRect)
        if draw:
            pygame.display.flip()

    def draw_init(self, draw=False):
        """
        Draws the initial screen.
        """
        self.screen.blit(self.background, self.backgroundRect)
        if draw:
            pygame.display.update()


if __name__ == '__main__':
    ca = LibetClock(None)
    ca.on_init()
    ca.on_play()


