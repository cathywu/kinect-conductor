#!/usr/bin/env python

#TODO: use soundtouch directly, write python/c interface/wrapper
#TODO: remake this demo for mixxx
#TODO: soundtouch uses states -- try giving it more information

import scikits.audiolab as al
import pygame.mixer as mixer
import pygame.sndarray as snd
import time # everything is in seconds
import numpy, random
import shlex, subprocess as sp
import os
import pickle
import re

soundstretch = './soundstretch'
mdir = os.path.expanduser('~/Dropbox/kinect-conductor/Music')
ddir = os.path.expanduser('~/Dropbox/kinect-conductor/mdata')
fname = 'clip2.wav'
snippet_duration = 1.0 # in seconds
multiplier = 1
f = 48000

def load_song(fname):
    ff = open(ddir + fname + '.pkl','w')

    mixer.init(f*multiplier)
    s_full = mixer.Sound(mdir + fname)
    a_full = snd.array(s_full)

    pickle.dump(a_full,ff)
    ff.close()

def stretch_audio(r,fname=fname):
    curr_sample = 0
    
    mixer.init(f*multiplier)
    
    (a_full) = pickle.load(open('%s/%s.pkl' % (ddir, fname),'r'))
    
    #f = mixer.get_init()[0]
    #mixer.quit()
    #mixer.init(f)
    
    c = mixer.Channel(0)
    c.set_volume(0.8)
    
    base_bpm = get_base_bpm(fname)
    if base_bpm > 80:
        base_bpm = base_bpm / 2
    print 'base_bpm: %f' % base_bpm

    # plays first few seconds of audio clip
    starttime = time.time()
    secondsin = 0
    cmd = '%s temp.wav output.wav -tempo=%d'
    #cmd = 'soundstretch temp.wav output.wav -bpm=%d'
    #for i in range(30):
    bpm = 0
    while curr_sample < a_full.shape[0] - f*multiplier:
        # get next chunk of wav
        time_btwn_beats = int(r.value)
        bpm = bpm/3 + 60000/time_btwn_beats*2/3
        bpm = max(base_bpm*3/4,bpm)
        rate = bpm/base_bpm

        (a, curr_sample) = getSamples(a_full, curr_sample, dur=rate)
        
        # write chunk to temp.wav
        out = al.Sndfile('temp.wav','w',al.Format(),2,f)
        out.write_frames(a)
        out.close()
    
        # fork a process to change tempo of chunk
        pargs = shlex.split(cmd % (soundstretch, 100*(rate-1)))
        #pargs = shlex.split(cmd % (60000/rate))
        p = sp.Popen(pargs, stdout=open(os.devnull,'w'), stderr=open(os.devnull,'w'))
        p.wait()
    
        # wait to queue it
        #print "Sec: %d, Rate: %f" % (secondsin, rate)#, n.shape
        print "Sec: %d, TBB: %d, Rate: %f, Tempo: %d" % (secondsin, time_btwn_beats, rate, (100*(rate-1)))#, n.shape
        while time.time()-starttime < secondsin-0.2:
            #print 'z'
            time.sleep(0.05)
        #enqueueSamples(c, a[n,:])
        
        # queue it
        # TODO: this is super choppy :(
        c.queue(mixer.Sound('output.wav'))
        secondsin+=1

def getSamples(array_full, start, f=f, dur=snippet_duration):
    return (array_full[start:start+f*dur,:],start+f*dur)

def enqueueSamples(channel, an_array):
    channel.queue(snd.make_sound(an_array))

def get_base_bpm(fname):
    cmd = '%s "%s/%s" output.wav -bmp' % (soundstretch, mdir, fname)
    print cmd
    pargs = shlex.split(cmd)
    # Ubuntu sends output to stdout, OSX sends output to stderr
    p = sp.Popen(pargs, stdout=sp.PIPE, stderr=sp.PIPE)
    (out,err) = p.communicate()
    if out == '': # OSX case
        out = err
    
    m = re.search('Detected BPM rate (.*)\n', out)
    return float(m.group(1))
