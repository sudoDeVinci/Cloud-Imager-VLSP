from Devinci.config import *

if __name__ == "__main__":

    CAM = Camera(camera_model.OV5640)

    global index
    global img
    global img_hsv
    global img_ycb
    global contour_img
    global contours

    def __update_image() -> None:
        global index
        global img
        global img_hsv
        global img_ycb
        global contour_img
        global contours
        global rects

        img = cv2.imread(os.path.join(CAM.reference_images_folder, images[index]))
        img = cv2.resize(img,size)
        contour_img = img.copy()
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_ycb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        contours = None
        rects = None

    index = 0
    size = (400, 300)
    images = os.listdir(CAM.reference_images_folder)
    __update_image()

    NEXT_KEY = ord('d')
    BACK_KEY = ord('a')
    STOP_KEY = ord('q')
    running = True
    # Taking a matrix of size 5 as the kernel 
    kernel = np.ones((5, 5), np.uint8) 


    def __nothing(x) -> None:   
        global contours
        global contour_img
        global rects

        rects = None
        contours = None
        contour_img = img.copy()

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
    cv2.createTrackbar("Erosion", "Tracking", 1, 10, __nothing)
    cv2.createTrackbar("Dilation", "Tracking", 1, 10, __nothing)

    cv2.setTrackbarPos("LS", "Tracking", 0)
    cv2.setTrackbarPos("HS", "Tracking", 85)
    cv2.setTrackbarPos("LCB", "Tracking", 1)
    cv2.setTrackbarPos("HCB", "Tracking", 148)
    cv2.setTrackbarPos("Erosion", "Tracking", 2)
    cv2.setTrackbarPos("Dilation", "Tracking", 3)


    while running:
        ls = cv2.getTrackbarPos("LS", "Tracking")
        hs = cv2.getTrackbarPos("HS", "Tracking")
        lcb = cv2.getTrackbarPos("LCB", "Tracking")
        hcb = cv2.getTrackbarPos("HCB", "Tracking")
        erosion = cv2.getTrackbarPos("Erosion", "Tracking")
        dilation = cv2.getTrackbarPos("Dilation", "Tracking")

        ub_sat = np.array([255, hs, 255], dtype=np.uint8)
        lb_sat = np.array([0, ls, 0], dtype=np.uint8)
        hsvMask = cv2.inRange(img_hsv, lb_sat, ub_sat)
        
        ub_cblue = np.array([255, 255, hcb], dtype=np.uint8)
        lb_cblue = np.array([0, 0, lcb], dtype=np.uint8)
        ycbMask = cv2.inRange(img_ycb, lb_cblue, ub_cblue)

        fullMask = cv2.bitwise_and(ycbMask, hsvMask)

        fullMask_eroded = cv2.erode(fullMask, kernel, iterations = erosion)
        fullMask_eroded = cv2.dilate(fullMask_eroded, kernel, iterations = dilation)

        outimage = cv2.bitwise_and(img, img, mask=fullMask)
        outimage_eroded = cv2.bitwise_and(img, img, mask=fullMask_eroded)

        n_contours, hier = cv2.findContours(fullMask_eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours is None or (not bool(np.array_equal(a, b) for a,b in zip(contours, n_contours))):
            inner = []
            outer=[]
            for i, con in enumerate(n_contours):
                if hier[0,i,3] != -1: inner.append(con)
                else: outer.append(con)
            
            contours = n_contours
            contour_img = img.copy()

            cv2.drawContours(contour_img, outer, -1, (0, 0, 255), 2)
            cv2.drawContours(contour_img, inner, -1, (0, 255, 0), 2)
            
            rects = tuple(cv2.boundingRect(contour) for contour in outer)
            for x,y,w,h in rects:
                cv2.rectangle(contour_img, (x, y), (x + w - 1, y + h - 1), (0, 255, 255), 2)
                (w, h), _ = cv2.getTextSize(" Cloud ", cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(contour_img, (x, y + 20), (x + w, y), (0,255,255), -1)
                cv2.putText(contour_img, "Cloud", (x, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)


        cv2.imshow("Image State", outimage)
        cv2.imshow("Cleaned Image State", outimage_eroded)
        cv2.imshow("YCBCR - Chroma Blue Mask", ycbMask)
        cv2.imshow("HSV - Saturation Mask", hsvMask)
        cv2.imshow("Countours", contour_img)

        key = cv2.waitKey(50)

        if key == BACK_KEY:
            __back()
        
        elif key == NEXT_KEY:
            __next()

        elif key == STOP_KEY:
            running = False


    cv2.destroyAllWindows()