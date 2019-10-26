#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2019 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse


# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from SimulationManager import SimulationManager

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--debug", action="store_true",
                         default=False, help="redirect the output from traci.start")

    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()
    experimentPrefix = 'deepq1_adaptative'
    #experimentParams = [{'prefix': f'{experimentPrefix}_th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
    experimentParams = [{'prefix': 'exp1', 'configFile': 'configs/simple_config.cfg'}]
    s = SimulationManager(options, experimentPrefix, experimentParams, 1)
