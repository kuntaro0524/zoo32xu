import os
import time
import glob
import re
import numpy
import datetime
import DBinfo

# Version 1.10 mod 2019/10/21
beamline = "BL32XU"


# Reference?: http://demos.jquerymobile.com/1.4.0/popup-iframe/#&ui-state=dialog

class ZOOhtmlLogMaker:
    def __init__(self, root_dir, name, online=True, dbname="zoo.db"):
        self.start_time = time.localtime()
        self.root_dir = root_dir
        self.name = name
        self.online = online

        if self.online:
            self.htmlout = os.path.join(root_dir, time.strftime("report_%y%m%d_%H%M%S.html", self.start_time))
        else:
            self.htmlout = os.path.join(root_dir, "report_%s.html" % name)

        print self.htmlout

        self.dbname = dbname

        self.make_header()
        self.conditions = []
    # __init__()

    def make_header(self):
        self.html_head = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
.dataset_table {
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
    width: 100%%;
    border-collapse: collapse;
}

.dataset_table td, .dataset_table th {
    font-size: 1em;
    border: 1px solid #98bf21;
    padding: 3px 7px 2px 7px;
}

.dataset_table th {
    font-size: 1.1em;
    text-align: left;
    padding-top: 5px;
    padding-bottom: 4px;
    background-color: #A7C942;
    color: #ffffff;
}

.dataset_table tr.alt td {
    color: #000000;
    background-color: #EAF2D3;
}

h1, h2 { text-align: center; text-indent: 0px; font-weight: bold; hyphenate: none;  
      page-break-before: always; page-break-inside: avoid; page-break-after: avoid; }
h3, h4, h5, h6 { text-indent: 0px; font-weight: bold; 
      hyphenate:  none; page-break-inside: avoid; page-break-after: avoid; }

