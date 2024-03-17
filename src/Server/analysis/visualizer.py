from config import *


index = 0
size = (400, 300)
images = os.listdir(reference_images_folder)
img = cv2.imread(os.path.join(reference_images_folder, images[index]))
img = cv2.resize(img,size)

NEXT_KEY = ord('d')
BACK_KEY = ord('a')
STOP_KEY = ord('q')
running = True
# Taking a matrix of size 5 as the kernel 
kernel = np.ones((5, 5), np.uint8) 


def __nothing(x) -> None:   
    pass

def __update_image() -> None:
    global index
    global img
    img = cv2.imread(os.path.join(reference_images_folder, images[index]))
    img = cv2.resize(img,size)

def __next() -> None:
    global index
    index = (index + 1 ) % len(images)
    __update_image()

def __back() -> None:
    global index
    index = (index - 1 ) % len(images)
    __update_image()


cv2.namedWindow("Tracking")
cv2.createTrackbar("LS", "Tracking", 0, 255, __nothing)
cv2.createTrackbar("HS", "Tracking", 0, 255, __nothing)
cv2.createTrackbar("LCB", "Tracking", 0, 255, __nothing)
cv2.createTrackbar("HCB", "Tracking", 0, 255, __nothing)


while running:
    ls = cv2.getTrackbarPos("LS", "Tracking")
    hs = cv2.getTrackbarPos("HS", "Tracking")
    lcb = cv2.getTrackbarPos("LCB", "Tracking")
    hcb = cv2.getTrackbarPos("HCB", "Tracking")

    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    ub_sat = np.array([255, hs, 255])
    lb_sat = np.array([0, ls, 0])
    hsvMask = cv2.inRange(img_hsv, lb_sat, ub_sat)

    img_ycb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    ub_cblue = np.array([255, 255, hcb])
    lb_cblue = np.array([0, 0, lcb])
    ycbMask = cv2.inRange(img_ycb, lb_cblue, ub_cblue)

    fullMask = cv2.bitwise_and(ycbMask, hsvMask)
    fullMask_eroded = cv2.erode(fullMask, kernel, iterations = 2s)
    fullMask_eroded = cv2.dilate(fullMask, kernel, iterations = 1)

    outimage = cv2.bitwise_and(img, img, mask=fullMask)
    outimage_eroded = cv2.bitwise_and(img, img, mask=fullMask_eroded)

    cv2.imshow("Image State", outimage)
    cv2.imshow("Cleaned Image State", outimage_eroded)
    cv2.imshow("YCrCb Mask", ycbMask)
    cv2.imshow("HSV Mask", hsvMask)

    key = cv2.waitKey(50)

    if key == BACK_KEY:
        __back()
    
    elif key == NEXT_KEY:
        __next()

    elif key == STOP_KEY:
        running = False


cv2.destroyAllWindows() 