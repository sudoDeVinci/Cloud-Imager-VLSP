import numpy as np
import numpy.typing
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
from PIL import Image
from gc import collect
import os
import cv2
from numba import cuda, jit
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

# For typing
Mat = numpy.typing.NDArray[np.uint8]

# Camera model
camera = "dslr"

# Global paths
root_image_folder = 'images'
blocked_images_folder = f"{root_image_folder}/blocked_{camera}"
reference_images_folder = f"{root_image_folder}/reference_{camera}"
cloud_images_folder = f"{root_image_folder}/cloud_{camera}"
sky_images_folder = f"{root_image_folder}/sky_{camera}"

root_graph_folder = 'Graphs'


def __separate(b_img: Mat, r_img: Mat, count:str) -> None:

    b_img = cv2.resize(b_img,(400, 300))
    r_img = cv2.resize(r_img,(400, 300))

    b_img = cv2.cvtColor(b_img, cv2.COLOR_BGR2HSV)
    r_img = cv2.cvtColor(r_img, cv2.COLOR_BGR2HSV)

    
    """
    First we make a mask for red colours
    We'll use Red to represent Clouds
    Red can have hue values between 0-10, but also 170-180
    """

    u_b_red1HSV = np.array([10, 255, 255])
    l_b_red1HSV = np.array([0, 30, 30])

    u_b_red2HSV = np.array([180, 255, 255])
    l_b_red2HSV = np.array([170, 50, 50])

    maskOneRedHSV = cv2.inRange(b_img,l_b_red1HSV,u_b_red1HSV)
    maskTwoRedHSV = cv2.inRange(b_img,l_b_red2HSV,u_b_red2HSV)

    redMask = cv2.bitwise_or(maskOneRedHSV,maskTwoRedHSV)

    """
    Now we do the same for Black.
    We'll use a range of black to represent The Sky
    """

    u_b_blackHSV = np.array([180, 255,30])
    l_b_blackHSV = np.array([0, 0, 0])

    blackMask = cv2.inRange(b_img, l_b_blackHSV, u_b_blackHSV)


    """
    Apply masks and create HSV versions of our images.
    """

    cloud_img = cv2.bitwise_and(r_img, r_img, mask = redMask)
    sky_img = cv2.bitwise_and(r_img, r_img, mask = blackMask)
    c_img = cv2.cvtColor(cloud_img, cv2.COLOR_HSV2BGR)
    s_img = cv2.cvtColor(sky_img, cv2.COLOR_HSV2BGR)

    return c_img, s_img



def separate_datasets(blocked_image_folder: str, reference_image_folder: str) -> None:
    """
    This iterates through colour-blocked images and separates them into two images, one sky and one cloud

    An assumption of this function is that all images are of the same size.
    As to not raise an error
    """
    count = 1
    for (ref_root, _, referenceImages), (blc_root, _, blockedImages) in zip(os.walk(reference_image_folder), os.walk(blocked_image_folder)):
        for ref, blc in zip(referenceImages, blockedImages):
            refPath = os.path.join(ref_root, ref)
            blockPath = os.path.join(blc_root, blc)

            b_img = cv2.imread(blockPath)
            r_img = cv2.imread(refPath)
            c_img, s_img = __separate(b_img, r_img, count)

            num = str(count).zfill(2)
            cv2.imwrite(f"{cloud_images_folder}/Image{num}.png",c_img)
            cv2.imwrite(f"{sky_images_folder}/Image{num}.png",s_img)
            count+=1


