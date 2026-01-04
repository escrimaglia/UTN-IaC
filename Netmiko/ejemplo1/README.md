# Netmiko Project - Cisco Network Automation Examples

## Project Description

This project contains a collection of Python scripts that demonstrate the use of **Netmiko** for automating Cisco network devices. The project includes progressive examples ranging from basic commands to more advanced implementations using configuration parsing with **TextFSM** and **CiscoConfParse**.

## Project Information

**Author:** Ed Scrimaglia  
**Version:** 1.0  
**Creation Date:** September 6, 2025
**Description**: First Netmiko example

## Dependencies

The project uses the following main libraries:

- **netmiko** (>=4.6.0): Multi-vendor library to simplify SSH connections to network devices
- **ciscoconfparse** (>=1.9.52): Library for parsing and analyzing Cisco device configurations

These dependencies are defined in the `pyproject.toml` file.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ejemplo1
```

### 2. Configure Python Environment

Using `uv` (recommended):

```bash
uv sync
```

## Project Structure

```tree
ejemplo1/
├── pyproject.toml          # Project configuration and dependencies
├── netmiko_clase.py        # Main NetmikoInicial class with reusable methods
├── netmiko_eje1.py         # Example 1: Basic commands
├── netmiko_eje2.py         # Example 2: TextFSM usage
├── netmiko_eje3.py         # Example 3: Optimization parameters
├── netmiko_eje4.py         # Example 4: CiscoConfParse
└── integrador1.py          # Integrator example using NetmikoInicial class
```

## Script Descriptions

### 1. `netmiko_clase.py` - NetmikoInicial Class

Implements a Python class that encapsulates Netmiko's most common functionalities:

**Main Methods:**

- `connect(device_params)`: Establishes SSH connection to the device
- `enable_mode(connection)`: Enters privileged mode
- `config_mode(connection)`: Enters global configuration mode
- `get_prompt(connection)`: Gets the device's current prompt
- `send_command(connection, command, expect_string, use_textfsm)`: Sends commands to the device
- `connection_status(connection)`: Verifies the connection status
- `parse_running_config(config_output)`: Parses configuration using CiscoConfParse
- `disconnect(connection)`: Closes the connection

**Features:**

- Robust exception handling
- TextFSM support
- Automatic configuration parsing with CiscoConfParse
- Interface and IP address extraction

### 2. `netmiko_eje1.py` - Basic Commands

**Objective**: Demonstrate basic Netmiko usage for connecting to a Cisco device and executing commands.

**Concepts covered:**

- Establishing SSH connection
- Verifying connection status with `is_alive()`
- Navigating between modes (user → privileged → configuration)
- Getting and analyzing the prompt with `find_prompt()`
- Sending commands with `send_command()`
- Using the `expect_string` parameter for output control
- Properly closing the connection

**Commands executed:**

- `show ip interface brief`

### 3. `netmiko_eje2.py` - TextFSM Usage

**Objective**: Demonstrate automatic parsing of command outputs using TextFSM.

**Concepts covered:**

- Using the `use_textfsm=True` parameter for automatic parsing
- Processing structured outputs (lists of dictionaries)
- Extracting specific information (IOS version)
- Validating returned data types

**Commands executed:**

- `show version` (with TextFSM parsing)

**TextFSM advantages:**

- Converts plain text outputs to structured data
- Facilitates extraction of specific information
- Enables programmatic data processing

### 4. `netmiko_eje3.py` - Performance Optimization

**Objective**: Demonstrate the use of optimization parameters to improve connection performance.

**Concepts covered:**

- `global_delay_factor` parameter: Adjusts wait times globally
  - Low values (0.1): Higher speed, useful with stable connections
  - High values (1.5): Greater stability, useful with slow connections
- Alternative `fast_cli=True` for fast connections
- Iteration over multiple devices with different configurations
- Performance comparison

**Commands executed:**

- `show version` (with different delay configurations)

**Best practices:**

- Use `global_delay_factor=0.1` or `fast_cli=True` for labs
- Use higher values in production environments or unstable connections

### 5. `netmiko_eje4.py` - CiscoConfParse

**Objective**: Demonstrate advanced configuration parsing using CiscoConfParse.

**Concepts covered:**

- Obtaining `running-config`
- Converting output to line list with `splitlines()`
- Creating `CiscoConfParse` object
- Searching for configuration objects with regular expressions
- Searching for child objects
- Two search methods:
  1. `re_search_children()`: Searches for children within a parent object
  2. `find_child_objects()`: Searches for specific parent-child relationships

**Commands executed:**

- `show running-config`

**Analysis performed:**

- Extraction of all interfaces
- Identification of IP addresses assigned to each interface
- Detection of interfaces without IP

### 6. `integrador1.py` - Class-based Implementation

**Objective**: Demonstrate the use of the `NetmikoInicial` class for a clean and reusable implementation.

**Concepts covered:**

- Instantiation of the `NetmikoInicial` class
- Using encapsulated methods
- Connection status validation
- Command processing with and without TextFSM
- Configuration parsing with class method
- JSON-formatted output

**Functionality:**

1. Establishes connection to the device
2. Validates connection status
3. Enters privileged mode
4. Executes commands with TextFSM parsing
5. Gets and parses the configuration
6. Closes the connection cleanly

**Advantages of object-oriented approach:**

- More organized and maintainable code
- Reuse of common logic
- Centralized error handling
- Easy extension of functionalities

## Device Configuration

Before running the scripts, you must configure the connection parameters in each file:

```python
device = {
    'device_type': 'cisco_ios',
    'host': 'X.X.X.X',        # Device IP address
    'username': 'xxxx',       # SSH username
    'password': 'xxxx',       # Password
    'ssh_config_file': '~/.ssh/config'  # SSH configuration file (optional)
}
```

### Additional Available Parameters

- `global_delay_factor`: Multiplication factor for delays (default: 1)
- `fast_cli`: Fast mode for stable connections (boolean)
- `timeout`: Timeout for initial connection (seconds)
- `secret`: Password for enable mode (if different)

## Usage

### Run individual examples

```bash
# Example 1: Basic commands
python netmiko_eje1.py

