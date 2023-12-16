from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

from config import *
from extract import process_images, get_tags


def pca(sky_folder:str, cloud_folder:str, colour_index: int) -> None:
    """
    Graph the Principle components. 
    The principle components depend on the color channels used.
    """
    temp = get_tags(colour_index)

    #debug(temp)

    components = temp[0] 
    colour_tag = temp[1]
    del temp

    #debug(colour_tag)

    # n_components = len(components)

    # Process images
    data_sky = process_images(sky_folder, colour_index)
    data_cloud = process_images(cloud_folder, colour_index)

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
    debug(f"\nEigenvectors {colour_index} : {colour_tag} - Sky:")
    for i in range(len(components)):
        debug(f"{components[i]}: {eigenvectors_sky[0, i]:.4f}")


    debug(f"\nPrincipal Component {colour_index} : {colour_tag} - Cloud:")
    for i in range(len(components)):
        debug(f"{components[i]}: {eigenvectors_cloud[0, i]:.4f}")
    
    # Print the Variance ratios
    debug(f"\nVariance ratios {colour_index} : {colour_tag} - Sky:")
    for i, ratio in enumerate(explained_variance_sky):
        debug(f"Component {i+1}: {ratio:.4f}")


    debug(f"\nVariance ratios {colour_index} : {colour_tag} - Cloud:")
    for i, ratio in enumerate(explained_variance_cloud):
        debug(f"Component {i+1}: {ratio:.4f}")

    del eigenvectors_cloud, eigenvectors_sky, explained_variance_cloud, explained_variance_sky
    collect()

    # Create Scatterplot
    debug(f"\nCreating {colour_index} : {colour_tag} PCA ScatterPlot ...")
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


def main(colour_index: int) -> None:
    
    # PCA performed for RGB, HSV or YCbCr.
    pca(sky_images_folder, cloud_images_folder, colour_index)

    debug(f"Process {colour_index} done.")


if __name__ == '__main__':
    start = datetime.now()
    workers = 3
    
    # create a process pool
    with ProcessPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(main, range(workers))
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')
