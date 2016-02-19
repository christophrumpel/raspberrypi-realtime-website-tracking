import RPi.GPIO as GPIO
import time
import sys
from pubnub import Pubnub


GPIO.setmode (GPIO.BCM)

# PINS
LED_PIN = 27
# Define GPIO Display to LCD mapping
LCD_RS = 26
LCD_E  = 19
LCD_D4 = 13
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 12


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setup(LED_PIN,GPIO.OUT)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def main(city, country):
    # Main program block

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7

    # Initialise display
    lcd_init()

    # Send some test
    lcd_string("WELCOME",LCD_LINE_1)
    lcd_string("a new user from",LCD_LINE_2)

    time.sleep(5)

    lcd_string(city,LCD_LINE_1)
    lcd_string(country,LCD_LINE_2)

    time.sleep(10)

    lcd_string("",LCD_LINE_1)
    lcd_string("",LCD_LINE_2)

    time.sleep(3)

# PubNub Settings
pubnub = Pubnub(publish_key='your-pubnub-publish-ley', subscribe_key='your-pubnub-subscribe-key')
channel = 'analytics-channel'

def _callback(m, channel):
    print(m)
    if m['led'] == 1:
        print('User is active')

        # Send data to the display
        main(m['city'], m['country'])
      
        # Turn the LED on and off to make it blink
        for i in range(6):
            GPIO.output(LED_PIN,True)
            time.sleep(0.5)
            GPIO.output(LED_PIN,False)
            time.sleep(0.5)
            GPIO.output(LED_PIN,True)
        

    elif m['led'] == 0:
            GPIO.output(LED_PIN,False)
            print('NO User is active')

def _error(m):
    print(m)

pubnub.subscribe(channels=channel, callback=_callback, error=_error)

