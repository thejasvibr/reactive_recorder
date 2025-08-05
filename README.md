# Reactive recorder with pre-event buffer
This module is a command-line tool to run automated audio recordings triggered when the ambient sound crosses a particular threshold. An event is the time-point when the threshold is crossed (defined in rms of the buffer audio)

The last X seconds pre-event and Y seconds post-event can be defined. 
Once a recording has been saved there is a non-functional time of 1 second by dafault. This can be altered if relevant.


## A small note on installing multiple audio-interface drivers
Esp. on windows - this will mess things up. You will need to un-install other audio-interface software and then re-install only the current one again. 
Also be ready to re-install the drivers and ASIO4ALL multiple times + restart the laptop a bunch of times until somehow everything is right again.
