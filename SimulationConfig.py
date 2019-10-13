
import ConfigParser
import io

SUMO_SIMULATION_CONFIGURATION_FILE = 'SUMO_SIMULATION_CONFIGURATION_FILE'

class SimulationConfig(object):

    def __init__(self, configFile):
        self.values = {}
        self._load(configFile)

    def _load(self, configFile):
        with open(configFile) as f:
            config_contents = f.read()
            config = ConfigParser.RawConfigParser(allow_no_value=True)
            config.readfp(io.BytesIO(config_contents))

            for key in config['DEFAULT']:  
                self.values[key] = config['DEFAULT'][key]

    def get(self, key):
        if key not in self.values:
            raise Exception(f"Key {key} not defined in configuration file.")
        return self.values[key]