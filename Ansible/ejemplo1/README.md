# Network Automation Project with Ansible

**Author:** Ed Scrimaglia  
**Version:** 0.1.0  
**Description:** Variable manipulation and usage in Ansible  
**Creation Date:** November 28, 2025

## Table of Contents

- [General Description](#-general-description)
- [Requirements](#-requirements)
- [Project Structure](#-project-structure)
- [Inventory](#-inventory)
- [Data Model](#-data-model)
- [Playbooks](#-playbooks)
- [Variables](#-variables)
- [Installation and Configuration](#-installation-and-configuration)
- [Usage](#-usage)

## General Description

This project implements automation for configuration and querying of Cisco IOS network devices using Ansible. It includes examples of:

- Executing show commands on Cisco IOS devices
- Managing variables and structured data
- Validating data models with JSON Schema
- Using Jinja2 templates for output formatting
- Configuring VLANs and interfaces

## Requirements

### Python Dependencies

The project requires Python 3.12 or higher. Dependencies are managed through `pyproject.toml`:

```toml
- ansible >= 12.2.0
- jsonschema >= 4.25.1
```

### Required Ansible Collections

```bash
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install ansible.netcommon
```

## Project Structure

```tree
ejemplo1/
├── pyproject.toml              # Project definition and dependencies
├── inventario.ini              # Network device inventory
├── playbook1.yaml              # Queries to Cisco IOS devices
├── playbook2.yaml              # Visualization and variable manipulation
├── playbook3.yaml              # Dynamic hosts usage from data model
├── modelo_datos/
│   └── modelo_datos.yaml       # Infrastructure data model
├── json_files/
│   └── validador_modelo.json   # JSON Schema for validation
├── host_vars/
│   ├── SW-Bld_A.yaml          # Host-specific variables
│   └── SW-Bld_B.yaml          # Host-specific variables
└── group_vars/
    └── cisco_ios.yaml          # Variables for cisco_ios group
```

## Inventory

The `inventario.ini` file defines the network infrastructure organized into groups:

### Defined Groups

- **`cisco_ios_access_bsas`**: Access switches in Buenos Aires
  - SW-Bld_A (10.2.0.10X)

- **`cisco_ios_access_cba`**: Access switches in Córdoba
  - SW-Bld_B (10.2.0.10X)

- **`cisco_ios_datacenter`**: Datacenter switches
  - SW-Data_Center (10.2.0.10X)

- **`cisco_ios_core`**: Core switches
  - SW-CORE_1 (10.2.0.10X)

- **`cisco_ios`**: Parent group that groups all Cisco IOS devices

### Global Variables

```ini
[all:vars]
ansible_connection=ansible.netcommon.network_cli
```

## Data Model

The `modelo_datos/modelo_datos.yaml` file contains the structured definition of the infrastructure:

### Model Structure

```yaml
modelo:
  metadatos:
    proyecto: "Examples of playbooks for variable handling"
    version: "1.0"
    autor: "Ed Scrimaglia"
    fecha_creacion: "2025-11-28"
    time_zone: "America/Argentina/Buenos_Aires"
  
  infra_spec:
    hosts_group: "cisco_ios"
    devices:
      - hostname: "SW_Bld_A"
        management:
          ip: "10.2.0.10X"
          interface: "GigabitEthernet0/0"
        connection:
          device_type: "cisco_ios"
          # ... credentials and SSH configuration
        interfaces:
          # ... trunk and access interface definition
        vlans:
          # ... VLAN definition
        config_spec:
          # ... configuration specifications
```

### Validation with JSON Schema

The `json_files/validador_modelo.json` file defines a JSON Schema (draft-07) that validates:

- Project metadata (name, version, author, date)
- Device specifications
- Management configuration (IP, interface)
- Connection parameters (type, host, credentials)
- Interfaces (name, description, access/trunk mode, VLANs)
- IP address formats (IPv4/IPv6)

## Playbooks

### playbook1.yaml - Device Queries

**Purpose:** Execute show commands on Cisco IOS devices

**Features:**

- Two separate plays for access and core devices
- Executes `show ip interface brief`
- Shows formatted output

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook1.yaml
```

**Target hosts:**

- Play 1: `cisco_ios` (all devices)
- Play 2: `cisco_ios_core` (core only)

### playbook2.yaml - Variable Visualization

**Purpose:** Demonstrate different techniques for variable manipulation and visualization

**Features:**

- Loading data model from YAML file
- Device visualization in JSON format
- Reading and validation with JSON Schema
- Creating variables with `set_fact`
- Accessing `hostvars` and system variables

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook2.yaml
```

**Demonstrated techniques:**

```yaml
# Jinja2 formatting
msg: |
  {% for device in modelo.infra_spec.devices -%}
  {{ device }}
  {% endfor -%}

# JSON Schema reading
msg: "{{ lookup('file', schema_path) | from_json }}"

# Variable definition
set_fact:
  mis_devices: "{{ modelo.infra_spec.devices }}"

# Accessing hostvars
var: hostvars[inventory_hostname]

# Direct access to the model metadata
var: modelo.metadatos

# Custom metadata formatting
msg: "Project: {{ modelo.metadatos.proyecto }}, Version: {{ modelo.metadatos.version }}"

# System variables Ansible exposes per host
var: hostvars[inventory_hostname].playbook_dir
```

---

### playbook3.yaml - Dynamic Hosts

**Purpose:** Use data model variables to dynamically define target hosts

**Features:**

- The `hosts` parameter is obtained from the data model
- Executes commands on devices defined in `modelo.infra_spec.hosts_group`
- Visualizes interfaces for each device

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook3.yaml
```

**Important note:** Using dynamic hosts can cause errors in `--syntax-check` since variables are not available at validation time.

## Variables

### Group Variables (`group_vars/cisco_ios.yaml`)

Common variables for all Cisco IOS devices:

```yaml
ansible_network_os: cisco.ios.ios
ansible_user: netsim
ansible_become: true
ansible_become_method: ansible.netcommon.enable
ansible_become_password: password
```

### Host Variables (`host_vars/`)

Device-specific credentials:

```yaml
# SW-Bld_A.yaml
ansible_password: password

# SW-Bld_B.yaml
ansible_password: password
```

### Data Model Variables

Accessible through `vars_files`:

```yaml
vars_files:
  - "./modelo_datos/modelo_datos.yaml"
```

Access in tasks:

- `modelo.metadatos.proyecto`
- `modelo.metadatos.autor`
- `modelo.infra_spec.devices`
- `modelo.infra_spec.hosts_group`

## Installation and Configuration

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

### 3. Install Ansible Collections

```bash
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install ansible.netcommon
```

### 4. Configure Credentials

Edit files in `host_vars/` and `group_vars/` with the appropriate credentials.

### 5. Verify Connectivity

```bash
ansible -i inventario.ini all -m ping
```

## Usage

### Run Basic Queries

```bash
ansible-playbook -i inventario.ini playbook1.yaml
```

### Explore Variables

```bash
ansible-playbook -i inventario.ini playbook2.yaml
```

### Use Dynamic Hosts

```bash
ansible-playbook -i inventario.ini playbook3.yaml
```

### Syntax Validation

```bash
ansible-playbook --syntax-check playbook1.yaml
```

### Dry-Run Mode

```bash
ansible-playbook -i inventario.ini playbook1.yaml --check
```

### Run on Specific Hosts

```bash
ansible-playbook -i inventario.ini playbook1.yaml --limit SW-Bld_A
```

### Verbose Mode

```bash
ansible-playbook -i inventario.ini playbook1.yaml -vvv
```

## Key Concepts Demonstrated

### 1. Inventory Organization

- Hierarchical groups
- Group and host variables
- Network-specific connection parameters

### 2. Data Model

- Separation of data and logic
- Validation with JSON Schema
- Reusable structure

### 3. Variable Handling

- `vars_files` for external data loading
- `set_fact` for dynamic variables
- `hostvars` for accessing other hosts' variables
- Jinja2 templates for formatting

### 4. Network Modules

- `cisco.ios.ios_command` for show commands
- Output registration with `register`
- Visualization with `ansible.builtin.debug`

### 5. Advanced Techniques

- Dynamic hosts from variables
- Task delegation
- Loop control with `loop_control`
- Output formatting with filters (`to_nice_json`, `from_yaml`)

## Important Notes

1. **Security:** Credentials in this project are examples. In production, use Ansible Vault.

2. **Dynamic Hosts:** Using variables in the `hosts` parameter can cause `--syntax-check` failures.

3. **Network Connection:** Playbooks require SSH connectivity to Cisco IOS devices.

4. **JSON Schema:** Data model validation ensures structure consistency.

5. **Loop Control:** Using `label` in `loop_control` reduces output verbosity.

## Troubleshooting

### SSH Connection Problems

```bash
# Verify connectivity
ansible -i inventario.ini all -m ping -vvv

# Verify variables
ansible-inventory -i inventario.ini --list
```

### Variables Not Available

```bash
# Verify that vars_files is correctly defined
# Verify that the path to data model is correct
# Use delegate_to: localhost for local variables
```

## References

- [Ansible Documentation](https://docs.ansible.com/)
- [Cisco IOS Collection](https://docs.ansible.com/ansible/latest/collections/cisco/ios/)
- [JSON Schema Draft 07](https://json-schema.org/draft-07/schema)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: December 2025
