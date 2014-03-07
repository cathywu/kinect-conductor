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

Run
----

Troubleshoot
----
