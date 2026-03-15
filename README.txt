==================================================
        How to Install RoboBuddy on Raspberry Pi
==================================================

1. Transfer Files
-----------------
The easiest way to move the files is using a USB Flash Drive:

   a. Copy the entire 'RoboBuddyApp' folder onto a USB drive.
   b. Plug the USB drive into your Raspberry Pi.
   c. Drag and drop the folder from the USB drive to your Pi's Desktop.

2. Install Kivy (The Software Framework)
----------------------------------------
Open the Terminal on your Raspberry Pi (the black icon with >_) and run these commands one by one.
Press Enter after each line and type 'Y' if asked to confirm.

   # Step 1: Update your system
   sudo apt update
   sudo apt upgrade -y

   # Step 2: Install necessary tools
   sudo apt install -y python3-pip python3-setuptools python3-dev libmtdev1 xclip xsel libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0

   # Step 3: Install Kivy
   pip3 install kivy --break-system-packages

   (Note: If you get an error about "externally managed environment", the --break-system-packages flag fixes this on newer Raspberry Pi OS versions.)

3. Run RoboBuddy
----------------
To start the app:

   a. Open Terminal.
   b. Navigate to the folder (assuming you put it on Desktop):
      cd ~/Desktop/RoboBuddyApp
   
   c. Run the program:
      python3 main.py

That's it! Your RoboBuddy should appear on the screen.
