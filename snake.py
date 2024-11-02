from PIL import Image
import serial.tools.list_ports
import turtle
import time
import random

ports = serial.tools.list_ports.comports()

for port in ports:
		print(str(port))
		
serialDevFile = '/dev/cu.usbmodem1101'
ser = serial.Serial(serialDevFile, 9600, timeout=1)

#--------------Game Body----------------#
global delay
delay = 50

# Score
global score
score = 0
global high_score
high_score = 0
global ppa
ppa = 10

# Set up the screen
wn = turtle.Screen()
wn.title("Snake Game by @TokyoEdTech (mod by YL)")
wn.colormode(255)
wn.bgcolor(255, 255, 255)
wn.setup(width=600, height=600)
wn.tracer(0) # Turns off the screen updates

# Snake head
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("black")
head.penup()
head.goto(0,0)
head.direction = "stop"

wn.addshape("apple.gif")
wn.addshape("apple_gold.gif")
# Snake food
food = turtle.Turtle()
food.speed(0)
food.shape("apple.gif")
#food.shape("circle")
#food.color("red")
food.penup()
food.goto(0,100)

def goldApple():
    food.shape("apple_gold.gif")

segments = []

# Pen
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0  High Score: 0  P/A: 10 Controller: JOYSTICK", align="center", font=("Courier", 24, "normal"))

global mode
mode = "JOYSTICK"
def change_mode(): 
    global mode
    global score
    global high_score
    global ppa
    if mode == "JOYSTICK":
        mode = "MPU"
    elif mode == "MPU":
        mode = "JOYSTICK"
    pen.clear()
    pen.color(0, 0, 0);
    pen.write("Score: {}  High Score: {}  P/A: {} Controller: {}".format(score, high_score, ppa, mode), align="center", font=("Courier", 14, "normal")) 


# Functions
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

global step
step = 5

def move():
    global step
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + step)

    if head.direction == "down":
        y = head.ycor()
        head.sety(y - step)

    if head.direction == "left":
        x = head.xcor()
        head.setx(x - step)

    if head.direction == "right":
        x = head.xcor()
        head.setx(x + step)

# Keyboard bindings
wn.listen()
wn.onkey(go_up, "w")
wn.onkey(go_down, "s")
wn.onkey(go_left, "a")
wn.onkey(go_right, "d")
wn.onkey(change_mode, "c")

global bonus
bonus = False

def serial_analyzer():
    global mode
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()  # Read a line of data
        if mode == "JOYSTICK":
            match data:
                case "JOYSTICK_LEFT":
                    go_left()
                    print("LEFT")
                case "JOYSTICK_RIGHT":
                    go_right()
                    print("RIGHT")
                case "JOYSTICK_UP":
                    go_up()
                    print("UP")
                case "JOYSTICK_DOWN":
                    go_down()
                    print("DOWN")
        elif mode == "MPU":
            match data:
                case "MPU_LEFT":
                    go_left()
                    print("LEFT")
                case "MPU_RIGHT":
                    go_right()
                    print("RIGHT")
                case "MPU_UP":
                    go_up()
                    print("UP")
                case "MPU_DOWN":
                    go_down()
                    print("DOWN")
                case "MPU_SHAKE":
                    goldApple()
                    bonus = True
                    print("SHAKE")

def send_buzzer():
    ser.write(("BUZZ\n").encode())

#------ Main game loop ------#
def game_loop():
    global delay
    global score
    global high_score
    global ppa
    global step
    global bonus
    global mode
    wn.update()

    #Serial Analyzer
    serial_analyzer();

    # TODO: notes by Prof. Luo
    # you need to add your code to read control information from serial port
    # then use that information to set head.direction
    # For example, 
    # if control_information == 'w':
    #     head.direction = "up"
    # elif control_information == 's':
    #     head.direction = "down"
    # elif ......
    #

    # Check for a collision with the border
    if head.xcor()>290 or head.xcor()<-290 or head.ycor()>290 or head.ycor()<-290:
        #time.sleep(1)
        head.goto(0,0)
        head.direction = "stop"

        # Hide the segments
        for segment in segments:
            segment.goto(1000, 1000)
        
        # Clear the segments list
        segments.clear()

        # Reset the score
        score = 0
        bonus = False
        step = 5
        food.shape("apple.gif")

        # Reset the delay
        delay = 50

        pen.clear()
        pen.color(0, 0, 0);
        pen.write("Score: {}  High Score: {}  P/A: {} Controller: {}".format(score, high_score, ppa, mode), align="center", font=("Courier", 14, "normal")) 


    # Check for a collision with the food
    if head.distance(food) < 10:

        # TODO: notes by Prof. Luo
        # you need to send a flag to Arduino indicating an apple is eaten
        # so that the Arduino will beep the buzzer
        # Hint: refer to the example at Serial-RW/pyserial-test.py

        # Move the food to a random spot
        x = random.randint(-290, 290)
        y = random.randint(-290, 290)
        food.goto(x,y)

        # Add a segment
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("circle")
        new_segment.color("grey")
        new_segment.penup()
        segments.append(new_segment)

        # Increase speed
        if step != 50:
            step += 1
        

        # Increase the score
        if bonus == True:
            score += 20
        else:
            score += 10

        send_buzzer()

        if score > high_score:
            high_score = score
        
        pen.clear()
        pen.color(0, 0, 0);
        pen.write("Score: {}  High Score: {}  P/A: {} Controller: {}".format(score, high_score, ppa, mode), align="center", font=("Courier", 14, "normal")) 

    # Move the end segments first in reverse order
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)

    # Move segment 0 to where the head is
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x,y)

    move()

    # Check for head collision with the body segments
    for segment in segments:
        if segment.distance(head) < 5:
            #time.sleep(1)
            head.goto(0,0)
            head.direction = "stop"
        
            # Hide the segments
            for segment in segments:
                segment.goto(1000, 1000)
        
            # Clear the segments list
            segments.clear()

            # Reset the score
            score = 0
            bonus = False
            step = 5
            food.shape("apple.gif")

            # Reset the delay
            delay = 50
        
            # Update the score display
            pen.clear()
            pen.color(0, 0, 0);
            pen.write("Score: {}  High Score: {}  P/A: {} Controller: {}".format(score, high_score, ppa, mode), align="center", font=("Courier", 14, "normal"))     

    wn.ontimer(game_loop, delay)
	
game_loop();
wn.mainloop();