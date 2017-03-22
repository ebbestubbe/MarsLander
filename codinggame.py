import sys
import math
import numpy as np
import random as rnd
import timeit
from collections import namedtuple

State = namedtuple("State", "x y vx vy fuel rotate power")

'''
stupid stuff:
    Angle and thrust is chosen from the whole range.
        Everything outside [-15,15][-1,1] are degenerate in the current solution, yet they might yield better solutions later

    The random perturbed index is chosen within the next 30 controls.
        The short sightedness makes it very likely that it will do something to the final solution
        Makes it impossible to plan far ahead
        Maybe change this to be within the longest/shortest/average sequence length until now?
    
    Error function is just arbitrarily chosen and hacked.
        ...Yep :[

Improvements:
    Try all possible valid combinations, use the best, or use some SA
        Then what about the currently degenerate, but in the future not degenerate solutions?
        
    Choose multiple controls simultaniously to improve
    
    Choose controls from the whole list
    
    Some states are obviously better, i.e. all errors are improved -> automatically choose those

Maybe even print and plot some outputs to get better understanding


Other strategies:
    Krotov-like - > requires (correct!) backprop algorithm
    
    Sequences of controls, inspired by dimension reduction. sequences of locked controls, defined by their (angle,thrust,seqlength)
        Simple enough scheme to propagate by integration instead of explicitly propagating
        Low dimensional enough to use some sort of optimizer?

    
'''
def main(inputmethod = input, outputmethod = print):
#def main():
    surface_n = int(inputmethod())  # the number of points used to draw the surface of Mars.
    lx = []
    ly = []
    for i in range(surface_n):
        # land_x: X co<ordinate of a surface point. (0 to 6999)
        # land_y: Y coordinate of a surface point. By linking all the points together in a sequential fashion, you form the surface of Mars.
        land_x, land_y = [int(j) for j in inputmethod().split()]
        #eprint(land_x,land_y)
        lx.append(land_x)
        ly.append(land_y)
    eprint("land in script:")
    eprint("lx: " + str(lx))
    eprint("ly: " + str(ly))
    #get the flat land indices(DOES NOT ACCOUNT FOR 3 HORIZONTAL POINTS IN A ROW)
    flat_ind = []
    for i in range(surface_n-1):
        if(ly[i] == ly[i+1]):
            flat_ind.append([i, i+1])
    x0 = lx[flat_ind[0][0]]
    x1 = lx[flat_ind[0][1]]
    
    x_mid = x0 +(x1-x0)/2
        

    flaty = ly[flat_ind[0][0]]
    
    roundNumber = 0
    a = [-72, 36, 76, -44, 77, -33, 78, 15, 26, 87, 14, -64, -41, -33, -78, 87, -37, 37, -90, -41, 30, 0, 45, 6, -45, 10, 54, -80, -66, -18, 13, 20, 30, -43, 25, -62, -13, -47, 76, -83, 73, -46, -50, -80, 74, -51, -62, 81, -67, 56, -60, 10, -33, -12, 63, 48, 2, 31, -8, -31, 81, -3, -47, -28, 43, -2, 16, -19, 63, 9, 17, 34, -66, 26, 2, 14, -49, -23, -58, 61, 53, -30, 83, -18, -25, 59, -10, -38, 61, -66, 38, 20, -54, -56, 75, 80, 89, 29, -52, 31, 6, 42, -3, 42, -28, -22, -70, 73, 67, -90, 90, 57, 59, 78, -70, 75, 71, 35, 42, 71, 23, 3, -75, 17, -84, 8, 74, -53, 72, 53, -8, 62, -16, -77, -19, 45, 16, -82, -22, -89, -1, -26, 31, -14, -25, -69, 66, -88, 18, 33, -34, -25, -3, -6, 49, 90, 49, 52, -90, -35, -7, 57, 24, -3, -2, -88, -36, 0, -78, -2, 44, 24, -5, -82, 66, -30, -68, 17, 74, -57, 71, 20, -38, 70, -43, -87, -39, 77, 8, 13, 7, 46, 85, -70, -13, -76, 49, -71, -67, 0, 83, -7, 72, 64, 77, -37, -83, -29, 32, 42, 28, 47, 18, -15, -16, 8, -60, 38, 72, 25, -67, 88, -18, 19, 36, 2, 39, 4, -16, -10, -84, -65, -35, -46, 57, -77, 25, 31, 21, -14, -33, 73, -37, -88, 53, 65, 39, 33, 5, -23, -24, 8, -53, 64, 87, 11, 82, 66, 9, -1, 48, 36, 10, 19, 7, 24, 12, -15, -49, 73, -46, 33, -41, 48, 39, -6, -28, 4, -36, -88, -16, 70, 86, -79, 34, 75, -52, 79, 23, -76, -48, 27, -50, 58, 48, -8, -60, -36, 60, -83]
    t = [1, 1, 4, 0, 3, 3, 3, 0, 1, 1, 4, 4, 4, 0, 2, 1, 1, 1, 0, 3, 4, 3, 2, 3, 2, 0, 3, 2, 4, 1, 1, 3, 0, 0, 4, 2, 2, 0, 0, 2, 3, 3, 4, 4, 4, 2, 2, 0, 3, 2, 0, 3, 1, 0, 4, 3, 1, 4, 0, 2, 1, 1, 1, 0, 3, 3, 1, 0, 1, 3, 1, 2, 3, 1, 4, 0, 3, 2, 4, 0, 1, 2, 4, 4, 0, 3, 4, 4, 2, 2, 2, 3, 1, 0, 1, 3, 4, 2, 1, 0, 3, 3, 2, 1, 1, 3, 4, 3, 3, 3, 3, 1, 1, 4, 4, 0, 1, 0, 4, 4, 3, 2, 2, 1, 1, 2, 0, 2, 1, 2, 3, 1, 4, 4, 2, 3, 4, 4, 0, 1, 0, 0, 4, 4, 4, 2, 1, 2, 0, 4, 1, 2, 2, 1, 0, 4, 4, 3, 0, 0, 3, 2, 2, 3, 1, 2, 2, 1, 0, 4, 0, 3, 0, 0, 4, 2, 4, 4, 1, 2, 4, 0, 4, 1, 3, 3, 4, 2, 0, 4, 0, 0, 3, 1, 1, 4, 0, 0, 4, 2, 4, 0, 3, 2, 4, 4, 0, 1, 1, 0, 2, 2, 1, 1, 2, 4, 4, 4, 1, 1, 4, 2, 1, 0, 0, 1, 0, 0, 1, 1, 4, 3, 3, 1, 1, 0, 2, 1, 0, 3, 2, 1, 4, 2, 3, 0, 3, 3, 2, 0, 4, 2, 1, 0, 3, 1, 1, 1, 3, 2, 3, 2, 0, 3, 2, 0, 0, 4, 0, 1, 0, 3, 1, 2, 2, 2, 3, 0, 2, 3, 0, 1, 0, 4, 2, 1, 0, 2, 4, 3, 4, 0, 0, 3, 3, 4, 1, 0, 2, 1]
    while True:
        eprint("game requesting rocket state, roundnumber=" + str(roundNumber))
        x, y, vx, vy, fuel, rotate, power = [int(i) for i in inputmethod().split()]
        eprint(x,y,vx,vy,fuel,rotate,power)
        
        roundNumber+=1
        #print(control_list[roundNumber][0],control_list[roundNumber][1])
        eprint("using outputmethod: ")
        outputmethod(a[roundNumber-1],t[roundNumber-1])


