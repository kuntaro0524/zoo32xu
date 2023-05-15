import sys, os, math, numpy, socket, time, cv2
import re

import MyException
import Capture
import Gonio
import Zoom
import CoaxPint
import logging
from configparser import ConfigParser, ExtendedInterpolation


def read_camera_inf(infin):
    ret = {}
    origin_shift_x, origin_shift_y = None, None
    for l in open(infin):
        if "ZoomOptions1:" in l:
            ret["zoom_opts"] = list(map(float, l[l.index(":") + 1:].split()))
        elif "OriginShiftXOptions1:" in l:
            origin_shift_x = list(map(float, l[l.index(":") + 1:].split()))
        elif "OriginShiftYOptions1:" in l:
            origin_shift_y = list(map(float, l[l.index(":") + 1:].split()))

    # TODO read tvextender

    if None not in (origin_shift_x, origin_shift_y):
        assert len(origin_shift_x) == len(origin_shift_y)
        ret["origin_shift"] = list(zip(origin_shift_x, origin_shift_y))

    return ret
# read_camera_inf()

def read_bss_config(cfgin):
    ret = {}
    for l in open(cfgin):
        if "#" in l: l = l[:l.index("#")]
        if "Microscope_Zoom_Options:" in l:
            ret["zoom_pulses"] = list(map(int, l[l.index(":") + 1:].split()))
    return ret

