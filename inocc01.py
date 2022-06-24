import cv2,sys
import numpy as np
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()
    cip.setDebugFlag(False)
    
    # set Target/Back images
    testimage = sys.argv[1]
    backimage = sys.argv[2]
    cip.setImages(testimage,backimage)
    prefix = sys.argv[3]

    # Get contour
    cont = cip.getContour()
    # Find top coordinate
    top_xy = cip.find_top_x(cont)

    print "TOPXY=",top_xy
    left_flag, right_flag, lower_flag, upper_flag = cip.isTouchedToEdge(cont)
    print "LEFT = ",left_flag
    print "RIGH = ",right_flag
    print "LOWE = ",lower_flag
    print "UPPE = ",upper_flag

    # ROI of the contour defined by 'horizontal' pixel range
    roi_len = 300.0 # [um]
    roi_xy = cip.selectHoriROI(cont, top_xy, roi_len)

    # Output the images
    outimage = "%s_horiroi.png"%prefix
    cip.drawContourTop(roi_xy, top_xy, outimage)

    #print "CX,CY=",cenx,ceny

    # Finding centering point at X of 'half of horizontal ROI length'
    ox, oy = cip.findCenteringPoint(roi_xy, roi_len)
    print "OX,OY=",ox,oy
      
    outimage = "raster_new.png"
    print cip.getRasterArea(roi_xy)
