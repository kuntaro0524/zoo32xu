"""
Assuming cheetah_client.py started with --pub-host="ipaddr:5559".
Here ipaddr is of the host where this script runs.
"""

import iotbx.phil
import libtbx.phil
import zmq
import time

master_params_str = """\
distl {
  res {
    outer = 5.
      .type=float
      .help="High resolution limit in angstroms"
    inner = 30.
      .type=float
      .help="Low resolution limit in angstroms"
  }
}
cheetah {
 ADCthresh = 5
  .type = float
 MinSNR = 8
  .type = float
 MinPixCount = 3
  .type = int
 MaxPixCount = 40
  .type = int
 LocalBGRadius = 2
  .type = int
 MinPeakSeparation = 0
  .type = float
 algorithm = 8
  .type = int
  .help = 6 or 8
}
"""

def run_not_from_args(subport=5559):
    master_params = libtbx.phil.parse(master_params_str)
    working_params = master_params.fetch(sources=[libtbx.phil.parse("")])
    params = working_params.extract()

    # change params (example below)
    params.distl.res.outer = 3
    params.cheetah.MinSNR = 5

    zmq_context = zmq.Context()
    control_send = zmq_context.socket(zmq.PUB)

    try:
        print("BINDS!")
        control_send.bind("tcp://*:%d"%subport)
    except zmq.ZMQError as e:
        print(("Error in binding SUB port: %s" % e.strerror))
        return

    control_send.send_pyobj(dict(params=params))
# run_not_from_args()

def run_from_args(args, subport=5559):
    cmdline = iotbx.phil.process_command_line(args=args, master_string=master_params_str)
    params = cmdline.work.extract()

    zmq_context = zmq.Context()
    control_send = zmq_context.socket(zmq.PUB)
    
    libtbx.phil.parse(master_params_str).format(params).show(prefix="")
    

    try:
        control_send.bind("tcp://*:%d"%subport)
    except zmq.ZMQError as e:
        print(("Error in binding SUB port: %s" % e.strerror))
        return

    print("Conn.")
    time.sleep(1)

    control_send.send_pyobj(dict(params=params))
    print("Sent.", params)
# run_from_args()

if __name__ == "__main__":
    import sys
    run_from_args(sys.argv[1:])
    #run_not_from_args()
