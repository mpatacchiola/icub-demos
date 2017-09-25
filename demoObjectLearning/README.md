Package containing the **iCub object learning demo** which consists in training the robot to recognize unknown objects. The demo works through vocal command given using a microphone. The following package has been tested successfully on a Ubuntu 14.04 LTS. The demo uses some computer vision modules built for the [Deepgaze project](https://github.com/mpatacchiola/deepgaze).

Installation
-------------

Install Pocket sphinx for speech recognition (for [Mac OS X look here](http://www.sphinx-doc.org/en/stable/install.html#debian-ubuntu-install-sphinx-using-packaging-system)):

`sudo apt-get install python-sphinx`

Install different utilities such as **Sox** a command line tool for audio management, **arecord** for microphone audio recording:

`sudo apt-get install sox libsox-fmt-all alsa-utils lame`


Install Yarp
--------------------------

This procedure is not required if the files `yarp.py` and `_yarp.so` (included in this package) work correctly. The two files included with this package have been compiled for Ubuntu 14.04 (intel 64 bit) and they may not work on your system. If you get an error when importing YARP in python (running the file `main.py`) it means that is necessary to get the compiled files from your machine and replace the one included in the package. The files are produced whit the installation of the [YARP](http://www.yarp.it/) Python bindings. To install the YARP binding follow this procedure:

```
sudo apt-get install git cmake cmake-curses-gui libgsl0-dev libace-dev libreadline-dev
sudo apt-get install qtbase5-dev qtdeclarative5-dev qtmultimedia5-dev \
qml-module-qtquick2 qml-module-qtquick-window2 \
qml-module-qtmultimedia qml-module-qtquick-dialogs \
qml-module-qtquick-controls libqt5svg5
git clone https://github.com/robotology/yarp.git
cd yarp; mkdir build; cd build; ccmake ../
```

Set to ON the flags `CREATE_GUIS` and `CREATE_LIB_MATH`. For the Python Bindings you have to turn ON the flag `YARP_COMPILE_BINDINGS` and `CREATE_PYTHON`.

NOTE: You can compile the Python binding after the YARP compilation following these steps:

```
cd $YARP_ROOT/bindings; mkdir build; cd build; ccmake ..;
```

Then switch ON the flag: `CREATE_PYTHON`

```
make: sudo make install;
export PYTHONPATH=$PYTHONPATH:/path/to/bindings/build
```

Now to import yarp in a python project you need the two files: yarp.py and _yarp.so
If you have problem with the export then you can copy the two files directly inside the project folder. 
In this demo I provide the two files compiled in Ubuntu 14.04 (64 bit).


Install iCub simulator (optional)
------------------------------------

This part is not required if the simulator is already installed or if you work only with the real robot.

Install ODE following: http://wiki.icub.org/wiki/Linux:_Installing_ODE

```
sudo apt-get install libglut3 libglut3-dev libsdl1.2-dev
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 57A5ACB6110576A6
sudo apt-get install icub-common
git clone https://github.com/robotology/icub-main.git
mkdir build; cd build; ccmake ..
```

Now you have to use CMAKE and turn ON the flags:

```
CMAKE_BUILD_TYPE to "Release"
If you want to use the virtual screen: OPENCV_GRABBER=ON
ENABLE_icubmod_cartesiancontrollerclient ON
ENABLE_icubmod_cartesiancontrollerserver ON
ENABLE_icubmod_gazecontrollerclient      ON
Make sure the compiler matches the one you used to compile YARP.
```

Finally you can compile and install:

`make; sudo make install`


Configuration and setup
------------------------

The file `main.py` contains the variables to set in order to run the code on your machine:

```python
ROOT_FOLDER ='/icub' #it is '/icub' in real robot and '/icubSim' in the simulator
OBJECTS_PATH = './objects' #in this folder the object thumbnail are saved
HARDDEV = '2,0' # Hardware ID 'card,device' of the microphone find with command: 'arecord --list-devices'
ACAPELA_CSV = "./acapela_config.csv" #this is a csv file containing the acapela credential
HMM_PATH = "./sphinx/model/en-us/en-us"
LANGUAGE_MODEL_PATH = "./sphinx/model/en-us/en-us.lm.bin"
DICTIONARY_PATH = "./sphinx/data/icub.dic"
GRAMMAR_PATH = "./sphinx/data/icub.gram"
```

The flag `ROOT_FOLDER` should point to the real robot `/icub` or to the simulated one `/icubSim`.
If you run the code inside the `demoObjectLearning` folder you do not need to setup the path location of the folders starting with `./` prefix. The `HARDDEV` ID can be obtained from terminal typing `arecord --list-devices`. If a microphone is connected to the machine then the ID is returned.
The configuration requires a file called `acapela_config.csv` containing the parameters of an Acapela speech syntethizer account (trial free). You can register at [http://vaas.acapela-group.com/VaaS/index.php](http://vaas.acapela-group.com/VaaS/index.php). The CSV file must contain the following parameters:

1. Your personal Acapela username
2. The Acapela app name
3. Your personal Acapela password
4. Synthesizer website (default: http://vaas.acapela-group.com/Services/Synthesizer)

All the parameters must be separated with a comma (no spaces) as follows:

```
acapela_username,acapela_app,acapela_password,http://vaas.acapela-group.com/Services/Synthesizer
``` 

Usage
-----

If everything is installed properly and the configuration variables and files point to the correct location then it is possible to run the file `main.py` from terminal:

```
python main.py
```

The robot should say the sentence "I'm ready!". Moreover you should see a window containing the video stream from one of the iCub eys. The interaction with the robot works through three keys which can be pressed to start/stop some routines. Attention: to allow the script to catch the key pressed is necessary to **select the main window** (the window that is showing the robot camera stream). This windows uses the OpenCV method `cv2.waitKey()` in order to record the key pressed. This is a list of the available commands:

- Button (q)uit stops everything and exit
- Button (f)orce stops object tracking
- Button (r)ecord start recording from microphone (5 seconds)

To **check** if everything is working you can ask to iCub your first question:

- Press `r` on the keyboard to start recording (5 seconds)
- Say: how are you?

The robot should give an answer. To **learn** a new object:

- Show the object to the robot (it must fill the red square on the camera window)
- Press `r` on the keyboard to start recording (5 seconds)
- Say: learn [object name] (where object name can be: ball, cup, chair, dog, book, table)

If the object has been learned the iCub will reply with the correct name, otherwise with a wrong one. To **remove** an object from memory:

- Press `r` on the keyboard to start recording (5 seconds)
- Say: forget [object name] (where object name can be: ball, cup, chair, dog, book, table)

At any time you can enter in the folder called `objects` and see if the thumbnail stored is coherent with the object name.
To **recall** an object that has been learned previously:

- Show the object to the robot (it must fill the red square on the camera window)
- Press `r` on the keyboard to start recording (5 seconds)
- Say: what is this?

To **start object tracking** of an object that has been previously learned:

- Press `r` on the keyboard to start recording (5 seconds)
- Say: find the [object name] (where object name can be: ball, cup, chair, dog, book, table)

To **stop object tracking** of an object you can press the button `f` on the keyboard (remember that the main window must be selected), or you can:

- Press `r` on the keyboard to start recording (5 seconds)
- Say: stop detection



Troubleshooting
---------------

The **terminal stops** at this line `[ICUB] Init: Waiting for /icub/cam/left ...`.  The robot is not connected and the `main.py` starts but does not find it. If you are using a real robot chek that the flag called `ROOT_FOLDER` in the `main.py` script is set to `/icub`. On the other hand, if you are using the simulator you should first run the simulator and then run the main script. In this case the flag should be `/icubSim`.

There is **no voice produced by the robot**. It may be that you have problems with your Acapela account, you should verify if the mp3 file returned by the service is correctly stored in the `/tmp` folder of your system. If the audio file is stored but it is empty then it is possible that you have a problem with your account. You should contact Acapela technical support. Moreover remember that the icub does not have internal speakers. This package used the speaker on the machine were it is running. Check if the speakers are correctly connected and configured. 

The **robot does not understand my questions**. Check if the microphone is working, if there are multiple microphones be sure you are using the correct one. Moreover the audio file is stored in the file `\tmp\audio.wav` you can check if it contains the correct sound you recorded.




