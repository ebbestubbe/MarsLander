# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 19:56:25 2017

@author: stubb
"""
import sys
import codinggame
from time import sleep
import io
import numpy as np

class referee():
    def __init__(self,level):
        self._turn = 0 #The turn number for the current turn, changes each call in the game
        self._lvl = level #Level specific information 
        self._n_init_input = int(self._lvl[0]) + 1 # Number of lines expected in the initial input wave
        self._counter_init_input = 0
        self._rocketstate = string_to_state(self._lvl[-1])
        #self._turn_input = 1#Number of lines expected every turn
        self._lx = [] #land x and y to check if the state is valid
        self._ly = []

    
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
        if(self._turn> 10):
            sys.exit()
        s = codinggame.State(self._rocketstate[0],self._rocketstate[1],self._rocketstate[2],self._rocketstate[3],self._rocketstate[4],self._rocketstate[5],self._rocketstate[6])
        if(codinggame.checkvalidstate(s))
        if(self._counter_init_input < self._n_init_input):
            codinggame.eprint("sending info number: " + str(self._counter_init_input))
            #load the land data for checking state validity
            self._counter_init_input += 1

            if(self._counter_init_input > 1):
                land_x,land_y = [int(j) for j in self._lvl[self._counter_init_input-1].split()]
                self._lx.append(land_x)
                self._ly.append(land_y)
            
            return self._lvl[self._counter_init_input-1]
        else:
            codinggame.eprint("            NEW ROUND DIVIDER!!          ")
            self._turn += 1
            return state_to_string(self._rocketstate)
    
    def engineoutput(self,angle,thrust):
        #codinggame.eprint(self._rocketstate)
        
        newstate = codinggame.state_propagate_forward(self._rocketstate,[angle,thrust])
        self._rocketstate = newstate
        valid = codinggame.checkvalidstate(newstate,self._lx,self._ly)
        
#Takes a bunch of ints, load them into a gamestate
def string_to_state(string):
    x,y,vx,vy,fuel,rotate,power = [int(j) for j in string.split()]
    state = codinggame.State(x,y,vx,vy,fuel,rotate,power)
    return state
    
#takes a state, outputs a string
def state_to_string(s):
    string = map(int,np.around([s.x,s.y,s.vx,s.vy,s.fuel,s.rotate,s.power]))
    
    #codinggame.eprint("state to string:")
    string = map(str,string)
    string = ' '.join(string)
    #codinggame.eprint(string)
    return string
    
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