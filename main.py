import cv2
import numpy as np
import math


cap = cv2.VideoCapture(0) # path of video file in palce of '0'
while(cap.isOpened()):
    #read image
    ret,img = cap.read()

    #------------------------------------------------------------------------------------------
    # BACKGROUND SUBSTRACTION - START
    #------------------------------------------------------------------------------------------


    #get hand data from the rectangle sub window on the screen
    cv2.rectangle(img,(300,300),(100,100),(0,255,0),0)
    crop_image = img[100:300,100:300]

    #convert to greyscale
    grey = cv2.cvtColor(crop_image,cv2.COLOR_BGR2GRAY)

    #applying gaussian blur
    value = (35,35) # square of 35*35px
    blured = cv2.GaussianBlur(grey,value,0) # why we blur the image - to remove small motions occured in 
    #nature

    #thresholdian: Otsu's binarization method - this method is autometically calculate threshold values
    _,thresh1 = cv2.threshold(blured,127,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) # all the pixels of 
    #value greater than 127 assign a value 1 and lesser are assign a value 0


    #show thresholded image
    cv2.imshow("thresholded",thresh1)

    #------------------------------------------------------------------------------------------
    # BACKGROUND SUBSTRACTION - END
    #------------------------------------------------------------------------------------------

    #------------------------------------------------------------------------------------------
    # FINDING CONTOURS AND SHOW IT ON IMAGE - START
    #------------------------------------------------------------------------------------------

    #check openCV veraion to avoid unpacking error
    (version,_,_) = cv2.__version__.split('.')

    if version == '3':
        image,contours,hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    elif version == '4':
        contours,hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    #find contour with max area
    cnt = max(contours,key = lambda x: cv2.contourArea(x))

    #create building rectangle around the contour (can skip below two lines)
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(crop_image,(x,y),(x+w,y+h),(0,0,255),0)

    #findding convex hull
    hull = cv2.convexHull(cnt) 

    #drawing contours
    drawing = np.zeros(crop_image.shape,np.uint8)
    cv2.drawContours(drawing,[cnt],0,(0,255,0),0)
    cv2.drawContours(drawing,[hull],0,(0,255,0),0)
     
    
    #finding convex hull
    hull = cv2.convexHull(cnt,returnPoints=False)


    # finding convexity defects 
    defects = cv2.convexityDefects(cnt,hull)
    count_defects = 0
    count_right = 0
    cv2.drawContours(thresh1,contours,-1,(0,255,0),3)

    #------------------------------------------------------------------------------------------
    # FINDING AND DRAWING CONTOURS - END
    #------------------------------------------------------------------------------------------
 
    #------------------------------------------------------------------------------------------
    # CALCULATING ANGLE BETWEEN THE FINGERS AND TOTAL FINGERS - START
    #------------------------------------------------------------------------------------------
 


    #applying cosine rule to find angle for all defects (between fingures)
    #with angle > 90 degrees and ignore defects
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]

        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])

        #find length of all sides of triangle
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

        #apply cosine rule here
        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c))*57

        #ignore angles > 90 and highlight rest with red dots
        if  angle <= 70:
            count_defects += 1
            cv2.circle(crop_image,far,1,[0,0,255],-1)
        if 75 <= angle <= 95  :
            count_right += 1    
    #------------------------------------------------------------------------------------------
    # CALCULATING ANGLE BETWEEN THE FINGERS AND TOTAL FINGERS - END
    #------------------------------------------------------------------------------------------
 
    #------------------------------------------------------------------------------------------
    # OUTPUT PHASE - START
    #------------------------------------------------------------------------------------------
 


    # define actions required
    if count_right >= 1:
        cv2.putText(img,"All is well",(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,2)  
    if count_defects == 1 and count_right == 0:
        cv2.putText(img,"Two fingers",(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,2)            
    elif count_defects == 2  and count_right == 0:
        cv2.putText(img," Three fingers",(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,2)            
    elif count_defects == 3  and count_right == 0:
        cv2.putText(img,"Four",(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,2)            
    elif count_defects == 4  and count_right == 0:
        cv2.putText(img,"Five",(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,2)            
    elif count_defects == 5  and count_right == 0:
        cv2.putText(img,"six ",(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,2) 
    else:
        cv2.putText(img,"not detected correctly ",(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,2)                
                   
    # show apprepropiate image in window 
    cv2.imshow('gesture',img)
    all_img = np.hstack((drawing,crop_image))
    cv2.imshow('contours',all_img)
    
    #------------------------------------------------------------------------------------------
    # OUTPUT PHASE - END
    #------------------------------------------------------------------------------------------
 


    k = cv2.waitKey(10)
    if k == 27:
        break               

