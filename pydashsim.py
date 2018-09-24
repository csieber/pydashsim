import logging
import os

import numpy as np
import simpy
import argparse

from sim.connection import Connection
from sim.player import Player

from sim.log import LogDir
from sim.logics.noadaptationlogic import NoAdaptationLogic


def read_input(trace, video):

    video = np.genfromtxt(video, skip_header=1, delimiter=',')
    traffictrace = np.genfromtxt(trace, skip_header=1, delimiter=',')

    # Remove duration for now
    video = video[:, 1:]

    return traffictrace, video


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Execute the simulation.")
    parser.add_argument("-o", "--opt_dir", help="Output folder", type=str, default="out")
    parser.add_argument("-t", "--trace", help="Goodput trace to use.", required=True)
    parser.add_argument("-s", "--segments", help="Video to use.", required=True)
    parser.add_argument("-l", "--logic", help="Adaptation logic (NO, KLUDCP, TRDA)", type=str, default="NO")
    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')

    cmdargs = parser.parse_args()

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}

    if cmdargs.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    traffictrace, video = read_input(cmdargs.trace, cmdargs.segments)

    env = simpy.Environment()

    # If it does not exist create directory for logs
    log_dir = os.path.join(cmdargs.opt_dir, cmdargs.logic)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Attach a LogDir object to the sim environment
    setattr(env, 'logdir', LogDir(log_dir))

    conn = Connection(env, traffictrace)

    if cmdargs.logic == 'KLUDCP':
        from sim.logics.kludcp import KLUDCPLogic
        player = Player(env, conn, video, KLUDCPLogic(20), traffictrace)
    elif cmdargs.logic == 'TRDA':
        from sim.logics.trda import TRDALogic
        player = Player(env, conn, video, TRDALogic(bmin=2, blow=5, bhigh=15, alpha1=0.75, alpha2=0.33, alpha3=0.5, alpha4=0.75, alpha5=0.9, faststart=True), traffictrace)
    elif cmdargs.logic == 'NN':
        from keras.models import Sequential
        from keras.models import load_model
        from sim.logics.neuralnetwork import NeuralNetworkLogic

        player = Player(env, conn, video, NeuralNetworkLogic("nnmodels/NN_model_sigmoid242_sigmoid110_softmax5_mobileTrace_realVideo.h5"), traffictrace)
    else:
        player = Player(env, conn, video, NoAdaptationLogic(), traffictrace)

    env.process(player.run())

    env.run()

    # Close all open logfiles
    env.logdir.close()
