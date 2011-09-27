# Instructions.py
# Author: Lovisa Irpa Helgadottir


import subprocess as sp
import time, sys, os

from FeedbackBase.MainloopFeedback import MainloopFeedback


class Instructions(MainloopFeedback):
    '''Instruction Feedback.

    This class opens up a html file or and url in browser and closes it after
    predetermined time or after a key press.

    Default browser is firefox.

    ### Windows ###
    Browsers:
    - Mozilla Firefox
    - Google Chrome
    - Internet Explorer
    - Opera


    ### LINUX ###
    Any browser can be used.
    The self.browser variable should be the command used to start the browser
    from a command line.  e.g. to start chrome:
    self.browser = 'chromium-browser'
    '''

    def init(self):
        '''Initialize parameters.'''
        self.urlname='' # Html file or url
        self.browser='firefox' #default firefox
        self.duration=10 #s
        # The browser can either be closed after a certain amount of time or
        # with a keypress
        close_opts=['time','keypress']
        self.close=close_opts[1] #default 'key'


    def tick(self):
        if sys.platform =='win32':
            self.win_tick()
        else:
            self.linux_tick()
        self._running = False


    def win_tick(self):
       dir_opts=['Mozilla Firefox/','Google/Chrome/Application/','Internet Explorer/','Opera/']
       if self.browser == 'firefox':
           directory=dir_opts[0]
       else:
           if self.browser=='chrome':
               directory=dir_opts[1]
           else:
               if self.browser=='ie':
                   directory=dir_opts[2]
               else:
                   if self.browser=='opera':
                       directory= dir_opts[3]
                   else:
                       print("Browser Not Defined \n ... Quitting ...")
                       sys.exit()
       if (os.path.isdir("C:/Program Files/"+directory)):
           instructions=sp.Popen([r"C:\Program Files/"+directory+self.browser+".exe",self.urlname])
       else:
           if (os.path.isdir("C:/Program Files (x86)/"+directory)):
               instructions=sp.Popen([r"C:/Program Files (x86)/"+directory+self.browser+".exe",self.urlname])
           else:
               print('Browser Directory Not Found \n ... Quitting ...')
               sys.exit()
       if (self.close=='time'):
           time.sleep(self.duration)
           instructions.kill()
       else:
           input()
           instructions.kill()


    def linux_tick(self):
        instructions = sp.Popen([self.browser,self.urlname])
        if (self.close=='time'):
            time.sleep(self.duration)
            instructions.kill()
        else:
            raw_input()
            instructions.kill()


if __name__ == '__main__':
    inst = Instructions()
    inst.on_init()
    inst.urlname='www.tu-berlin.de'
    inst.browser='chrome'
    inst.on_play()

