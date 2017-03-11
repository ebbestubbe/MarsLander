# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 19:56:25 2017

@author: stubb
"""
import sys
#from subprocess import Popen, PIPE, STDOUT
import subprocess as sp
from time import sleep

'''look into: 
    
    http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
    http://stackoverflow.com/questions/6346650/keeping-a-pipe-to-a-process-open
    stringIO to write/read from a file-like object?

'''
def main():
    #game = Popen(["python","codinggame.py"], stdin=PIPE, stdout=PIPE)
    #out = game.communicate(input = "7".encode())
    '''
    lvl = level01()
    print(lvl)
    surface_n = int(lvl[0])
    print(surface_n)
    for i in range(surface_n):
        land_x,land_y = [int(j) for j in lvl[i+1].split()]
        print(land_x,land_y)
    '''
    lvl = level01()
    
    print("opening process")
            
    game = sp.Popen(["python","codinggame.py"], stdin=sp.PIPE,stdout = sp.PIPE)
    
    print("sending n surfaces")
    surface_n = lvl[0]
    game.stdin.write(surface_n.encode())
    return
    print("sending the land params")
    for i in range(int(surface_n)):
        print("sending " + str(i) + " out of " + str(surface_n))
        game.stdin.write(lvl[i+1].encode())
    
    print("sending initial ship config")
    game.stdin.write(lvl[-1].encode())
    print("waiting 1000 ms")
    sleep(1)
    print("loading the first status")
    output = game.stdout.readline()
    print("done reading output")
    print("output: " + str(output.decode()))
    #print(out)
    #print(err)
    #print("message sent1")
    #out,err = game.communicate(input = '7'.encode())
    #print(out)
    #print(err)
    #print("message sent2")
    
    #result = game.returncode
    #print(result)

def level01():
    level = []
    #surface
    level.append("7") 
    #land (x,y)
    level.append("0 100")
    level.append("1000 500")
    level.append("1500 1500")
    level.append("3000 1000")
    level.append("4000 150")
    level.append("5500 150")
    level.append("6999 800")
    #initial state:
    level.append("2500 2700 0 0 550 0 0")
    return level
    
if __name__ == "__main__":
    main()