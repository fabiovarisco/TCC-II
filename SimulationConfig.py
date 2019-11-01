
import configparser
import io

SUMO_SIMULATION_CONFIGURATION_FILE = 'sumo_simulation_configuration_file'
SUMO_SIMULATION_OUTPUT_FILE = 'sumo_simulation_output_file'
SUMO_SIMULATION_STEP_LENGTH = 'sumo_simulation_step_length'

DEMAND_NUMBER_SIMULATION_STEPS = 'demand_number_simulation_steps'

CONSTANT_SATURATION_FLOW = 'constant_saturation_flow'

ISOLATED_INTERSECTION_DEMAND_PWE = 'isolated_intersection_demand_pwe'
ISOLATED_INTERSECTION_DEMAND_PEW = 'isolated_intersection_demand_pew'
ISOLATED_INTERSECTION_DEMAND_PNS = 'isolated_intersection_demand_pns'
ISOLATED_INTERSECTION_DEMAND_PSN = 'isolated_intersection_demand_psn'

TL_STAGE_MIN_GREEN_TIME = 'tl_stage_min_green_time'
TL_STAGE_LOST_TIME = 'tl_stage_lost_time'
TLC_STAGE_INITIAL_LENGTH = 'tlc_stage_initial_length'
TLC_STAGE_MAX_LENGTH = 'tlc_stage_max_length'
TL_STAGE_GREEN_TIME = 'tl_stage_green_time'

TLC_QLEARNING_ACTION_MIN_GREEN = 'tlc_qlearning_action_min_green'
TLC_QLEARNING_ACTION_MAX_GREEN = 'tlc_qlearning_action_max_green'
TLC_QLEARNING_ACTION_UNIT_LENGTH = 'tlc_qlearning_action_unit_length'
TLC_QLEARNING_DISCRETIZE_QUEUE_LENGTH = 'tlc_qlearning_discretize_queue_length'

QLEARNING_REWARD_WEIGHT_THROUGHPUT = 'qlearning_reward_weight_throughput'
QLEARNING_REWARD_WEIGHT_QUEUE_RATIO = 'qlearning_reward_weight_queue_ratio'

LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY = 'lane_max_acceptable_queue_occupancy' # Max acceptable queue occupancy for each lane (used in QueueRatio reward function)
VEHICLE_AVG_LENGTH = 'vehicle_avg_length'

TLC_TYPE='tlc_type'
QLEARNING_REWARD_PARAM='qlearning_reward_param'
QLEARNING_PENALTY_BASE_REWARD_PARAM='qlearning_penalty_base_reward_param'
QLEARNING_STATE_PARAMS='qlearning_state_params'
QLEARNING_STATE_DISCRETIZE_PARAMS='qlearning_state_discretize_params'

QLEARNING_STATE_LENGTH='qlearning_state_length'
DEEP_QLEARNING_HIDDEN_LAYER='deep_qlearning_hidden_layer'

class SimulationConfig(object):

    def __init__(self, configFile):
        self.values = {}
        self._load(configFile)

    def _load(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)
        for key in config['DEFAULT']:
            self.values[key] = config['DEFAULT'][key]
            # try:
            #     self.values[key] = int(v)
            # except ValueError:
            #     self.values[key] = v

        #for key, value in self.values.items():
        #    print(f"Key: {key}; Value: {value}")

    def get(self, key):
        if key not in self.values:
            raise Exception(f"Key {key} not defined in configuration file.")
        return self.values[key]

    def getInt(self, key):
        try:
            return int(self.values[key])
        except ValueError:
            raise Exception(f"Key {key} is not an integer.")

    def getFloat(self, key):
        try:
            return float(self.values[key])
        except ValueError:
            raise Exception(f"Key {key} is not a float.")
