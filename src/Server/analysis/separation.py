from config import *

def __separate(b_img: Mat, r_img: Mat, count:str) -> list[Mat, Mat]:
    """
    Separate a single image of the sky into two images,
    One of the clouds and one of the rest of the sky.
    """

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
            __separate(blockPath, refPath, count)
            count+=1


def filesync(blc:str, ref:str, cld:str, sky:str) -> bool:
    """
    Make sure filenames are synced before running.
    """
    for (_, _, b_imgs), (_, _, r_imgs),(_, _, c_imgs),(_, _, s_imgs) in zip (os.walk(blc),os.walk(ref),os.walk(cld),os.walk(sky)):
        for b_img, r_img, c_img, s_img in zip(b_imgs, r_imgs, c_imgs, s_imgs):
            if not (b_img == r_img == c_img == s_img):
                debug(f"Image Desync!\nRef: {r_img}\nBlocked: {b_img}\nCloud: {c_img}\nSky: {s_img}")
                return False 
    debug("Files Synced")
    return True 


if __name__ == '__main__':
    start = datetime.now()
    empty = False
    
    if ( not os.path.exists(blocked_images_folder) or not os.path.exists(reference_images_folder)):
        debug("bad path")
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
            debug("File Desync")
            os._exit(1)