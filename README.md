# Reactive recorder with pre-event buffer
This module is a command-line tool to run automated audio recordings triggered when the ambient sound crosses a particular threshold. An event is the time-point when the threshold is crossed (defined in rms of the buffer audio)

The last X seconds pre-event and Y seconds post-event can be defined. 
Once a recording has been saved there is a non-functional time of 1 second by dafault. This can be altered if relevant.


