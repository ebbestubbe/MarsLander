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
def main():
    surface_n = int(input())  # the number of points used to draw the surface of Mars.

    lx = []
    ly = []
    for i in range(surface_n):
        # land_x: X coordinate of a surface point. (0 to 6999)
        # land_y: Y coordinate of a surface point. By linking all the points together in a sequential fashion, you form the surface of Mars.
        land_x, land_y = [int(j) for j in input().split()]
        lx.append(land_x)
        ly.append(land_y)
    eprint(lx)
    eprint(ly)
    #get the flat land indices(DOES NOT ACCOUNT FOR 3 HORIZONTAL POINTS IN A ROW)
    flat_ind = []
    for i in range(surface_n-1):
        if(ly[i] == ly[i+1]):
            flat_ind.append([i, i+1])
    x0 = lx[flat_ind[0][0]]
    x1 = lx[flat_ind[0][1]]
    
    x_mid = x0 +(x1-x0)/2
        
    
    flaty = ly[flat_ind[0][0]]
    
    #State = namedtuple("State", "x y vx vy fuel angle thrust")
    
    g = -3.711
    #parameters required for landing (PID)
    
    state_list_actual = []
    roundNumber = 0
    
    control_list = []
    
    #Make a list of random commands
    for i in range(300):
        #angle_rand = rnd.randrange(-90,91)
        #thrust_rand = rnd.randrange(0,5)
        angle_rand = 0
        thrust_rand = 3
        control_list.append([angle_rand, thrust_rand])

    while True:

        x, y, vx, vy, fuel, rotate, power = [int(i) for i in input().split()]
        state_curr = State(x,y,vx,vy,fuel,rotate,power)
        state_list_actual.append(state_curr)
        
            
        height = y - flaty

        error_comb_min = 100000000
        time_sum = 0
        time_max = 0.14
        
        #Keep optimizing while we still have time
        while(time_sum < time_max):
            time_start = timeit.default_timer()
            
            #The absolute index of the perturbed control:
            to_perturb = rnd.randrange(roundNumber,roundNumber+30)
            
            #The perturbed control is just taken at random, regardless of thrust/angle restrictions
            control_perturb = [rnd.randrange(-90,91),rnd.randrange(0,5)]
            
            #Make a list of the future states in 'state_list_proj', keep iterating until the last one is no longer valid
            state_new = state_propagate_forward(state_curr,control_list[roundNumber])
            state_list_proj = [state_new]
            k=1
            while(checkvalidstate(state_list_proj[k-1],lx,ly)):
                if(roundNumber+k == to_perturb):
                    state_new = state_propagate_forward(state_list_proj[k-1],control_perturb)
                else:
                    state_new = state_propagate_forward(state_list_proj[k-1],control_list[roundNumber+k])
                state_list_proj.append(state_new)
                k+=1
            #If very close to landing -> 'manual' landing
            if(k<5):
                print(0,4)
                
            end_x = state_list_proj[-2].x
            end_y = state_list_proj[-2].y
            end_vx = state_list_proj[-2].vx
            end_vy = state_list_proj[-2].vy
            
            error_x = math.sqrt((end_x - x_mid)**2)
            
            if(x>x0 and x <x1):
                error_x *= 0.2
            
            error_y = math.sqrt((end_y - flaty)**2)
            

            vx_sp = 15 #vx_setpoint
            if(abs(end_vx) > vx_sp):
                error_vx = math.sqrt((abs(end_vx) - vx_sp)**2)
            else:
                error_vx = 0
                
            vy_sp = -20
            if(end_vy < vy_sp):
                error_vy = math.sqrt((end_vy - vy_sp)**2)
            else:
                error_vy = 0
                
            error_x*=1
            error_y*=0.1
            error_vx*=15
            error_vy*=20
            
            error_comb = error_x + error_y + error_vx + error_vy
            
            #If the new error is better, use the new 'solution'
            if(error_comb < error_comb_min):
                '''
                eprint("\n")
                eprint(control_perturb)
                eprint("end_x: " + str(end_x) + "; error_x:     " + str(error_x))
                eprint("end_y: " + str(end_y) + "; error_y:     " + str(error_y))
                eprint("end_vx: " + str(end_vx) + "; error_vx:  " + str(error_vx))
                eprint("end_vy: " + str(end_vy) + "; error_vy:  " + str(error_vy))
                eprint("error_comb:                             " + str(error_comb))
                '''
                error_comb_min = error_comb
                control_list[to_perturb] = control_perturb
            
            time_stop = timeit.default_timer()
            time_sum += time_stop-time_start
        #When we are done improving, just output the next control in the list
        roundNumber+=1
        print(control_list[roundNumber][0],control_list[roundNumber][1])



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
    main()