def eprint(*args,**kwargs):
    print(*args, file=sys.stderr, **kwargs)

#takes a state s0, applies the control u, and returns s1
#states internal variables are floats, round() to compare with CodingGame states
def state_propagate_forward(s0,u):
    #Angle:
    #   error if under -90 or over 90
    #   clamp angle at +/-15 per turn
    assert(u[0] > -91 and u[0] < 91)
    if(u[0] - s0.rotate > 15):
        s1rotate = s0.rotate + 15
    elif(u[0] - s0.rotate < -15):
        s1rotate = s0.rotate - 15
    else:
        s1rotate = u[0]
        
    #Thrust
    #   if <0 or >4: give error
    #   clamp at +/- 1 per turn
    assert(u[1] > -1 and u[1] < 5)
    
    if(u[1] - s0.power > 1):
        s1power = s0.power + 1
    elif(u[1] - s0.power < -1):
        s1power = s0.power - 1
    else:
        s1power = u[1]
    
    #fuel
    #If not enough fuel:
    #   use the rest and set fuel to 0
    #   does not account for the +/- 1 rule for thrust
    if(s1power > s0.fuel):
        s1power = s0.fuel
        s1fuel = 0
    else:
        s1fuel = s0.fuel - s1power
        
    #x,y,vx,vy,fvx,fvy
            
    ax = -s1power*math.sin(s1rotate*math.pi/180)
    ay = s1power*math.cos(s1rotate*math.pi/180) - 3.711
    
    s1vx = s0.vx + ax
    s1vy = s0.vy + ay
    
    s1x = s0.x + (s1vx + s0.vx)/2
    s1y = s0.y + (s1vy + s0.vy)/2

    s1 = State(s1x, s1y, s1vx, s1vy, s1fuel, s1rotate, s1power)
    return s1

