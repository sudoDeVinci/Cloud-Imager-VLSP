__author__ = 'Tadj Cazaubon'
__credits__ = ["Tadj Cazaubon"]


# TODO: Multiprocessing in read() function. 
# from multiprocessing.context import Process
import os
import gc
import cv2
import numpy as np
from numba import jit
from matplotlib import pyplot as plt
from datetime import datetime


def read(Blocked, Reference, cloudBGR, skyBGR, cloudHSV, skyHSV):
    """
    An assumption of this function is that all images are of the same size.
    As to not raise an error

    We read in our images and convert them to HSV
    """


    blockedImage = cv2.imread(Blocked)
    blockedImage = cv2.resize(blockedImage,(100, 100))
    blockedImageHSV = cv2.cvtColor(blockedImage,cv2.COLOR_BGR2HSV)

    

    referenceImage = cv2.imread(Reference)
    referenceImage = cv2.resize(referenceImage,(100, 100))
    referenceImageHSV = cv2.cvtColor(referenceImage,cv2.COLOR_BGR2HSV)

    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#

    """
    First we make a mask for red colours
    We'll use Red to represent Clouds
    Red can have hue values between 0-10, but also 170-180
    """

    u_b_red1HSV = np.array([10, 255, 255])
    l_b_red1HSV = np.array([0, 30, 30])

    u_b_red2HSV = np.array([180, 255, 255])
    l_b_red2HSV = np.array([170, 50, 50])

    maskOneRedHSV = cv2.inRange(blockedImageHSV,l_b_red1HSV,u_b_red1HSV)
    maskTwoRedHSV = cv2.inRange(blockedImageHSV,l_b_red2HSV,u_b_red2HSV)

    redMaskHSV = cv2.bitwise_or(maskOneRedHSV,maskTwoRedHSV)

    """
    Now we do the same for Black.
    We'll use a range of black to represent The Sky
    """

    u_b_blackHSV = np.array([180, 255,30])
    l_b_blackHSV = np.array([0, 0, 0])

    blackMaskHSV = cv2.inRange(blockedImageHSV,l_b_blackHSV,u_b_blackHSV)

    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#

    """
    Apply masks and create HSV versions of our images.
    """

    cloudImageHSV = cv2.bitwise_and(referenceImageHSV,referenceImageHSV,mask = redMaskHSV)
    skyImageHSV = cv2.bitwise_and(referenceImageHSV,referenceImageHSV,mask = blackMaskHSV)

    cloudImageBGR = cv2.cvtColor(cloudImageHSV,cv2.COLOR_HSV2BGR)
    skyImageBGR =  cv2.cvtColor(skyImageHSV,cv2.COLOR_HSV2BGR)

    """
    cv2.imshow("cloudBGR", cloudImageBGR)
    cv2.imshow("skyBGR", skyImageBGR)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """

    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#
    
    """
    Delete so my celeron laptop doesnt explode
    Hurts speed slightly but helps to be able to run on lower end devices.
    """
    del u_b_red1HSV 
    del l_b_red1HSV 
    del u_b_red2HSV 
    del l_b_red2HSV 
    del maskOneRedHSV 
    del maskTwoRedHSV 
    del redMaskHSV 
    del u_b_blackHSV 
    del l_b_blackHSV 
    del blackMaskHSV
    gc.collect()

    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#

    """
    We iterate through our two masked images using zip() and take note of the values
    of pixels that aren't true black (0,0,0) and adding them to binary search trees
    """

    cbgrch = cv2.split(cloudImageBGR)

    sbgrch = cv2.split(skyImageBGR)

    chsvch = cv2.split(cloudImageHSV)

    shsvch = cv2.split(skyImageHSV)

    @jit(nopython=True, cache=True)
    def readoutbgr(bgr, nparray):
        b, g, r = bgr
        for x,y,z in zip(b,g,r):
            for i,o,u in zip(x,y,z):
                if i!= 0 or o!=0 or u!=0:
                    if i and o and u:
                        nparray[0][i] += 1
                        nparray[1][o] += 1
                        nparray[2][u] += 1
        return nparray
    
    @jit(nopython=True, cache=True)
    def readouthsv(hsv, nparray):
        h, s, v = hsv
        for x,y,z in zip(h,s,v):
            for i,o,u in zip(x,y,z):
                if u!=0:
                    nparray[0][i] += 1
                    nparray[1][o] += 1
                    nparray[2][u] += 1
        return nparray
    

    cloudBGR = readoutbgr(cbgrch, cloudBGR)
    skyBGR = readoutbgr(sbgrch, skyBGR)

    skyHSV = readouthsv(shsvch, skyHSV)
    cloudHSV = readouthsv(chsvch, cloudHSV)

    return cloudBGR, skyBGR, cloudHSV, skyHSV

#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#

"""
Generate BGR and HSV Bar Graphs
"""

