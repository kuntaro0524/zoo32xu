import cv2,sys
import matplotlib.pyplot as plt
import numpy as np
import copy

class CryImageProc():
    def __init__(self):
        self.debug = False
        # ROI definition 
        # the values can be reloaded from the target image size
        # by calling 'setImages"
        self.xmin = 100
        self.xmax = 500
        self.ymin = 10
        self.ymax = 470
        self.roi_len_um = 200.0 #[um]

        # Pixel resolution
        self.pix_size=2.780 #[um]
        self.roi_len_pix = self.roi_len_um / self.pix_size
        
        # Gonio direction
        self.gonio_direction = "FROM_RIGHT"
        #self.gonio_direction = "FROM_LEFT"

    def setDebugFlag(self, flag):
        self.debug = flag

    def calcPixLen(self, length):
        self.roi_len_um = length
        self.roi_len_pix = self.roi_len_um / self.pix_size
        return int(self.roi_len_pix)

    def setImages(self, target_file, back_file):
        self.target_file = target_file
        self.back_file = back_file
        self.timg = cv2.imread(target_file)
        self.bimg = cv2.imread(back_file)
        print "TRY1"
        self.tgrey = cv2.cvtColor(self.timg, cv2.COLOR_BGR2GRAY)
        self.bgrey = cv2.cvtColor(self.bimg, cv2.COLOR_BGR2GRAY)
        print "TRY2"
        self.dimg=cv2.absdiff(self.tgrey,self.bgrey)

        self.im_height = self.timg.shape[0]
        self.im_width = self.timg.shape[1]

        self.im_width_um = float(self.im_width) * self.pix_size
        self.im_height_um = float(self.im_height) * self.pix_size

        # target image on the memory for debug image
        self.target_save = copy.deepcopy(self.timg)

        # min - max in XY directions
        self.xmin = 10
        self.xmax = self.im_width - 10
        self.ymin = 10
        self.ymax = self.im_height - 10

    def getImageHeight(self):
        return self.im_height_um

    # This routine squeeze contours 
    # Reduce the dimensions
    def squeeze_contours(self, contours):
        new_array=[]
        # contours structure
        # found contours are included in 'contours'
        # This loop is a treatment for each 'found contour'.
        print "Found contours are not single. Len =", len(contours)
        if len(contours)!=1:
            max_len = -9999
            for i, cnt in enumerate(contours):
                tmplen = len(cnt)
                if tmplen > max_len:
                    max_len = tmplen
                    target_contour = cnt
        else:
            target_contour = contours[0]
    
        # Delete non-required dimension
        single_contour = np.squeeze(target_contour)
        ndim_contour = single_contour.ndim
        print "Acquired contour dimensions = ", ndim_contour

        return single_contour

    def drawContourOnTarget(self, contour, outimage):
        baseimg = copy.deepcopy(self.timg)

        for x,y in contour:
            cv2.circle(baseimg,(x,y),2,(0,0,255),1)
        cv2.imwrite(outimage, baseimg)

    def drawTopOnTarget(self, top_xy, outimage):
        baseimg = copy.deepcopy(self.timg)
        #baseimg = cv2.imread(self.target_file)
        x,y = top_xy
        cv2.circle(baseimg,(x,y),2,(0,0,255),3)
        cv2.imwrite(outimage, baseimg)

    def drawContourTop(self, contour, top_xy, outimage):
        print "drawContourTop"
        #baseimg = cv2.imread(self.target_file)
        baseimg = copy.deepcopy(self.timg)

        for x,y in contour:
            cv2.circle(baseimg,(x,y),1,(0,0,255),1)

        topx, topy = top_xy
        #print topx, topy
        cv2.circle(baseimg,(topx,topy),3,(255,0,0),3)
        cv2.imwrite(outimage, baseimg)
        print "drawContourTop"

    def drawRasterSquare(self, xmin, xmax, ymin, ymax, xcen, ycen, outimage):
        #baseimg = cv2.imread(self.target_file)
        baseimg = copy.deepcopy(self.timg)

        #print xmin, xmax, ymin, ymax
        corner1 = (int(xmin), int(ymin))
        corner2 = (int(xmax), int(ymax))
        cv2.rectangle(baseimg, corner1, corner2, (255,0,0),3)
        cv2.circle(baseimg, (xcen, ycen), 1, (255,255,0),3)
        cv2.imwrite(outimage, baseimg)

    # Largely modified on 2019/05/14 K. Hirata
    # roi_pix_len: ROI horizontal length in unit of [pix]
    def findCenteringPoint(self, roi_xy, roi_pix_len, top_xy):
        half_roi_len_pix = int(roi_pix_len/2.0)
        topx, topy = top_xy
        target_x = topx + half_roi_len_pix
        width_x_ywidth=[]

        print "TARGETTARGET=",target_x

        ymin = 1000
        ymax = 0
        yget = 0

        # Sort along 'x'
        roi_xy_sorted = sorted(roi_xy, key=lambda x: x[0],reverse=False)

        # Loop2
        for x,y in roi_xy_sorted:
            if x > target_x:
                break
            if target_x==x:
                if y >= ymax:
                    ymax = y
                if y <= ymin:
                    ymin = y

        # width of Y direction
        print "YMIN,YMAX=",ymin, ymax
        ycenter = int((ymin + ymax)/2.0)
        return (target_x, ycenter)

    def getRasterArea(self, contour):
        baseimg = copy.deepcopy(self.timg)
        x, y, w, h = cv2.boundingRect(contour)
        roi_xmin = x
        roi_xmax = x + w
        roi_ymin = y
        roi_ymax = y + h
        roi_cenx = (roi_xmin + roi_xmax) / 2.0
        roi_ceny = (roi_ymin + roi_ymax) / 2.0

        cv2.rectangle(baseimg, (roi_xmin, roi_ymin), (roi_xmax, roi_ymax), (255, 125, 125), 2)
        cv2.imwrite("rasterArea.png", baseimg)

        return roi_xmin, roi_xmax, roi_ymin, roi_ymax, roi_cenx, roi_ceny

    def calcYdistAgainstGoniometer(self, ymm):
        if self.gonio_direction == "FROM_RIGHT":
            return -1.0 * ymm
        else:
            return ymm

    def getContour(self):
        filter_thresh = 20
        baseimg = cv2.imread(self.target_file)
        # bluring to eliminate noise
        blur = cv2.bilateralFilter(self.dimg,15,filter_thresh,filter_thresh)
        # debugging file
        cv2.imwrite("blur.png",blur)
        # binirization1
        result1 = cv2.threshold(blur,10,150,0)[1]
        # debugging file
        cv2.imwrite("bin.png", result1)
        # Contour finding
        cont1, hi1 = cv2.findContours(result1 ,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(cont1) == 0:
            print "No contour was found in getContour()"
            return cont1

        if self.debug == True:
            print "the first element of 'cont1' =", cont1[0]
            print "a shape of the element = ", len(cont1)

        # This 'squeezing' makes a single contour of numpy.array(NPOINTS,2)
        cnt = self.squeeze_contours(cont1)

        if self.debug == True:
            print "Hierarchy:",hi1
            print "Contour  :",cont1
            print "Contour type, length=",type(cont1),len(cont1)
            for c in cnt:
                print c

        # debugging file
        cv2.drawContours(baseimg,cont1,-1,(0,255,0),3)
        cv2.imwrite("con.png", baseimg)

        return cnt
    
    def ana_contours(contours):
        for contour in contours:
            if len(contour.shape) == 1:
                print contour
                continue
            else:
                ndata,dummy=contour.shape
                for i in range(0,ndata):
                    print contour[i]

    def find_top_x(self, contours):
        # Gonio from right 
        if self.gonio_direction == "FROM_RIGHT":
            xmin = 9999
            ytop = 9999
            for contour in contours:
                if len(contour.shape) == 1:
                    x,y=contour
                    #print x
                    if xmin > x:
                        xmin = x
                        ytop = y
                else:
                    ndata,dummy=contour.shape
                    for i in range(0,ndata):
                        x,y=contour[i]
                        if xmin > x:
                            xmin = x
                            ytop = y
            return xmin,ytop
        # Gonio from Left
        else:
            xmax = 0
            for contour in contours:
                if len(contour.shape) == 1:
                    x,y=contour
                    print x
                    if xmax < x:
                        xmax = x
                else:
                    ndata,dummy=contour.shape
                    for i in range(0,ndata):
                        x,y=contour[i]
                        if xmax < x:
                            xmax = x
            return xmax, ytop
    
    # This routine selects ROI in horizontal direction
    # len_from_top [pix]
    def selectHoriROI(self, contours, top_xy, len_pix):
        roi_xy=[]
        top_x, ytop = top_xy
        # gonio direction
        # "FROM_RIGHT" : BL32XU, BL41XU
        if self.gonio_direction == "FROM_RIGHT":
            xmin = top_x
            xmax = xmin + len_pix
        # "FROM_LEFT" : BL45XU
        else:
            xmax = top_x
            xmin = top_x - len_pix

        def isInRange(x):
            if x >= xmin and x <= xmax:
                return True
            else:
                return False
        for contour in contours:
            if len(contour.shape) == 1:
                x,y=contour
                if isInRange(x):
                    roi_xy.append((x,y))
                continue
            else:
                ndata,dummy=contour.shape
                for i in range(0,ndata):
                    x,y=contour[i]
                    if isInRange(x):
                        roi_xy.append((x,y))
        return np.array(roi_xy)

    # A squeezed single contour should be given.
    # contour : (N, 2) numpy array
    def isTouchedToEdge(self, contour):
        # edge region
        left_edge = self.xmin
        upper_edge = self.ymin
        lower_edge = self.ymax
        right_edge = self.xmin

        # Flags
        left_flag = False
        right_flag = False
        upper_flag = False
        lower_flag = False

        # Edge detection
        n_true = 0
        for x,y in contour:
            if x < left_edge:
                left_flag = True
            if x > right_edge:
                right_flag = True
            if y > lower_edge:
                lower_flag = True
            if y < upper_edge:
                upper_flag = True

        if left_flag == True: n_true += 1
        if right_flag == True: n_true += 1
        if lower_flag == True: n_true += 1
        if upper_flag == True: n_true += 1

        return left_flag, right_flag, lower_flag, upper_flag, n_true

    def checkExistence(self, contour):
        left_flag, right_flag, lower_flag, upper_flag = self.isTouchedToEdge(contour)
        if (left_flag == False and right_flag == False and 
                lower_flag == False and upper_flag == False):
            print "No loop was detected."
            return False
        return True

    def find_lower_edge(roi_xy):
        lower_edge=[]
        # Loop 1
        for xscan in range(self.xmin,self.xmax):
            ymax=0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    if y > ymax:
                        ymax=y
                        xsave=x
                        ysave=y
                    else:
                        continue
                else:
                    continue
            #print "CONTOUR=",xsave,ysave
            lower_edge.append((xsave,ysave))
    
        return lower_edge

    def getXrangeFromROI(self, roi_xy):
        xmin = 9999
        xmax = 0
        for x,y in roi_xy:
            if x >= xmax:
                xmax = x
            if x <= xmin:
                xmin = x
        return xmin, xmax

    # New function inspired from find_middle_line
    # coded on 2019/04/30 (Last coding in Heisei)
    def findMiddleLine(self, roi_xy):
        middle_line=[]
        xmin, xmax = self.getXrangeFromROI(roi_xy)
        for xscan in range(xmin, xmax+1):
            # No meaning values for searching ymin & ymax
            ymin = 1000
            ymax = 0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    #print "xscan,y=",xscan,y
                    if y >= ymax:
                        ymax = y
                    if y <= ymin:
                        ymin = y
            # Middle point of ymin, ymax
            ymean = int((ymin + ymax)/2.0)
            middle_line.append((xscan,ymean))
    
        return middle_line

    # this finds a neck of the targeted loop
    def findLoopNeck(self, roi_xy):
        width_x_ywidth=[]
        xmin, xmax = self.getXrangeFromROI(roi_xy)
        for xscan in range(xmin, xmax+1):
            # No meaning values for searching ymin & ymax
            ymin = 1000
            ymax = 0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    #print "xscan,y=",xscan,y
                    if y >= ymax:
                        ymax = y
                    if y <= ymin:
                        ymin = y
            # width of Y direction
            ywidth = int(np.fabs(ymin - ymax))
            width_x_ywidth.append((xscan,ywidth))

        ywa = np.array(width_x_ywidth)
        #ywa = sorted(ywa, key=lambda x: x[1],reverse=False)

        for x,y in ywa:
            print "DEDED:",x,y
    
        return width_x_ywidth
    
    # This is old version
    # ROI is set in the 'initizalization' of this class
    # This means that the ROI is very wide and not suitable
    # for finding middle line
    # This code should be removed if this is not required
    def find_middle_line(self, roi_xy):
        middle_line=[]
        # scanning along 'horizontal axis' of ROI
        # 'roi_xy' includes contour of the target
        # at the same value of 'x'(horizontal pixel) 
        # there might be 2 or more 'y' values
        # this function calculates 'middle line' of
        # ymin and ymax in ROI x region.
        for xscan in range(self.xmin, self.xmax):
            # No meaning values for searching ymin & ymax
            ymin = 1000
            ymax = 0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    if y > ymax:
                        ymax = y
                    elif y <= ymin:
                        ymin = y
                    else:
                        continue
                else:
                    continue
            # Middle point of ymin, ymax
            ymean = int((ymin + ymax)/2.0)
            middle_line.append((xscan,ymean))
    
        return middle_line
    
    def find_upper_edge(roi_xy):
        upper_edge=[]
        for xscan in range(self.xmin,self.xmax):
            ymin=999
            xsave=ysave=0
            for x,y in roi_xy:
                if xscan==x:
                    if y < ymin:
                        ymin=y
                        xsave=x
                        ysave=y
                    else:
                        continue
                else:
                    continue
            #print "CONTOUR=",xsave,ysave
            upper_edge.append((xsave,ysave))
    
        return upper_edge
    
    # Fitting 1D for X,Y of lower-edge of the loop
    # from side view camera
    def fitting_pix_line(self, xy_array):
        # Making X,Y numpy array
        xlist=[]
        ylist=[]
        for x,y in xy_array:
            #print "OBS=,",x,y
            xlist.append(x)
            ylist.append(y)
        
        xa=np.array(xlist)
        ya=np.array(ylist)
    
        # Linear arregression
        a,b=np.polyfit(xa,ya,1)
        ab = a,b
        print "A,B = ",ab
        
        # scoring the fitting
        score=0.0
        
        # Print log
        fitted_array = []
        for x,y in zip(xa,ya):
            fitted_y = int(a*x+b)
            residual=(a*x+b)-y
            score+=residual*residual
            fitted_array.append((x, fitted_y))
    
        final_score=score/float(len(xa))
    
        meany = ya.mean()
        angle=np.degrees(np.arctan(a))
        
        return fitted_array,angle,final_score,meany
    
    def analyzeWidth(lower_contour, upper_contour):
        dy_list = []
        for each_lc in lower_contour:
            lx,ly = each_lc
            for each_uc in upper_contour:
                ux,uy = each_uc
                if ux == lx:
                    dy = uy - ly
                    dy_list.append(dy)
                    continue
    
        dya = np.array(dy_list)
        thick_mean = dya.mean()
        thick_std = dya.std()
        print "Thick mean = ",thick_mean,thick_std
        return thick_mean, thick_std
    
    def printROI(self, roi_xy):
        for x,y in roi_xy:
            print x,y

    # Evaluate dekoboko of the line
    def calculateGradient(self, xy_data):
        # Calculate gradient of the line
        xa=[]
        ya=[]
        for x,y in xy_data:
            xa.append(x)
            ya.append(y)
    
        xna = np.array(xa)
        yna = np.array(ya)
        dy = np.gradient(yna)
        
        x_dy_array = []
        for x,y,dy in zip(xna,yna,dy):
            print "GRAD:",x,y,dy
            x_dy_array.append((x,dy))
    
        return x_dy_array

    def calcSmoothHenkyokuten(self, xy_data):
        #return x_ysmooth_grad_array, x_ysmooth_array

        # calculate a smoothen line of loop shape
        xy_smooth_grad, xy_smooth = self.calcSmoothGrad(xy_data)

        # calculate a smoothen nijibibun
        xy_smooth_grad2, xy_smooth2 = self.calcSmoothGrad(xy_smooth_grad)

        for i in range(0, len(xy_smooth_grad)):
            print i
            x = xy_smooth_grad[i][0]
            yg = xy_smooth_grad[i][1]
            ys = xy_smooth[i][1]
            yss = xy_smooth2[i][1]
            ygg = xy_smooth_grad2[i][1]
            print "SSSS:",x,ys,yg,yss,ygg

    def calcSmoothLine(self, xy_data, nsmooth = 15):
        # Calculate gradient of the line
        xa=[]
        ya=[]
        for x,y in xy_data:
            xa.append(x)
            ya.append(y)

        v = np.ones(nsmooth)/5.0 # 'nsmooth' averages
        y2a = np.convolve(ya, v, mode='same')

        for x,y in zip(xa, y2a):
            print "SMOOTH:",x,y

    #def calcYdistAgainstGoniometer

    # smoothing and calculate gradients
    def calcSmoothGrad(self, xy_data, nsmooth = 15):
        # Calculate gradient of the line
        xa=[]
        ya=[]
        for x,y in xy_data:
            xa.append(x)
            ya.append(y)

        v = np.ones(nsmooth)/5.0 # 'nsmooth' averages
        y2a = np.convolve(ya, v, mode='same')

        xna = np.array(xa)
        yna = np.array(ya)
        dy = np.gradient(yna)
        dys = np.gradient(y2a)
        
        x_ysmooth_array = []
        x_ysmooth_grad_array = []
        for x,y,ysmooth,dy,dys in zip(xna,yna,y2a,dy,dys):
            print "SMS:",x,y,ysmooth,dy,dys
            x_ysmooth_array.append((x,int(ysmooth)))
            x_ysmooth_grad_array.append((x,int(dys)))
        
        #return x_ysmooth_array
        return x_ysmooth_grad_array, x_ysmooth_array
    
if __name__=="__main__":
    cip = CryImageProc()
    
    # set Target/Back images
    #testimage = "Data/test03.ppm" # upper hamideteru
    #testimage = sys.argv[1]
    testimage = "Data/test01.ppm"
    cip.setImages(testimage,"Data/bg.ppm")

    prefix = "tttt"
    cont = cip.getContour()
    #cip.printROI(roi_xy)

    #roi_len_pix = cip.setRegionFromTop(300.0)

    top_xy = cip.find_top_x(cont)
    #xmax = xtop + roi_len_pix
    #print "XTOP = ",xtop
    roi_len_um = 200.0
    roi_xy = cip.selectHoriROI(cont, top_xy, roi_len_um)

    print type(roi_xy)
    print roi_xy

    outimage = "con_check.png"
    cip.drawContourOnTarget(roi_xy, outimage)
    outimage = "top_check.png"
    cip.drawTopOnTarget(top_xy, outimage)

    # ROI
    left_flag, right_flag, lower_flag, upper_flag = cip.isTouchedToEdge(roi_xy)
    print "LEFT = ",left_flag
    print "RIGH = ",right_flag
    print "LOWE = ",lower_flag
    print "UPPE = ",upper_flag

    # Defining raster area
    xmin,xmax,ymin,ymax = cip.makeEnvelope(roi_xy)
    outimage = "raster.png"
    cip.drawRasterSquare(xmin, xmax, ymin, ymax, outimage)
    #cip.drawRasterSquare(xmin, xmax, ymin, ymax, outimage)

    # ALL
    roi_xy = cip.selectHoriROI(cont, top_xy, 10000)
    left_flag, right_flag, lower_flag, upper_flag = cip.isTouchedToEdge(roi_xy)
    print "LEFT = ",left_flag
    print "RIGH = ",right_flag
    print "LOWE = ",lower_flag
    print "UPPE = ",upper_flag
    outimage = "con_check2.png"
    cip.drawContourOnTarget(roi_xy, outimage)
    outimage = "top_check2.png"
    cip.drawTopOnTarget(top_xy, outimage)

    conf = open("contour.dat","w")
    for xy in roi_xy:
        x,y = xy
        conf.write("%8d %8d\n"%( x,y))
    conf.close()

    # middle line of target ROI
    #middleLine=cip.find_middle_line(roi_xy)
    #l_angle,l_score,l_meany=cip.fitting_pix_line(middleLine)
    #print l_angle, l_score, l_meany
  
    """
    l_text = "Lower angle = %5.1f score = %5.1f meany = %5.3f"%(l_angle,l_score,l_meany)
    cv2.putText(baseimg, l_text, (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255,255,255), thickness=1)

    line_start_x = xmin
    line_end_x = xmax
    l_line_start_y = int(l_meany)
    xlen = xmax - xmin

    l_diff_y = int(xlen*np.tan(np.radians(l_angle)))

    cv2.line(baseimg, (xmin,l_line_start_y), (xmax,l_line_start_y+l_diff_y),(0,0,255),3)
    cv2.imwrite("%s_ana.png"%prefix,baseimg)
    """
