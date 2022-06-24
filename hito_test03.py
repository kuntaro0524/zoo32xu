import sys,math,numpy,os,socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import datetime, logging
import LoopMeasurement
import Zoo
import ESA
import DiffscanMaster

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))
    zoo=Zoo.Zoo()
    zoo.connect()

    esa=ESA.ESA("zoo.db")
    esa_csv=sys.argv[1]
    is_renew_db=True
    esa.makeTable(esa_csv,force_to_make=is_renew_db)

    # Logging setting
    beamline = "BL32XU"
    logname = "hito.log"
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    conds=esa.getDict()
    cond = conds[0]

    root_dir="/isilon/users/target/target/AutoUsers/200706/kuntaro/TEST1/"
    prefix="vscan"
    lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)
    lm.prepDataCollection()

    phosec = 2E12
    face_angle= -50.0

    dm = DiffscanMaster.NOU(zoo, lm, face_angle, phosec)

    prefix="vscan"
    init_xyz = numpy.array((1.4289,-10.0980,-1.2512))
    scan_length = 100.0

    left_xyz = numpy.array((1.7050, -10.2780, -1.0197))
    right_xyz = numpy.array((1.7050, -10.4180, -1.0197))

    try:
        dm.startHelical(left_xyz, right_xyz, cond, 0, 90.0, "hito_test")
    except Exception as e:
        logger.info(e.args[0])
    # def startHelical(self, left_xyz, right_xyz, cond, osc_start, osc_end, prefix):

    # dm.doVscan(prefix, center, cond, scan_length, face_angle)