'''
BROKEN AS FUCK
#propagate s1 and u0 to state u0
#CLAMP OR DO NOT CLAMP ANGLES?, WHAT ABOUT FUEL?
def state_propagate_backward(s1,u):
    eprint("backpropagating with " + str(u))
    
    #Angle:
    #   error if under -90 or over 90
    #   clamp angle at +/-15 per turn
    assert(u[0] > -91 and u[0] < 91)
    if(u[0] - s1.rotate > 15):
        s0rotate = s1.rotate + 15
    elif(u[0] - s1.rotate < -15):
        s0rotate = s1.rotate - 15
    else:
        s0rotate = u[0]
        
    #Thrust
    #   if <0 or >4: give error
    #   clamp at +/- 1 per turn
    assert(u[1] > -1 and u[1] < 5)
    
    if(u[1] - s1.power > 1):
        s0power = s1.power + 1
    elif(u[1] - s1.power < -1):
        s0power = s1.power - 1
    else:
        s0power = u[1]
    
    #fuel
    #If not enough fuel:
    #   use the rest and set fuel to 0
    #   does not account for the +/- 1 rule for thrust
    if(s0power > s1.fuel):
        s0power = s1.fuel
        s0fuel = 0
    else:
        s0fuel = s1.fuel + s0power
        
    #x,y,vx,vy,fvx,fvy
            
    ax = -s0power*math.sin(s0rotate*math.pi/180)
    ay = s0power*math.cos(s0rotate*math.pi/180) - 3.711
    
    s0vx = s1.vx - ax
    s0vy = s1.vy - ay
    
    s0x = s1.x - (s0vx + s1.vx)/2
    s0y = s1.y - (s0vy + s1.vy)/2

    s0 = State(s0x, s0y, s0vx, s0vy, s0fuel, s0rotate, s0power)
    return s0
'''
#returns true if the state is valid
#returns false if the state is not valid
def checkvalidstate(state,lx,ly):
    #Check sorrounding box
    if(state.x < 0 or state.x > 6999):
        return False
    if(state.y < 0 or state.y > 2999):
        return False
    
    #check line segments
    #find which part of the landscape the ship is over, and the height
    i = 0
    while(state.x > lx[i]):
        i += 1
    height = ly[i-1] + (state.x - lx[i-1])*(ly[i] - ly[i-1])/(lx[i] - lx[i-1])
    if(state.y < height):
        return False
    return True

def trunc(num,borders):
    if(num < borders[0]):
        return borders[0]
    elif(num > borders[1]):
        return borders[1]
    else:
        return round(num)

if __name__=="__main__":
    eprint("calling __name__")
    #import sys
    #main()
    sys.exit(main())

'''
General documentation for the problem:
    States 's' currently encoded as a named tuple State(x,y,vx,vy,fuel,rotate,power)
    Controls 'u' an array [desired_angle, desired_thrust]
    
    Turn propagation goes like this:
        clamp rotation to be within 15 degrees of previous turn
        clamp shippower to be within -1/+1 of previous turn
        
        set acceleration,velocity and position:
            constant acceleration in y-direction from gravity.
            accelerations are directly added to this turns velocity.
            positions are averages of this turn and previous turns velocities
            
            ax = -s1power*math.sin(s1rotate*math.pi/180)
            ay = s1power*math.cos(s1rotate*math.pi/180) - 3.711
    
            s1vx = s0.vx + ax
            s1vy = s0.vy + ay
    
            s1x = s0.x + (s1vx + s0.vx)/2
            s1y = s0.y + (s1vy + s0.vy)/2
    

    The internal states are floating point numbers, but the values from input() are rounded to integers
    
    
    If we want to propagate from turn 'n' with constant acceleration:
        The running variable 'i' denotes the absolute turn number, 'i-n' is then the number of turns from 'n':
        by insertion we can find the velocity and position at state 'i'
        ax = cst
        
        vx_n = vx_{n-1} + ax
        vx_{n+1} = vx_n + ax = vx_{n-1} + 2*ax
        vx_{n+2} = vx_{n+1} + ax = vx_{n-1} + 3*ax
        ...
        vx_i = vx_{n-1} + (i-n+1)*ax
        
        x_n = x_{n-1} + (x_n + x_{n-1})/2
        x_{n+1} = x_n + (x_{n+1} + x_n)/2
        x_{n+2} = x_{n+1} + (x_{n+2} + x_{n+1})/2
        ...
        x_i = x_{n-1} + (i-n+1)*vx_{n-1} + (i-n+1)^2 * ax/2
        
'''