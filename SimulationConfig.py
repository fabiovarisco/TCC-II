
import configparser
import io

SUMO_SIMULATION_CONFIGURATION_FILE = 'sumo_simulation_configuration_file'
SUMO_SIMULATION_OUTPUT_FILE = 'sumo_simulation_output_file'
SUMO_SIMULATION_STEP_LENGTH = 'sumo_simulation_step_length'

DEMAND_NUMBER_SIMULATION_STEPS = 'demand_number_simulation_steps'

ISOLATED_INTERSECTION_DEMAND_PWE = 'isolated_intersection_demand_pwe'
ISOLATED_INTERSECTION_DEMAND_PEW = 'isolated_intersection_demand_pew'
ISOLATED_INTERSECTION_DEMAND_PNS = 'isolated_intersection_demand_pns'
ISOLATED_INTERSECTION_DEMAND_PSN = 'isolated_intersection_demand_psn'

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

        for key, value in self.values.items():
            print(f"Key: {key}; Value: {value}")

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
