# Network Automation Project with Ansible

**Author:** Ed Scrimaglia  
**Project:** Programming Structures - Ansible  
**Version:** 1.0  
**Creation Date:** November 28, 2025

## General Description

This project is a collection of Ansible playbooks designed to automate the configuration and management of Cisco IOS network devices. The project demonstrates different Ansible concepts and techniques applied to network automation, including:

- Conditional structures
- Variable and hostvars handling
- Loops and iterations
- Error handling with block/rescue
- Data model validation with JSON Schema
- Configuration management through centralized data model

## Project Structure

```tree
.
├── README.md                      # This file
├── inventario.ini                 # Network device inventory
├── pyproject.toml                 # Python project configuration
├── cfg/
│   └── ansible.cfg               # Ansible configuration
├── modelo_datos/
│   └── modelo_datos.yaml         # Centralized data model
├── json_files/
│   └── validador_modelo.json     # JSON schema for validation
├── tasks/
│   ├── validate.yaml             # Reusable validation task
│   └── timestamp.yaml            # Task to get timestamp
└── playbooks:
    ├── playbook1.yaml            # Basic conditionals
    ├── playbook2.yaml            # Hostvars and shared variables
    ├── playbook3.yaml            # Loops with data model
    ├── playbook4.yaml            # Loops with static list
    ├── playbook5.yaml            # Error handling (block/rescue)
    └── playbook6.yaml            # Validation with JSON Schema
```

## Environment Configuration

### Configuration File (`cfg/ansible.cfg`)

```ini
[defaults]
transport = ssh
timeout = 30
forks = 10
host_key_checking = False
deprecation_warnings = False

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

**Key features:**

- Persistent connections to improve performance
- Pipelining enabled to reduce overhead
- Host_key verification disabled for lab environments

### Inventory (`inventario.ini`)

The inventory defines four groups of Cisco IOS devices:

- **cisco_ios_access_bsas**: Buenos Aires access switch (SW-Bld_A)
- **cisco_ios_access_cba**: Córdoba access switch (SW-Bld_B)
- **cisco_ios_datacenter**: Datacenter switch (SW-Data_Center)
- **cisco_ios_core**: Core switch (SW-CORE_1)
- **cisco_ios**: Parent group that includes all access and datacenter switches

**Credentials:**

- User: `netsim`
- Password: `****`
- Network OS: `cisco.ios.ios`
- Escalation method: `ansible.netcommon.enable`

## Data Model

### Model Structure (`modelo_datos/modelo_datos.yaml`)

The centralized data model contains:

#### Metadata

```yaml
metadatos:
  proyecto: "Ansible programming structures"
  version: "1.0"
  autor: "Ed Scrimaglia"
  fecha_creacion: "2025-11-28"
  time_zone: "America/Argentina/Buenos_Aires"
```

#### Infrastructure Specification

- **hosts_group**: Target host group (cisco_ios)
- **devices**: Device list with:
  - Hostname and management address
  - Connection parameters
  - Interface configuration (trunk/access)
  - Configured VLANs
  - Configuration specifications (templates and files)

### Model Validation (`json_files/validador_modelo.json`)

JSON schema that validates:

- **Metadata:** project, version, author, creation date, time zone
- **Infrastructure:**
  - IP addresses (IPv4/IPv6)
  - Interfaces with modes (access/trunk)
  - VLANs (range 1-4094)
  - Connection credentials

## Playbooks

### Playbook 1: Conditional Structures (`playbook1.yaml`)

**Purpose:** Demonstrate the use of basic conditionals in Ansible.

**Features:**

- Executes commands only when `ejecuta = true`
- Validates data model version (`version == '1.0'`)
- Gets IP interface status with `show ip interface brief`
- Registers output and shows it conditionally

**Variables:**

- `ejecuta`: Boolean to control execution
- `device`: Target device name

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook1.yaml
```

---

### Playbook 2: Hostvars and Shared Variables (`playbook2.yaml`)

**Purpose:** Demonstrate the use of `hostvars` to share variables between hosts.

**Flow:**

1. **Play 1 (localhost):** Defines variables from the data model
   - version
   - autor
   - fecha_de_creacion
   - zona_horaria

2. **Play 2 (cisco_ios):** Consumes localhost variables using `hostvars['localhost']`
   - Executes commands only if version matches
   - Shows interface output

**Key concept:** Variables defined in one host can be accessed by other hosts through `hostvars`.

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook2.yaml
```

---

### Playbook 3: Loops with Data Model (`playbook3.yaml`)

**Purpose:** Iterate over complex structures from the data model.

**Features:**

- Loads device list from the model
- Iterates over each device using `loop`
- Shows interfaces for each device
- Uses `loop_control` with `label` to simplify output

**Advantage:** Allows working with structured and complex data efficiently.

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook3.yaml
```

---

### Playbook 4: Loops with Static List (`playbook4.yaml`)

**Purpose:** Demonstrate iteration over a simple and static list.

**Features:**

- Defines device list directly in the playbook
- Iterates over each element
- Shows customized message per device

**Devices in the loop:**

