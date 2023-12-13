import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

from config import *
from extract import raw_images


def __count(xyz_sk:np.array) -> np.array:
    """
    """
    unique, counts = np.unique(xyz_sk, return_counts=True)
    freq = np.asarray((unique, counts)).T
    return freq
    
    


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
    
    x_cloud_freq = __count(np.array(data_cloud[:, 0]))
    y_cloud_freq = __count(np.array(data_cloud[:, 1]))
    z_cloud_freq = __count(np.array(data_cloud[:, 2]))
    
    x_sky_freq = __count(np.array(data_sky[:, 0]))
    y_sky_freq = __count(np.array(data_sky[:, 1]))
    z_sky_freq = __count(np.array(data_sky[:, 2]))
    
    del data_cloud, data_sky
    
    debug(x_cloud_freq[0])
    
    distributionBarGraphGenerator([x_cloud_freq, x_sky_freq], [y_cloud_freq, y_sky_freq], [z_cloud_freq, z_sky_freq], components, colour_tag)
    



def distributionBarGraphGenerator(x, y, z, components: list[str,str,str], colour_tag: str):
    """
    Generate BGR and HSV Bar Graphs
    """
    
    x_c = x[0]
    x_s = x[1]
    y_c = y[0]
    y_s = y[1]
    z_c = z[0]
    z_s = z[1]
    
    #bins = [*range(0,256,1)]

    #print(f"> There are: \n └  {sum(cloudBlues)} cloud datapoints\n └  {sum(skyBlues)} sky datapoints")

    debug(f"\n> Creating {colour_tag} Bar Histogram ...")
    fig1,axes1 = plt.subplots(nrows = 3, ncols = 1)
    axes1 = axes1.flatten()

    axes1[0].bar(x_s[:,0], x_s[:,1], color = 'red', alpha= 0.3, label = f'Sky {components[0]}')
    axes1[0].bar(x_c[:,0], x_c[:,1], color = 'orange',alpha = 0.3,label = f'Cloud {components[0]}')
    axes1[0].set_xlabel(f'{colour_tag} {components[0]} (0 - 255)')
    axes1[0].set_ylabel('frequency')
    axes1[0].legend(loc="upper left")
    del x_s, x_c

    axes1[1].bar(y_s[:,0], y_s[:,1], color = 'green', alpha= 0.3, label = f'Cloud {components[1]}')
    axes1[1].bar(y_c[:,0], y_c[:,1], color = 'yellow', alpha = 0.3, label = f'Sky {components[1]}')
    axes1[1].set_xlabel(f'{colour_tag} {components[1]} (0 - 255)')
    axes1[1].set_ylabel('frequency')
    axes1[1].legend(loc="upper left")
    del y_s, y_c

    axes1[2].bar( z_s[:,0], z_s[:,1], color = 'blue', alpha= 0.3, label = f'Cloud {components[2]}')
    axes1[2].bar(z_c[:,0], z_c[:,1], color = 'purple', alpha = 0.3, label = f'Sky {components[2]}')
    axes1[2].set_xlabel(f'{colour_tag} {components[2]} (0 - 255)')
    axes1[2].set_ylabel('frequency')
    axes1[2].legend(loc="upper left")
    del z_s, z_c
    
    fig1.tight_layout()
    plt.title(f"{colour_tag} Colour Frequency")
    plt.savefig(f"{root_graph_folder}/new_hist_{camera}_{colour_tag}.png")
    plt.clf()
    plt.close("all")
    collect()
    print(f" └ {colour_tag} Bar Graph created.")
    collect()
    
    
def __main(colour_index: int) -> None:
    
    # PCA performed for RGB, HSV or YCbCr.
    __plot(sky_images_folder, cloud_images_folder, colour_index)

    debug(f"Process {colour_index} done.")
    

if __name__ == '__main__':
    start = datetime.now()
    
    # create a process pool
    with ProcessPoolExecutor(max_workers=4) as executor:
        _ = executor.map(__main, range(3))
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')