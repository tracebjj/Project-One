#!/usr/bin/env python3

# STUDENT version for Project 1.
# TPRG2131 Fall 202x
# Updated Phil J (Fall 202x)
# 
# Louis Bertrand
# Oct 4, 2021 - initial version
# Nov 17, 2022 - Updated for Fall 2022.
# 

# PySimpleGUI recipes used:
#
# Persistent GUI example
# https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-2a-persistent-window-multiple-reads-using-an-event-loop
#
# Asynchronous Window With Periodic Update
# https://pysimplegui.readthedocs.io/en/latest/cookbook/#asynchronous-window-with-periodic-update

import PySimpleGUI as sg
from time import sleep

# Hardware interface module
# Button basic recipe: *** define the pin you used
# https://gpiozero.readthedocs.io/en/stable/recipes.html#button
# Button on GPIO channel, BCM numbering, same name as Pi400 IO pin

#Where am I?
hardware_present = True
try:
    #Used pin 26
    from gpiozero import Button, Servo
    button = Button(5)
    servo = Servo(12)
    hardware_present = True
except ModuleNotFoundError:
    print("Not on a Raspberry Pi or gpiozero not installed.")



# Setting this constant to True enables the logging function
# Set it to False for normal operation
TESTING = False

# Print a debug log string if TESTING is True, ensure use of Docstring, in definition
def log(s):
    
    if TESTING:
        print(s)

#quantities
QTomatoSoup = 3
QRaspberryStew = 1
QLemonJuice = 6
QCanOpener = 1
QSaladDressing = 2

def add_coins(Amount, total):
    if Amount == 200:
        print ("\nToonie Added")
        total += 200
        print(total)
    elif Amount == 100:
        print("\nLoonie Added")
        total += 100
        print(total)
    elif Amount == 25:
        print("\nQuarter Added")
        total += 25
        print(total)
    elif Amount == 10:
        print("\nDime Added")
        total += 10
        print(total)
    elif Amount == 5:
        print("\nNickel Added")
        total += 5
        print(total)
    return total
    
def serv_op():
    servo.min()
    sleep(0.1)
    servo.max()
    sleep(0.1)
    servo.mid()
    sleep(0.2)

# The vending state machine class holds the states and any information
# that "belongs to" the state machine. In this case, the information
# is the products and prices, and the coins inserted and change due.
# For testing purposes, output is to stdout, also ensure use of Docstring, in class
class VendingMachine(object):
    
    PRODUCTS = [("Tomato Soup   $2", 200),  # Using an integer as the key
                ("Raspberry Stew   $2.50", 250), 
                ("Lemon Juice   25\u00A2", 25),
                ("Can Opener   $1", 100),
                ("Salad Dressing   5\u00A2", 5)
                ]

    # List of coins: each tuple is ("VALUE", value in cents)
    COINS = [ ("$2", 200),  
              ("$1", 100),  
              ("25\u00A2", 25),
              ("10\u00A2", 10),
              ("5\u00A2", 5),
            ]


    def __init__(self):
        self.state = None  # current state
        self.states = {}  # dictionary of states
        self.event = ""  # no event detected
        self.amount = 0  # amount from coins inserted so far
        
    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            log('Exiting %s' % (self.state.name))
            self.state.on_exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.on_entry(self)

    def update(self):
        if self.state:
            #log('Updating %s' % (self.state.name))
            self.state.update(self)

    def button_action(self):
        """Callback function for Raspberry Pi button."""
        self.event = 'RETURN'
        self.update()

# Parent class for the derived state classes
# It does nothing. The derived classes are where the work is done.
# However this is needed. In fomachine.eventrmal terms, this is an "abstract" class.
class State(object):
    """Superclass for states. Override the methods as required."""
    _NAME = ""
    def __init__(self):
        pass
    @property
    def name(self):
        return self._NAME
    def on_entry(self, machine):
        print("Vending Machine\n")
        pass
    def on_exit(self, machine):
        pass
    def update(self, machine):
        pass

# In the waiting state, the machine waits for the first coin
class WaitingState(State):
    _NAME = "waiting"
    def update(self, machine):
        if machine.event in (5, 10, 25, 100, 200):
            machine.total = add_coins(machine.event, machine.total)
            print(machine.total)
        elif machine.event in ("Tomato Soup   $2", "Raspberry Stew   $2.50", "Lemon Juice   25\u00A2", "Can Opener   $1", "Salad Dressing   5\u00A2"):
            machine.go_to_state("item")
        elif machine.event == 'RETURN':
            machine.go_to_state('return')

