import board
import digitalio
import usb_cdc
import time

# Initialize variables
TIME_UNIT = 30 * 60
onTerm = TIME_UNIT
offTerm = TIME_UNIT

from config import *

# IO setting
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
pwrOff = digitalio.DigitalInOut(board.D5)
pwrOff.direction = digitalio.Direction.OUTPUT

# USB CDC (Serial)
usb_cdc.console.timeout = 0

def printHelp():
  print('HELP message')
  print("  '+' or '=': increase ON time")
  print("  '-': decrease ON time")
  print("  'u': increase OFF time")
  print("  'd': decrease OFF time")
  print("  'o': immediate ON")
  print("  'x': immediate OFF")

def printTerms():
  print(f'current setting: ON = {onTerm / 3600} hour, OFF = {offTerm / 3600} hour')

def setPower(flag):
  pwrOff.value = not flag
  print('ON' if flag else 'OFF')

time.sleep(2)  # to wait serial terminal
timeLastTransition = time.time()
printHelp()
printTerms()
powerStatus = True
setPower(powerStatus)

count = 0
while True:
  timeNow = time.time()
  data = usb_cdc.console.read(-1)   # read up to 32 bytes
  forceFlag = False
  changeFlag = False
  if data is not None and len(data) > 0:
    text = ''.join([chr(b) for b in data])  # convert bytearray to string
    updateConfig = False
    if '=' in text or '+' in text:
      onTerm += TIME_UNIT
      updateConfig = True
    elif '-' in text:
      if onTerm > TIME_UNIT:
        onTerm -= TIME_UNIT
        updateConfig = True
    elif 'u' in text:
      offTerm += TIME_UNIT
      updateConfig = True
    elif 'd' in text:
      if offTerm > TIME_UNIT:
        offTerm -= TIME_UNIT
        updateConfig = True
    elif 'o' in text:
      forceFlag = True
      powerStatus = True
    elif 'x' in text:
      forceFlag = True
      powerStatus = False
    else:
      updateConfig = False
      printHelp()
    printTerms()
    if updateConfig:
      with open("config.py", "w") as f:
        f.write(f'onTerm = {onTerm}\n')
        f.write(f'offTerm = {offTerm}')
  if powerStatus:
    if timeNow - timeLastTransition >= onTerm:
      changeFlag = True
  else:
    if timeNow - timeLastTransition >= offTerm:
      changeFlag = True
  if forceFlag or changeFlag:
    timeLastTransition = timeNow
    if changeFlag:
      powerStatus = not powerStatus
    setPower(powerStatus)
  led.value = count % 10 > (0 if powerStatus else 8)
  count += 1
  time.sleep(0.1)
