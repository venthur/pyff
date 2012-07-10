# MainloopFeedback.py -
# Copyright (C) 2008-2009  Bastian Venthur
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


from Feedback import Feedback


class MainloopFeedback(Feedback):
    """Mainloop Feedback Base Class.

    This feedback derives from the Feedback Base Class and implements a main
    loop. More specifically it implements the following methods from it's base:

        * :func:`on_init`
        * :func:`on_play`
        * :func:`on_pause`
        * :func:`on_stop`
        * :func:`on_quit`

    which means that you should not need to re-implement those methods. If you
    choose to do so anyways, make sure to call MainloopFeedback's version
    first::

        def on_play():
            MainloopFeedback.on_play(self)
            # your code goes here

    MainloopFeedback provides the following new methods:

        * :func:`init`
        * :func:`pre_mainloop`
        * :func:`post_mainloop`
        * :func:`tick`
        * :func:`pause_tick`
        * :func:`play_tick`

    the class takes care of the typical steps needed to run a feedback with a
    mainloop, starting, pausing, stopping, quiting, etc.

    While running it's internal mainloop it calls :func:`tick` repeatedly.
    Additionally it calls either :func:`play_tick` or :func:`pause_tick`
    repeatedly afterwards, depending if the Feedback is paused or not.

    """

    def on_init(self):
        self._running = False
        self._paused = False
        self._inMainloop = False
        self.init()

    def on_play(self):
        self.pre_mainloop()
        self._mainloop()
        self.post_mainloop()

    def on_pause(self):
        self._paused = not self._paused

    def on_stop(self):
        self._running = False

    def on_quit(self):
        self._running = False
        while self._inMainloop:
            pass

    def _mainloop(self):
        """
        Calls tick repeatedly.

        Additionally it calls either :func:`pause_tick` or :func:`play_tick`,
        depending if the Feedback is paused or not.
        """
        self._running = True
        self._inMainloop = True
        while self._running:
            self.tick()
            if self._paused:
                self.pause_tick()
            else:
                self.play_tick()
        self._inMainloop = False

    def init(self):
        """Called at the beginning of the Feedback's lifecycle.

        More specifically: in :func:`on_init`.
        """
        pass

    def pre_mainloop(self):
        """Called before entering the mainloop, e.g. after :func:`on_play`."""
        pass

    def post_mainloop(self):
        """Called after leaving the mainloop, e.g. after stop or quit."""
        pass

    def tick(self):
        """
        Called repeatedly in the mainloop no matter if the Feedback is paused
        or not.
        """
        pass

    def pause_tick(self):
        """
        Called repeatedly in the mainloop if the Feedback is paused.
        """
        pass

    def play_tick(self):
        """
        Called repeatedly in the mainloop if the Feedback is not paused.
        """
        pass

