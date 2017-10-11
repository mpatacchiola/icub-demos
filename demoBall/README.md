Package containing the **iCub ball demo** which consists in following a ball of defined colour. The demo uses some computer vision modules built for the [Deepgaze project](https://github.com/mpatacchiola/deepgaze). The demo also requires YARP and OpenCV.


Install Yarp
-----------------

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

Set to ON the flags `CREATE_GUIS` and `CREATE_LIB_MATH`.

```
make: sudo make install;
export PYTHONPATH=$PYTHONPATH:/path/to/bindings/build
```


Compile 
------------

If YARP and OpenCV have been installed you can compile the demo in a few command line:

```
cd demoBall
cmake .
make
```

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







