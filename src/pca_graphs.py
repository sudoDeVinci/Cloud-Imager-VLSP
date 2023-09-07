__author__ = 'Tadj Cazaubon'
__credits__ = ["Tadj Cazaubon"]


# TODO: Multiprocessing in read() function. 
# from multiprocessing.context import Process
import os
from gc import collect
from turtle import pd
import cv2
import numpy as np
import pandas as pd
from numba import jit
from matplotlib import pyplot as plt
from multiprocessing import Pipe
from multiprocessing import Process
from sklearn.decomposition import PCA 
from sklearn import preprocessing
from datetime import datetime


def read(Blocked:str, Reference:str, bgr_dict:dict, hsv_dict:dict, cloud_bgr_num:int, cloud_hsv_num:int, sky_bgr_num:int, sky_hsv_num:int) -> tuple[dict, dict, int, int, int, int]:
    """
    An assumption of this function is that all images are of the same size.
    As to not raise an error

    We read in our images and convert them to HSV
    """


    blockedImage = cv2.imread(Blocked)
    blockedImage = cv2.resize(blockedImage,(150, 150))
    blockedImageHSV = cv2.cvtColor(blockedImage,cv2.COLOR_BGR2HSV)

    

    referenceImage = cv2.imread(Reference)
    referenceImage = cv2.resize(referenceImage,(150, 150))
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
    del u_b_red1HSV, l_b_red1HSV, u_b_red2HSV, l_b_red2HSV 
    del maskOneRedHSV 
    del maskTwoRedHSV 
    del redMaskHSV 
    del u_b_blackHSV 
    del l_b_blackHSV 
    del blackMaskHSV
    del blockedImageHSV 
    del referenceImage
    del referenceImageHSV
    collect()

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

    del cloudImageBGR
    del skyImageBGR
    del cloudImageHSV
    del skyImageHSV
    collect()

    """
    I save the values into the dictionaries a strings because for some reason when they
    are saved as int, and later converted into dataframes, the integers somehow overflow
    into negative numbers. eg: if  int was 56, it would now be -200, as 200+56 = 256

    I have nno idea how, but this also only happened to some of the rows, not all.
    """


    def readoutbgr(bgr, bgr_dict, bgr_num, indicator) -> tuple[dict, int]:
        b, g, r = bgr
        for x,y,z in zip(b,g,r):
            for i,o,u in zip(x,y,z):
                if i!= 0 or o!=0 or u!=0:
                    if i and o and u:
                        pixel_num = indicator+str(bgr_num).zfill(5)
                        bgr_dict[pixel_num] = [str(i), str(o), str(u)]
                        bgr_num += 1
        return bgr_dict, bgr_num



    def readouthsv(hsv, hsv_dict, hsv_num, indicator)-> tuple[dict, int]:
        h, s, v = hsv
        for x,y,z in zip(h,s,v):
            for i,o,u in zip(x,y,z):
                if u!=0:
                    pixel_num = indicator+str(hsv_num).zfill(5)
                    hsv_dict[pixel_num] = [str(i), str(o), str(u)]
                    hsv_num += 1
        return hsv_dict, hsv_num


    bgr_dict, cloud_bgr_num = readoutbgr(cbgrch, bgr_dict, cloud_bgr_num, 'c')
    bgr_dict, sky_bgr_num = readoutbgr(sbgrch, bgr_dict, sky_bgr_num, 's')

    hsv_dict, cloud_hsv_num = readouthsv(chsvch, hsv_dict, cloud_hsv_num, 'c')
    hsv_dict, sky_hsv_num = readouthsv(shsvch, hsv_dict, sky_hsv_num, 's')

    return bgr_dict, hsv_dict, cloud_bgr_num, cloud_hsv_num, sky_bgr_num, sky_hsv_num

#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#

"""
Make sure filenames are synced before running
"""
def filesync(Blocked:str, Reference:str) -> bool:
    for (_, _, referenceImages), (_, _, blockedImages) in zip(os.walk(Reference), os.walk(Blocked)):
        for refImage, blockedImage in zip(referenceImages, blockedImages):
            if refImage != blockedImage:
                print("Image desync!")
                return False

    print("Files Synced")
    return True


#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#

