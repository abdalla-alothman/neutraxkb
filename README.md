NeutraXkbSwitch
----------------
(sampleImages/Openbox-razor-qt-Panel.png)

This file descirbes NeutraXkbSwitch, along with how to install it and how to use it.

This release of NeutraXkbSwitch is Version 1.0, released on July 3, 2014.

About NeutraXkbSwitch
--------------------
NeutraXkb Switch is a utility written in Python 3 to enable X environments users to
switch between keyboard layouts in a neutrally independent way. The tool has been tested
on XFCE, Openbox, and even KDE.

* Requirements

This tools requires PyQt4 -- the newer the release, the better.

* Limitations

NeutraXkb Switch will globally switch between keyboard layouts. Per-window
layout switching is not implemented. Further more, hot-key switching is also
not implemented.

* License

NeutraXkb Switch uses the GPL.

Installation and Usage
----------------------
The simplest way to install NeutraXkb is to run the supplied bash script:

prompt:> sudo ./INSTALL.sh

once this is successfull, you can try running:

prompt:> neutraswitch

and then add the keyboard layouts of your choice by clicking the right mouse button
and selecting "Configure." The "Configure" dialog allows you to select the layout
you wish to add along with a default icon (usually a country flag), or an icon of
your choice.

Once a desired layout is added in the "Configure" dialog, it can be prioritized
by moving it up or down and pressing the "Apply" or "OK" button. You can check
the icon menu on the system tray and with the command:

prompt:> setxkbmap -query

to verify that the order of the layouts is in tact with the way you intended.

The config file is located in:

~/.config/neutraxkb/neutraxkb.conf

### Autostart ###
*neutraxkb* is started by the a simple script named *neutraswitch*. This script
should be installed in /usr/bin. It looks like that:

    #!/bin/bash
    NXKBPATH=/usr/bin/neutrakb.py
    if [ -f $NXKBPATH ]
      then
        (nohup env python3 $NXKBPATH) >/dev/null 2>&1 &
      else
        echo "$NXKBPATH not found."
      fi

This shows that *neutraxkb* is started thrown to the background when it starts,
therefore, it is unnecessary to edit any config files and start neutraxkb with
an "&." If, for example, we would like start neutraxkb in Openbox, there is no
need to add an entry like that:

(sleep 35s && neutraswitch) &

The last "&" is not required.

----------
Abdalla S. A. Alothman    
Kuwait July 3, 2014    
GSM: +965-666-22-595    

