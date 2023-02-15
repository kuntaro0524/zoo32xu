#coding: UTF-8
"""
(C) RIKEN/JASRI 2020 :
Author: Kunio Hirata
ESA -> the main function : the class to read & write zoo database file
This code is originally written by K.Hirata and modified by N.Mizuno.
NM added function to read xlsx file directly and output zoo.db by using ESA class.

Author: Nobuhiro Mizuno
"""
import sys, os, math, numpy, csv, re, datetime, xlrd, codecs

class UserESA():
    def __init__(self, fname=None, root_dir=".", beamline=None):
        self.beamline = beamline
        self.fname = fname
        self.isRead = None
        self.isPrep = None
        self.isGot  = None
        self.zoocsv = None
        self.contents = []

        sys.path.append("/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/"%self.beamline.upper())
        import BeamsizeConfig
        if beamline.upper() == "BL32XU":
            self.confdir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
        else:
            self.confdir = "/isilon/blconfig/%s/" % beamline.lower()
            print("DIRDIR=", self.confdir)
        self.bsconf = BeamsizeConfig.BeamsizeConfig(self.confdir)

    def getParams(self, desired_exp_string, type_crystal, mode):
        type_crystal = type_crystal.lower()
        desired_exp_string = desired_exp_string.lower()

        # DEFAULT PARAMETER
        score_min   = 10
        score_max   = 100
        raster_dose = 0.1
        dose_ds     = 10
        raster_roi  = 1
        if self.beamline.lower() == "bl32xu":
            exp_raster = 0.01
        elif self.beamline.lower() == "bl45xu":
            exp_raster = 0.02
        att_raster  = 20
        hebi_att    = 20
        cover_flag  = 1

        # PARAMTER CONDITION
        self.param = {
            "scan_only":{
                "soluble":{
                    "single":   [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
                    "helical":  [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
                    "multi":    [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
                    "mixed":    [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
                },
            },
            "normal":{
                "soluble":{
                    "single":   [score_min, score_max, 0.1, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "helical":  [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "multi":    [score_min, score_max, 0.1, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "mixed":    [score_min, 9999, 0.1, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                },
            },
            "high_dose_scan":{
                "soluble":{
                    "single":   [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "helical":  [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "multi":    [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "mixed":    [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                },
            },
            "ultra_high_dose_scan":{
                "soluble":{
                    "single":   [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                    "helical":  [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                    "multi":    [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                    "mixed":    [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                },
            },
            "phasing":{
                "soluble":{
                    "single":   [score_min, score_max, 0.1, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "helical":  [score_min, 9999, 0.05, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "multi":    [score_min, score_max, 0.1, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                    "mixed":    [score_min, score_max, 0.1, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                },
            },
            "rapid":{
                "soluble":{
                    "single":   [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                    "helical":  [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                    "multi":    [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                    "mixed":    [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                },
            },
        }

        return self.param[desired_exp_string][type_crystal][mode]

    def defineScanCondition(self, desired_exp_string, wavelength, beam_h, beam_v, flux, exp_raster):
        # Dose for scan
        import Raddose
        e = Raddose.Raddose()
    
        energy = 12.3984 / wavelength

        # Normal raster scan : 2E10 photons/frame
        if desired_exp_string == "normal" or desired_exp_string == "scan_only" or desired_exp_string == "phasing" or desired_exp_string == "rapid":
            photons_per_image = 4E10 # photons
            photons_per_exptime = flux * exp_raster
            trans = photons_per_image / photons_per_exptime * 100.0
            print("Transmission = %10.5f" % trans)
            att_raster = trans
            hebi_att = trans

        elif desired_exp_string == "high_dose_scan":
            dose_for_raster = 0.3 # MGy
            dose_per_exptime = e.getDose(beam_h, beam_v, flux, exp_raster, energy=energy)
            trans = dose_for_raster / dose_per_exptime * 100.0
            print("Transmission = %10.5f" % trans)

        elif desired_exp_string == "ultra_high_dose_scan":
            dose_for_raster = 1.0  # MGy
            dose_per_exptime = e.getDose(beam_h, beam_v, flux, exp_raster, energy=energy)
            trans = dose_for_raster / dose_per_exptime * 100.0
            print("Transmission = %10.5f" % trans)

        # When a calculated transmission exceeds '1.00'
        if trans > 100.0:
            mod_exp_raster = exp_raster * trans / 100.0
            trans = 100.0
            print("The transmission is over 1.000!", trans)
            print("Exposure time for raster scan is set to %5.2f sec" % mod_exp_raster)
        else:
            mod_exp_raster = exp_raster

        return trans, mod_exp_raster

    def makeCSV(self, zoo_csv=None):
        if not zoo_csv:
            return None

        ctime=datetime.datetime.now()
        time_str = datetime.datetime.strftime(ctime, '%y%m%d%H%M%S')
        db_fname = "zoo_%s.db"%time_str

        import ESA
        esa = ESA.ESA(db_fname)
        if os.path.exists(self.csvout):
            esa.makeTable(self.csvout, force_to_make=True)

        return

    def read(self):
        self.cols = []

        self.basename = os.path.splitext(self.fname)

        if self.basename[1].count("xls"):
            book = xlrd.open_workbook(self.fname)
            for sname in book.sheet_names():
                #print("SNAME=",sname)
                # 2021/04/06 modified by mat (can read both current and previous sample sheet)
                if sname.count("Sheet") or sname.count("ZOOPREP_YYMMDD_NAME_BLNAME_v2"):
                    sheet = book.sheet_by_name(sname)
                    xkey = None
                    print(("ROW=",sheet.nrows))
                    for row in range(sheet.nrows):
                        line = []
                        print(sheet.cell(row, 0))
                        if sheet.cell(row, 0).value == "PuckID":
                            xkey = True
                        if xkey and sheet.cell(row, 0).value == "":
                            break
                        for col in range(sheet.ncols):
                            cell = sheet.cell(row, col)
                            if cell.ctype == xlrd.XL_CELL_NUMBER:
                                outval = cell.value
                                if outval.is_integer():
                                    outval = int(outval)
                            else:
                                outval = cell.value.encode('utf-8')
                            line.append(str(outval))
                        self.cols.append(line)
#            print(self.cols)
#            sys.exit()
#            for sheet in book.sheets():
#                for row in range(sheet.nrows):
#                    line = []
#                    for col in range(sheet.ncols):
#                        cell = sheet.cell(row, col)
#                        if cell.ctype == xlrd.XL_CELL_NUMBER:
#                            outval = cell.value
#                            if outval.is_integer():
#                                outval = int(outval)
#                        else:
#                            print(cell.value)
#                            outval = cell.value.encode('utf-8')
#                        line.append(str(outval))
#                    self.cols.append(line)
        elif self.basename[1].count("csv"):
            lines = open(self.fname, "r").readlines()
            for line in lines:
                cols = line.splilt(',')
                self.cols.append(cols)

        self.isRead = True
        return self.isRead

    def exRealList(self):
        if not self.isRead:
            self.read()
        print((self.cols))
        key = None
        for cols in self.cols:
            if cols[0] == "":
                key = None
            if key:
                self.contents.append(cols)
            if cols[0] == "PuckID":
                key = True

        self.isPrep = True
        return self.isPrep

    def calcDist(self, wavelength, resolution_limit):
        if self.beamline.lower() == "bl32xu":
            min_dim = 233.0
        elif self.beamline.lower() == "bl45xu":
            min_dim = 422.0
        theta = numpy.arcsin(wavelength / 2.0 / resolution_limit)
        bunbo = 2.0 * numpy.tan(2.0 * theta)
        camera_len = min_dim / bunbo
        # camera_len_minimum is 125.0 mm at BL32XU (added by HM 2020/11/24)
        if camera_len <= 125.0 and self.beamline.lower() == "bl32xu":
            camera_len = 125.0
        return camera_len

    def checkBeamsize(self, beamsize_char):
        cols = beamsize_char.split('x')
        if len(cols) > 1:
            hbeam = float(cols[0])
            vbeam = float(cols[1])
            return hbeam, vbeam

    def makeCondList(self):
        if self.isGot:
            return
        if self.fname.count("_zoo.csv"):
            self.csvout = self.fname
            return
        if not self.isPrep:
            self.exRealList()

        self.conds  = []
        p_index = 0

        keys = "root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,raster_hbeam,att_raster,\
        hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam,\
        exp_ds,dist_ds,dose_ds,offset_angle,reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um,\
        hel_full_osc,hel_part_osc".split(",")

        pin_param = []
        line_strs = []
        line_strs.append("root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,"
                         "raster_hbeam,att_raster,hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,"
                         "maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam,exp_ds,dist_ds,dose_ds,offset_angle,"
                         "reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um,hel_full_osc,hel_part_osc,"
                         "raster_roi,ln2_flag,cover_scan_flag,zoomcap_flag,warm_time")

        for cols in self.contents:
            puckid              = cols[0].replace("-", "")
            pinid               = cols[1]
            mode                = cols[4]
            print((cols[6]))
            wavelength          = float(cols[6])
            loop_size           = float(cols[7])
            resolution_limit    = float(cols[8]) if float(cols[8]) <= 10.0 else 1.5
            max_crystal_size    = float(cols[10])
            beamsize            = cols[9]
            sample_name         = cols[2].replace("(", "-").replace(")", "-")
            desired_exp         = cols[3]
            n_crystals          = int(cols[11])
            total_osc           = float(cols[12])
            osc_width           = float(cols[13])
            type_crystal        = "soluble"
            anomalous_flag      = cols[5]
            ln2_flag            = 0 if cols[14].lower == "no" else 1
            pin_flag            = cols[15]
            zoom_flag           = 0 if cols[16].lower == "no" else 1

            if pin_flag.lower() == "spine":
                wait_time = 10
            elif pin_flag.lower() == "als + ssrl":
                wait_time = 20
            elif pin_flag.lower() == "copper": 
                wait_time = 60
            elif pin_flag.lower() == "no-wait":
                wait_time = 0
            else:
                wait_time = 30

            #distance = math.floor(self.calcDist(wavelength, resolution_limit)/10)*10 # by N.Mizuno at 2020/02/06
            distance = math.floor(self.calcDist(wavelength, resolution_limit)*10)/10 # 2020/11/24 modified by HM 
            hbeam, vbeam = self.checkBeamsize(beamsize)

            # Reading flux value
            flux = self.bsconf.getFluxAtWavelength(hbeam, vbeam, wavelength)
            print("Flux value is read from beamsize.conf: %5.2e\n" % flux)

            # Dose estimation for raster scan
            score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag = self.getParams(desired_exp, type_crystal, mode)
            # Calculate 'att_raster', 'exp_raster'
            att_raster, mod_exp_raster = self.defineScanCondition(desired_exp, wavelength, hbeam, vbeam, flux, exp_raster)

            exp_raster = round(mod_exp_raster, 3)
            hebi_att = round(att_raster,3)
            att_raster = hebi_att

            cry_min_size = max_crystal_size
            cry_max_size = max_crystal_size
            # Special code
            if mode == "multi" and cry_max_size > 100.0:
                cry_min_size = 25.0
                cry_max_size = 25.0

            self.conds.append((puckid, pinid, mode, wavelength, loop_size, resolution_limit, max_crystal_size, beamsize, 
                sample_name, desired_exp, n_crystals, total_osc, osc_width, type_crystal, anomalous_flag))

            if self.beamline.lower() == "bl32xu":
                dist_raster = 200.0
            elif self.beamline.lower() == "bl45xu":
#                dist_raster = 500.0
                dist_raster = math.floor(self.calcDist(wavelength, 2.53)/10)*10

            line_str = "%s,%d,%s,%s,%s,%s," % (root_dir,p_index,mode,puckid,pinid,sample_name)
            line_str += "%7.5f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%f,%f,%f,%f,0.02,%f,%f,%f,%f,%f,%s,%f,%f,%f," \
                        "%f,%d,%d,%d,%d,%d" % \
                (wavelength,vbeam,hbeam,att_raster,hebi_att,exp_raster,dist_raster,
                loop_size,score_min,score_max,n_crystals,total_osc,osc_width,vbeam,hbeam,distance,dose_ds,0.0,1.0,1.0,
                 desired_exp,cry_min_size,cry_max_size,60,40,raster_roi,ln2_flag,cover_flag,zoom_flag,wait_time)
            line_strs.append(line_str)
            pin_param = []
            p_index += 1

        self.csvout = "%s_zoo.csv"%self.basename[0]
        fin = open(self.csvout, "w")
        for line in line_strs:
            fin.write("%s\n" % line)
        fin.close()

        self.isGot = True
        return pin_param

if __name__ == "__main__":
    root_dir = os.getcwd()
    u2db = UserESA(sys.argv[1], root_dir, beamline="BL32XU")
    u2db.makeCondList()
    u2db.makeCSV(u2db.csvout)
