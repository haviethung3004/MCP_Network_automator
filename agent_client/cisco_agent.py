from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from dotenv import load_dotenv, find_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv(find_dotenv(), override=True)


# Logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AgentCiscoClient:

    def __init__(self, HOST=None, USERNAME=None, PASSWORD=None):
        """
    
        Initialize the AgentClient with device credentials.
        :param HOST: The host of the Cisco device.
        :param USERNAME: The username for the Cisco device.
        :param PASSWORD: The password for the Cisco device.
        """
        self.device_info_cisco = {
            'device_type': 'cisco_ios',
            'host': HOST,
            'username': USERNAME,
            'password': PASSWORD,
        }

        self.device_info_linux = {
            'device_type': 'linux',
            'host': HOST,
            'username': USERNAME,
            'password': PASSWORD,
        }


        self.api_key = os.getenv("API_KEY")
        self.logger = logging.getLogger(__name__)

    def show_command(self, command, HOST, USERNAME, PASSWORD):
        """
        Send a show command to the Cisco device and return the output.
        :param command: The command to be executed on the device.
        :return: The output of the command.
        """
        try:
            self.device_info_cisco['host'] = HOST
            self.device_info_cisco['username'] = USERNAME
            self.device_info_cisco['password'] = PASSWORD
            
            self.logger.info(f"Connecting to {self.device_info_cisco['host']} with provided credentials.")
            with ConnectHandler(**self.device_info_cisco) as connection:
                self.logger.info(f"Connected to {self.device_info_cisco['host']}")
                self.logger.info(f"Sending command: {command}")

                output = connection.send_command(command, read_timeout=20)
                self.logger.debug("Command output:")
                for line in output.splitlines():
                    self.logger.debug(line)

                connection.disconnect()
                self.logger.info(f"Disconnected from {self.device_info_linux['host']}")

                return output

        except NetmikoTimeoutException as e:
            self.logger.error(f"Timeout error while executing command '{command}' on {self.device_info_cisco['host']}: {e}")
            return "Timeout error"
        except NetmikoAuthenticationException as e:
            self.logger.error(f"Authentication error while executing command '{command}' on {self.device_info_cisco['host']}: {e}")
            return "Authentication error"

    def config_command(self, commands, HOST, USERNAME, PASSWORD):
        """
        Send configuration commands to the Cisco device and return the output.
        :param commands: A list of configuration commands to be executed.
        :return: The output of the commands.
        """
        try:
            self.device_info_cisco['host'] = HOST
            self.device_info_cisco['username'] = USERNAME
            self.device_info_cisco['password'] = PASSWORD
            with ConnectHandler(**self.device_info_cisco) as connection:
                self.logger.info(f"Connected to {self.device_info_cisco['host']}")
                self.logger.info(f"Applying configuration commands: {commands}")

                # Enter enable mode
                connection.enable()
                            # Process commands properly based on type
                if isinstance(commands, str):
                    # Split string commands by newline
                    commands = [command.strip() for command in commands.split("\n") if command.strip()]

                commands = [command.strip() for command in commands if command.strip()]
                if not commands:
                    self.logger.warning("No valid commands provided.")
                    return None

                # Send configuration commands
                output = connection.send_config_set(commands)
                self.logger.info("Configuration applied successfully.")
                self.logger.debug(f"Configuration output: {output}")

                connection.disconnect()
                self.logger.info(f"Disconnected from {self.device_info_linux['host']}")

                return output

        except NetmikoTimeoutException as e:
            self.logger.error(f"Timeout error while executing command '{commands}' on {self.device_info_cisco['host']}: {e}")
            return "Timeout error"
        except NetmikoAuthenticationException as e:
            self.logger.error(f"Authentication error while executing command '{commands}' on {self.device_info_cisco['host']}: {e}")
            return "Authentication error"
        
    def ping_cisco_command(self, command, HOST, USERNAME, PASSWORD):
        """
        Send ping commands to Cisco device and return the output with wait time.
        The input should start with "ping" and be followed by the IP address.
        :param command: The ping command to be executed on the device.
        """
        try:
            if not command.startswith("ping"):
                return "Invalid command. Please use 'ping' command."
            self.device_info_cisco['host'] = HOST
            self.device_info_cisco['username'] = USERNAME
            self.device_info_cisco['password'] = PASSWORD
            with ConnectHandler(**self.device_info_cisco) as connection:
                self.logger.info(f"Connected to {self.device_info_cisco['host']}")
                self.logger.info(f"Sending ping command: {command}")

                # Send ping command
                output = connection.send_command(command, read_timeout=30, expect_string=r"#", strip_prompt=False, strip_command=False)
                if "!" in output:
                    return output
                else:
                    return "Ping failed. No response received."
        except NetmikoTimeoutException as e:
            self.logger.error(f"Timeout error while executing command '{command}' on {self.device_info_cisco['host']}: {e}")
            return "Timeout error"
        except NetmikoAuthenticationException as e:
            self.logger.error(f"Authentication error while executing command '{command}' on {self.device_info_cisco['host']}: {e}")
            return "Authentication error"

if __name__ == "__main__":
    agent_client = AgentCiscoClient()
    connection = agent_client.ssh_to_linux_device_and_send_command(commands=["ls \nls"], HOST="172.168.1.11", USERNAME="root", PASSWORD="root")