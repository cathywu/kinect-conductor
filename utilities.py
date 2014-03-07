#!/usr/bin/env python
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
from colormap import rgb as map2rgb
import cv  
import numpy as np
import time, os, pickle
from filter import blur_image

MIN_DEPTH = 350
MAX_DEPTH = 650 #2**10 - 1
INVALID_DEPTH = 2047
DATA_DIR = "data/"
  
def set_params(min_depth=MIN_DEPTH, max_depth=MAX_DEPTH):
    global MIN_DEPTH, MAX_DEPTH
    MIN_DEPTH = min_depth
    MAX_DEPTH = max_depth

def stack_depth(stack=1,verbose=True):
    depth = None
    for i in range(stack):
        (temp,_) = get_depth()
        if depth is None:
            depth = temp
            if verbose:
                print "Init invalids: %d" % depth[depth >= INVALID_DEPTH].shape[0]
        else:
            mask1 = (depth >= INVALID_DEPTH)
            mask2 = ((mask1*temp > 0) * (mask1*temp < INVALID_DEPTH))
            depth = depth.copy() + mask2*temp - mask2*INVALID_DEPTH
    if verbose:
        print "Final invalids: %d" % depth[depth >= INVALID_DEPTH].shape[0]
    return depth

# streams video and optionally saves frames (raw info)
def timed_snapshot(sec=10,name="tmp_",timestamp=True,save=True, \
                    interval=0,ret=False,stack=1):
    start_time = time.time()
    # update depth and rgb each time through loop

    depth=None
    (rgb,_) = get_video()
    # Get a fresh frame
    depth = stack_depth(stack=stack)
    c = 1
    while (time.time()-start_time) < sec:
        # Get a fresh frame
        depth = stack_depth(stack=stack)
        view_frame(normalize_depth(depth),rgb)
        #depth[depth>=INVALID_DEPTH]=0
        print "%d - %d (avg: %s)" % (depth.min(), depth.max(), depth.mean())
        #print depth[235+30:245+30,315:325]

        # saves frame per specified interval
        if save and interval > 0 and (time.time()-start_time) > c*interval:
            c+=1
            fname = "%s%s%s.pkl" % (DATA_DIR, name, int(time.time())) \
                        if timestamp else "%s%s.pkl" % (DATA_DIR, name)
            save_frame((depth, rgb), fname)
            
    # saves frame at the very end
    if save and interval == 0:
        fname = "%s%s%s.pkl" % (DATA_DIR, name, int(time.time())) \
                    if timestamp else "%s%s.pkl" % (DATA_DIR, name)
        save_frame((depth, rgb), fname)

    # optionally returns frame
    if ret: return (depth,rgb)

def get_current(wait=False,stack=1):
    if wait:
        raw_input("Press enter to continue...")
    return timed_snapshot(sec=0,save=False,ret=True,stack=stack)

def view_frame(depth,rgb,scale=2):
    # Build a two panel color image
    d3 = np.dstack(map2rgb(depth,MIN_DEPTH,MAX_DEPTH)).astype(np.uint8)
    da = np.hstack((d3,rgb))
    
    # Simple Downsample
    cv.ShowImage('both',down_sample(da,scale).copy())
    cv.WaitKey(100)

def view_depth(depth,scale=2):
    # Build a two panel color image
    da = np.dstack(map2rgb(depth,MIN_DEPTH,MAX_DEPTH)).astype(np.uint8)
    
    # Simple Downsample
    cv.ShowImage('both',cv.fromarray(down_sample(da,scale).copy()))
    cv.WaitKey(100)

def view_depths(depth1,depth2,rgb,scale=2):
    # Build a two panel color image
    d3 = np.dstack(map2rgb(depth1,MIN_DEPTH,MAX_DEPTH)).astype(np.uint8)
    d32 = np.dstack(map2rgb(depth2,MIN_DEPTH,MAX_DEPTH)).astype(np.uint8)
    da = np.hstack((d3,d32,rgb))
    
    # Simple Downsample
    cv.ShowImage('both',down_sample(da,scale))
    cv.WaitKey(100)

