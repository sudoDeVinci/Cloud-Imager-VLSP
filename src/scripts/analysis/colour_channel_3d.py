import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

from config import *
from extract import raw_images


def __plot(sky_folder:str, cloud_folder:str, colour_index: int) -> None:
 
    components:list[3]
    # The colour tag is a tag used to show the corresponding graphs whihc channels were used.
    colour_tag:str

    match colour_index:
        case 0:
            components = ['red', 'green', 'blue']
            colour_tag = 'rgb'
        case 1:
            components = ['hue','saturation','value']
            colour_tag = 'hsv'
        case 2:
            components = ['brightness','Chroma Blue','Chroma Red']
            colour_tag = 'YCbCr'
        case _:
            components = ['red', 'green', 'blue']
            colour_tag = 'rgb'
    
    # Process images
    data_sky = raw_images(sky_folder, colour_index)
    data_cloud = raw_images(cloud_folder, colour_index)
    
    fig = plt.figure()
 
    # syntax for 3-D projection
    ax = plt.axes(projection ='3d')
    
    ax.scatter3D(data_cloud[:, 0], data_cloud[:, 1], data_cloud[:, 2],  c='r', alpha = 0.2, marker = 'X', label = 'cloud value')
    ax.scatter3D(data_sky[:, 0], data_sky[:, 1], data_sky[:, 2], c='b', alpha = 0.2, marker = 'X', label = 'sky value')
    plt.legend(loc="upper left")
    plt.title(f"{colour_tag} colour space point cloud")
    ax.set_xlabel(f'{components[0]}', fontsize=12)
    ax.set_ylabel(f'{components[1]}', fontsize=12)
    ax.set_zlabel(f'{components[2]}', fontsize=12)
    ax.view_init(45, 180)
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
    empty = False
    
    # create a process pool
    with ProcessPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(__main, range(workers))
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')