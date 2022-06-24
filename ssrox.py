    def collectSSROX(self,cond,sphi):
            scan_id="ssrox"
                gxyz=self.sx,self.sy,self.sz
                raster_schedule,raster_path=self.lm.prepRotRaster(scan_id,gxyz,sphi,
                dist=cond.distance,att_idx=self.att_idx,exptime=cond.raster_exp,rot_per_frame=cond.osc_width,
                            crystal_id=cond.sample_name)
                self.zoo.doRaster(raster_schedule)
                self.zoo.waitTillReady()
