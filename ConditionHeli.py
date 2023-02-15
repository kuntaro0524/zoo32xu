import sys,os,math,cv2,socket,time,copy
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")


class Condition:
        def __init__(self, uname, pucks_and_pins, wavelength, h_beam, v_beam, raster_exp, osc_width, total_osc,
                        exp_henderson, exp_time, distance, att_raster, shika_minscore, shika_mindist, loop_size, helical_hbeam,
			helical_vbeam, phosec, ntimes):
                # adopt init args
                for k, v in list(locals().items()):
                        if k == "self": continue
                        setattr(self, k, v)

                self._check_errors()
        # __init__()

        def _check_errors(self):
                prohibit_chars = set(" /_*")
                assert not prohibit_chars.intersection(self.uname)

                assert type(self.pucks_and_pins) == list
                assert all([len(x)==2 for x in self.pucks_and_pins])
                for puck, pins in self.pucks_and_pins:
                        assert type(puck) == str
                        assert not prohibit_chars.intersection(puck)
                        assert all([1 <= x <= 16 for x in pins])
        # _check_errors()

        def show(self):
                print(self.uname)
                for pp in self.pucks_and_pins:
                        print("", pp)

        def customized_copy(self, **kwds):
                c = copy.copy(self)
                for k, v in list(kwds.items()):
                        assert hasattr(c, k)
                        setattr(c, k, v)
                self._check_errors()
                return c
        # customized_copy()

        def make_shika_direction(self, scandir):
                ofs = open(os.path.join(scandir, "shika_auto.config"), "w")
                if self.shika_minscore is not None: ofs.write("min_score= %.3f\n" % self.shika_minscore)
                if self.shika_mindist is not None: ofs.write("min_dist= %.3f\n" % self.shika_mindist)
                ofs.close()
        # make_shika_direction()

# class Condition
