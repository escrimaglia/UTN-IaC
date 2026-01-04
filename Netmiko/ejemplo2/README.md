# Network Automation Project with Netmiko and Jinja2

## Project Description

This project implements a complete automation solution for configuring Cisco IOS network devices using Python, Netmiko, and Jinja2 templates. The objective is to simplify and standardize network configuration management through modular and reusable scripts.

**Author:** Ed Scrimaglia  
**Version:** 1.0  
**Creation Date:** September 13, 2025
**Description**: Example with Netmiko, configuration and rendering of jinja2 templates

---

## Main Features

- Automated SSH connection to Cisco IOS devices
- Configuration via direct commands (`send_config_set`)
- Configuration from text files (`send_config_from_file`)
- Dynamic configuration generation using Jinja2 templates
- Automatic configuration error validation
- Multi-line command management with interaction patterns
- Reusable class for network operations (`ConfigurationClass`)
- Robust connection exception handling

---

## Dependencies

The project uses the following Python libraries:

```toml
[dependencies]
netmiko >= 4.6.0    # Library for SSH connections to network devices
jinja2 >= 3.1.6     # Template engine for configuration generation
```

To install dependencies:

```bash
uv add netmiko jinja2
```

---

## Project Structure

```tree
ejemplo2/
├── config.txt                      # Generated configuration file
├── datos_config.py                 # Data for templates (interfaces)
├── datos_device.py                 # Device connection parameters
├── integrador2.py                  # Main integrator script
├── netmiko_clase.py                # ConfigurationClass class
├── netmiko_eje1.py                 # Example 1: send_config_set
├── netmiko_eje2.py                 # Example 2: send_config_from_file
├── netmiko_eje3.py                 # Example 3: Jinja2 templates
├── netmiko_eje4.py                 # Example 4: send_multiline
├── pyproject.toml                  # Project configuration
├── README.md                       # This file
└── templates/
    ├── temp_interfaces.j2          # Main interfaces template
    └── ejemplos_templates/
        ├── filters.j2              # Jinja2 filter examples
        ├── include.j2              # Template inclusion example
        ├── included.j2             # Included template
        ├── namespace.j2            # Namespace example
        └── variables.j2            # Variable examples
```

---

## Project Components

### 1. **ConfigurationClass Class** (`netmiko_clase.py`)

Main class that encapsulates all network device configuration operations.

**Main Methods:**

| Method | Description |
|--------|-------------|
| `connect(device_params)` | Establishes SSH connection to the device |
| `send_config_from_file(connection, file_path)` | Sends configuration from file |
| `send_config_set(connection, config_commands)` | Sends list of configuration commands |
| `check_config_errors(output)` | Validates errors in configuration output |
| `send_command(connection, command)` | Executes show command with TextFSM support |
| `save_config(connection)` | Saves device configuration |
| `disconnect(connection)` | Closes SSH connection |
| `create_config_template(template_file, data, config_file)` | Generates configuration from Jinja2 template |

### 2. **Data Files**

**`datos_device.py`:** Defines device connection parameters:

```python
datos_device = {
    'device_type': 'cisco_ios',
    'host': '10.2.0.10X',
    'username': 'netsim',
    'password': 'password',
    'ssh_config_file': '~/.ssh/config'
}
```

**`datos_config.py`:** Data structure for rendering templates:

```python
datos_config = {
    'interfaces': [
        {
            'name': 'loopback1',
            'ip': '10.1.0.X',
            'mask': '255.255.255.255',
            'description': 'Loopback 1',
            'shutdown': False
        },
        # ... más interfaces
    ]
}
```

### 3. **Jinja2 Templates**

**Main template** (`templates/temp_interfaces.j2`):

```jinja
{% for inter in interfaces -%}
interface {{ inter.name }} 
  ip address {{ inter.ip }} {{ inter.mask }}
  description {{ inter.description }}
{%- if inter.shutdown %}
  shutdown
{%- else %}
  no shutdown
{%- endif %}
{% endfor %}
```

The `ejemplos_templates/` directory contains educational examples of:

- Using Jinja2 filters (upper, lower, join, etc.)
- Variables and scope
- Template inclusion
- Namespaces

---

## Usage Examples

### **Example 1: Configuration with send_config_set** (`netmiko_eje1.py`)

Sends commands directly as a list:

```python
config_commands = [
    'no interface loopback0',
    'interface loopback1',
    'ip address 192.168.1.1 255.255.255.0'
]
output = connect.send_config_set(config_commands)
```

### **Example 2: Configuration from file** (`netmiko_eje2.py`)

Reads configuration from `config.txt` and applies it:

```python
output = connect.send_config_from_file('config.txt')
```

### **Example 3: Jinja2 Templates** (`netmiko_eje3.py`)

Generates dynamic configuration from template:

```python
template = env.get_template('temp_interfaces.j2')
output = template.render(datos)
```

### **Example 4: Multi-line Commands** (`netmiko_eje4.py`)

Handles complex interactions (e.g., file deletion):

```python
# Using timing
commands = ["del flash:/eje1.txt", "\n", "y"]
output = connection.send_multiline_timing(commands)

# Using patterns
commands = [
    ["del flash:/eje2.txt", r"Delete filename"],
    ["\n", r"confirm"],
    ["y", ""]
]
output = connection.send_multiline(commands)
```

### **Integrator Script** (`integrador2.py`)

Combines all functionalities in complete workflows:

**Flow 1: Configuration from template**

1. Connects to the device
2. Generates configuration from Jinja2 template
3. Applies the configuration
4. Validates errors
5. Saves changes
6. Verifies final configuration
7. Saves

---

## Use Cases

1. **Mass Provisioning**: Configure multiple devices with custom parameters
2. **Standardization**: Apply consistent base configurations
3. **Migrations**: Update configurations in a controlled manner
4. **Troubleshooting**: Execute show commands and analysis with TextFSM
5. **Complex Configurations**: Use templates for BGP, OSPF, VLANs, etc.

---

## Error Handling

The project implements:

- **Connection exceptions**: `NetmikoTimeoutException`, `NetmikoAuthenticationException`
- **Syntax validation**: Detection of "Invalid input" with exact line indication
- **Status verification**: Active connection check before operations
- **Informative logging**: Clear success/error messages in each operation

Validation example:

```python
if "Invalid input" in output:
    print("Error en la configuración enviada")
    output_list = output.splitlines()
    for ind, line in enumerate(output_list):
        if "^" in line:
            print(f"Error en el comando: '{output_list[ind-1]}'")
```

---

## Security

- Credentials are stored in `datos_device.py` (do not include in version control)
- Use of `ssh_config_file` for custom SSH configuration
- Recommended use of environment variables for credentials in production

---

## References and Resources

- [Netmiko Documentation](https://github.com/ktbyers/netmiko)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Cisco IOS Command Reference](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/products-command-reference-list.html)

---

## Learning

This project is ideal for:

- Networking and automation students
- Network engineers starting in DevOps
- Python practice applied to networks
- Understanding dynamic templates with Jinja2

---

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: December 2025
