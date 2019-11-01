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

    #experimentParams = [{'prefix': f'{experimentPrefix}_th2qr1', 'configFile': 'configs/fpvpl_throughput2_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr1', 'configFile': 'configs/fpvpl_throughput1_queueratio1.cfg'},
    #                    {'prefix': f'{experimentPrefix}_th1qr2', 'configFile': 'configs/fpvpl_throughput1_queueratio2.cfg'}]
    experimentPrefix = 'exp11_entire_day'
    experimentParams = [{'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_deep_avg_queue_length.cfg'},
                        {'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_deep_avg_vehicle_number.cfg'},
                        {'prefix': 'rf_throughput', 'configFile': 'configs/simple_deep_throughput.cfg'},
                        {'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_deep_reward_vehicle_delay.cfg'},
                        {'prefix': 'rf_vehicle_delay_diff', 'configFile': 'configs/simple_deep_reward_vehicle_delay_diff.cfg'},
                        {'prefix': 'rf_number_stops', 'configFile': 'configs/simple_deep_number_stops.cfg'},
                        {'prefix': 'rf_number_stops_diff', 'configFile': 'configs/simple_deep_number_stops_diff.cfg'},
                        {'prefix': 'webster_like', 'configFile': 'configs/simple_webster_like.cfg'}]
    experimentParams = [{'prefix': 'fixed_time', 'configFile': 'configs/simple_fixed_time.cfg'}]
    #                    {'prefix': 'rf_adaptive_lane_occup', 'configFile': 'configs/simple_deep_adaptive_lane_occupancy.cfg'}]
    #experimentParams = [{'prefix': 'webster_like', 'configFile': 'configs/simple_webster_like.cfg'}]
    experimentPrefix = 'exp12_half_day'
    experimentParams = [{'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_qlearning_avg_queue_length.cfg'},
                        {'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'prefix': 'rf_throughput', 'configFile': 'configs/simple_qlearning_throughput.cfg'},
                        {'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_qlearning_reward_vehicle_delay.cfg'},
                        #{'prefix': 'rf_vehicle_delay_diff', 'configFile': 'configs/simple_qlearning_reward_vehicle_delay_diff.cfg'},
                        {'prefix': 'rf_number_stops', 'configFile': 'configs/simple_qlearning_number_stops.cfg'},
                        {'prefix': 'rf_avg_queue_length_w_p_stps', 'configFile': 'configs/simple_qlearning_avg_queue_length_w_penalty_stops.cfg'},
                        {'prefix': 'rf_vehicle_number_w_p_stps', 'configFile': 'configs/simple_qlearning_avg_vehicle_number_w_penalty_stops.cfg'},
                        {'prefix': 'rf_veh_delay_w_p_stps', 'configFile': 'configs/simple_qlearning_veh_delay_w_penalty_stops.cfg'},
                        {'prefix': 'fixed_time', 'configFile': 'configs/simple_fixed_time.cfg'}]
    experimentPrefix = 'dummy'
    experimentParams = [{'prefix': 'rf_vehicle_number_w_p_stps', 'configFile': 'configs/simple_qlearning_avg_vehicle_number_w_penalty_stops.cfg'}]
    s = SimulationManager(options, experimentPrefix, experimentParams, 1)
