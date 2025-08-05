# -*- coding: utf-8 -*-
"""
All the support functions to get the reactive recording going 
=============================================================
Created on Mon Aug  4 22:53:02 2025

@author: theja
"""
from collections import deque
import sounddevice as sd
import soundfile as sf
import numpy as np 

def get_device_indexnumber(device_name='US-16x08', hostapi='MME'):
    '''
    Check for the device name in all of the recognised devices and
    return the index number within the list.

    Parameters
    ----------
    device_name : str, optional
        Name of the device as it appears on sd.query_devices()
        Defaults to 'US-16x08'
    when_manyofsamename: str, optional 
        What to do when >1 devices with the same sounddevice name are
        found. Defaults to 'first', which takes the first device. 
        Alternately if 'last' is given, then the last index is chosen.
    '''
    device_list = sd.query_devices()
    all_hostapis = [each['name']  for each in sd.query_hostapis()]
    
    tgt_ind_found = False
    for each in device_list:
        #print(each['name'])
        name_is_there = device_name in each['name']
        hostapi_is_same = hostapi in all_hostapis[each['hostapi']]
        details_match = np.logical_and(name_is_there, hostapi_is_same) 
        #print(each['name'])
        if details_match:
            tgt_ind = each['index']
            tgt_ind_found = True
            break
        else:
            pass
        

    if not tgt_ind_found:
        print (sd.query_devices())

        raise ValueError('The input device \n' + device_name+
        '\n could not be found, please look at the list above'+
                         ' for all the recognised devices'+
                         ' \n Please use sd.query_devices to check the  recognised'
                         +' devices on this computer')

    return tgt_ind


def rms(X):
    return np.sqrt(np.mean(X**2))

def monitor_peak(data, monitor_channels, threshold=0.1):
    '''
    Parameters
    ----------
    data : (M,N) np.array
        M samples x N channels audio buffer
    monitor_channels : array-like
        Array-like with channel indices to check if they're
        above the threshold
    threshold : float>0
        The RMS threshold value. If greater or equal, this channel
        will be True for above_threshold
    
    Returns
    -------
    above_threshold : array-like
    '''
    chwise_peak = np.tile(False, len(monitor_channels))
    for i,ch in enumerate(monitor_channels):
        chwise_peak[i] = np.max(abs(data[:,ch])) >=threshold
    return chwise_peak

def monitor_rms(data, monitor_channels, threshold=0.1):
    '''
    Parameters
    ----------
    data : (M,N) np.array
        M samples x N channels audio buffer
    monitor_channels : array-like
        Array-like with channel indices to check if they're
        above the threshold
    threshold : float>0
        The RMS threshold value. If greater or equal, this channel
        will be True for above_threshold
    
    Returns
    -------
    above_threshold : array-like
    '''
    chwise_rms = np.tile(False, len(monitor_channels))
    for i,ch in enumerate(monitor_channels):
        chwise_rms[i] = rms(data[:,ch]) >=threshold
    return chwise_rms

def empty_dequeue_object(deque_obj):
    '''
    Empties out a deque object with audio buffers into an np.array
    
    deque_obj: collections.deque
        A double-ended queue with np.arrays of (blocksize,Nchannels) shape
    
    Returns
    -------
    audio_data : np.array, (M,Nchannels)
        Audio data with the deque data flipped into the 'correct' order
    '''      
    current_size = len(deque_obj)
    # reverse the deque
    deque_obj.reverse()
    audio_buffers = [deque_obj.popleft() for i in range(current_size)]
    audio_data = np.row_stack(audio_buffers)
    return audio_data

def save_nparray_to_file(multich_audio, timestamp, **kwargs):
    '''
    Parameters
    ----------
    multich_audio : np.array (Msamples, Nchannels)
    timestamp : str
        The suffix
    
    Keyword Arguments
    -----------------
    file_prefix : optional 
        Defaults to 'multichannel_<timestamp>.wavs'
    samplerate
    channels

    Returns
    -------
    None, writes a file with 'multichannel_<yyyy-mm-dd_HH-MM-SS>.wav' 
    format
    
    '''
    audiofilename = kwargs.get('prefix','multichannel_') + timestamp+'.wav'
    sf.write(audiofilename, multich_audio, samplerate=kwargs['samplerate'],)