def normalize_depth(depth):
    # TODO better handling of out of range values
    return np.clip(depth,MIN_DEPTH,MAX_DEPTH)

# compute average of depths, disregarding invalid values
def avg_depth(depth):
    invalid = depth[depth >= INVALID_DEPTH]
    total = depth.sum() - invalid.shape[0] * INVALID_DEPTH
    average = total / (depth.shape[0] * depth.shape[1] - invalid.shape[0])
    return average

# downsample frame with option to average values
def down_sample(a,n=2,avg=False):
    if n==1:
        return a
    elif len(a.shape) == 3:
        return np.array(a[::n,::n,::-1])
    elif avg:
        (NbigX,NbigY) = a.shape
        NsmallX = int(NbigX/n)
        NsmallY = int(NbigY/n)

        small = a.reshape([NsmallX,n,NsmallY,n]).mean(3).mean(1)
        return small
    else:
        return np.array(a[::n,::n])

# saves frame as pickle dump
def save_frame(frame, fname):
    f = open(fname, 'w')
    pickle.dump(frame,f)
    f.close()

# loads and displays a saved frame
def load_frame(fname,display=True):
    data = pickle.load(open(fname,'r'))
    if data.__class__ == type(()): # frame = (depth,rgb)
        (depth, rgb) = data
        if display:
            view_frame(normalize_depth(depth), rgb)
        return (depth, rgb)
    else:
        depth = data
        if display:
            view_depth(normalize_depth(depth),scale=1)
        return depth
 
def load_depth(fname,display=True):
    depth = pickle.load(open(fname,'r'))
    if display:
        view_depth(normalize_depth(depth),scale=1)
    return depth

# list files in data directory with option to filter for certain filenames
def ls_data_dir(prefix=None,suffix=None):
    fnames = os.listdir("%s/%s" % (os.getcwd(),DATA_DIR))
    if prefix and suffix:
        return [fname for fname in fnames if fname.find(prefix) > -1 and fname.find(suffix) > -1]    
    elif prefix:
        return [fname for fname in fnames if fname.find(prefix) > -1]    
    elif suffix:
        return [fname for fname in fnames if fname.find(suffix) > -1]    
    else: 
        return fnames

def pretty_depth(depth):
    """Converts depth into a 'nicer' format for display

    This is abstracted to allow for experimentation with normalization

    Args:
        depth: A numpy array with 2 bytes per pixel

    Returns:
        A numpy array that has been processed whos datatype is unspecified
    """
    np.clip(depth, 0, MAX_DEPTH, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)
    return depth


def pretty_depth_cv(depth):
    """Converts depth into a 'nicer' format for display

    This is abstracted to allow for experimentation with normalization

    Args:
        depth: A numpy array with 2 bytes per pixel

    Returns:
        An opencv image who's datatype is unspecified
    """
    import cv
    depth = pretty_depth(depth)
    image = cv.CreateImageHeader((depth.shape[1], depth.shape[0]),
                                 cv.IPL_DEPTH_8U,
                                 1)
    cv.SetData(image, depth.tostring(),
               depth.dtype.itemsize * depth.shape[1])
    return image


def video_cv(video):
    """Converts video into a BGR format for opencv

    This is abstracted out to allow for experimentation

    Args:
        video: A numpy array with 1 byte per pixel, 3 channels RGB

    Returns:
        An opencv image who's datatype is 1 byte, 3 channel BGR
    """
    import cv
    video = video[:, :, ::-1]  # RGB -> BGR
    image = cv.CreateImageHeader((video.shape[1], video.shape[0]),
                                 cv.IPL_DEPTH_8U,
                                 3)
    cv.SetData(image, video.tostring(),
               video.dtype.itemsize * 3 * video.shape[1])
    return image