def distributionBarGraphGenerator(cloudBGR, skyBGR, cloudHSV, skyHSV , graphFolder, bins):

    bgrGraphsavePath = os.path.join(graphFolder,'BGRBarGraph-esp.png')
    hsvGraphsavePath = os.path.join(graphFolder,'HSVBarGraph-esp.png')

    cloudBlues,cloudGreens,cloudReds = cloudBGR
    skyBlues,skyGreens,skyReds = skyBGR

    skyHues, skySats, skyValues = skyHSV
    cloudHues, cloudSats, cloudValues = cloudHSV


    print(f"> There are: \n └  {sum(cloudBlues)} cloud datapoints\n └  {sum(skyBlues)} sky datapoints")

    print("\n> Creating BGR Bar Graph ...")
    fig1,axes1 = plt.subplots(nrows = 3,ncols = 1)
    axes1 = axes1.flatten()

    axes1[0].bar(bins, skyBlues, color = 'blue',alpha= 0.3,label = 'Sky Blues')
    axes1[0].bar(bins, cloudBlues, color = 'purple',alpha = 0.3,label = 'Cloud Blues')
    axes1[0].set_xlabel('BGR Blues (0 - 255)')
    axes1[0].set_ylabel('frequency')
    axes1[0].legend(loc="upper left")
    del skyBlues,cloudBlues

    axes1[1].bar(bins, cloudGreens, color = 'green',alpha= 0.3,label = 'Cloud Greens')
    axes1[1].bar(bins, skyGreens, color = 'yellow',alpha = 0.3,label = 'Sky Greens')
    axes1[1].set_xlabel('BGR Greens (0 - 255)')
    axes1[1].set_ylabel('frequency')
    axes1[1].legend(loc="upper left")
    del cloudGreens,skyGreens

    axes1[2].bar( bins, cloudReds,color = 'red',alpha= 0.3,label = 'Cloud Reds')
    axes1[2].bar(bins, skyReds, color = 'purple',alpha = 0.3,label = 'Sky Reds')
    axes1[2].set_xlabel('BGR Reds(0 - 255)')
    axes1[2].set_ylabel('frequency')
    axes1[2].legend(loc="upper left")
    del cloudReds,skyReds
    fig1.tight_layout()
    plt.title("BGR Colour Frequency")
    plt.savefig(bgrGraphsavePath)
    fig1.clf()
    plt.close("all")
    gc.collect()
    print(" └ BGR Bar Graph created.")
    del fig1
    gc.collect()

    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#

    print(" \n> Creating HSV Graph ...")
    fig2,axes2 = plt.subplots(nrows = 3,ncols = 1)
    axes2 = axes2.flatten()

    axes2[0].bar(bins, cloudHues, color = 'purple',alpha = 0.3,label = 'Cloud Hues')
    axes2[0].bar(bins, skyHues, color = 'blue',alpha= 0.3,label = 'Sky Hues')
    axes2[0].set_xlabel('HSV Hues (0 - 255)')
    axes2[0].set_ylabel('frequency')
    axes2[0].legend(loc="upper left")
    del skyHues,cloudHues

    axes2[1].bar(bins, cloudSats, color = 'green',alpha= 0.3,label = 'Cloud Saturation')
    axes2[1].bar(bins, skySats, color = 'yellow',alpha = 0.3,label = 'Sky Saturation')
    axes2[1].set_xlabel('HSV Saturation (0 - 255)')
    axes2[1].set_ylabel('frequency')
    axes2[1].legend(loc="upper left")
    del skySats,cloudSats

    axes2[2].bar(bins, cloudValues, color = 'red',alpha= 0.3,label = 'Cloud Value')
    axes2[2].bar(bins, skyValues, color = 'purple',alpha = 0.3,label = 'Sky Value')
    axes2[2].set_xlabel('HSV Value (0 - 255)')
    axes2[2].set_ylabel('frequency')
    axes2[2].legend(loc="upper left")
    del skyValues,cloudValues

    fig2.tight_layout()
    plt.title("HSV Colour Frequency")
    plt.savefig(hsvGraphsavePath)
    fig2.clf()
    plt.close("all")

    print(" └ HSV Graph created.")
    del fig2
    gc.collect()

#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#

"""
Make sure filenames are synced before running
"""
def filesync(Blocked, Reference):
    for (_, _, referenceImages), (_, _, blockedImages) in zip(os.walk(Reference), os.walk(Blocked)):
        for refImage, blockedImage in zip(referenceImages, blockedImages):
            if refImage != blockedImage:
                print("Image desync!")
                return False

    print("Files Synced")
    return True

#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#

def main(Blocked, Reference, Graphs):
    """
    Space for important variables
    """

    bins = [*range(0,256,1)]

    
    cloudBGR = np.array([np.array([0 for n in range(0,256)]) for i in range(3)])
    skyBGR = np.array([np.array([0 for n in range(0,256)]) for i in range(3)])
    cloudHSV = np.array([np.array([0 for n in range(0,256)]) for i in range(3)])
    skyHSV = np.array([np.array([0 for n in range(0,256)]) for i in range(3)])
   

    for (refroot, _, referenceImages), (blockroot, _, blockedImages) in zip(os.walk(Reference), os.walk(Blocked)):
        for refImage, blockedImage in zip(referenceImages, blockedImages):
            refPath = os.path.join(refroot, refImage)
            blockPath = os.path.join(blockroot, blockedImage)
            print(f"> Processing: {refImage}", end='\r')
            cloudBGR, skyBGR, cloudHSV, skyHSV = read(blockPath, refPath, cloudBGR, skyBGR, cloudHSV, skyHSV)
    print("\n")

    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#

    """
    Now we create our BGR Bar Graph
    """
    distributionBarGraphGenerator(cloudBGR, skyBGR, cloudHSV, skyHSV , Graphs, bins)
    
    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#

if __name__ == '__main__':

    start = datetime.now()
    Blocked = r'Blocked-Images-esp'
    Reference = r'Reference-Images-esp'
    Graphs = r"Graphs"

    if filesync(Blocked, Reference):
        main(Blocked, Reference, Graphs)
    
    end = datetime.now()
    runtime = end-start
    print(f'\n> Runtime : {runtime} \n')

#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#