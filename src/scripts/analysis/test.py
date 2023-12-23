import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

from config import *
from extract import raw_images, get_tags




def __plot(sky_folder:str, cloud_folder:str) -> None:
    """
    Plot the 3D point cloud of the selected colour channels for the image samples.
    """
    
    _ = plt.figure()
 
    # syntax for 3-D projection
    ax = plt.axes(projection ='3d')
    
    ax.scatter3D(data_cloud[:, 0], data_cloud[:, 1], data_cloud[:, 2],  c='r', alpha = 0.2, marker = 'X', label = 'cloud value')
    ax.scatter3D(data_sky[:, 0], data_sky[:, 1], data_sky[:, 2], c='b', alpha = 0.2, marker = 'X', label = 'sky value')
    plt.legend(loc="upper left")
    plt.title(f"{colour_tag} colour space point cloud")
    ax.set_xlabel(f'{components[0]}', fontsize=12)
    ax.set_ylabel(f'{components[1]}', fontsize=12)
    ax.set_zlabel(f'{components[2]}', fontsize=12)
    # plt.show()
    plt.savefig(f"{root_graph_folder}/new_3D_{camera}_{colour_tag}.png")
    plt.clf
    collect()



def __process(sky_folder:str, cloud_folder:str) -> None:
    # Process RGB images
    data_sky = raw_images(sky_folder, 0)
    data_cloud = raw_images(cloud_folder, 0)
    red_cloud = data_cloud[:,0]
    red_sky = data_sky[:,0]
    del data_sky, data_cloud

    # Process HSV images
    data_sky = raw_images(sky_folder, 0)
    data_cloud = raw_images(cloud_folder, 0)
    sat_cloud = data_cloud[:,1]
    sat_sky = data_sky[:,1]
    del data_sky, data_cloud

    # Process YCBCR images
    data_sky = raw_images(sky_folder, 0)
    data_cloud = raw_images(cloud_folder, 0)
    sat_cloud = data_cloud[:,1]
    sat_sky = data_sky[:,1]
    del data_sky, data_cloud




def __main(colour_index: int) -> None:
    try:
    # PCA performed for RGB, HSV or YCbCr.
        __plot(sky_images_folder, cloud_images_folder)
    except Exception as e:
        debug(e)
    debug(f"Process {colour_index} done.")



if __name__ == '__main__':
    start = datetime.now()
    workers = 3
    
    
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')