# Example 2: TextFSM
python netmiko_eje2.py

# Example 3: Optimization
python netmiko_eje3.py

# Example 4: CiscoConfParse
python netmiko_eje4.py

# Integrator example with class
python integrador1.py
```

### Use the class in your own scripts

```python
from netmiko_clase import NetmikoInicial

device_params = {
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "password"
}

net = NetmikoInicial()
conn = net.connect(device_params)
net.enable_mode(conn)
output = net.send_command(conn, "show version", use_textfsm=True)
net.disconnect(conn)
```

## Main Functionalities

### 1. Connection Management

- Automatic SSH connection
- Status verification
- Timeout and authentication error handling
- Safe connection closing

### 2. Mode Navigation

- User mode (USER EXEC)
- Privileged mode (PRIVILEGED EXEC)
- Global configuration mode (CONFIG)
- Automatic current mode detection

### 3. Command Execution

- Show commands
- Custom expect_string support
- Automatic parsing with TextFSM
- Configuration parsing with CiscoConfParse

### 4. Configuration Analysis

- Interface extraction
- IP address identification
- Parent-child relationship analysis in configurations
- Search with regular expressions

## Error Handling

All scripts implement exception handling for:

- `NetmikoTimeoutException`: Connection timeout
- `NetmikoAuthenticationException`: Authentication errors
- `Exception`: Generic Netmiko errors

The `NetmikoInicial` class provides descriptive error messages to facilitate debugging.

## Best Practices

1. **Security**:
   - Don't hardcode credentials in the code
   - Use environment variables or configuration files
   - Configure SSH keys when possible

2. **Performance**:
   - Use `fast_cli=True` or `global_delay_factor=0.1` in labs
   - Adjust timeouts according to network latency
   - Always close connections

3. **Code**:
   - Use the `NetmikoInicial` class for reusable code
   - Implement robust error handling
   - Validate states before executing commands

4. **Parsing**:
   - Use TextFSM for standard show commands
   - Use CiscoConfParse for complex configuration analysis
   - Validate the returned data type before processing

## Additional Resources

- [Official Netmiko Documentation](https://github.com/ktbyers/netmiko)
- [CiscoConfParse Documentation](https://github.com/mpenning/ciscoconfparse)
- [TextFSM Templates](https://github.com/networktocode/ntc-templates)

## Troubleshooting

### Problem: Connection timeout

**Solution**: Verify network connectivity and increase the `timeout` parameter

### Problem: Authentication error

**Solution**: Verify credentials and that SSH is enabled on the device

### Problem: TextFSM doesn't parse the output

**Solution**: Verify that a template exists for the command and IOS version

### Problem: CiscoConfParse doesn't find objects

**Solution**: Review the regular expressions and the configuration structure

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: December 2025