class CoaxImage:
    def __init__(self, ms):
        self.thread = None
        self.ms = ms

        self.logger = logging.getLogger('ZOO').getChild("CoaxImage")

        # configure file を読む
        # Get information from beamline.ini file.
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(os.path.join(os.environ["ZOOCONFIGPATH"], "beamline.ini"))

        # camera.inf パスは beamline.ini から取得
        # section: files, option: camera_inf
        self.camera_inf_path = self.config.get("files", "camera_inf")
        # bss.config パスは beamline.ini から取得
        # section: files, option: bss_config
        self.bss_config_path = self.config.get("files", "bss_config")

        # gonio direction : beamline.local.ini から取得
        self.gonio_direction = self.config.get("experiment", "gonio_direction")

        self.camera_inf = read_camera_inf(self.camera_inf_path)
        self.bss_config = read_bss_config(self.bss_config_path)
        self.coax_pulse2zoom = dict(list(zip(self.bss_config["zoom_pulses"], self.camera_inf["zoom_opts"])))
        self.coax_zoom2pulse = dict(list(zip(self.camera_inf["zoom_opts"], self.bss_config["zoom_pulses"])))
        self.coax_zoom2oshift = dict(list(zip(self.camera_inf["zoom_opts"], self.camera_inf["origin_shift"])))

        # self.config 'coaximage' sectionから数値を読む (beamline.ini)
        self.width = self.config.getfloat("coaximage", "width")
        self.height = self.config.getfloat("coaximage", "height")
        self.pix_size = self.config.getfloat("coaximage", "pix_size")
        self.image_size = self.config.getfloat("coaximage", "image_size")

        # This is very dangerous. Values should be referred from 'bl32xu.conf'
        # このコードもはや不要なのではないかという説が
        # 使用しているのは set_zoom だけなのでこの関数をどっかで使っているかどうかって話 2023/05/12 K.Hirata
        self.coax_zpulse2pint = {0: 20367, -16000: 20367, -32000: 20367, -38000: 20367}  # zoom pulse to pint pulse   YK@210302
        self.gonio = Gonio.Gonio(ms)
        self.capture = Capture.Capture(ms)

        # Flag for dark experiment
        self.isDark = False

    def setDark(self):
        self.isDark = True
        self.capture.setDark()

    def closeCapture(self):
        self.capture.disconnect()

    def read_camera_inf(self, infin):
        ret = {}
        origin_shift_x, origin_shift_y = None, None
        for l in open(infin):
            if "ZoomOptions1:" in l:
                ret["zoom_opts"] = list(map(float, l[l.index(":") + 1:].split()))
            elif "OriginShiftXOptions1:" in l:
                origin_shift_x = list(map(float, l[l.index(":") + 1:].split()))
            elif "OriginShiftYOptions1:" in l:
                origin_shift_y = list(map(float, l[l.index(":") + 1:].split()))
        return ret

    def read_bss_config(self, cfgin):
        ret = {}
        for l in open(cfgin):
            if "#" in l: l = l[:l.index("#")]
            if "Microscope_Zoom_Options:" in l:
                ret["zoom_pulses"] = list(map(int, l[l.index(":") + 1:].split()))

        if None not in (origin_shift_x, origin_shift_y):
            assert len(origin_shift_x) == len(origin_shift_y)
            ret["origin_shift"] = list(zip(origin_shift_x, origin_shift_y))

        return ret

    # read_camera_inf()

    def get_pixel_size(self):  # returns in microns
        # BL45XU
        # X[mm] = X[px] / (C * Zoom * TvExtender)
        # C = 102.4375
        # TvExtender = 1.5
        #
        #     MM2P = _MM2P * ci[GetVideoChannel()].zoom * ci[GetVideoChannel()].tvext / (GetBinning()+1);
        # #define _MM2P 102.4375
        #     double X = ((double)px - WIDTH/2.0) / MM2P;
        # GetBinning()+1 == 4 when 4x4 bin (2 for 2x2 bin, 1 for 1x1 bin)
        # BL45XU MM2P = 102.4375*
        """
        zoom, tvext: see $BLCONFIG/video/camera.inf
        (for st2_coax_1_zoom pulse value, see $CLBONFIG/bss/bss.config Microscope_Zoom_Options:
        """
        """
                XXX Not-thread safe!... but how this happened?
        debug:: video_vdclickemu/put/3812_video_server/ok/0
        Traceback (most recent call last):
          File "shinoda_centering_server.py", line 500, in BtnRun_onclick
            self.intr.do_centering()
          File "shinoda_centering_server.py", line 398, in do_centering
            oneaction(20*rotate_sign, i==0)
          File "shinoda_centering_server.py", line 385, in oneaction
            log_write("%.2d_shift= %.2f%% %.2f%% (%.2f %.2f um)"%((self.count, self.last_shift[0]*100., self.last_shift[1]*100.)+self.calc_shift_by_img_px(sx,sy, unit="um")))
          File "shinoda_centering_server.py", line 256, in calc_shift_by_img_px
            um_per_px = self.get_pixel_size()
          File "shinoda_centering_server.py", line 148, in get_pixel_size
            bin =  self.capture.getBinning()
          File "/isilon/BL32XU/BLsoft/Other/Yam/yamtbx/bl32xu/centering_support/hiratalib/Capture.py", line 178, in getBinning
            return int(sp[-2])
        ValueError: invalid literal for int() with base 10: 'ok'
        video_binning/get/3812_video_server/4/0
        """
        # 2016/09/18 Videosrv is very very unstable
        # binning is 1 though real value is 4
        # bin =  self.capture.getBinning()
        # print "Binnign = ",bin

        # Binning is fixed
        # bin = 1

        # zoom = self.get_zoom()
        # print "Zoom=", zoom

        # videosrv is not stable to acquire 'dynamic parameters' such as zoom, binning
        # DANGEROUS: 
        # they should be corrected after tuning ROI/magnification factor of OAV
        # This is hard-coded on 2019/04/20 K.Hirata
        # return 2.1626 #[um/pixel] at x3.0 magnification
        # This is the newest pixel resolution without an extender 
        # 2019/05/16 updated by K. Hirata
        # For BL32XU
        # return 2.7800 #[um/pixel] at x14.0 magnification

        # 2020/01/21 K.Hirata CentOS6 videosrv running on BSS machine
        return self.pix_size

        """ ORIGINAL CODE
        if zoom == 3.0:
        else:
            return 1.e3/(102.4375*zoom/1.5/bin)
        """

    # get_pixel_size()

    def communicate(self, comstr):
        sending_command = comstr.encode()
        self.ms.sendall(sending_command)
        recstr = self.ms.recv(8000)
        return repr(recstr)

    def get_coax_center(self):
        zoom = self.get_zoom()
        origin_shift = self.coax_zoom2oshift[zoom]
        self.logger.info("Origin shift = %s %s" % origin_shift)
        print("origin_shift = ", origin_shift)
        return origin_shift

    # get_coax_center()

    def get_zoom(self):
        command = "get/bl_32in_st2_coax_1_zoom/query"
        recbuf = self.communicate(command)
        print("RRRRRRRRRRRRRRRR%s"%recbuf)

        sp = recbuf.split("/")
        if len(sp) == 5:
            ret = sp[-2]
            r = re.search("(.*)_([0-9-]+)pulse", ret)
            if r:
                assert r.group(1) == "inactive"
                return self.coax_pulse2zoom[int(r.group(2))]

    # get_zoom()

    def set_zoom(self, zoom):
        if zoom not in self.coax_zoom2pulse:
            print("Possible zoom:", list(self.coax_zoom2pulse.keys()))
            return

        zoomaxis = Zoom.Zoom(self.ms)
        zoom_pulse = self.coax_zoom2pulse[zoom]
        zoomaxis.move(zoom_pulse)

        # Currently this function, at least required for BL32XU, is skipped
        if zoom_pulse not in self.coax_zpulse2pint:
            print("Error. Unknown zoom pulse for pint adjustment:", zoom_pulse)
            return
        else:
            pintaxis = CoaxPint.CoaxPint(self.ms)
            pint_pulse = self.coax_zpulse2pint[zoom_pulse]
            pintaxis.move(pint_pulse)

    # set_zoom()

    # vserv control
    def set_binning(self, bin):
        if bin == 1:
            setbin = 0
        elif bin == 2:
            setbin = 1
        elif bin == 4:
            setbin = 3
        else:
            print("Invalid binning size")
            return None

        self.capture.setBinning(setbin)

    # set_binning()

    def get_cross_pix(self):
        um_per_px = self.get_pixel_size()
        origin_shift = self.get_coax_center()
        origin_shift = [x / um_per_px * 1.e3 for x in origin_shift]
        w, h = self.width, self.height
        cen_x, cen_y = w / 2 + origin_shift[0], h / 2 - origin_shift[1]
        print("cen_x = %8.2f" % cen_x)
        print("cen_y = %8.2f" % cen_y)
        return int(cen_x), int(cen_y)

    def calc_shift_by_img_px(self, sx, sy, units=("um",)):
        """
        sx,sy: x,y on videosrv's coordinate system. origin is left top.
        """
        if sx < 0 or sy < 0:
            print("Invalid sx or sy:", sx, sy)

        um_per_px = self.get_pixel_size()
        origin_shift = self.get_coax_center()
        origin_shift = [x / um_per_px * 1.e3 for x in origin_shift]
        w, h = self.width, self.height
        cen_x, cen_y = w / 2 + origin_shift[0], h / 2 - origin_shift[1]
        self.logger.debug("cen_x, cen_y = (%8.2f, %8.2f)" % (cen_x, cen_y))

        dx, dy = -(sx - cen_x), (sy - cen_y)

        """
        if self.gonio_direction == "FROM_RIGHT":
        # For BL32XU
            dx, dy = -(sx-cen_x), (sy-cen_y)
        ## For BL45XU
        else:
            dx, dy = (sx-cen_x), -(sy-cen_y)
            print "DX,DY=",dx,dy
        """

        ret = []
        for unit in units:
            if sx < 0 or sy < 0:
                ret.append((unit, (0, 0)))
            elif unit == "um":
                ret.append((unit, (dx * um_per_px, dy * um_per_px)))
            elif unit == "px":
                ret.append((unit, (dx, dy)))
            elif unit == "rel":
                ret.append((unit, (dx / float(w), dy / float(h))))
            else:
                raise Exception("Unknown unit: %s" % unit)

        if len(ret) == 1:
            return ret[0][1]
        else:
            return dict(ret)

    # calc_shift_by_img_px()

    def move_by_img_px(self, sx, sy):
        """
        sx,sy: x,y on shinoda's coordinate system. origin is right top.
        """
        if sx < 0 or sy < 0:
            print("Invalid sx or sy:", sx, sy)
            return
        dx, dy = self.calc_shift_by_img_px(sx, sy)
        print("move=", dx, dy)
        self.move(dx, dy)

    # move_by_img_px()

    # Calculation goniometer coordinate from given pixel coordinate
    # gcenx, gceny, gcenz should be given in unit of "mm"
    # ph: pixel coordinate of horizontal axis
    # pv: pixel coordinate of vertical axis
    def calc_gxyz_of_pix_at(self, ph, pv, gcenx, gceny, gcenz, phi):
        print("CoaxImage.calc_gxyz_of_pix_at is called")
        if ph < 0 or pv < 0:
            print("Invalid ph or ph:", ph, pv)
            return
            # distance from center cross [um]
        dh, dv = self.calc_shift_by_img_px(ph, pv)
        # distance from center cross [mm]
        dh_mm = dh / 1000.0
        dv_mm = dv / 1000.0
        # print "%12.4f %12.4f %12.4f"%(gcenx,gceny,gcenz)
        print("dH(mm),dV(mm)=", dh_mm, dv_mm)

        # Horizontal direction -> Gonio Y axis
        gy = gceny + dh_mm  # unit [mm]

        # Vertical direction -> Gonio X/Z axes
        mm_dx, mm_dz = self.gonio.calcUpDown(dv, phi)
        gx = gcenx + mm_dx  # unit [mm]
        gz = gcenz + mm_dz  # unit [mm]

        print("(Xpix,Ypix,GX,GY,GZ)=%5d %5d %12.5f %12.5f %12.5f" % (ph, pv, gx, gy, gz))
        print("CoaxImage.calc_gxyz_of_pix_at ends")
        # print "GX,GY,GZ=",gx,gy,gz
        return gx, gy, gz

    # calc_gxyz_of_pix_at()

    def rotatePhi(self, phi):
        self.gonio.rotatePhi(phi)

    def getGXYZphi(self):
        x, y, z = self.gonio.getXYZmm()
        phi = self.gonio.getPhi()
        return x, y, z, phi

    def moveGXYZphi(self, x, y, z, phi):
        self.gonio.moveXYZmm(x, y, z)
        self.gonio.rotatePhi(phi)

    def calc_gxyz_diff_mm(self, ph, pv):
        if ph < 0 or pv < 0:
            print("Invalid ph or ph:", ph, pv)
            return
            # distance from center cross [um]
        dh, dv = self.calc_shift_by_img_px(ph, pv)
        # distance from center cross [mm]
        dh_mm = dh / 1000.0
        dv_mm = dv / 1000.0

        return dh_mm, dv_mm

    # 2016/04/13 Videoserv unstable
    def get_coax_image(self, imgout):
        print("%s size check" % imgout)
        for i in range(0, 10):
            try:
                self.capture.capture(imgout)
                while (os.path.getsize(imgout) != self.image_size):
                    print("Waiting...for generate the capture image on the storage")
                    time.sleep(1.0)
                print("%s size check Okay" % imgout)
                return True
            except:
                return False

    # get_coax_image()
    def move_to_pix_at(self, ph, pv, gcenx, gceny, gcenz, phi):
        # Calculation of gonio xyz first
        tx, ty, tz = self.calc_gxyz_of_pix_at(ph, pv, gcenx, gceny, gcenz, phi)
        print("move to %10.4f %10.4f %10.4f" % (tx, ty, tz))
        self.gonio.moveXYZmm(tx, ty, tz)


