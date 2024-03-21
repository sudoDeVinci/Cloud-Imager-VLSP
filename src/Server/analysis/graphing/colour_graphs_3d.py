import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from src.Server.analysis.config import *
from src.Server.analysis.extract import raw_images, get_tags



sub_graph_dir = f"3d_dist_basic/{camera}"



def __plot(sky_folder:str, cloud_folder:str, colour_index: int) -> None:
    """
    Plot the 3D point cloud of the selected colour channels for the image samples.
    """
    temp = get_tags(colour_index)

    #debug(temp)

    components = temp[0] 
    colour_tag = temp[1]
    del temp

    #debug(colour_tag)
    
    # Process images
    data_sky = raw_images(sky_folder, colour_index)
    data_cloud = raw_images(cloud_folder, colour_index)
    
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
    ax.view_init(45, -45)
    #plt.show()
    plt.savefig(f"{root_graph_folder}/new_3D_{camera}_{colour_tag}.png")
    plt.clf
    collect()
    
def __main(colour_index: int) -> None:
    
    # PCA performed for RGB, HSV or YCbCr.
    __plot(sky_images_folder, cloud_images_folder, colour_index)

    debug(f"Process {colour_index} done.")
    

if __name__ == '__main__':
    workers = 3
    start = datetime.now()
    mkdir(f"{root_graph_folder}/{sub_graph_dir}")
    workers = 3
    
    # create a process pool
    with ProcessPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(__main, range(workers))
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')