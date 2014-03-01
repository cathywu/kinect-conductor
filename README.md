kinect-conductor
================

Setup
-----

Install OpenKinect

    brew install libfreenect

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

Run
----

Troubleshoot
----