- Router-1
- SW-Bld_A
- SW-Bld_B
- SW-Data_Center
- SW-CORE_1

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook4.yaml
```

---

### Playbook 5: Error Handling (`playbook5.yaml`)

**Purpose:** Implement robust error handling with `block/rescue/always`.

**Structure:**

- **Block:** Attempts to execute commands on devices
  - Gets interfaces with `show ip interface brief`
  - Prints the result
  
- **Rescue:** Executes if there's an error
  - Shows connection error message
  - Suggests verifying connectivity and credentials
  
- **Always:** Always executes
  - Shows completion message
  - Useful for cleanup or logging

**Advantage:** Ensures connection errors don't stop the entire execution.

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook5.yaml
```

---

### Playbook 6: Validation with JSON Schema (`playbook6.yaml`)

**Purpose:** Validate the data model against a JSON schema before using it.

**Features:**

- Defines paths to data model and schema
- Includes reusable task `tasks/validate.yaml`
- Validates structure, data types, and constraints

**Variables:**

- `modelo_datos_path`: Path to the model's YAML file
- `schema_path`: Path to validation JSON schema

**Validation process:**

1. Loads YAML data model
2. Loads JSON schema
3. Validates using `ansible.utils.validate` with `jsonschema` engine
4. Shows validation result

**Execution:**

```bash
ansible-playbook -i inventario.ini playbook6.yaml
```

## Reusable Tasks

### `tasks/validate.yaml`

Modular task to validate data models against JSON schemas.

**Input:**

- `modelo_datos_path`: Path to YAML file
- `schema_path`: Path to JSON schema

**Process:**

1. Reads YAML file and converts to object
2. Reads JSON schema
3. Validates using `ansible.utils.jsonschema` engine
4. Registers result in `validation_result`

**Advantage:** Can be included in multiple playbooks without duplicating code.

---

### `tasks/timestamp.yaml`

Gets timestamps in different time zones.

**Functionality:**

- Gets UTC date/time
- Gets date/time in model's time zone
- Uses environment variables (`TZ`)
- Delegates execution to localhost

**Required variables:**

- `model.metadatos.time_zone`: Project time zone

## Usage Guide

### Prerequisites

1. **Ansible collections:**

   ```bash
   ansible-galaxy collection install cisco.ios
   ansible-galaxy collection install ansible.utils
   ansible-galaxy collection install ansible.netcommon
   ```

2. **Network connectivity:**
   - SSH access to devices defined in inventory
   - Correct credentials configured

### Executing Playbooks

**Run specific playbook:**

```bash
ansible-playbook -i inventario.ini playbook1.yaml
```

**Run with verbosity:**

```bash
ansible-playbook -i inventario.ini playbook1.yaml -v
```

**Run in check mode (dry-run):**

```bash
ansible-playbook -i inventario.ini playbook1.yaml --check
```

**Run only on specific hosts:**

```bash
ansible-playbook -i inventario.ini playbook1.yaml --limit SW-Bld_A
```

### Data Model Validation

Before running any configuration playbook, it's recommended to validate the model:

```bash
ansible-playbook -i inventario.ini playbook6.yaml
```

## Demonstrated Ansible Concepts

### 1. **Variables and Facts**

- Local variables (`vars`)
- Variables from files (`vars_files`)
- Shared variables between hosts (`hostvars`)
- Inventory variables

### 2. **Conditional Structures**

- Simple condition: `when: ejecuta`
- Compound conditions: `when: ejecuta and modelo.metadatos.version == '1.0'`
- Using `hostvars` in conditions

### 3. **Loops and Iterations**

- Simple loop over static lists
- Loop over complex model structures
- Output control with `loop_control` and `label`

### 4. **Error Handling**

- `block/rescue/always` blocks
- Output registration with `register`
- Custom error messages

### 5. **Data Validation**

- Validation with JSON Schema
- `ansible.utils.jsonschema` engine
- Format conversion (`from_yaml`, `from_json`)

### 6. **Code Reusability**

- Includable tasks with `include_tasks`
- Separating logic into independent files
- Centralized data model

### 7. **Network Modules**

- `cisco.ios.ios_command`: Execute commands on Cisco devices
- Output registration and visualization
- Connection via `network_cli`

## Implemented Best Practices

1. **Separation of data and logic:** Centralized data model
2. **Data validation:** JSON Schema to ensure integrity
3. **Reusable code:** Tasks in `tasks/` directory
4. **Error handling:** Rescue blocks for robustness
5. **Documentation:** Comments in each playbook and task
6. **Organization:** Clear directory structure
7. **Versioning:** Metadata with version and author

## Troubleshooting

### SSH connection error

If you see connection errors, verify:

```bash
# Test connectivity
ping 10.2.0.10X

# Test manual SSH
ssh netsim@10.2.0.10X

# Verify inventory credentials
ansible-inventory -i inventario.ini --list
```

### Model validation error

If validation fails:

1. Verify YAML syntax of the model
2. Review JSON schema requirements
3. Run only validation for details:

   ```bash
   ansible-playbook -i inventario.ini playbook6.yaml -v
   ```

### Missing collections

If Ansible can't find modules:

```bash
# List installed collections
ansible-galaxy collection list

# Install missing collections
ansible-galaxy collection install cisco.ios ansible.utils ansible.netcommon
```

## References

- [Official Ansible Documentation](https://docs.ansible.com/)
- [Cisco IOS Collection](https://galaxy.ansible.com/cisco/ios)
- [Ansible Network Automation](https://docs.ansible.com/ansible/latest/network/index.html)
- [JSON Schema](https://json-schema.org/)

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: December 2025
