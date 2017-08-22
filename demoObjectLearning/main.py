#!/usr/bin/python

# Copyright (C) 2017 Massimiliano Patacchiola
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ATTENTION: to work in simulator it requires to lunch the following commands:
# yarpserver
# ./iCub_SIM
# ./iKinGazeCtrl --from configSim.ini
# yarpdev --device opencv_grabber
# yarp connect /grabber /icubSim/texture/screen
#
# For the cartesian controller of the left arm
# ./simCartesianControl
# ./iKinCartesianSolver --context simCartesianControl --part left_arm

# PocketSphinx valid Commands are:
# The prefix [iCub] or [hey] is optional
# learn <object name>
# this is a <object name>
# forget <object name>
# what is this
# find the <object name>
# stop detection
# look at me

from speech_recognition import SpeechRecognizer
from icub import iCub
import cv2
import random
import time
import os

#Main parameters, to change based on the file locations
ROOT_FOLDER ='/icub' #it is '/icub' in real robot and '/icubSim' in the simulator
OBJECTS_PATH = './objects'
HARDDEV = '2,0' # Hardware ID 'card,device' of the microphone find with command: 'arecord --list-devices'
ACAPELA_CSV = "./acapela_config.csv" #this is a csv file containing the acapela credential
HMM_PATH = "./sphinx/model/en-us/en-us"
LANGUAGE_MODEL_PATH = "./sphinx/model/en-us/en-us.lm.bin"
DICTIONARY_PATH = "./sphinx/data/icub.dic"
GRAMMAR_PATH = "./sphinx/data/icub.gram"

def initialise(root='/icubSim'):
    # Initialise the speech recognition engine and the iCub controller
    my_speech = SpeechRecognizer(
        hmm_path=HMM_PATH,
        language_model_path=LANGUAGE_MODEL_PATH,
        dictionary_path=DICTIONARY_PATH,
        grammar_path=GRAMMAR_PATH,
        rule_name='icub.basicCmd',
        fsg_name="icub")
    # iCub initialization
    my_icub = iCub(icub_root=root)
    # Load acapela configuration from file
    my_icub.set_acapela_credential(ACAPELA_CSV)
    account_login, application_login, application_password, service_url = my_icub.get_acapela_credential()
    print("[ACAPELA]Acapela configuration parameters:")
    print("Account Login: " + str(account_login))
    print("Application Login: " + str(application_login))
    print("Account Password: " + str(application_password))
    print("Service URL: " + str(service_url))
    print("")
    # Return the objects
    return my_speech, my_icub


def speech_to_action(speech_string):
    """ Take the sentence from the speech recognition and plan an action
    <action> = (learn new object | watch | inspect | find | search | look | what | start | stop);
    <target> = (ball | cup | book | dog | chair | table | at me | is this | movement detection);
    @param speech_string: 
    @return: 
    """
    if speech_string.find('learn') > -1 or speech_string.find('this is a') > -1:
        response_list = ['I like to learn! This is a ',
                         'Ok, this is a ',
                         'I learned a new object, ',
                         '']
        object_name = speech_string.rsplit(None, 1)[-1]
        response_string = response_list[random.randint(0, len(response_list)-1)] + object_name
        state = 'learn'
    elif speech_string.find('forget') > -1:
            response_list = ['Fine, I will remove the  ',
                             'Ok, I will forget the  ',
                             'Removing object, ']
            object_name = speech_string.rsplit(None, 1)[-1]
            response_string = response_list[random.randint(0, len(response_list) - 1)] + object_name
            state = 'forget'
    elif speech_string.find('what is this') > -1:
        response_string = ""
        state = 'what'
    elif speech_string.find('find the') > -1 or speech_string.find('search the') > -1:
        object_name = speech_string.rsplit(None, 1)[-1]
        object_path = OBJECTS_PATH + '/' + str(object_name) + ".png"
        if not os.path.isfile(object_path):
            print("[SPEECH-TO-ACTION][WARNING] " + "this file does not exist: " + str(object_path) + "\n")
            response_string = "Sorry I do not know this object!"
            state = 'key'
        else:
            response_list = ["Ok, now I'm looking for a ",
                             'Ok I will track the ',
                             'Ready to track the ']
            response_string = response_list[random.randint(0, len(response_list)-1)] + object_name
            state = 'movedetect on'
    elif speech_string.find('stop detection') > -1:
        response_list = ["Ok, no more movements",
                         'Ok I will stop it',
                         "I'm gonna stop it!"]
        response_string = response_list[random.randint(0, len(response_list)-1)]
        state = 'movedetect off'
    elif speech_string.find('look at me') > -1:
        response_list = ["Ok!",
                         'Sure!']
        response_string = response_list[random.randint(0, len(response_list)-1)]
        state = 'look'
    elif speech_string.find('how are you') > -1:
        response_list = ["I am fine, and you?",
                         "It's all right, thanks."]
        response_string = response_list[random.randint(0, len(response_list)-1)]
        state = 'key'
    else:
        response_list = ["Sorry I did not understand.",
                         'Sorry, can you repeat?',
                         'Repeat again please.']
        response_string = response_list[random.randint(0,len(response_list)-1)]
        state = 'key'
    return response_string, state


