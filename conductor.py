#!/usr/bin/env python
import freenect
import numpy as np
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
from constants import *
import time
import argparse
from utilities import view_frame, set_params, avg_depth, normalize_depth,\
                        INVALID_DEPTH, view_depth
import pickle
from multiprocessing import Process, Value, Lock
from audiotest3 import stretch_audio, load_song

# constants
RIGHT = 0
LEFT = 1

# parameters
tilt = 0;
led = LED_OFF;
MIN_DEPTH = 300
MAX_DEPTH = 1200
BACK_DEPTH_FNAME = 'back_depth.pkl'
VERBOSE = 0
REDUCTION = 90

# use for test multiprocessing package
def test_print(args):
    i = 0
    while True:
        print r.value
        time.sleep(1)
        i+=1

def body(dev, ctx):
    freenect.set_led(dev, led)
    freenect.set_tilt_degs(dev, tilt)
    #(depth,_), (rgb,_) = get_depth(), get_video()
    #view_frame(normalize_depth(depth),rgb)

def filter_arms(depth):
    # filter out background
    depth[depth>=BACK_DEPTH] = INVALID_DEPTH

    # filter out body
    body_depth = avg_depth(depth)
    arms_depth = depth.copy()
    arms_depth[depth>=body_depth-REDUCTION] = INVALID_DEPTH

    # TODO: consider filtering out forearm
    return arms_depth

if __name__ == '__main__':
    # cmd line arguments
    parser = argparse.ArgumentParser(description='OpenKinect Symphony Conductor' 
                 + ' Demo')
    parser.add_argument('-i','--init',action='store_true')
    parser.add_argument('-r','--record',action='store_true') ##???
    ## calibrate background
    parser.add_argument('-c','--calibrate',action='store_true')
    ## specify file in Music directory
    parser.add_argument('-f','--filename')
    ## child mode
    parser.add_argument('-k','--kid',action='store_true')
    ## load a new song as pkl dump
    parser.add_argument('-l','--load',action='store_true')
    parser.add_argument('-s','--list',action='store_true')
    args = parser.parse_args()
    print args

    if args.load:
        load_song(args.filename)    
        import sys
        sys.exit()

    if args.list:
        import os
        songs = os.listdir('mdata')
        for i in range(len(songs)):
            print "%s: %s" % (i,songs[i])
        select = raw_input("Select a song by number:")
        fname = songs[int(select)].split('.pkl')[0]
    else:
        fname = args.filename

    if args.kid:
        REDUCTION = 100
        global REDUCTION

    #TODO fix this comment: make rate accessible to audio thread
    if args.init:
        freenect.runloop(body=body)

    # calculates average depth and stores it
    # use it for calibrating depth of background
    if args.calibrate:
        (depth,_) = get_depth()
        background_depth = avg_depth(depth)
        print 'calibated depth of background: %d' % background_depth
        f = open(BACK_DEPTH_FNAME, 'w')
        pickle.dump(background_depth,f)
        f.close()
    # load the approximate depth of the background
    BACK_DEPTH = pickle.load(open(BACK_DEPTH_FNAME,'r'))
        
    # share rate with other audio process
    r = Value('f', 1)
    # spawn audio process
    p = Process(target=stretch_audio, args=(r,fname,))
    p.start()

    thresh = 2 # measurements in other direction before we change directions

    # for image output
    set_params(MIN_DEPTH, MAX_DEPTH) 
    c = 0

    (depth,_) = get_depth()

    #TODO make class for state
    y = depth.shape[1]/2
    y_minus1 = depth.shape[1]/2

    r_votes = 0
    l_votes = 0

    r_saved_y = [depth.shape[1]/2, depth.shape[1]/2, depth.shape[1]/2]
    l_saved_y = [depth.shape[1]/2, depth.shape[1]/2, depth.shape[1]/2]

    now = time.time()
    r_saved_time = [now, now, now]
    l_saved_time = [now, now, now]

    r_ind = 0
    l_ind = 0

    r_end = 0
    l_end = depth.shape[1]

    r_time = now
    l_time = now + 1000

    direction = RIGHT # 0 - right, 1 - left
    y_left = depth.shape[1]/2
    y_right = depth.shape[1]/2

    while True:
        # Get a fresh frame
        (depth,_) = get_depth()
        c+=1
        arms_depth = filter_arms(depth)
        # background filtered out, body filtered out, rgb views
        if c % 20 == 0:
            view_depth(normalize_depth(arms_depth))

        # estimate location of hand (only supports 1 hand for now)
        (hand_x, hand_y) = np.where(arms_depth < INVALID_DEPTH)
        hand_x = hand_x.sum() / hand_x.shape[0] # x is vertical
        hand_y = hand_y.sum() / hand_y.shape[0] # y is horizontal
        #print "estimated hand position: (%d,%d)" % (hand_x,hand_y)

        # update history
        y_minus1 = y
        y = hand_y
 
        # guess which direction we're going in
        if y-y_minus1 < 0: 
            r_votes+=1
            r_saved_y[r_ind] = float(y)
            r_saved_time[r_ind] = time.time()*1000
            r_ind=(r_ind+1) % thresh
            if VERBOSE:
                print "RIGHT @ (%d,%d)" % (hand_x,hand_y)
        else: 
            l_votes+=1
            l_saved_y[l_ind] = float(y)
            l_saved_time[l_ind] = time.time()*1000
            l_ind=(l_ind+1) % thresh
            if VERBOSE:
                print "LEFT @ (%d,%d)" % (hand_x,hand_y)

        # guess if there is a transition in direction
        if r_votes >= thresh and l_votes >= thresh:
            if r_votes > l_votes:
                r_end = ((min(r_saved_y) + min(l_saved_y))/2)
                r_time = (sum(r_saved_time) + sum(l_saved_time))/(2*thresh)
                print "RIGHT --> LEFT @ %d \tdy=%d \t(dt=%d)" % (r_end, abs(l_end-r_end), abs(r_time-l_time))
                r_votes = 0
                r.value = abs(r_time-l_time)
            else:
                l_end = ((max(r_saved_y) + max(l_saved_y))/2)
                l_time = (sum(r_saved_time) + sum(l_saved_time))/(2*thresh)
                print "LEFT --> RIGHT @ %d \tdy=%d \t(dt=%d)" % (l_end, abs(l_end-r_end), abs(r_time-l_time))
                l_votes = 0
                r.value = abs(r_time-l_time)

