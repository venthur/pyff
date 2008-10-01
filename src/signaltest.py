import bcinetwork

import time
import socket

CONTROL_SIGNAL = """
<bci-signal>
<control-signal version="1.0">
    <tuple name="tuple">
        <i name="id" value="%(id)i" />
        <f name="time" value="%(time)f" />
    </tuple>
</control-signal>
</bci-signal>
"""

def load_feedback():
    bcinet = bcinetwork.BciNetwork(bcinetwork.LOCALHOST, bcinetwork.FC_PORT)
    bcinet.send_init("BenchmarkFeedback")

def get_data():
    bcinet = bcinetwork.BciNetwork(bcinetwork.LOCALHOST, bcinetwork.FC_PORT, bcinetwork.GUI_PORT)
    return bcinet.get_variables()["data"]

def foo(packets, delay, id=0):
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (bcinetwork.LOCALHOST, bcinetwork.FC_PORT)
    
    data = []
    for i in range(packets):
        time.sleep(delay)
        id += 1
        t = time.time()
        s = CONTROL_SIGNAL % {"id" : id, "time" : t}
        sock.sendto(s, address)
        data.append((id, t))

def calculate_min_max_avg(data):
    t = []
    for id, t1, t2 in data:
        t.append(t2 - t1)
    return min(t), max(t), sum(t) / len(t)
    
    

if __name__ == "__main__":
    # Make some selftest
    # Initialize the Feedback
    # Send the Data
    # Get results from the Feedback
    # Calculate

    t = []
    t1, s, t2 = None, None, None
    for i in xrange(1):#000000):
        t1 = time.time()
        s = CONTROL_SIGNAL % {"id" : 1, "time" : .1}
        t2 = time.time()
        t.append( (t2 - t1) )
    
    #print "Min, Max, Avg: %f, %f, %f" % (min(t) * 1000, max(t) * 1000, sum(t) / len(t) * 1000)

    load_feedback()
    time.sleep(1)
    foo(100, 0.1)
    foo(100, 0.01, 100)
    foo(100, 0.001, 200)
    foo(100, 0.0001, 300)
    foo(100, 0.00001, 400)
    foo(100, 0.000001, 500)
    foo(100, 0.0000001, 600)
    foo(100, 0, 700)
    time.sleep(1)
    d = get_data()
    min, max, avg = calculate_min_max_avg(d)
    min *= 1000. 
    max *= 1000.
    avg *= 1000.
    print "#packet delay"
    for i in d: print i[0], (i[2]-i[1])*1000
    #print min, max, avg
