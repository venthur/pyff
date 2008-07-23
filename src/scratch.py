
import os
import Feedback
import traceback

def test_feedback(root, file):
    # remove trailing .py if present
    if file.lower().endswith(".py"):
        file2 = file[:-3]
    root = root.replace("/", ".")
    while root.startswith("."):
        root = root[1:]
    if not root.endswith(".") and not file2.startswith("."):
        module = root + "." + file2
    else:
        module = root + file2
    valid, name = False, file2
    mod = None
    try:
        mod = __import__(module, fromlist=[None])
        #print "1/3: loaded module (%s)." % str(module)
        fb = getattr(mod, file2)(None)
        #print "2/3: loaded feedback (%s)." % str(file2)
        if isinstance(fb, Feedback.Feedback):
            #print "3/3: feedback is valid Feedback()"
            valid = True
    except:
        print "Ooops! Something went wrong loading the feedback"
        print traceback.format_exc()
    finally:
        del mod
        return valid, name
    
    

def get_feedbacks():
    """Returns the valid feedbacks in this directory."""
    feedbacks = {}
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.lower().endswith(".py"):
                # ok we found a candidate, check if it's a valid feedback
                isFeedback, name = test_feedback(root, file)
                if isFeedback:
                    feedbacks[name] = root+file
    for i in feedbacks.items():
        print i

    

if __name__ == "__main__":
    fb = get_feedbacks()
    print dir()

