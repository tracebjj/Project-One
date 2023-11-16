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


# Hardware interface module
# Button basic recipe: *** define the pin you used
# https://gpiozero.readthedocs.io/en/stable/recipes.html#button
# Button on GPIO channel, BCM numbering, same name as Pi400 IO pin

#Where am I?
hardware_present = False
try:
    #Used pin 26
    from gpiozero import Button
    key1 = Button(26)
    hardware_present = True
except ModuleNotFoundError:
    print("Not on a Raspberry Pi or gpiozero not installed.")

# Setting this constant to True enables the logging function
# Set it to False for normal operation
TESTING = True

# Print a debug log string if TESTING is True, ensure use of Docstring, in definition
def log(s):
    
    if TESTING:
        print(s)


# The vending state machine class holds the states and any information
# that "belongs to" the state machine. In this case, the information
# is the products and prices, and the coins inserted and change due.
# For testing purposes, output is to stdout, also ensure use of Docstring, in class
class VendingMachine(object):
    
    PRODUCTS = {("Tomato Soup   $2", 200),  # Using an integer as the key
                ("Raspberry Stew   $2.50", 250), 
                ("Lemon Juice   25\u00A2", 25),
                ("Can Opener   $1", 100),
                ("Salad Dressing   5\u00A2", 5),
                }

    # List of coins: each tuple is ("VALUE", value in cents)
    COINS = [ ("$2", 200),  
              ("$1", 100),  
              ("25\u00A2", 25),
              ("10\u00A2", 10),
              ("5\u00A2", 5),
              ("RETURN", "Return")
            ]


    def __init__(self):
        self.state = None  # current state
        self.states = {}  # dictionary of states
        self.event = ""  # no event detected
        self.amount = 0  # amount from coins inserted so far
        self.change_due = 0  # change due after vending
        # Build a list of coins in descending order of value
        values = []
        for k in self.COINS:
            values.append(self.COINS[k][1])
        self.coin_values = sorted(values, reverse=True)
        log(str(self.coin_values))

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
# However this is needed. In formal terms, this is an "abstract" class.
class State(object):
    """Superclass for states. Override the methods as required."""
    _NAME = ""
    def __init__(self):
        pass
    @property
    def name(self):
        return self._NAME
    def on_entry(self, machine):
        print("Vending Machine/n")
        pass
    def on_exit(self, machine):
        pass
    def update(self, machine):
        pass

# In the waiting state, the machine waits for the first coin
class WaitingState(State):
    _NAME = "waiting"
    def update(self, machine):
        if machine.event == 5:
            machine.total = coin_added(machine.event, machine.total)
        elif machine.event == 10:
            machine.total = coin_added(machine.event, machine.total)
        elif machine.event == 25:
            machine.total = coin_added(machine.event, machine.total)
        elif machine.event == 100:
            machine.total = coin_added(machine.event, machine.total)
        elif machine.event == 200:
            machine.total = coin_added(machine.event, machine.total)
        if machine.event == "CHIPS   $1.00" or machine.event == "CHOCOLATE   $2.50" or machine.event == "HEINEKEN   $0.05" or machine.event == "POP   $2.25" or machine.event == "JUICE   $1.25":
            machine.go_to_state ("item")
        if machine.event == 'Return':
            machine.go_to_state ('cancel')


# Print the product being delivered
class DeliverProductState(State):
    _NAME = "deliver_product"
    def on_entry(self, machine):
        # Deliver the product and change state
        machine.change_due = machine.amount - machine.PRODUCTS[machine.event][1]
        machine.amount = 0
        print("Buzz... Whir... Click...", machine.PRODUCTS[machine.event][0])
        if machine.change_due > 0:
            machine.go_to_state('count_change')
        else:
            machine.go_to_state('waiting')


# MAIN PROGRAM
if __name__ == "__main__":
    #define the GUI
    sg.theme('BluePurple')    # Keep things interesting for your users

    coin_col = []
    coin_col.append([sg.Text("ENTER COINS", font=("Helvetica", 24))])
    for item in VendingMachine.COINS:
        log(item)
        button = sg.Button(item, font=("Helvetica", 18))
        row = [button]
        coin_col.append(row)

    select_col = []
    select_col.append([sg.Text("SELECT ITEM", font=("Helvetica", 24))])
    for item in VendingMachine.PRODUCTS:
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
    vending.add_state(DeliverProductState())
    vending.add_state(CountChangeState())

    # Reset state is "waiting for coins"
    vending.go_to_state('waiting')

   # Checks if being used on Pi
    if hardware_present:
        # Set up the hardware button callback (do not use () after function!)
        key1.when_pressed = vending.button_action

    # The Event Loop: begin continuous processing of events
    # The window.read() function reads events and values from the GUI.
    # The machine.event variable stores the event so that the
    # update function can process it.
    # Now that all the states have been defined this is the
    # main portion of the main program.
    while True:
        event, values = window.read(timeout=10)
        if event != '__TIMEOUT__':
            log((event, values))
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        vending.event = event
        vending.update()

    window.close()
    print("Normal exit")