def main():
    STATE = 'show'
    speech_string = ""
    fovea_offset = 25 # side of the fovea square
    my_speech, my_icub = initialise(ROOT_FOLDER)
    is_connected = my_icub.check_connection()
    if is_connected:
        print("[STATE Init] internet connection present.")
    else:
        print("[STATE Init][ERROR] internet connection not present!!!")
        return
    my_icub.say_something(text="I'm ready!")
    cv2.namedWindow('main')

    while True:
        if STATE == 'record':
            #image = my_icub.return_left_camera_image(mode='BGR')
            my_speech.record_audio("/tmp/audio.wav", seconds=3, extension='wav', harddev=HARDDEV)
            raw_file_path = my_speech.convert_to_raw(file_name="/tmp/audio.wav", file_name_raw="/tmp/audio.raw", extension='wav')
            speech_string = my_speech.return_text_from_audio("/tmp/audio.raw")
            print("[STATE " + str(STATE) + "] " + "Speech recognised: " + speech_string)
            STATE = 'understand'

        elif STATE == 'understand':
            response_string, local_state = speech_to_action(speech_string)
            print("[STATE " + str(STATE) + "] " + "Speech recognised: " + speech_string)
            print("[STATE " + str(STATE) + "] " + "Next state: " + local_state)
            my_icub.say_something(text=response_string)
            STATE = local_state

        elif STATE == 'show':
            left_image = my_icub.return_left_camera_image(mode='BGR')
            img_cx = int(left_image.shape[1] / 2)
            img_cy = int(left_image.shape[0] / 2)
            cv2.rectangle(left_image,
                          (img_cx-fovea_offset, img_cy-fovea_offset),
                          (img_cx+fovea_offset, img_cy+fovea_offset),
                          (0, 0, 255), 3)
            cv2.imshow('main', left_image)
            STATE = 'key'

        elif STATE == 'movedetect on':
            object_name = response_string.rsplit(None, 1)[-1]
            print("[STATE " + str(STATE) + "] " + "start tracking of: " + str(object_name) + "\n")
            object_path = OBJECTS_PATH + '/' + str(object_name) + ".png"
            if my_icub.is_movement_detection():
                    my_icub.stop_movement_detection()
                    time.sleep(0.5)
                    my_icub.start_movement_detection(template_path=object_path, delay=1.0)
            else:
                    my_icub.start_movement_detection(template_path=object_path, delay=1.0)
            STATE = 'key'

        elif STATE == 'movedetect off':
            print("[STATE " + str(STATE) + "] " + "stop movement tracking" + "\n")
            my_icub.stop_movement_detection()
            time.sleep(0.5)
            my_icub.reset_head_pose()
            STATE = 'key'

        elif STATE == 'look':
            print("[STATE " + str(STATE) + "] " + "gaze reset" + "\n")
            my_icub.reset_head_pose()
            STATE = 'key'

        elif STATE == 'learn':
            object_name = response_string.rsplit(None, 1)[-1]
            print("[STATE " + str(STATE) + "] " + "Learning new object: " + object_name + "\n")
            left_image = my_icub.return_left_camera_image(mode='BGR')
            #left_image = image
            img_cx = int(left_image.shape[1] / 2)
            img_cy = int(left_image.shape[0] / 2)
            left_image = left_image[img_cy-fovea_offset:img_cy+fovea_offset,
                                    img_cx-fovea_offset:img_cx+fovea_offset]
            my_icub.learn_object_from_histogram(left_image, object_name)
            print("[STATE " + str(STATE) + "] " + "Writing new template in " + OBJECTS_PATH + '/' + object_name + ".png" + "\n")
            cv2.imwrite(OBJECTS_PATH + '/' + str(object_name) + '.png', left_image)
            STATE = 'key'

        elif STATE == 'forget':
            object_name = response_string.rsplit(None, 1)[-1]
            print("[STATE " + str(STATE) + "] " + "Forgetting object: " + object_name + "\n")
            my_icub.remove_object_from_histogram(object_name)
            object_path = OBJECTS_PATH + '/' + str(object_name) + '.png'
            if os.path.isfile(object_path):
                os.remove(object_path)
            else:
                print("[STATE " + str(STATE) + "][ERROR] " + "This image does not exist: " + object_path + "\n")
            STATE = 'key'

        elif STATE == 'what':
            print("[STATE " + str(STATE) + "] " + "Recalling object from memory..." + "\n")
            left_image = my_icub.return_left_camera_image(mode='BGR')
            #left_image = image
            img_cx = int(left_image.shape[1] / 2)
            img_cy = int(left_image.shape[0] / 2)
            left_image = left_image[img_cy-25:img_cy+25, img_cx-25:img_cx+25]
            object_name = my_icub.recall_object_from_histogram(left_image)
            if object_name is None:
                my_icub.say_something("My memory is empty. Teach me something!")
            else:
                print("[STATE " + str(STATE) + "] " + "Name returned: " + str(object_name) + "\n")
                response_list = ["Let me see. I think this is a ",
                                 "Let me think. It's a ",
                                 "Just a second. It may be a ",
                                 "It should be a "]
                response_string = response_list[random.randint(0, len(response_list) - 1)]
                my_icub.say_something(response_string + str(object_name))
            STATE = 'key'

        elif STATE == 'key':
            key_pressed = cv2.waitKey(10) # delay in millisecond
            if key_pressed==ord('q'):  #q=QUIT
                print("[STATE " + str(STATE) + "] " + "Button (q)uit pressed..." + "\n")
                STATE = "close"
            elif key_pressed==110: #n=
                print("[STATE " + str(STATE) + "] " + "Button (n) pressed..." + "\n")
            elif key_pressed==ord('f'): #f=FORCE STOP TRACKING
                print("[STATE " + str(STATE) + "] " + "Button (f)orce stop pressed..." + "\n")
                STATE = "movedetect off"
            elif key_pressed == ord('r'):  # r=RECORD
                print("[STATE " + str(STATE) + "] " + "Button (r)ecord pressed..." + "\n")
                STATE = "record"
            else:
                STATE = 'show'

        elif STATE == 'close':
            my_icub.say_something(text="See you soon, bye bye!")
            my_icub.stop_movement_detection()
            my_icub.close()
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    main()
