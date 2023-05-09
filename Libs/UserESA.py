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
import configparser
import pandas as pd
import numpy as np

class UserESA():
    def __init__(self, fname=None, root_dir=".", beamline=None):
        # beamlineの名前はconfigから読む
        self.config = configparser.ConfigParser()
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)

        self.fname = fname
        self.isRead = None
        self.isPrep = None
        self.isGot  = None
        self.zoocsv = None
        self.contents = []

        # configure file から情報を読む: beamlineの名前
        self.beamline = self.config.get("beamline", "beamline")
        import BeamsizeConfig
        self.bsconf = BeamsizeConfig.BeamsizeConfig()

    def setDefaults(self):
        # self.df に以下のカラムを追加する
        # self.config.getfloat("experiment", "score_min") などで読み込む
        # "score_min"
        # "score_max"
        # "raster_dose"
        # "dose_ds"
        # "raster_roi"
        # "exp_raster"
        # "att_raster"
        # "hebi_att"
        # "cover_flag"
        self.df["score_min"] = self.config.getfloat("experiment", "score_min")
        self.df["score_max"] = self.config.getfloat("experiment", "score_max")
        self.df["raster_dose"] = self.config.getfloat("experiment", "raster_dose")
        self.df["dose_ds"] = self.config.getfloat("experiment", "dose_ds")
        self.df["raster_roi"] = self.config.getfloat("experiment", "raster_roi")
        self.df["exp_raster"] = self.config.getfloat("experiment", "exp_raster")
        self.df["att_raster"] = self.config.getfloat("experiment", "att_raster")
        self.df["hebi_att"] = self.config.getfloat("experiment", "hebi_att")
        self.df["cover_flag"] = self.config.getint("experiment", "cover_flag")

    # ビームライン、実験モードと結晶のタイプから実験パラメータを取得する
    def getParams(self, desired_exp_string, type_crystal, mode):
        type_crystal = type_crystal.lower()
        desired_exp_string = desired_exp_string.lower()

        # DEFAULT PARAMETER
        # beamline.ini から読む
        #self.beamline = self.config.get("beamline", "beamline")
        score_min   = self.config.getfloat("experiment", "score_min")
        score_max   = self.config.getfloat("experiment", "score_max")
        raster_dose = self.config.getfloat("experiment", "raster_dose")
        dose_ds     = self.config.getfloat("experiment", "dose_ds")
        raster_roi  = self.config.getfloat("experiment", "raster_roi")
        exp_raster = self.config.getfloat("experiment", "exp_raster")
        att_raster  = self.config.getfloat("experiment", "att_raster")
        hebi_att    = self.config.getfloat("experiment", "hebi_att")
        cover_flag  = self.config.getint("experiment", "cover_flag")

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
    
    def checkLN2flag(self):
        # self.dfのカラム "ln2_flag" について以下のパターンで処理を行う
        # 'NaN'であれば ０
        # 'Yes' or 'yes' or "YES" であれば １
        # 'Unavailable' であれば ０
        # それ以外であれば ０
        self.df['ln2_flag'] = self.df['ln2_flag'].fillna(0)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('Yes', 1)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('yes', 1)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('YES', 1)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('Unavailable', 0)

        print(self.df)

    def checkZoomFlag(self):
        # self.dfのカラム "ln2_flag" について以下のパターンで処理を行う
        # 'NaN'であれば ０
        # 'Yes' or 'yes' or "YES" であれば １
        # 'Unavailable' であれば ０
        # それ以外であれば ０
        self.df['zoom_flag'] = self.df['zoom_flag'].fillna(0)
        self.df['zoom_flag'] = self.df['zoom_flag'].replace('Yes', 1)
        self.df['zoom_flag'] = self.df['zoom_flag'].replace('yes', 1)
        self.df['zoom_flag'] = self.df['zoom_flag'].replace('YES', 1)
        # self.df['zoom_flag']が　'No' or 'no' or 'NO' or 'Unavailable' であれば ０
        self.df['zoom_flag'] = self.df['zoom_flag'].replace('No', 0)
        self.df['zoom_flag'] = self.df['zoom_flag'].replace('no', 0)
        self.df['zoom_flag'] = self.df['zoom_flag'].replace('NO', 0)
        self.df['zoom_flag'] = self.df['zoom_flag'].replace('Unavailable', 0)

        # DataFrameを省略することなく表示する
        pd.set_option('display.max_rows', None)
        print(self.df)

    def checkPinFlag(self):
        print(self.df['pin_flag'])
        # self.df['wait_time']の初期値を30.0とする
        self.df['wait_time'] = 30.0
        # self.df にはすでに"pin_flag"があるので、それを利用する
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "spine"　であれば self.df['wait_time'] = 10.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'spine', 'wait_time'] = 10.0
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "als + ssrl"　であれば self.df['wait_time'] = 20.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'als + ssrl', 'wait_time'] = 20.0
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "copper"　であれば self.df['wait_time'] = 60.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'copper', 'wait_time'] = 60.0
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "no-wait"　であれば self.df['wait_time'] = 0.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'no-wait', 'wait_time'] = 0.0

    def fillFlux(self):
        # self.df['flux']の数値を読み込む
        # self.bsconf.getFluxAtWavelength(hbeam, vbeam, wavelength)を呼び出す
        # この関数の引数に self.df['hbeam'], self.df['vbeam'], self.df['wavelength']を渡す
        # 戻り値はfluxである
        # fluxの値をself.df['flux']に代入する
        self.df['flux'] = self.df.apply(lambda x: self.bsconf.getFluxAtWavelength(x['hbeam'], x['vbeam'], x['wavelength']), axis=1)

    def splitBeamsizeInfo(self):
        # self.df['beamsize']の文字列をself.checkBeamsizeの引数として渡す
        # self.checkBeamsize()は self.df['beamsize']を引数とし、戻り値は(hbeam, vbeam)である(どちらもfloatのタプル)
        # hbeam, vbeamの数値は新たなカラムとしてself.dfに追加される 'hbeam', 'vbeam'
        self.df['hbeam'], self.df['vbeam'] = zip(*self.df['beamsize'].map(self.checkBeamsize))
        
    # Raster scanの露光条件を定義する
    def defineScanCondition(self, desired_exp_string, wavelength, beam_h, beam_v, flux, exp_raster):
        # Dose for scan
        import Raddose
        e = Raddose.Raddose()
    
        # energy <> wavelength 変換
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

    def read_new(self):
        # pandasを利用して.xlsxファイルを読み込む
        # tabの名前を指定して読む "ZOOPREP_YYMMDD_NAME_BLNAME_v2"
        # pandasを利用してエクセルのタブのリストを取得して表示する
        print(pd.ExcelFile(self.fname).sheet_names)

        # エクセルのタブ名が "ZOOPREP_YYMMDD_NAME_BLNAME_v2" であるタブを読み込む
        # Index(['PuckID', 'PinID', 'SampleName', 'Objective', 'Mode', 'HA',
        # 'Wavelength [Å]', 'Hor. scan length [µm]', 'Resolution limit [Å]',
        # 'Beam size [um]\n(H x V)', 'Crystal size [µm]',
        # '# of crystals\n / Loop', 'Total osc \n/ Crystal', 'Osc. Width',
        # 'LN2\nSplash', 'PIN Type', 'Zoom\nCapture', 'Unnamed: 17',
        # 'Confirmation required'],
        # column名を指定する
        columns = ['puckid', 'pinid', 'sample_name', 'desired_exp', 'mode', 'anomalous_flag', \
            'wavelength', 'loop_size', 'resolution_limit', 'beamsize', 'max_crystal_size', 'n_crystals', 'total_osc', 'osc_width', \
                'ln2_flag', 'pin_flag', 'zoom_flag', 'what', 'confirmation_require']

        # データは4行目から
        self.df = pd.read_excel(self.fname, sheet_name="ZOOPREP_YYMMDD_NAME_BLNAME_v2", header=2)
        # 列名を指定する
        self.df.columns = columns
        self.isPrep = True
        
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

        camera_len = math.floor(camera_len*10)/10 # 2020/11/24 modified by HM 

        return camera_len

    def checkBeamsize(self, beamsize_char):
        cols = beamsize_char.split('x')
        if len(cols) > 1:
            hbeam = float(cols[0])
            vbeam = float(cols[1])
            return hbeam, vbeam

    # データフレームの分解能限界からカメラ長を計算して格納する
    def addDistance(self):
        self.df['distance'] = self.df.apply(lambda x: self.calcDist(x['wavelength'], x['resolution_limit']), axis=1)
        print(self.df['distance'])

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
            # resolution_limitが10.0より大きい場合は1.5に設定するという意味だそうな
            resolution_limit    = float(cols[8]) if float(cols[8]) <= 10.0 else 1.5
            max_crystal_size    = float(cols[10])
            beamsize            = cols[9]
            # sample名に()が入っている場合は-に置換する
            sample_name         = cols[2].replace("(", "-").replace(")", "-")
            desired_exp         = cols[3]
            n_crystals          = int(cols[11])
            total_osc           = float(cols[12])
            osc_width           = float(cols[13])
            type_crystal        = "soluble"
            anomalous_flag      = cols[5]
            # LN2 flagについては、"no"の場合は0、それ以外は1とする
            ln2_flag            = 0 if cols[14].lower == "no" else 1
            pin_flag            = cols[15]
            # Zoom flag については、"no"の場合は0、それ以外は1とする
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

            # カメラ長を計算する 最も近い整数にしてしまう
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
    u2db.read_new()
    u2db.checkLN2flag()
    u2db.checkZoomFlag()
    u2db.addDistance()
    u2db.checkPinFlag()
    u2db.splitBeamsizeInfo()
    u2db.fillFlux()
    u2db.setDefaults()

    print(u2db.df.flux)
    print(u2db.df.columns)
    #u2db.makeCondList()
    #u2db.makeCSV(u2db.csvout)