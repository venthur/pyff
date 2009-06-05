
from FeedbackBase.Feedback import Feedback
from lib.iothread import IOThread
from lib.PluginController import PluginController

class FeedbackProcess(Feedback):
    """Feedback that runs in it's own process.
    """
    
    def __init__(self, pipeEnd):
        self._pipeEnd = pipeEnd
        self._ioThread = IOThread(pipeEnd)
        self._ioThread.start()
        
    
    def stop(self):
        self._ioThread.stop()
        self._ioThread.join()



def start_feedback_process(feedbackClass, pipeEnd):
    try:
        feedbackClass = self.pluginController.load_plugin(name)
    except ImportError:
        # TODO: Hmm anything else we can do?
        raise
    feedbackClass.pipe_loop = pipe_loop
    feedback = feedbackClass()

    feedback.conn = self.fbPipe
    feedback.playEvent = Event()
    feedback.on_init()
    pipeThread = Thread(target=feedback.pipe_loop)
    pipeThread.start()
    while True:
        feedback.playEvent.wait()
        try:
            feedback.on_play()
        except:
            print "Feedbacks on_play threw an exception:"
            print traceback.format_exc()
        feedback.playEvent.clear()
        print "Feedback's on_play terminated."    