def __process_images(folder_path:str, colour_index: int = 0) -> np.ndarray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    default or 0: RGB, 1: HSV, 2: YCbCr
    """
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            image = Image.open(os.path.join(folder_path, filename))

            match colour_index:
                case 0:
                    image = np.array(image)
                    non_black_data = __process_RGB(image)
                    
                    
                case 1:
                    image = image.convert('HSV')
                    image = np.array(image)
                    non_black_data = __process_HSV(image)

                case 2:
                    image = image.convert('YCbCr')
                    image = np.array(image)
                    non_black_data = __process_YBR(image)
                
                case _:
                    image = np.array(image)
                    non_black_data = __process_RGB(image)
            
            # Mean-centering
            non_black_data = non_black_data - np.mean(non_black_data, axis=0)
            
            data.append(non_black_data)
    return np.vstack(data)


def __process_RGB(image: np.array) -> np.array:
    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((red != 0) | (green != 0) | (blue != 0))
    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
    return non_black_data

def __process_HSV(image: np.array) -> np.array:
    h, s, v = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((v != 0))
    non_black_data = np.column_stack((h[non_black_indices], s[non_black_indices], v[non_black_indices]))
    return non_black_data

def __process_YBR(image: np.array) -> np.array:
    Y, b, r = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((Y != 0))
    non_black_data = np.column_stack((Y[non_black_indices], b[non_black_indices], r[non_black_indices]))
    return non_black_data



def pca(sky_folder:str, cloud_folder:str, colour_index: int) -> None:
    # The principle coponents deåpend on the color channels used.
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

    # n_components = len(components)

    # Process images
    data_sky = __process_images(sky_folder, colour_index)
    data_cloud = __process_images(cloud_folder, colour_index)

    # Standardize the data
    scaler = StandardScaler()
    data_sky_standardized = scaler.fit_transform(data_sky)
    data_cloud_standardized = scaler.fit_transform(data_cloud)
    
    # Perform PCA
    pca_sky = PCA(n_components = 3)
    pca_cloud = PCA(n_components = 3)

    pca_result_sky = pca_sky.fit_transform(data_sky_standardized)
    pca_result_cloud = pca_cloud.fit_transform(data_cloud_standardized)

    # Get the eigenvectors (principal components)
    eigenvectors_sky = pca_sky.components_
    eigenvectors_cloud = pca_cloud.components_

    # Get the explained variance ratios
    explained_variance_sky = pca_sky.explained_variance_ratio_
    explained_variance_cloud = pca_cloud.explained_variance_ratio_

    # Delete unneeded ararys
    del data_cloud, data_sky, pca_cloud, pca_sky, data_sky_standardized, data_cloud_standardized
    collect()

    # Print the Eigenvectors
    print(f"\nEigenvectors {colour_index} : {colour_tag} - Sky:")
    for i in range(len(components)):
        print(f"{components[i]}: {eigenvectors_sky[0, i]:.4f}")


    print(f"\nPrincipal Component {colour_index} : {colour_tag} - Cloud:")
    for i in range(len(components)):
        print(f"{components[i]}: {eigenvectors_cloud[0, i]:.4f}")
    
    # Print the Variance ratios
    print(f"\nVariance ratios {colour_index} : {colour_tag} - Sky:")
    for i, ratio in enumerate(explained_variance_sky):
        print(f"Component {i+1}: {ratio:.4f}")


    print(f"\nVariance ratios {colour_index} : {colour_tag} - Cloud:")
    for i, ratio in enumerate(explained_variance_cloud):
        print(f"Component {i+1}: {ratio:.4f}")

    del eigenvectors_cloud, eigenvectors_sky, explained_variance_cloud, explained_variance_sky
    collect()

    # Create Scatterplot
    print(f"\nCreating {colour_index} : {colour_tag} PCA ScatterPlot ...")
    _,ax = plt.subplots(figsize=(10,6))
    ax.scatter(pca_result_sky[:, 0], pca_result_sky[:, 1], c='b', alpha = 0.1, marker = 'X', label = 'sky value')
    ax.scatter(pca_result_cloud[:, 0], pca_result_cloud[:, 1], c='r', alpha = 0.1, marker = 'X', label = 'cloud value')
    plt.legend(loc="upper left")
    plt.title('PCA')
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.savefig(f"{root_graph_folder}/new_pca_{camera}_{colour_tag}.png")
    plt.clf

    collect()


def filesync(blc:str, ref:str, cld:str, sky:str) -> bool:
    """
    Make sure filenames are synced before running
    """
    for (_, _, b_imgs), (_, _, r_imgs),(_, _, c_imgs),(_, _, s_imgs) in zip (os.walk(blc),os.walk(ref),os.walk(cld),os.walk(sky)):
        for b_img, r_img, c_img, s_img in zip(b_imgs, r_imgs, c_imgs, s_imgs):
            if not (b_img == r_img == c_img == s_img):
                print(f"Image Desync!\nRef: {r_img}\nBlocked: {b_img}\nCloud: {c_img}\nSky: {s_img}")
                return False 
    print("Files Synced")
    return True        

def main(colour_index: int) -> None:
    
    # PCA performed for RGB, HSV or YCbCr.
    pca(sky_images_folder, cloud_images_folder, colour_index)

    print(f"Process {colour_index} done.")


if __name__ == '__main__':
    start = datetime.now()
    empty = False
    
    if ( not os.path.exists(blocked_images_folder) or not os.path.exists(reference_images_folder)):
        print("bad path")
        os._exit(1)
    
    if (not os.path.exists(cloud_images_folder)):
        os.mkdir(cloud_images_folder)
        empty = True
    
    if (not os.path.exists(sky_images_folder)):
        os.mkdir(sky_images_folder)
        empty = True
    
    if empty:
        separate_datasets(blocked_images_folder, reference_images_folder)

    else:
        synced = filesync(blocked_images_folder, reference_images_folder, cloud_images_folder, sky_images_folder)
        if (not synced):
            os._exit(1)


    # create a process pool
    with ProcessPoolExecutor(max_workers=4) as executor:
        _ = executor.map(main, range(3))
    end = datetime.now()
    runtime = end-start
    print(f'\n> Runtime : {runtime} \n')