from netmiko import ConnectHandler
from dotenv import load_dotenv, find_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv(find_dotenv(), override=True)


# Logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AgentClient:

    def __init__(self):
    
        self.device_info = {
            'device_type': 'cisco_ios',
            'host': os.getenv("CISCO_HOST"),
            'username': os.getenv("CISCO_USERNAME"),
            'password': os.getenv("CISCO_PASSWORD"),
        }

        self.api_key = os.getenv("API_KEY")
        self.logger = logging.getLogger(__name__)

    def show_command(self, command):
        """
        Send a show command to the Cisco device and return the output.
        :param command: The command to be executed on the device.
        :return: The output of the command.
        """
        try:
            with ConnectHandler(**self.device_info) as connection:
                self.logger.info(f"Connected to {self.device_info['host']}")
                self.logger.info(f"Sending command: {command}")

                output = connection.send_command(command)
                self.logger.debug("Command output:")
                for line in output.splitlines():
                    self.logger.debug(line)

                return output

        except Exception as e:
            self.logger.error(f"Failed to execute command '{command}' on {self.device_info['host']}: {e}")
            return None

    def config_command(self, commands: list):
        """
        Send configuration commands to the Cisco device and return the output.
        :param commands: A list of configuration commands to be executed.
        :return: The output of the commands.
        """
        try:
            with ConnectHandler(**self.device_info) as connection:
                self.logger.info(f"Connected to {self.device_info['host']}")
                self.logger.info(f"Applying configuration commands: {commands}")

                # Enter enable mode
                connection.enable()

                # Send configuration commands
                output = connection.send_config_set(commands)
                self.logger.info("Configuration applied successfully.")
                self.logger.debug(f"Configuration output: {output}")

                return output

        except Exception as e:
            self.logger.error(f"Failed to apply configuration on {self.device_info['host']}: {e}")
            return None
    
if __name__ == "__main__":
    agent_client = AgentClient()
    connection = agent_client.send_command(command="show version")


