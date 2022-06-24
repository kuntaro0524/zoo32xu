import os, sys, math, numpy, socket, datetime, time

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio, BS
import Device
import LoopMeasurement
import StopWatch
import MyException
import logging
import AnaHeatmap
import CrystalList
import logging
import logging.config

# 2021/06/10 22:50

beamline="BL32XU"

class Okkotonushi:
    def __init__(self, server_instance, dev_instance, self.zoo_instance, loop_measurement_instance):
        self.s = server_instance
        self.dev = dev_instance
        self.zoo = zoo_instance
        self.lm = loop_measurement_instance

        # Logger
        logname = "./okkotonushi.log"
        logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline,
                                  defaults={'logfile_name': logname})

        self.logger = logging.getLogger('ZOO')

    def conduct(self, puckid, pinid, cond):
        # preparation
        self.dev.colli.off()

        # NAGO initialized for each pin
        nago = IboINOCC.IboINOCC(self.dev)
        prefix = "%s-%02d" % (puckid, pinid)

        nago.setPrefix(prefix)

        # the backlight should be up before mounting the loop
        self.dev.light.on()
        # Mounting the loop
        self.zoo.mountSample(puckid, pinid)
        self.zoo.waitTillReady()

        # Alignment with 'beam stopper on'
        nago.captureMatchBackcam()

        # Alignment without 'beam stopper on'
        self.dev.prepCenteringLargeHolderCam1()
        nago.centerHolder(prefix)

        # Alignment of 'pint' direction
        nago.alignGonioPintDirection(scan_wing=1250.0, scan_div=25.0)

        # Alignment without 'beam stopper on'
        self.dev.prepCenteringLargeHolderCam1()
        nago.fit_tateyoko()

        sx, sy, sz = self.dev.gonio.getXYZmm()
        sphi = self.dev.gonio.getPhi()

        ################# Loop measurement
        cxyz = sx, sy, sz
        raster_id = "2d"
        self.lm.setWavelength(cond['wavelength'])
        self.lm.prepDataCollection()
        # scan V and H length is fixed
        scanv_um = cond['scanv_um']
        scanh_um = cond['scanh_um']
        vstep_um = cond['raster_vbeam']
        hstep_um = cond['raster_hbeam']

        scan_id="2d"
        scan_mode="2D"
        raster_schedule, raster_path = self.lm.rasterMaster(scan_id, scan_mode, cxyz,
                                                            scanv_um, scanh_um, vstep_um, hstep_um,
                                                            sphi, cond)

        self.zoo.doRaster(raster_schedule)
        self.zoo.waitTillReady()

        # Raster scan results
        # Analyzing raster scan results
        try:
            glist = []
            cxyz = sx, sy, sz
            scan_id = self.lm.prefix
            # Crystal size setting
            raster_hbeam = cond['raster_hbeam']
            raster_vbeam = cond['raster_vbeam']

            # getSortedCryList copied from HEBI.py
            # Size of crystals?
            cxyz = 0, 0, 0
            ahm = AnaHeatmap.AnaHeatmap(raster_path)
            min_score = cond['score_min']
            max_score = cond['score_max']
            ahm.setMinMax(min_score, max_score)

            # Crystal size setting
            cry_size_mm = cond['cry_max_size_um'] / 1000.0  # [mm]
            # Analyze heatmap and get crystal list
            crystal_array = ahm.searchMulti(scan_id, cry_size_mm)
            crystals = CrystalList.CrystalList(crystal_array)
            glist = crystals.getSortedPeakCodeList()

            # Limit the number of crystals
            maxhits = cond['maxhits']
            if len(glist) > maxhits:
                glist = glist[:maxhits]

            # number of found crystals
            n_crystals = len(glist)
            # self.esa.updateValueAt(o_index, "nds_multi", n_crystals)

            # Writing down the goniometer coordinate list
            gfile = open("%s/collected.dat" % self.lm.raster_dir, "w")
            gfile.write("# Found crystals = %5d\n" % n_crystals)
            for gxyz in glist:
                x, y, z = gxyz
                gfile.write("%8.4f %8.4f %8.4f\n" % (x, y, z))
            gfile.close()

        except MyException as tttt:
            raise Exception("Something wrong in the main data collection loop.")
            sys.exit(1)

        # Number of detected crystals = 0
        if len(glist) == 0:
            logger.info("Skipping this loop!!")
            # Disconnecting capture in this loop's 'capture' instance
            logger.info("Disconnecting capture")
            lm.closeCapture()
            continue

        # Data collection
        time.sleep(5.0)
        data_prefix = "%s-%02d-multi" % (puckid, pinid)
        multi_sch = lm.genMultiSchedule(sphi, glist, cond, flux, prefix=data_prefix)
        time.sleep(5.0)

        self.dev.gonio.moveXYZmm(sx, sy, sz)
        self.zoo.doDataCollection(multi_sch)
        self.zoo.waitTillReady()

        # Writing CSV file for data processing
        sample_name = cond['sample_name']
        root_dir = cond['root_dir']
        # data_proc_file.write("%s/_kamoproc/%s/,%s,no\n" % (root_dir, prefix, sample_name))
        # data_proc_file.flush()

        # Writing Time table for this data collection
        # Disconnecting capture in this loop's 'capture' instance
        logger.info("Data collection has been finished.")
        lm.closeCapture()

        # prep the next data collection
        self.dev.colli.off()

    self.zoo.disconnect()
