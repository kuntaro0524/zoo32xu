import sys, os, math, numpy, scipy
import AnaHeatmap

if __name__ == "__main__":
    phi = 20.0
    prefix = "2d01"
    # scan_path=sys.argv[1]
    # scan_path = "/Users/kuntaro0524/Dropbox/PPPP/Sandbox/14.HITO/01.SHIKA2map"
    # scan_path = "/Users/kuntaro0524/Dropbox/PPPP/Sandbox/14.HITO/02.MergedFunction/Data/"
    scan_path = sys.argv[1]
    ahm = AnaHeatmap.AnaHeatmap(scan_path)

    min_score = int(sys.argv[2])
    max_score = int(sys.argv[3])
    dist_thresh = float(sys.argv[4])

    # Multi crystal 
    # cry_size=float(sys.argv[2])
    # ahm.setMinMax(min_score,max_score)
    cry_array = ahm.searchMulti(prefix,dist_thresh)
    print(len(cry_array))

    for idx,cry in enumerate(cry_array):
        #print "CRYCRYCRYCRYCRYCRYCRYCRY"
        #cry.printAll()
        xyz=cry.getPeakCode()
        print("Advanced gonio coordinates %d: %9.5f %9.5f %9.5f"%(idx,xyz[0],xyz[1],xyz[2]))
        #print cry.getTotalScore(), cry.getRoughEdges(), cry.getCryHsize()
        #print "CRYCRYCRYCRYCRYCRYCRYCRY"
