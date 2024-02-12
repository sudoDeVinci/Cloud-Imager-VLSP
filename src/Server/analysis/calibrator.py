from config import *
import glob
import pickle




def calibrate():
    ################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################

    chessboardSize = (9,6)
    frameSize = (4032, 3024)

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)56v 
    objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)

    size_of_chessboard_squares_mm = 23
    objp = objp * size_of_chessboard_squares_mm

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.


    images = glob.glob('src/calibration_images/*.jpg')

    for image in images:

        img = cv2.imread(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, chessboardSize, None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(corners)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)


    cv2.destroyAllWindows()
    return (objpoints, imgpoints, frameSize)




def undistort(objpoints, imgpoints, frameSize):
    ############## CALIBRATION #######################################################

    ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frameSize, None, None)

    # Save calibration results.
    # Save the camera calibration result for later use (we won't worry about rvecs / tvecs)
    pickle.dump((cameraMatrix, dist), open( "src/calibration_images/calibration.pkl", "wb" ))
    pickle.dump(cameraMatrix, open( "src/calibration_images/cameraMatrix.pkl", "wb" ))
    pickle.dump(dist, open( "src/calibration_images/dist.pkl", "wb" ))
    ############## UNDISTORTION #####################################################

    img = cv2.imread('src/calibration_images/can.jpg')
    h,  w = img.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

    # Undistort
    dst = cv2.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    cv2.imwrite('src/calibration_images/undistorted_can.png', dst)
    
    # Undistort with Remapping
    mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
    dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
    
    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    cv2.imwrite('src/calibration_images/undistorted_remapped_can.png', dst)


    # Reprojection Error
    #mean_error = 0

    """for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], cameraMatrix, dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error"""
    
    return dst




def undistort(cameraMatrix, dist):
    ############## UNDISTORTION #####################################################

    name = "can"
    img = cv2.imread(f"src/calibration_images/{name}.jpg")
    h, w = img.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

    # Undistort
    dst = cv2.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

    # crop the image
    #x, y, w, h = roi
    #dst = dst[y:y+h, x:x+w]
    cv2.imwrite(f"src/calibration_images/undistorted_{name}.png", dst)
    
    # Undistort with Remapping
    mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
    dst = cv2.remap(img, mapx, mapy, cv.INTER_LINEAR)
    
    # crop the image
    #x, y, w, h = roi
    #dst = dst[y:y+h, x:x+w]
    cv2.imwrite(f"src/calibration_images/undistorted_remapped_{name}.png", dst)


cameraMatrix = pickle.load(open( "src/calibration_images/cameraMatrix.pkl", "rb" ))
dist = pickle.load(open( "src/calibration_images/dist.pkl", "rb" ))
undistort(cameraMatrix, dist)
