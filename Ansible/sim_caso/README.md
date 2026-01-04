# Use Case Simulation - Ansible Network Automation

**Author:** Ed Scrimaglia  
**Version:** 1.0  
**Creation Date:** December 12, 2025  
**Project:** Comprehensive Use Case Simulation

---

## General Description

This project implements a complete network infrastructure automation solution using Ansible. The system is designed to automatically generate Cisco IOS device configurations, apply them to network equipment, and generate comprehensive technical documentation of the process.

The project follows the **Infrastructure as Code (IaC)** paradigm, where all network configuration is defined in a centralized data model and rendered through Jinja2 templates, ensuring consistency, reproducibility, and traceability in network operations.

---

## Infrastructure Architecture

### Network Topology

The simulated infrastructure includes:

- **2 Core Switches (SW-CORE_1, SW-CORE_2)**: Core switches with EIGRP routing and VRRP redundancy
- **2 Access Switches (SW-Bld_A, SW-Bld_B)**: Access switches for buildings A and B
- **1 Data Center Switch (SW-Data_Center)**: Access switch for the data center

### Configured VLANs

- **VLAN 10 - Engineering**: Engineering department network (192.168.10.0/24)
- **VLAN 20 - Production**: Production department network (192.168.20.0/24)
- **VLAN 30 - Finance**: Finance/data center department network (192.168.30.0/24)

### High Availability Features

- **VRRP (Virtual Router Redundancy Protocol)**: Implemented on core switches for redundant gateway
- **EIGRP (Enhanced Interior Gateway Routing Protocol)**: Dynamic routing protocol (AS 10)
- **Trunk Ports**: Trunk links with dynamic modes for VLAN exchange

---

## Project Structure

```tree
sim_caso/
├── pyproject.toml                   # Project definition and Python dependencies
├── README.md                        # This file
├── configs/                         # Automatically generated configurations
│   ├── SW-Bld_A_int_access.cfg      # Access interface config
│   ├── SW-Bld_A_int_trunk.cfg       # Trunk interface config
│   ├── SW-Bld_A_vlans.cfg           # VLANs config
│   └── ...                          # (Similar files per device)
├── documentacion/                   # Technical project documentation
│   ├── Reporte Simulacro...md       # Complete generated report
│   └── modulos/                     # Documentation modules per component
├── inventario/                      # Ansible device inventory
│   └── inventario.ini               # Host and group definitions
├── jsons/                           # Validation schemas
│   └── json-schema-model.json       # JSON Schema to validate data model
├── modelo_datos/                    # Centralized data model
│   └── modelo.yaml                  # Complete infrastructure definition
├── playbooks/                       # Ansible playbooks
│   ├── play_config_devices.yaml     # Apply configurations to devices
│   ├── play_create_codigo.yaml      # Generate configurations from templates
│   └── play_create_documentacion.yaml # Generate project documentation
├── tasks/                           # Reusable tasks
│   ├── task_check_empty_dir.yaml    # Check file existence
│   ├── task_timestamp.yaml          # Get system timestamp
│   └── task_validator.yaml          # Schema validation
└── templates/                       # Jinja2 templates
    ├── eigrp_cfg.j2                 # Template for EIGRP
    ├── inter_access_cfg.j2          # Template for access interfaces
    ├── inter_svi_cfg.j2             # Template for SVIs (Switched Virtual Interfaces)
    ├── inter_trunk_cfg.j2           # Template for trunk interfaces
    ├── vlans_cfg.j2                 # Template for VLANs
    └── *_doc.j2                     # Documentation templates
```

---

## Main Components

### 1. Data Model (`modelo_datos/modelo.yaml`)

Centralized YAML file that defines the entire network infrastructure:

- **Project metadata**: Name, version, author, timezone
- **Host groups**: Device category definitions
- **Infrastructure specifications**: For each device:
  - Physical interfaces (trunk/access)
  - VLANs
  - SVIs with IP addressing
  - VRRP configuration
  - EIGRP routing

**Featured characteristics:**

- Use of **YAML anchors** (`&` and `<<:`) for reusing common configurations
- Declarative definition of complete infrastructure
- Separation of configuration from implementation logic

### 2. Jinja2 Templates (`templates/`)

Templates allow generating two types of output:

- **Configurations (`.cfg`)**: Executable Cisco IOS code
- **Documentation (`.md`)**: Technical documentation in Markdown

**Available templates:**

- `inter_trunk_cfg.j2`: Trunk port configuration (802.1Q, DTP)
- `inter_access_cfg.j2`: Access port configuration
- `vlans_cfg.j2`: VLAN creation and naming
- `inter_svi_cfg.j2`: SVI configuration with VRRP
- `eigrp_cfg.j2`: EIGRP routing configuration

### 3. Playbooks (`playbooks/`)

#### `play_create_codigo.yaml`

Generates all configurations and documentation from templates:

- Renders Jinja2 templates with model data
- Creates `.cfg` files in `configs/` directory
- Creates `.md` files in `documentacion/modulos/` directory
- Executes in parallel for different device types

#### `play_config_devices.yaml`

Applies configurations to real/simulated devices:

- Configures trunk interfaces on all switches
- Configures access interfaces on access/datacenter switches
- Configures VLANs on all switches
- Configures SVIs and VRRP on core switches
- Saves changes automatically via handlers

