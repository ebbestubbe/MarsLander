# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 19:56:25 2017

@author: stubb
"""
import sys
import codinggame
#from subprocess import Popen, PIPE, STDOUT
import subprocess as sp
from time import sleep
#import StringIO
import io
#import winpexpect
'''look into: 
    
    http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
    http://stackoverflow.com/questions/6346650/keeping-a-pipe-to-a-process-open
    stringIO to write/read from a file-like object?

'''
class referee():
    def __init__(self,level):
        self._turn = 0 #The turn number for the current turn, changes each call in the game
        self._lvl = level #Level specific information 
        self._n_init_input = int(self._lvl[0]) + 1 # Number of lines expected in the initial input wave
        self._counter_init_input = 0
        self._rocketstate = self._lvl[-1]
        #self._turn_input = 1#Number of lines expected every turn
    
    #starts the codinggame code
    def play(self):
        codinggame.eprint("running own engine")
        codinggame.main(inputmethod = self.engineinput, outputmethod = self.engineoutput)
    
    #When the game requests input() via the inputmethod, this method returns the stuff it needs.
    #This is done in place of the input() method, for relatively seamless integration
    #For the initial 'self._n_init_input' number of calls, the initial state is inputted.
    #For the next infinity calls, the output is the rocket state(the while(True): input required)
    def engineinput(self):
        #For the first turn, count up to the number of expected init inputs, and return them
        if(self._counter_init_input < self._n_init_input):
            codinggame.eprint("sending info number: " + str(self._counter_init_input))
            self._counter_init_input += 1
            return self._lvl[self._counter_init_input-1]
        else:
            self._turn += 1
            x,y,vx,vy,fuel,rotate,power = [int(j) for j in self._rocketstate.split()]
            inputstring = str(int(x)) + " " + str(int(y)) + " " + str(int(vx)) + " " + str(int(vy)) + " " + str(int(fuel)) + " " + str(int(rotate)) + " " + str(int(power)) 
            return inputstring
 
    
    def engineoutput(self,angle,thrust):
        #remember to split it into ints, and not just output the long string
        #codinggame.eprint(self._rocketstate)
        x,y,vx,vy,fuel,rotate,power = [int(j) for j in self._rocketstate.split()]
        #y = int(self._rocketstate[1])
        #vx = int(self._rocketstate[2])
        #vy = int(self._rocketstate[3])
        #fuel = int(self._rocketstate[4])
        #rotate = int(self._rocketstate[5])
        #power = int(self._rocketstate[6])
        codinggame.eprint("state unpacking:")
        codinggame.eprint(x,y,vx,vy,fuel,rotate,power)
        state = codinggame.State(x,y,vx,vy,fuel,rotate,power)
        newstate = codinggame.state_propagate_forward(state,[angle,thrust])
        
        newx = newstate.x
        newy = newstate.y
        newvx = newstate.vx
        newvy = newstate.vy
        newfuel = newstate.fuel
        newrotate = newstate.rotate
        newpower = newstate.power
        codinggame.eprint(self._rocketstate)
        self._rocketstate = str(newx) +" "+ str(newy) +" "+ str(newvx) +" "+ str(newvy) +" "+ str(newfuel) +" "+ str(newrotate) +" "+ str(newpower)
        codinggame.eprint(self._rocketstate)
        #Set the internal gamestate to this new state
        
if __name__ == "__main__":
    level01 = ["7",
           "0 100",
           "1000 500",
           "1500 1500",
           "3000 1000",
           "4000 150",
           "5500 150",
           "6999 800",
           "2500 2700 0 0 550 0 0"]
    
    ref = referee(level01)
    ref.play()