</style>
</head>
<body>
<h1>ZOO report</h1>
<h2>(read from %(dbname)s)</h2>
<h2>%(name)s</h2>
<div align="right">
root dir: %(root_dir)s<br>
%(datename)s on %(cdate)s
</div>
""" % dict(name=self.name, root_dir=self.root_dir, dbname=self.dbname, datename="started" if self.online else "created",
           cdate=time.strftime("%Y-%m-%d %H:%M:%S", self.start_time))
    # make_header()

    def get_sample_info(self, conds):
        # Counting measured sample
        n_meas = 0
        for cond in conds:
            if cond['isDone'] != 0:
                n_meas += 1
            
        wavelength = conds[0]['wavelength']
        exp_ds = conds[0]['exp_ds']
        dist_ds = conds[0]['dist_ds']
        dose_ds = conds[0]['dose_ds']
        ds_vbeam = conds[0]['ds_vbeam']
        ds_hbeam = conds[0]['ds_hbeam']
        att_raster = conds[0]['att_raster']
        dist_raster = conds[0]['dist_raster']
        exp_raster = conds[0]['exp_raster']
        score_min = conds[0]['score_min']
        score_max = conds[0]['score_max']
        cry_max_size_um = conds[0]['cry_max_size_um']
        #cry_max_size_um = cond['cry_max_size_um']

        return n_meas, wavelength, exp_ds, dist_ds, dose_ds, ds_vbeam, ds_hbeam, dist_raster, att_raster, exp_raster, score_min, score_max, cry_max_size_um

    def treat_condition(self, cond):
        root_dir = cond['root_dir']
        p_index = cond['p_index']
        mode = cond['mode']
        puckid = cond['puckid']
        pinid = cond['pinid']
        sample_name = cond['sample_name']
        wavelength = cond['wavelength']
        raster_vbeam = cond['raster_vbeam']
        raster_hbeam = cond['raster_hbeam']
        att_raster = cond['att_raster']
        hebi_att = cond['hebi_att']
        exp_raster = cond['exp_raster']
        dist_raster = cond['dist_raster']
        loopsize = cond['loopsize']
        score_min = cond['score_min']
        score_max = cond['score_max']
        maxhits = cond['maxhits']
        total_osc = cond['total_osc']
        osc_width = cond['osc_width']
        ds_vbeam = cond['ds_vbeam']
        ds_hbeam = cond['ds_hbeam']
        exp_ds = cond['exp_ds']
        dist_ds = cond['dist_ds']
        dose_ds = cond['dose_ds']
        offset_angle = cond['offset_angle']
        reduced_fact = cond['reduced_fact']
        ntimes = cond['ntimes']
        meas_name = cond['meas_name']
        cry_min_size_um = cond['cry_min_size_um']
        cry_max_size_um = cond['cry_max_size_um']
        hel_full_osc = cond['hel_full_osc']
        hel_part_osc = cond['hel_part_osc']
        isSkip = cond['isSkip']
        isMount = cond['isMount']
        isLoopCenter = cond['isLoopCenter']
        isRaster = cond['isRaster']
        isDS = cond['isDS']
        scan_height = cond['scan_height']
        scan_width = cond['scan_width']
        n_mount = cond['n_mount']
        nds_multi = cond['nds_multi']
        nds_helical = cond['nds_helical']
        nds_helpart = cond['nds_helpart']
        t_meas_start = cond['t_meas_start']
        t_mount_end = cond['t_mount_end']
        t_cent_start = cond['t_cent_start']
        t_cent_end = cond['t_cent_end']
        t_raster_start = cond['t_raster_start']
        t_raster_end = cond['t_raster_end']
        t_ds_start = cond['t_ds_start']
        t_ds_end = cond['t_ds_end']
        t_dismount_start = cond['t_dismount_start']
        t_dismount_end = cond['t_dismount_end']

        # is started?

    def get_sample_list(self, conds):
        puck_id_list = []
        pin_id_list = []
        saved_puckid = conds[0]['puckid']
        saved_pinid = conds[0]['pinid']

        n_pins = [0]*8

        for cond in conds:
            puck_id = cond['puckid']
            saved_flag = False
            if len(puck_id_list) != 0:
                for saved_puck in puck_id_list:
                    if saved_puck == puck_id:
                        print "already saved"
                        saved_flag = True
                        break
                    else:
                        continue
                if saved_flag == False:
                    puck_id_list.append(puck_id)
            else:
                puck_id_list.append(puck_id)

        print puck_id_list
        # counting each
        for cond in conds:
            puck_id = cond['puckid']
            pin_id = cond['pinid']
            isDone = cond['isDone']
            if isDone == 0 or isDone > 1000:
                continue
            idx = 0
            print "CHECK ", puck_id, pin_id
            for index in range(0, len(puck_id_list)):
                if puck_id == puck_id_list[index]:
                    n_pins[index] += 1

        print puck_id_list, pin_id_list
        print n_pins

        logstr = ""
        for npin, puck_id in zip(n_pins, puck_id_list):
            print "%10s(%d)" % (puck_id, npin)
            logstr += "%10s(%d) " % (puck_id, npin)

        return logstr

    def add_condition(self, conds, uname):
        n_meas, wavelength, exp_ds, dist_ds, dose_ds, ds_vbeam, ds_hbeam, dist_raster, att_raster, exp_raster, score_min, score_max, cry_max_size_um = self.get_sample_info(conds)
        print "EEEEEEEEEEEEEEEEEEEEEEEE"
        puck_pins = self.get_sample_list(conds)

        #samples = map(lambda x: "%s (%d pins)" % (x[0], len(x[1])), condition.pucks_and_pins)
        #totalpins = sum(map(lambda x: len(x[1]), condition.pucks_and_pins))
        #info = dict(samples=", ".join(samples),
                    #totalpins=totalpins)
        #info.update(condition.__dict__)

        total_osc = conds[0]['total_osc']
        osc_width = conds[0]['osc_width']
        exp_ds = conds[0]['exp_ds']
        sample_name = conds[0]['sample_name']

        info_html = dict(uname=uname, h_beam=ds_hbeam, v_beam=ds_vbeam, att_raster=att_raster, raster_exp=exp_raster, score_min=score_min, score_max=score_max, 
                        crysize = cry_max_size_um, osc_width=osc_width, total_osc=total_osc, dose_ds=dose_ds, exp_time=exp_ds, dist=dist_ds, samples=puck_pins,
                        totalpins=n_meas, dist_raster=dist_raster)
        s = """
