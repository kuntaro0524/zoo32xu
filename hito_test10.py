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
    prefix = "dddd"
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    conds=esa.getDict()
    cond = conds[0]

    root_dir="/isilon/users/target/target/AutoUsers/200706/kuntaro/TEST1/"

    lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)
    lm.prepDataCollection()

    phosec = 5E13
    face_angle= 130.0

    dm = DiffscanMaster.NOU(zoo, lm, face_angle, phosec)


    prefix="heltest1"
    left_xyz = numpy.array((1.6639,-9.9180,-0.6521))
    right_xyz = numpy.array((1.6155,-10.0780,-0.7395))

    dc_block = {}
    dc_block['lxyz'] = left_xyz
    dc_block['rxyz'] = right_xyz
    dc_block['osc_start'] = -10.0
    dc_block['osc_end'] = 10.0
    dc_block['mode']="helical_full"

    try:
        dm.dododo(cond, dc_block, dc_index=0)

    except Exception as e:
        logger.info(e.args[0])

    dc_block = {}
    dc_block['lxyz'] = numpy.array((1.7700,    -9.8780,    -0.4602 ))
    dc_block['rxyz'] = numpy.array((1.7412,    -9.7780,    -0.5124))
    dc_block['osc_start'] = -40.0
    dc_block['osc_end'] = 40.0
    dc_block['mode']="helical_part"

    try:
        dm.dododo(cond, dc_block, dc_index=1)

    except Exception as e:
        logger.info(e.args[0])

    dc_block = {}
    dc_block['cxyz'] = numpy.array((1.7508,   -10.1380,    -0.4950))
    dc_block['osc_start'] = -40.0
    dc_block['osc_end'] = 40.0
    dc_block['mode']="single_part"

    try:
        dm.dododo(cond, dc_block, dc_index=2)

    except Exception as e:
        logger.info(e.args[0])