#checks availability of stock
def StorageCheck(Event, total):
    global QTomatoSoup, QRaspberryStew, QLemonJuice, QCanOpener, QSaladDressing
    
    if machine.event == "Tomato Soup   $2":
        if QTomatoSoup <= 0:
            print ("\n OUT OF STOCK\n")
            return "NoStock"
        if total >= 200 and QTomatoSoup > 0:
            QTomatoSoup -= 1
            total -= 200
        return total
    
    elif machine.event == "Raspberry Stew   $2.50":
        if QRaspberryStew <= 0:
            print ("\n OUT OF STOCK\n")
            return "NoStock"
        if total >= 250 and QRaspberryStew > 0:
            QRaspberryStew -= 1
            total -= 250
        return total
        
    elif machine.event == "Lemon Juice   25\u00A2":
        if QLemonJuice <= 0:
            print ("\n OUT OF STOCK\n")
            return "NoStock"
        if total >= 25 and QLemonJuice > 0:
            QLemonJuice -= 1
            total -= 25
        return total
        
    elif machine.event == "Can Opener   $1":
        if QCanOpener <= 0:
            print ("\n OUT OF STOCK\n")
            return "NoStock"     
        if total >= 100 and QCanOpener > 0:
            QCanOpener -= 1
            total -= 100
        return total
        
    elif machine.event == "Salad Dressing   5\u00A2":
        if QSaladDressing <= 0:
            print ("\n OUT OF STOCK\n")
            return "NoStock"  
        if total >= 5 and QSaladDressing > 0:
            QSaladDressing -= 1
            total -= 5
        return total
    
    
    
# finish check and direct next steps
class ItemState(State):
    _NAME = "item"
    def on_entry(self, machine):
        StockStatus = StorageCheck(machine.event, machine.total)
        if machine.total == "NoStock":
            machine.go_to_state('waiting')
        if machine.total != StockStatus and isinstance(StockStatus, int):
            machine.total = StockStatus
            machine.go_to_state ("delivery")  
        else:
            print(Selection)
            print("\nInsufficient Funds", machine.total, "\u00A2")
            machine.go_to_state ("waiting")

# Deliver Items
class DeliveryState(State):
    _NAME = "delivery"
    def on_entry(self, machine):    
        print("Item Delivered!")
        time.sleep(0.2)
        print("Balance is: ", machine.total)
        time.sleep(0.4)
        machine.go_to_state ("waiting")

class ReturnState(State):
    _NAME = "return"
    
# MAIN PROGRAM
if __name__ == "__main__":
    #define the GUI
    sg.theme('BluePurple')    # Keep things interesting for your users

    coin_col = []
    coin_col.append([sg.Text("ENTER COINS", font=("Helvetica", 24))])
    for item, _ in VendingMachine.COINS:
        log(item)
        button = sg.Button(item, font=("Helvetica", 18))
        row = [button]
        coin_col.append(row)

    select_col = []
    select_col.append([sg.Text("SELECT ITEM", font=("Helvetica", 24))])
    for item, _ in VendingMachine.PRODUCTS:  # Iterate over the tuples but only use the first element
        log(item)
        button = sg.Button(item, font=("Helvetica", 18))
        row = [button]
        select_col.append(row)



    layout = [ [sg.Column(coin_col, vertical_alignment="TOP"),
                     sg.VSeparator(),
                     sg.Column(select_col, vertical_alignment="TOP")
                    ] ]
    layout.append([sg.Button("RETURN", font=("Helvetica", 12))])
    window = sg.Window('Vending Machine', layout)

    # new machine object
    vending = VendingMachine()

    # Add the states
    vending.add_state(WaitingState())
    vending.add_state(ItemState())
    vending.add_state(DeliveryState())
    vending.add_state(ReturnState())
    # Reset state is "waiting for coins"
    vending.go_to_state('waiting')

   # Checks if being used on Pi
    if hardware_present:
        # Set up the hardware button callback (do not use () after function!)
        button.when_pressed = vending.button_action

    # The Event Loop: begin continuous processing of events
    # The window.read() function reads events and values from the GUI.
    # The machine.event variable stores the event so that the
    # update function can process it.
    # Now that all the states have been defined this is the
    # main portion of the main program.
    while True:
        button.when_pressed = serv_op
        event, values = window.read(timeout=10)
        if event == "__TIMEOUT__":
            pass  # no user interaction event occurred
        elif event == sg.WIN_CLOSED:
            print("Event sg.WIN_CLOSED")
            break
        else:
            print("Event", event)

    window.close()
    print("Exiting...")
