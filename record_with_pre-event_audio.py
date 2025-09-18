'''
Implementing a threshold based recording trigger with a pre-event buffer
=========================================================================
Channel based triggering of recording - along with a 'duty-cycle' for recording -  to limit disk size


The idea
~~~~~~~~
* Start stream
* Always read the incoming buffer and put it into a deque object of e.g. 30 seconds size. 
* When one channel in the incoming buffer is above threshold mark the time of event. 
* Keep loading buffers into deque post-event until the recording duration is reached. 
    * By 'recording duration' I mean current_time - event_time = recording duration
* Unload deque contents into a WAV file - with the last buffer's timestamp

'''

import sounddevice as sd
import numpy as np 
import soundfile as sf
import scipy.signal as signal 
import queue
import datetime as dt
import time
from collections import deque 
from utils_reactive_recorder import *
import argparse    



import argparse
help_text = """

hostapi: the host API to use for the audio recording. Either MME, WASAPI, or WDM-KS, defaults to MME

file_prefix : text to add at the beginning of a file. Defaults to 'multichannel_' with the timestamp after

preevent_durn : float>0. Duration in seconds. Defaults to 3 seconds

postevent_durn : float>0. Duration in seconds after the threshold has been crossed. Defaults to 9 seconds. 

devicename: the name of the device as it appears on sd.query_devices()

samplerate : int>0. Sample rate in Hz. Defaults to 192000. 

blocksize : int. Buffer size in samples. Defaults to 2048

threshold : float>0. The peak amplitude (absolute) threshold at which the post-event recording starts. 

monitor_channels : str with the channel numbers (0-indexed) and comma separated e.g. "0,1,2,3" . 

nchannels : int>0. Total number of channels to be used for recording. 

"""

def parse_monitor_channels(inputstr):
    '''
    '''
    chnums = [int(each) for each in inputstr.split(',')]
    return chnums

parser = argparse.ArgumentParser(description=help_text,)
parser.add_argument('-hostapi', type=str, help=help_text, default='MME')
parser.add_argument('-file_prefix', type=str, default='multichannel_')
parser.add_argument('-preevent_durn', type=float, help=help_text, default=3)
parser.add_argument('-postevent_durn', type=float, help=help_text, default=9)
parser.add_argument('-devicename', type=str, help=help_text)
parser.add_argument('-samplerate', type=int, help=help_text, default=192000)
parser.add_argument('-blocksize', type=int, help=help_text, default=2048)
parser.add_argument('-threshold', type=float, help=help_text, default=0.1)
parser.add_argument('-monitor_channels', type=parse_monitor_channels, help=help_text)

parser.add_argument('-nchannels', type=int, help=help_text)

args = parser.parse_args()


device_name = args.devicename
dev_hostapi = args.hostapi
prefix = args.file_prefix
fs = args.samplerate
exp_blocksize = args.blocksize
# pre-event buffer
preevent_durn = args.preevent_durn # seconds
postevent_durn = args.postevent_durn # seconds

device_num = get_device_indexnumber(device_name=device_name, hostapi=dev_hostapi)
nchannels = args.nchannels
monitor_channels = args.monitor_channels


total_durn = preevent_durn + postevent_durn 
# get the approx size of the queue based on block-size and total durn
queue_size = int(total_durn/(exp_blocksize/fs))
data_deque = deque([], maxlen=queue_size)
#%%

S = sd.InputStream(samplerate=fs, blocksize=exp_blocksize, 
                        device=device_num, channels=nchannels)
S.start()
print('...monitoring started....\n')
while True:
    data, success = S.read(exp_blocksize)
    data_deque.appendleft((data))
    above_thresh_channels = monitor_peak(data, monitor_channels,threshold=args.threshold)
    if np.any(above_thresh_channels):
        event_time = dt.datetime.now()    
        print(f'event detected,,,{event_time.strftime("%Y-%m-%d_%H-%M-%S")}', )
        recording_endtime = event_time + dt.timedelta(seconds=postevent_durn)
        print(f'event stop time,,,{recording_endtime.strftime("%Y-%m-%d_%H-%M-%S")}', )
        while dt.datetime.now() <= recording_endtime:
            data, success = S.read(exp_blocksize)
            data_deque.appendleft(data)
        # save data to file and fill up the deque with ones
        current_endtime = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(f'Current stop time,,,{current_endtime}')
        multich_audio = empty_dequeue_object(data_deque)
        save_nparray_to_file(multich_audio, current_endtime, samplerate=fs,
                             prefix=prefix)
        print(f'time post saving: {dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
        
        time.sleep(total_durn)
        print(f'time post sleep: {dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
    else:
        pass