def main(Blocked:str, Reference:str, Graphs:str) -> None:
    
    """
    I like to lay these things out one by one to allow for better 
    """

    bgr_dict = {}
    hsv_dict = {}
    cloud_hsv_num = 1
    cloud_bgr_num = 1
    sky_hsv_num = 1
    sky_bgr_num = 1

    bgrBarPath = os.path.join(Graphs,'BGRPcaGraph.png')
    hsvBarPath = os.path.join(Graphs,'HSVPcaGraph.png')
    bgrScreePath = os.path.join(Graphs,'BGRScree.png')
    hsvScreePath = os.path.join(Graphs,'HSVScree.png')
   
   # Scraping each image in our designated image folders
    for (refroot, _, referenceImages), (blockroot, _, blockedImages) in zip(os.walk(Reference), os.walk(Blocked)):
        for refImage, blockedImage in zip(referenceImages, blockedImages):
            refPath = os.path.join(refroot, refImage)
            blockPath = os.path.join(blockroot, blockedImage)
            print(f"> Processing: {refImage}", end='\r')
            bgr_dict, hsv_dict, cloud_bgr_num, cloud_hsv_num, sky_bgr_num, sky_hsv_num = read(blockPath, refPath, bgr_dict, hsv_dict, cloud_bgr_num, cloud_hsv_num, sky_bgr_num, sky_hsv_num)

    # Sort dictionaries for easier separating later
    sorted_bgr_dict = sorted(bgr_dict)
    sorted_hsv_dict = sorted(hsv_dict)
    bgr_dict = {key:bgr_dict[key] for key in sorted_bgr_dict}
    hsv_dict = {key:hsv_dict[key] for key in sorted_hsv_dict}
    bgr_indexes = list(bgr_dict.keys())
    hsv_indexes = list(hsv_dict.keys())

    cloud_final = "c"+str(cloud_bgr_num).zfill(5)
    sky_final = 's'+str(sky_bgr_num-2).zfill(5)
    
    # Show pixels counts
    print(f" └ {cloud_bgr_num} cloud pixels")
    print(f" └ {sky_bgr_num} sky pixels")
    print("\n")

    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#
    
    del sorted_bgr_dict
    del sorted_hsv_dict
    collect()

    def create_df(df: pd.DataFrame):
        df.astype(float, errors='ignore', copy=False)  # Convert columns to float (numeric) type
        df = df.T  # Transpose DataFrame
        return df

    print("> Creating BGR dataframe ...")
    bgr_df = create_df(pd.DataFrame(bgr_dict, index=['b', 'g', 'r']))
    print(" └ BGR dataframe created.")

    print("> Creating HSV dataframe ...")
    hsv_df = create_df(pd.DataFrame(hsv_dict, index=['h', 's', 'v']))
    print(" └ HSV dataframe created.")

    collect()
    #----------------------------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------------------------#

    
    """ Now we scale our bgr and hsv values"""
    print("> Scaling and fitting Data ...")
    scaled_bgr = preprocessing.scale(bgr_df)
    scaled_hsv = preprocessing.scale(hsv_df)

    """Now we fit both our datasets"""
    bgr_pca = PCA()
    hsv_pca = PCA()

    bgr_pca.fit(scaled_bgr)
    hsv_pca.fit(scaled_hsv)
    print("\n")


    """Now we generate our coordinates for PCA Graph"""
    print("> Generating Graph Data ...")
    bgr_pca_data = bgr_pca.transform(scaled_bgr)
    hsv_pca_data = hsv_pca.transform(scaled_hsv)


    """At this point we don't need the original dataframes"""
    del scaled_bgr
    del scaled_hsv
    del bgr_df
    del hsv_df
    del bgr_dict
    del hsv_dict
    collect()
    print("\n")


    """Calculate variance and labels"""
    print("> Creating BGR Screeplot ...")
    bgr_per_var = np.round(bgr_pca.explained_variance_ratio_*100, decimals=1)
    bgr_labels = ["red","green","blue"]
    plt.bar(x=range(1, len(bgr_per_var)+1), height = bgr_per_var, tick_label = bgr_labels)
    plt.ylabel('Variance percentage')
    plt.xlabel('Principle component')
    plt.title('BGR Scree Plot')
    plt.savefig(bgrScreePath)
    plt.clf()
    print(" └ BGR Screeplot created.")

    print("> Creating HSV Screeplot...")
    hsv_per_var = np.round(hsv_pca.explained_variance_ratio_*100, decimals=1)
    hsv_labels = ["value","saturation","hue"]
    plt.bar(x=range(1, len(hsv_per_var)+1), height = hsv_per_var, tick_label = hsv_labels)
    plt.ylabel('Variance percentage')
    plt.xlabel('Principle component')
    plt.title('HSV Scree Plot')
    plt.savefig(hsvScreePath)
    plt.clf()
    print(" └ HSV Screeplot created.")

    print("\n")

    """Create the dataframes we use for our scatterplot"""
    
    bgr_pca_df = pd.DataFrame(bgr_pca_data, index = bgr_indexes, columns = bgr_labels)
    hsv_pca_df = pd.DataFrame(hsv_pca_data, index = [hsv_indexes], columns = hsv_labels)

    del hsv_pca
    del bgr_pca
    del hsv_pca_data
    del bgr_pca_data
    del bgr_labels
    del hsv_labels
    collect()


    #---------------------------------------------------------------------------------------------------------#
    #---------------------------------------------------------------------------------------------------------#
    
    """
    Create A scatterplot for our pca data.
    First we split our dataframe into two so wee can colour code them
    """


    bgr_cloud_df = bgr_pca_df.loc["c00001" : cloud_final, :]
    bgr_sky_df = bgr_pca_df.loc["s00001" : sky_final, :]
    del bgr_pca_df

    hsv_cloud_df = hsv_pca_df.loc["c00001" : cloud_final, :]
    hsv_sky_df = hsv_pca_df.loc["s00001" : sky_final, :]
    del hsv_pca_df

    collect()

    print("> Creating BGR PCA Scatterplot ...")
    _,ax = plt.subplots(figsize=(10,6))
    ax.scatter(bgr_cloud_df.red,bgr_cloud_df.green, c = 'lightblue',alpha = 0.3,marker = 'X',label = 'Cloud BGR Value')
    ax.scatter(bgr_sky_df.red,bgr_sky_df.green,c = 'red',alpha = 0.1,marker = 'o',label = 'Sky BGR Value')
    plt.legend(loc="upper left")
    plt.title('BGR PCA')
    plt.xlabel('Red - {0}%'.format(bgr_per_var[0]))
    plt.ylabel('Green - {0}%'.format(bgr_per_var[1]))
    plt.savefig(bgrBarPath)
    plt.clf
    print(" └ BGR Scatterplot created.")

    del bgr_cloud_df
    del bgr_sky_df
    del bgr_per_var
    collect()


    print("> Creating HSV PCA ScatterPlot ...")
    _,ax = plt.subplots(figsize=(10,6))
    ax.scatter(hsv_cloud_df.value,hsv_cloud_df.saturation, c = 'lightblue',alpha = 0.3,marker = 'X',label = 'Cloud HSV Value')
    ax.scatter(hsv_sky_df.value,hsv_sky_df.saturation,c = 'red',alpha = 0.1,marker = 'o',label = 'Sky HSV Value')
    plt.legend(["my legend"],loc="upper left")
    plt.title('HSV PCA')
    plt.xlabel('Value - {0}%'.format(hsv_per_var[0]))
    plt.ylabel('Saturation- {0}%'.format(hsv_per_var[1]))
    plt.savefig(hsvBarPath)
    plt.clf
    print(" └ HSV Screeplot created")

    del hsv_cloud_df
    del hsv_sky_df
    del hsv_per_var
    collect()

#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':

    start = datetime.now()

    root_image_folder = 'CloudMeshVLSP/images'
    blocked_images_folder = f"{root_image_folder}/blocked_dslr"
    reference_images_folder = f"{root_image_folder}/reference_dslr"
    cloud_images_folder = f"{root_image_folder}/cloud_dslr"
    sky_images_folder = f"{root_image_folder}/sky_dslr"

    root_graph_folder = 'CloudMeshVLSP/Graphs'

    if filesync(blocked_images_folder, reference_images_folder):
        main(blocked_images_folder, reference_images_folder, root_graph_folder)

    end = datetime.now()
    runtime = end-start
    print(f'\n> Runtime : {runtime} \n')

#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#