<h3>%(uname)s's sample</h3>
<h4>Conditions</h4>
<table class="dataset_table">
 <tr>
  <th>Beam size [&mu;m]</th> <td>h=%(h_beam).2f, v= %(v_beam).2f</td>
 </tr>
 <tr>
  <th>Raster scan</th> <td>Att= %(att_raster).1f%% trans., Exp= %(raster_exp).3f [s], dist=%(dist_raster).1f[mm] </td>
 </tr>
 <tr>
  <th>SHIKA criteria</th> <td>min_score= %(score_min)s, max_score= %(score_max)s, min_dist(for Multi-mode)= %(crysize)s [&mu;m]</td>
 </tr>
 <tr>
  <th>Data collection</th> <td>&Delta;&phi;= %(osc_width).3f&deg;, &phi;-range= %(total_osc).2f&deg;, Dose= %(dose_ds).2f [MGy], ExpTime= %(exp_time).2f [sec], Distance= %(dist).2f [mm]</td>
 </tr>
 <tr>
  <th>Samples (%(totalpins)d pins)</th> <td>%(samples)s</td>
 </tr>
</table>
""" % info_html
        self.conditions.append([s])
    # add_condition()

    def add_result(self, cond):
        dbinfo = DBinfo.DBinfo(cond)

        isDone = dbinfo.getIsDone()
        if isDone == 0 or isDone > 5000:
            return
        nds = dbinfo.getNDS()
        prefix = dbinfo.getPrefix()
        mode = dbinfo.getMode()

        loop_dir = dbinfo.getLoopDir()
        shika_workdir = "%s/" % dbinfo.getSHIKAdir()
        max_score = read_max_score(os.path.join(shika_workdir, "summary.dat"))
        scan_idx = 0

        # Relative path for report
        shika_relpath = os.path.relpath(shika_workdir, self.root_dir)
        loop_relpath = os.path.relpath(loop_dir, self.root_dir)
        #print shika_workdir
        phid = "%d" % dbinfo.getOindex()
        puckid, pinid = dbinfo.getPinInfo()
        scan_height, scan_width = dbinfo.getScanSquare()

        t_meas_start = dbinfo.getMeasStartTime()
        # Dic for html
        if beamline == "BL32XU":
            raster_pic_file = "2d_selected_map.png"
            report_file = "report_zoo.html"
        else:
            raster_pic_file = "plot_2d_n_spots.png"
            report_file = "report.html"

        dichtml = dict(mode=mode, puckid=puckid, pin=pinid, scan_height=scan_height, scan_width=scan_width, nds=nds, max_score=max_score,
            loop_dir=loop_relpath, phid=phid, shika_workdir=shika_relpath, start_time=t_meas_start, raster_pic_file=raster_pic_file, report_html_file=report_file)

        #print dichtml

        s = """
 <tr>
  <td>%(mode)s</td> <td>%(puckid)s</td> <td>%(pin).2d</td> <td>%(scan_height).1f&times;%(scan_width).1f</td> <td>%(nds)d</td> <td>%(max_score).d</td>
  <td><a href="%(loop_dir)s/raster.jpg" onmouseover="document.getElementById('ph-%(phid)s').style.display='block';" onmouseout="document.getElementById('ph-%(phid)s').style.display='none';">loop</a><div style="position:absolute;"><img src="%(loop_dir)s/raster.jpg" height="240" id="ph-%(phid)s" style="zindex: 100; position: absolute; top: -260px; display:none;" /></div>
      <a href="%(shika_workdir)s/%(raster_pic_file)s" onmouseover="document.getElementById('ph2-%(phid)s').style.display='block';" onmouseout="document.getElementById('ph2-%(phid)s').style.display='none';">map</a><div style="position:absolute;"><img src="%(shika_workdir)s/%(raster_pic_file)s" width="600" id="ph2-%(phid)s" style="zindex: 100; position: absolute; top: -400px; display:none;" /></div>
      <a href="%(shika_workdir)s/%(report_html_file)s">detail</a></td>
  <td>%(start_time)s</td>
 </tr>
""" % dichtml
        #self.conditions[-1].append(s)
        self.conditions[-1].append(s)
    # add_result

    def write_html(self):
        kamodir = os.path.join(self.root_dir, "_kamoproc")
        kamo_relpath = os.path.relpath(kamodir, self.root_dir)
        kamo_report = os.path.join(kamo_relpath, "report.html")

        result_header = """