if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ms.connect(("192.168.163.1", 10101))
    ms.connect(("172.24.242.41", 10101))
    coax = CoaxImage(ms)
    print("pix_size=", coax.get_pixel_size())
    print(coax.get_cross_pix())
    # def get_cross_pix(self):

    """
    coax.set_zoom(-48000)
    #coax.set_binning(2)
    filename="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/test001.ppm"
    coax.get_coax_image(filename, 200)

    cip=CIP.CryImageProc(filename)
    edge_codes=cip.get_edge_after_bin(filename)
    grav_x,grav_y,ywmax,xedge,area=cip.getGravWidthArea(edge_codes)
    print grav_x,grav_y,ywmax,xedge,area

    im = cv2.imread(filename)
    cv2.circle(im,(grav_x,grav_y),2,(0,0,255),2)
    cv2.circle(im,(xedge,grav_y),2,(0,0,255),2)
    center_x=int((grav_x+xedge)/2.0)
    cv2.circle(im,(center_x,grav_y),2,(0,0,255),2)

    start_x=xedge
    dist_cenx_edgex=np.fabs(center_x-xedge)
    end_x=int(xedge+2*dist_cenx_edgex)

    start_y=int(grav_y-int(ywmax/2.0))
    end_y=int(grav_y+int(ywmax/2.0))

    cv2.rectangle(im,(start_x,start_y),(end_x,end_y),(0,255,0),1)

    cv2.imshow("Show Image",im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """
