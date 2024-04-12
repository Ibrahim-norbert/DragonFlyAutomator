# -*- coding: utf-8 -*-
import numpy as np
import re, sys

# this script writes a g-code file for crystal screening.
# you must prepare a calibration file before running this
# an example of such a file is printed if the format is wrong
# Procedure: use bCNC to center on the top right drop and set this as zero
# go to the bottom right drop and record the xyz coordinates (br)
# go to the top left drop and record the xyz coordinates (tl)
# go to the bottom left drop and record the xyz coordinates (bl)
# decide on the number of images per drop and their z-spacing 
# (at higher magnification, you'll want more closely spaced images)
# the first image is at 20% of the total translation in Z below the calculated bottom of the drop

try:
    with open(sys.argv[1]) as f:
        nx=int((f.readline()).split('#', 1)[0])
        ny=int((f.readline()).split('#', 1)[0])
        tl=np.array(map(float,(re.findall(r'\S+', (f.readline()).split('#', 1)[0]))))
        br=np.array(map(float,(re.findall(r'\S+', (f.readline()).split('#', 1)[0]))))
        bl=np.array(map(float,(re.findall(r'\S+', (f.readline()).split('#', 1)[0]))))
        zstep=float((f.readline()).split('#', 1)[0])
        nimages=int((f.readline()).split('#', 1)[0])
except:
    print'The configuration file was missing or the format was not right'
    print'usage: python plate_scan.py config_file.txt >plate_scan.gcode'
    print 'Tthe configuration file should look something like this:'
    print'  12                # number of wells in the x '
    print'  8                 # number of wells in y '
    print'  98.8  -1.5  0.4   # coordinates of the top left drop'
    print'   0.7  62.9  0.5   # coordinates of the bottom right drop'
    print'  99.5  61.0  1.1   # coordinates of the bottom left drop'
    print'  0.3               # default image spacing in z'
    print'  4                 # default number of images per drop'

f_out=open(sys.argv[2],'w')
alphabet=('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

print 'preparing gcode for a ',nx,' x ',ny,' plate'
print 'default z-spacing = ',zstep
tmpx=raw_input("new spacing (return to keep default):")
if tmpx!="":zstep=float(tmpx)
print 'default number of images per drop = ',nimages
tmpx=raw_input("new number (return to keep default):")
if tmpx!="":nimages=int(tmpx)
print 'using: ', zstep,nimages

# in the calculation below, the coordinates of each drop are first calculated based on tl and br.
# Then the bl coordinate is used to make a secondary, correction as needed.

corx=tl/float(nx-1)
cory=br/float(ny-1)

#cor is the correction matrix to account for misalignment of the plate vs. translation directions in x,y,z
cor=np.array(([corx[0],cory[0],0],
             [corx[1],cory[1],0],
             [corx[2],cory[2],0]))

blpred=np.dot(cor,np.array(((nx-1),(ny-1),0)))  #predicted position of bl based on tl and br
fixit=(bl-blpred)/float((nx-1)*(ny-1)) # this is the correction based on bl 

dropnum=1
for dropy in range(ny):
    for dropx in range((nx-1),-1,-1):
        drop=np.array((dropx,dropy,0))  # counting reversed so drops are in the right order A1 - A12, B1 - B12, ...
        ans=np.dot(cor,np.array(drop))
        anscor=ans+fixit*(dropx*dropy) # predicted position of the bottom end of the drop)
       # print 'drop: ',(dropnum),' (',(alphabet[dropy]),(12-dropx),') : ',round(anscor[0],5),round(anscor[1],5),round(anscor[2],5)
        print 'drop %3d (%1s%2d) %7.3f %7.3f %7.3f \n'%(dropnum,(alphabet[dropy]),(12-dropx),round(anscor[0],5),round(anscor[1],5),round(anscor[2],5))
	dropnum+=1
        f_out.write(str('g0 x %7.3f y %7.3f z %7.3f \n'%(round(anscor[0],5),round(anscor[1],5),round(anscor[2],5))))  
	# this part is confusing.  top and bottom refer to the position of the plate, not the scope
	# at the top, the plate is close to the scope and the bottom of the drop is in focus  and vise versa
        top=anscor[2]+((nimages-1)*0.3*zstep) 
        bottom=anscor[2]-((nimages-1)*0.7*zstep) - zstep/2 # zstep/2 is subtracted from the bottom so python loops through nimages not nimages-1 
        for dropz in np.arange(top,bottom,(-1.*zstep)):
            f_out.write(str('g0 z %7.3f \n'%(round(dropz,5))))
	    f_out.write(str('g4 p 0.4 \n'))
            f_out.write(str('m3 \n'))
            f_out.write(str('g4 p 0.1 \n'))
            f_out.write(str('m5 \n'))
            f_out.write(str('g4 p 0.4 \n'))
	# take an out-of-focus image at the end of the series (1 mm below from last one)
	f_out.write(str('g0 z %7.3f \n'%(round((top+1.),5))))
        f_out.write(str('g4 p 0.4 \n'))
        f_out.write(str('m3 \n')) 
        f_out.write(str('g4 p 0.1 \n'))
        f_out.write(str('m5 \n'))
        f_out.write(str('g4 p 0.4 \n'))
f_out.write(str('g0 x0 y0 z0 \n')) 
print 'G-code has been written to %s'%(sys.argv[2])