<h4>Results</h4>
<td><a href="%(kamo_dir)s" > Data processing results </a></td>
<table class="dataset_table">
 <tr>
  <th rowspan="2">Mode</th> <th rowspan="2">Puck ID</th> <th rowspan="2">Pin</th> <th colspan="4">Raster result</th> <th rowspan="2">Scan started</th>
 </tr>
 <tr>
                <th>Scan area(V x H) [&mu;m]</th> <th>Hits</th> <th>MaxScore</th> <th>Detail</th>
 </tr>
""" % dict(kamo_dir = kamo_report)
        result_footer = "\n</table>\n"

        ofs = open(self.htmlout, "w")
        ofs.write(self.html_head)
        for c in self.conditions:
            for i, r in enumerate(c):
                ofs.write(r)
                if i==0: ofs.write(result_header)

            ofs.write(result_footer)
                
        ofs.write("\n</body>\n</html>\n")
        ofs.close()

# class ZooHtmlLog

re_scanstart = re.compile("Diffraction scan \(([0-9A-Za-z/:\[\] ]+)\)")

def read_diffscanlog(logf):
    h_grid, v_grid, datestr = None, None, None
    for l in open(logf):
        if "Vertical   scan No. of point:" in l:
            v_grid = int(l.split()[5])
        elif "Horizontal scan No. of point:" in l:
            h_grid = int(l.split()[5])
        elif "Diffraction scan " in l:
            r = re_scanstart.search(l)
            datestr = re.sub("\[[A-Za-z]+\] ", "", r.group(1))
            if datestr.count(":") == 3: datestr = datestr[:datestr.rindex(":")]
            datestr = datestr.replace("/","-")

    return h_grid, v_grid, datestr
# read_diffscanlog()

def read_max_score(datf, kind="n_spots"):
    scores = []
    if not os.path.exists(datf): return float("nan")

    for l in open(datf):
        if " %s " % kind in l: scores.append(float(l.split()[4]))

    print scores
    print "MMMMMM", max(scores)
    if len(scores) > 0:
        return max(scores)
    else:
        return -1
# read_max_score()

def read_nhits(wdir):
    found = glob.glob(os.path.join(wdir, "*_selected.dat"))
    assert len(found) <= 1
    if len(found) == 0: return "", 0
    prefix = os.path.basename(found[0]).replace("_selected.dat", "")

    datf = found[0]
    count = 0
    for l in open(datf):
        if l.startswith("#"): continue
        count += 1

    return prefix, count - 1 # first line is header
# read_nhits()

def make_offline(module_name, root_dir, name):
    md = __import__(module_name)
    zhl = ZooHtmlLog(root_dir, name, online=False)

    for cond in md.conditions:
        zhl.add_condition(cond)
        for trayid, pin_list in cond.pucks_and_pins:
            for pinid in pin_list:
                print "doing", trayid, pinid
                scan_dir = os.path.join(root_dir, "%s-%s-%.2d" % (cond.uname, trayid, pinid), "scan")
                shika_workdir = os.path.join(scan_dir, "_spotfinder")
                raster_log = os.path.join(scan_dir, "diffscan.log")
                if not os.path.exists(raster_log): continue
                h_grid, v_grid, scanstart = read_diffscanlog(raster_log)
                prefix, nhits = read_nhits(shika_workdir)
                zhl.add_result(puckname=trayid, pin=pinid,
                               h_grid=h_grid, v_grid=v_grid,
                               nhits=nhits,
                               shika_workdir=shika_workdir,
                               prefix=prefix,
                               start_time=scanstart)
                zhl.write_html()
# make_offline()

if __name__ == "__main__":
    import sys, ESA

    # reading DB file
    esa = ESA.ESA(sys.argv[1])
    esa_result = esa.getDict()

    for p in esa_result:
        root_dir = p['root_dir']
        break 
        #print root_dir
        #zhl.add_result(self, puckname, pin, h_grid, v_grid, nhits, shika_workdir, prefix, start_time):

    name = sys.argv[2]
    zhl = ZOOhtmlLogMaker(root_dir, name, online=False, dbname=sys.argv[1])
    zhl.add_condition(esa_result, name)
    #make_offline(esa_result, root_dir, name, online=False)
    for p in esa_result:
        #if p['isDS'] != 0:
        zhl.add_result(p)
    #def add_result(self, puckname, pin, h_grid, v_grid, nhits, shika_workdir, prefix, start_time):

    zhl.write_html()
