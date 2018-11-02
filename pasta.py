#!/usr/bin/python
#
# https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/hall.py
# 
# Import required libraries
import time
import datetime
import RPi.GPIO as GPIO
import argparse
from pythonosc import osc_message_builder
from pythonosc import udp_client

def videoPaths(x):
    return {
       0: [globalVideoPath+"/01.mov", 78 ],
       1: [globalVideoPath+"/02.mov", 95 ],
       2: [globalVideoPath+"/03.mov", 71 ],
       3: [globalVideoPath+"/04.mov", 114 ],
       4: [globalVideoPath+"/05.mov", 85 ],
       5: [globalVideoPath+"/06.mov", 57 ],
       6: [globalVideoPath+"/07.mov", 117 ],
       7: [globalVideoPath+"/08.mov", 79 ],
    }.get(x, [globalVideoPath+"/Loop_pasta.mov", 10 ])    # 9 is default if x not found

def sensorCallback(channel):
  global playVideo
  global counter
  playVideo = False
  th = 3
  #print("Counter#: "+str(counter))
  # Called if sensor output changes
  timestamp = time.time()
  stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
  if GPIO.input(channel):
    # No magnet
    print("Sensor HIGH " + stamp)
  else:
    # Magnet
    print("Sensor LOW " + stamp)
    #if not playVideo and counter == th:
    if not playVideo:
      playVideo = True
      counter = 0
      print("PlayVideo: True")
    else:
      print("Sensor LOW " + stamp)
      #if counter == th:
      #  playVideo = True
      #  counter = 0
      #  print("PlayVideo: True")
      #else:
      #  counter = counter+1
      #  print("Counter: "+str(counter))

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)

print("Setup GPIO pin as input on GPIO14")

counter = 0
# Set Switch GPIO as input
# Pull high by default
GPIO.setup(14 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.add_event_detect(14, GPIO.BOTH, callback=lambda x: sensorCallback(14,counter), bouncetime=200)
GPIO.add_event_detect(14, GPIO.BOTH, callback=sensorCallback, bouncetime=200)

globalVideoPath = "/home/pi/media"
isPlaying = False

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1",  help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=9000,  help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)
client.send_message("/load", globalVideoPath )

# Get initial reading
sensorCallback(14)

videoId = 0

try:
  # Loop until users quits with CTRL-C
  path = videoPaths(videoId)
  while True :
    if playVideo:
      if not isPlaying:
        print("/play "+path[0])
        client.send_message("/play", path[0] )
        starTime = time.time()
        #print "time.time(): %f " %  time.time()
        isPlaying = True
      else:
        timer = time.time() - starTime
        if timer >= path[1]:
          print("/play "+globalVideoPath+"/Loop_pasta.mov")
          client.send_message("/play", globalVideoPath+"/Loop_pasta.mov" )
          isPlaying = False
          playVideo = False
          videoId = (videoId+1)%8
          path = videoPaths(videoId)
        #else:
          #print(timer)
    else:
      #print("Wait")
      time.sleep(0.1)

except KeyboardInterrupt:
  # Reset GPIO settings
  GPIO.cleanup()

#if __name__=="__main__":
#  main()

'''
is_playing = false
is_paused = false

If speed > th
  if !is_playing
    if is_paused
      /resume
    else
      /play getFolder
    reset(stop_clock)
    is_playing = true
  else
    //non fare un cazzo
else
  if is_playing || is_paused
    if !stop_clock.set()
      set(stop_clock)
    dClock = clock - stop_clock
    if dClock == 2 sec
      /pause
      is_playing = false
      is_paused = true
    else if dClock == 10 sec
      /play LOOP
      is_playing = false
      is_paused = false
  else
    //non fare un cazzo
'''