#### `play_create_documentacion.yaml`

Assembles complete technical documentation:

- Generates report title with timestamp
- Assembles ordered documentation modules
- Creates final report with date/time

### 4. Inventory (`inventario/inventario.ini`)

Defines hosts and credentials:

- **Device groups**: cisco_ios, cisco_ios_core, cisco_ios_datacenter
- **Subgroups**: cisco_ios_access_bsas, cisco_ios_access_cba
- **Connection variables**: Credentials, privilege escalation method, network_os
- **Management IP addresses**: Range 10.2.0.101-105

### 5. Reusable Tasks (`tasks/`)

- **`task_timestamp.yaml`**: Gets UTC and local date/time with configurable timezone
- **`task_check_empty_dir.yaml`**: Verifies file existence for assembly
- **`task_validator.yaml`**: Validates data model against JSON Schema

### 6. JSON Schema (`jsons/json-schema-model.json`)

Validation schema that defines:

- Mandatory data model structure
- Allowed data types
- Required vs optional properties
- Format validations
- The validation model should be reviewed and adjusted if necessary

---

## Project Usage

### Prerequisites

```bash
# Python >= 3.12
# Ansible >= 13.0.0
# ansible-pylibssh >= 1.3.0
```

### Installation

```bash
# Install dependencies with uv
uv sync
```

### Typical Workflow

#### 1. Generate Configurations

```bash
cd playbooks
ansible-playbook -i ../inventario/inventario.ini play_create_codigo.yaml
```

This will generate:

- `.cfg` files in `configs/`
- `.md` files in `documentacion/modulos/`

#### 2. Validate Configurations

Review the generated files in `configs/` before applying.

#### 3. Apply Configurations to Devices

```bash
ansible-playbook -i ../inventario/inventario.ini play_config_devices.yaml
```

**Note**: Requires connectivity to real devices or simulator.

#### 4. Generate Documentation

```bash
ansible-playbook -i ../inventario/inventario.ini play_create_documentacion.yaml
```

Creates a consolidated report in `documentacion/` with timestamp.

---

## Configuration

### Modify the Infrastructure

Edit `modelo_datos/modelo.yaml`:

```yaml
devices:
  SW-Nuevo:
    management:
      ip: "10.2.0.10X"
      interface: "GigabitEthernet0/0"
    interfaces:
      - name: "GigabitEthernet0/1"
        description: "Conexion a SW-CORE_1"
        mode: trunk
        trunk_mode: auto
        allowed_vlans: 10,20
    vlans:
      - id: 10
        name: "Ingenieria"
```

### Update Inventory

Edit `inventario/inventario.ini`:

```ini
[cisco_ios_nuevo_grupo]
SW-Nuevo ansible_host=10.2.0.10X
```

### Create New Templates

1. Create `.j2` file in `templates/`
2. Use Jinja2 syntax with access to model variables
3. Reference in playbooks with loop to generate cfg and doc

---

## Technical Features

### Configuration Management

- **Idempotency**: Playbooks can be executed multiple times without adverse effects
- **Handlers**: Save configuration only if there are changes
- **Modular templates**: Each configuration aspect is independent

### Data Validation

- JSON Schema for structural validation
- Separation of data and logic (YAML model vs templates)

### Documentation Generation

- Documentation as code
- Automatic synchronization between configuration and documentation
- Reports with unique timestamps

### Connectivity

- Use of `network_cli` connection plugin
- Support for privilege escalation (enable mode)
- Centralized credential configuration

---

## Use Cases

1. **Initial provisioning**: Configure multiple switches from scratch
2. **Massive changes**: Modify VLANs across entire infrastructure
3. **Audit**: Generate updated network state documentation
4. **Disaster Recovery**: Restore configurations from data model
5. **Development environments**: Replicate configurations in lab/simulators

---

## Generated Outputs

### Configuration Files (`.cfg`)

- Native Cisco IOS syntax
- Ready for copy-paste or `ios_config`
- Separated by function (vlans, trunk, access, svi)

### Documentation (`.md`)

- Readable Markdown format
- Includes metadata and timestamps
- Assemblable modular structure

### Consolidated Reports

- Single document with all configuration
- Date/time nomenclature: `Reporte Simulacro de Caso de Uso Ansible 2025-12-12_05:05:56.md`

---

## Maintenance and Extension

### Add New Configuration Type

1. Create template in `templates/` (e.g.: `ospf_cfg.j2`)
2. Add data to YAML model
3. Create play in playbook to render template
4. Update JSON Schema if necessary

### Support Other Vendors

1. Create vendor-specific templates
2. Adjust variables in inventory (`ansible_network_os`)
3. Modify playbooks to use appropriate modules

---

## Security Considerations

- **Credentials**: Use Ansible Vault to encrypt passwords
- **Version control**: Do not commit credentials to Git
- **Limited access**: Restrict playbook execution permissions
- **Backups**: Perform backup before applying massive changes

---

## References

- [Ansible Documentation](https://docs.ansible.com/)
- [Cisco IOS Collection](https://galaxy.ansible.com/cisco/ios)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [VRRP Protocol RFC 5798](https://tools.ietf.org/html/rfc5798)
- [EIGRP Protocol](https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/16406-eigrp-toc.html)

---

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: December 2025  
