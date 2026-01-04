# Data Modeling for Network Automation

This project demonstrates YAML data modeling techniques and JSON Schema validation for network infrastructure automation.

## Description

The project includes examples of:

- Network infrastructure data modeling in YAML format
- Data validation using JSON Schema
- Code reuse in YAML using anchors and aliases
- Python scripts for automated validation

## Project Structure

```tree
├── main_schema.py           # Main validation script
├── main_reutilizacion.py   # Script to demonstrate YAML reuse
├── modelo_datos.yaml       # Main infrastructure model
├── modelo_schema.json      # Main validation schema
├── ejemplo1_datos.yaml     # Basic metadata example
├── ejemplo1_schema.json    # Schema for basic example
├── ejemplo2_datos.yaml     # Network devices example
├── ejemplo2_schema.json    # Schema for devices
├── reutilizacion_a.yaml    # Merge keys example (<<)
├── reutilizacion_b.yaml    # Anchors and aliases example
├── pyproject.toml          # Project configuration
└── .python-version         # Required Python version
```

## Requirements

- Python 3.12+
- Dependencies (defined in [pyproject.toml](pyproject.toml)):
  - `jsonschema>=4.25.1`
  - `pyyaml>=6.0.3`

## Installation

```bash
# Install dependencies
uv add jsonschema pyyaml
```

## Usage

### Data Model Validation

Use the [`main_schema.py`](main_schema.py) script to validate YAML models against JSON schemas:

```bash
# Validate main model
python main_schema.py modelo_datos.yaml modelo_schema.json

# Validate examples
python main_schema.py ejemplo1_datos.yaml ejemplo1_schema.json
python main_schema.py ejemplo2_datos.yaml ejemplo2_schema.json
```

### Explore YAML Code Reuse

Use the [`main_reutilizacion.py`](main_reutilizacion.py) script to see reuse examples:

```bash
# Merge keys example
python main_reutilizacion.py reutilizacion_a.yaml

# Anchors and aliases example
python main_reutilizacion.py reutilizacion_b.yaml
```

## Modeling Examples

### 1. Main Model ([modelo_datos.yaml](modelo_datos.yaml))

Complete network infrastructure model that includes:

- **Metadata**: Project information, version, author
- **Devices**: Switches with management and connectivity configuration
- **Interfaces**: Detailed port configuration (access/trunk)
- **VLANs**: Virtual network definitions
- **Configuration specifications**: Templates and configuration files

### 2. Basic Examples

- **[ejemplo1_datos.yaml](ejemplo1_datos.yaml)**: Simple model with basic metadata
- **[ejemplo2_datos.yaml](ejemplo2_datos.yaml)**: Device model with IPv4/IPv6 IPs

### 3. YAML Code Reuse

#### Merge Keys ([reutilizacion_a.yaml](reutilizacion_a.yaml))

```yaml
defaults: &defaults
  user: admin
  password: secret
  timeout: 30

database1:
  <<: *defaults
  host: db1.example.com
```

#### Anchors and Aliases ([reutilizacion_b.yaml](reutilizacion_b.yaml))

```yaml
commands: &base_commands
  - Starting
  - Executing main task
  - Finished

job1:
  steps: *base_commands
```

## Validation Schemas

JSON Schema files define validation rules:

- **[modelo_schema.json](modelo_schema.json)**: Complete schema for infrastructure
- **[ejemplo1_schema.json](ejemplo1_schema.json)**: Basic schema for metadata
- **[ejemplo2_schema.json](ejemplo2_schema.json)**: Schema for network devices

### Validation Features

- Data types (string, integer, boolean, array, object)
- Specific formats (date, ipv4, ipv6)
- Length and range constraints
- Required and optional fields
- Enum and pattern validation

## Functionalities

### Validation Script ([main_schema.py](main_schema.py))

- Loads and validates YAML files against JSON schemas
- Provides detailed error messages
- Format validation support (IP, dates)
- Error handling with specific paths

### Reuse Script ([main_reutilizacion.py](main_reutilizacion.py))

- Demonstrates YAML reuse techniques
- Loads and displays resulting structure
- Useful for understanding anchors, aliases, and merge keys

## Use Cases

This project is useful for:

1. **Network Automation**: Model switch and router configurations
2. **Infrastructure Management**: Define network topologies in structured form
3. **Configuration Validation**: Ensure consistency in data models
4. **Network Documentation**: Maintain structured device inventories
5. **Configuration Templates**: Generate configurations from models

## Modeling Benefits

- **Consistency**: Schemas guarantee uniform structure
- **Validation**: Early error detection
- **Reusability**: Avoids code duplication
- **Maintainability**: Clear and documented structure
- **Scalability**: Easy addition of new devices

## Contribution

To contribute to the project:

1. Ensure all models are validated before committing
2. Keep documentation updated
3. Follow existing naming conventions
4. Include tests for new functionalities

## Author

Ed Scrimaglia - Network Automation Course, UTN Academy