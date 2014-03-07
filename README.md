kinect-conductor
================

Setup
-----

Install OpenKinect, OpenCV

    brew install libfreenect
    brew install opencv

Check if libfreenect is set up and the kinect is working

    glview

Install python wrapper for OpenKinect

    git clone git://github.com/OpenKinect/libfreenect.git
    cd libfreenect/wrappers/python
    python setup.py install

Check if python wrapper is set up

    cd ../../../
    ipython
    import freenect

Install scikits.audiolab

    brew install libsndfile
    sudo easy_install scikits.audiolab

Install pygame

    brew install mercurial
    brew install sdl sdl_image sdl_mixer sdl_ttf portmidi
    sudo pip install hg+http://bitbucket.org/pygame/pygame

Download [SoundStretch](http://www.surina.net/soundtouch/soundstretch.html) utility to `kinect-conductor` directory

Run
----

To run a specific song:

    python conductor.py --filename "Everything is Awesome.wav"

To list available songs:

    python conductor.py --list

To calibrate the background (make sure no one is in the view of the Kinect when running this):

    python conductor.py --calibrate

To load new a new song (only supports WAV):

    python conductor.py --load --filename "Everything is Awesome.wav"

Troubleshoot
----
