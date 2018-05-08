# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:18:48 2017

@author: TWang

Heigh_Analysis 5.0

GUI

"""

import scipy.io as scio  
import numpy as np
import math

dataFile = r"D:\MatlabProject\Single-View-Metrology-master\All_Parameters_test8.mat" 
data = scio.loadmat(dataFile)  

#==============================================================================
# print ("data['Hxy']: ", data['Hxy'])
# print ("data['Hxz']: ", data['Hxz'])
# print ("data['Hyz']: ", data['Hyz'])
# 
# print ("data['Origin']: ", data['Origin'])
# print ("data['ProjectionMatrix']: ", data['ProjectionMatrix'])
# print ("data['X_O']: ", data['X_O'])
# print ("data['Y_O']: ", data['Y_O'])
# print ("data['Z_O']: ", data['Z_O'])
# print ("data['len_X_O']: ", data['len_X_O'])
# print ("data['len_Y_O']: ", data['len_Y_O'])
# print ("data['len_Z_O']: ", data['len_Z_O'])
# print ("data['scale_X']: ", data['scale_X'])
# print ("data['scale_Y']: ", data['scale_Y'])
# print ("data['scale_Z']: ", data['scale_Z'])
# 
# print ("data['vX']: ", data['vX'])
# print ("data['vY']: ", data['vY'])
# print ("data['vZ']: ", data['vZ'])
#==============================================================================


#Load All parameters
'''step 0 preppare some parameters'''
Vanishing_X = data['vX']
Vanishing_Y = data['vY']

Vanishing_X = np.squeeze(Vanishing_X)
Vanishing_Y = np.squeeze(Vanishing_Y)

t0 = data['Z_O']
b0 = data['Origin']

t0 = np.squeeze(t0)
b0 = np.squeeze(b0)

print("b0 = ", b0)
print("t0 = ", t0)

Reference_Height = data['len_Z_O']
Reference_Height = np.squeeze(Reference_Height)

print("Reference Height =", Reference_Height)

Vz = data['vZ']
Vz = np.squeeze(Vz)

#height analysis

'''step 1 : define Vx-Vy horizon line'''
horizon = np.cross(Vanishing_Y,Vanishing_X)
length = math.sqrt(math.pow(horizon[0],2) + math.pow(horizon[1],2))
horizon = horizon/length

print("Horizon =", horizon)

# selected object coordinate in image 
#==============================================================================
# b = [x1,y1,1]
# r = [x2,y2,1]
#==============================================================================

b = [656, 42, 1]
r = [656, 135, 1]

b = np.asarray(b)
r = np.asarray(r)

print("b =", b)
print("r =", r)


''' step2 connect b0, b as line1 '''
line1 = np.cross(b0,b)

print("line1 =", line1)

'''step3 line1 and horizon intersect at V'''
v = np.cross(line1, horizon)
v = v/v[2]

print("v =" ,v)

'''step 4 connect v, t0 as line2'''

line2 = np.cross(v.T, t0) # result is 3*1, need 1*3

print("line2 =" ,line2)

'''step5 line2 and tb intersect at t '''
vertical_line = np.cross(r, b)

t = np.cross(line2, vertical_line) # matlab is 1*3 

t = t/t[2]

print("vertical_line =" ,vertical_line)
print("t  =" ,t )

'''step 6 calculate Height '''

np.square(r-b)

height = Reference_Height * math.sqrt(np.sum(np.square(r-b))) * math.sqrt(np.sum(np.square(Vz.T-t))) / ((math.sqrt(np.sum(np.square(t.T-b)))) * math.sqrt(np.sum(np.square(Vz.T-r))))

print("height = ", height)
