import sys, os, math, time, tempfile, datetime
import Raddose

if __name__ == "__main__":
    e = Raddose.Raddose()
    # 6.0-30.0 keVまでを0.1 keV刻みで計算
    import numpy as np
    en_list = np.arange(6.0, 30.0, 0.1)

    ofile = open("dose.txt", "w")
    for en in en_list:
        #dose = e.getDose(beam_h, beam_v, flux, exptime, energy=en)
        dddd=e.getDose1sec(1.0, 1.0, 1.0, 1.0, energy=en)
        ofile.write("%8.1f %8.3f MGy\n" % (en, dddd))
    ofile.close()