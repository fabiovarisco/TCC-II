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
from SimulationConfig import *

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
    experimentPrefix = 'exp13_half_day'
    experimentParams = [{'prefix': 'rf_avg_queue_length', 'configFile': 'configs/simple_qlearning_avg_queue_length.cfg'},
                        {'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg'},
                        {'prefix': 'rf_throughput', 'configFile': 'configs/simple_qlearning_throughput.cfg'},
                        {'prefix': 'rf_actual_throughput', 'configFile': 'configs/simple_qlearning_actual_throughput.cfg'},
                        {'prefix': 'rf_vehicle_delay', 'configFile': 'configs/simple_qlearning_reward_vehicle_delay.cfg'},
                        #{'prefix': 'rf_vehicle_delay_diff', 'configFile': 'configs/simple_qlearning_reward_vehicle_delay_diff.cfg'},
                        {'prefix': 'rf_number_stops', 'configFile': 'configs/simple_qlearning_number_stops.cfg'},
                        {'prefix': 'rf_avg_queue_length_w_p_stps', 'configFile': 'configs/simple_qlearning_avg_queue_length_w_penalty_stops.cfg'},
                        {'prefix': 'rf_vehicle_number_w_p_stps', 'configFile': 'configs/simple_qlearning_avg_vehicle_number_w_penalty_stops.cfg'},
                        {'prefix': 'rf_veh_delay_w_p_stps', 'configFile': 'configs/simple_qlearning_veh_delay_w_penalty_stops.cfg'},
                        {'prefix': 'rf_avg_queue_length_w_p_residual_queue', 'configFile': 'configs/simple_qlearning_avg_queue_length_w_penalty_residual_queue.cfg'},
                        {'prefix': 'rf_vehicle_number_w_p_residual_queue', 'configFile': 'configs/simple_qlearning_avg_vehicle_number_w_penalty_residual_queue.cfg'},
                        {'prefix': 'rf_veh_delay_w_p_residual_queue', 'configFile': 'configs/simple_qlearning_veh_delay_w_penalty_residual_queue.cfg'},
                        {'prefix': 'fixed_time', 'configFile': 'configs/simple_fixed_time.cfg'},
                        {'prefix': 'webster_like', 'configFile': 'configs/simple_webster_like.cfg'}]
    experimentPrefix = 'dummy'
    experimentParams = [{'prefix': 'rf_veh_delay_w_p_residual_queue', 'configFile': 'configs/simple_qlearning_veh_delay_w_penalty_residual_queue.cfg'}]
    experimentParams = [{'prefix': 'rf_actual_throughput', 'configFile': 'configs/simple_qlearning_actual_throughput.cfg'}]
    experimentPrefix = 'exp14_hyperparam_tuning_2'
    experimentParams = [{'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_qlearning_avg_vehicle_number.cfg',
                            'params': [{'key': QLEARNING_LEARNING_RATE, 'from': 1e-03, 'to': 1e-03, 'increment_factor': 10},
                                        {'key': QLEARNING_GAMMA_VALUE, 'from': 0.8, 'to': 0.9, 'increment_value': 0.1},
                                        {'key': QLEARNING_EPSILON_GREEDY_RATE, 'from': 0.6, 'to': 0.8, 'increment_value': 0.1}]}]
    #experimentPrefix = 'exp15_hyperparam_tuning'
    # experimentParams = [{'prefix': 'rf_avg_veh_number', 'configFile': 'configs/simple_deep_avg_vehicle_number.cfg',
    #                          'params': [{'key': QLEARNING_LEARNING_RATE, 'from': 1e-06, 'to': 0.1, 'increment_factor': 10},
    #                                     {'key': DEEP_QLEARNING_HIDDEN_NEURON_COUNT, 'from': 40, 'to': 40, 'increment_factor': 1.5},
    #                                     {'key': DEEP_QLEARNING_DISCOUNTING_RATE, 'from': 0.1, 'to': 0.1, 'increment_factor': 10},
    #                                     {'key': DEEP_QLEARNING_SEQUENCE_LENGTH, 'from': 5, 'to': 5, 'increment_value': 3},
    #                                     {'key': QLEARNING_EPSILON_GREEDY_RATE, 'from': 0.7, 'to': 0.7, 'increment_value': 0.1}]}]

                        #                 {'key': DEEP_QLEARNING_HIDDEN_NEURON_COUNT, 'from': 5, 'to': 150, 'increment_factor': 1.5},
                        #                 {'key': DEEP_QLEARNING_DISCOUNTING_RATE, 'from': 1e-04, 'to': 0.1, 'increment_factor': 10},
                        #                 {'key': DEEP_QLEARNING_SEQUENCE_LENGTH, 'from': 1, 'to': 20, 'increment_value': 3},
                        #                 {'key': QLEARNING_EPSILON_GREEDY_RATE, 'from': 0.5, 'to': 0.8, 'increment_value': 0.1}]}
                        # ]
    experimentPrefix = 'exp20_penalty_rfs_2'
    experimentParams = [
        #{'prefix': 'fxt', 'configFile': 'configs/single_half_day_fixed_time.cfg'},
        #{'prefix': 'delay', 'configFile': 'configs/single_half_day_qlearning_delay.cfg'},
        #{'prefix': 'delay_prq', 'configFile': 'configs/single_half_day_qlearning_delay_res_queue_penalty.cfg'}]
        {'prefix': 'delay_pwt', 'configFile': 'configs/single_half_day_qlearning_delay_wasted_time_penalty.cfg'},
        {'prefix': 'delay_pwtl', 'configFile': 'configs/single_half_day_qlearning_delay_wasted_time_penalty_log.cfg'}]

    experimentPrefix = 'exp21_rf_80p'
    experimentParams = [
        {'prefix': 'ql', 'configFile': 'configs/single_basic_qlearning_avg_queue_length.cfg'},
        {'prefix': 'veh_n', 'configFile': 'configs/single_basic_qlearning_avg_vehicle_number.cfg'},
        {'prefix': 'delay', 'configFile': 'configs/single_basic_qlearning_delay.cfg'},
        {'prefix': 'throughput', 'configFile': 'configs/single_basic_qlearning_throughput.cfg'},
        {'prefix': 'delay_prq', 'configFile': 'configs/single_basic_qlearning_delay_res_queue_penalty.cfg'},
        {'prefix': 'delay_pwtl', 'configFile': 'configs/single_basic_qlearning_delay_wasted_time_penalty_log.cfg'},
        {'prefix': 'act_throughput_mqr', 'configFile': 'configs/single_basic_qlearning_act_throughput_mqr.cfg'}]

    experimentParams = [
        #{'prefix': 'veh_n_pwtl', 'configFile': 'configs/single_basic_qlearning_veh_n_wasted_time_penalty_log.cfg'},
        {'prefix': 'throughput_pwtl', 'configFile': 'configs/single_basic_qlearning_throughput_wasted_time_penalty_log.cfg'}
    ]
    experimentPrefix = 'test_adaptive'
    experimentParams = [
        {'prefix': 'adapt_veh_n_thp', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg'},
    ]

    experimentPrefix = 'dummy'
    experimentParams = [
        {'prefix': 'adapt_veh_n_thp', 'configFile': 'configs/single_basic_qlearning_adaptative_veh_n_throughput.cfg',
        'params': [{'key': QLEARNING_REWARD_ADAPTIVE_INFLECTION_POINT, 'from': 0.5, 'to': 0.5, 'increment_value': 0.1}]},
    ]

    experimentPrefix = 'exp23'
    experimentParams = [
        {'prefix': 'adap_vehn', 'configFile': 'configs/single_final_qlearning_adaptative_veh_n_throughput.cfg'},
        {'prefix': 'veh_n', 'configFile': 'configs/single_final_qlearning_avg_vehicle_number.cfg'}
    ]

    experimentPrefix = 'exp23_2'
    experimentParams = [
        {'prefix': 'adap_dwtp', 'configFile': 'configs/single_final_qlearning_adaptative_delay_throughput.cfg'},
        {'prefix': 'dwtp', 'configFile': 'configs/single_final_qlearning_delay_wasted_time_penalty_log.cfg'},
    ]
    
    experimentPrefix = 'exp23_3'
    experimentParams = [
        #{'prefix': 'thp', 'configFile': 'configs/single_final_qlearning_throughput.cfg'},
        {'prefix': 'fxm', 'configFile': 'configs/single_final_fixed_time.cfg'}
    ]

    experimentPrefix = 'exp25_1'
    experimentParams = [{'prefix': 'adap_vehn', 'configFile': 'configs/single_final_qlearning_adaptative_veh_n_throughput.cfg'}]

    #experimentPrefix = 'exp25_2'
    #experimentParams = [{'prefix': 'veh_n', 'configFile': 'configs/single_final_qlearning_avg_vehicle_number.cfg'}]

    #experimentPrefix = 'exp25_3'
    #experimentParams = [{'prefix': 'thp', 'configFile': 'configs/single_final_qlearning_throughput.cfg'}]
    
    s = SimulationManager(options, experimentPrefix, experimentParams, 100)
