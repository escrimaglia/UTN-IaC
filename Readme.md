# Network Automation - UTN-FRC Cisco Academy

**Author:** Ed Scrimaglia  
**Institution:** National Technological University - Córdoba Regional Campus  
**Course:** Network Automation Engineer  
**Creation Date:** December 2, 2025  

---

## Overview

This repository contains the complete practical material for the Network Automation course, organized in progressive modules ranging from Python fundamentals to enterprise Infrastructure as Code (IaC) implementations with Ansible and Netmiko.

**Pedagogical approach:** Each module includes incremental examples, real-world use cases, and integrative simulations that prepare for professional scenarios in enterprise network management and automation.

---

## Project Structure

```tree
Codigo/
├── Python_Basics/         # Python programming fundamentals
├── json/                  # JSON file manipulation
├── yaml/                  # YAML file manipulation
├── Modelado/              # Data modeling and validation → README.md
├── Netmiko/               # Netmiko automation
│   ├── ejemplo1/          # Basic commands and TextFSM → README.md
│   ├── ejemplo2/          # Configuration with Jinja2 templates → README.md
│   └── sim_caso/          # Integration simulation → README.md
├── Ansible/               # Ansible automation
│   ├── ejemplo1/          # Variables and show commands → README.md
│   ├── ejemplo2/          # Programming structures → README.md
│   ├── ejemplo3/          # Ansible Vault and templates → README.md
│   ├── sim_caso/          # Complete enterprise simulation → README.md
│   └── ssh-config/        # SSH config for devices with legacy algorithms
└── RestApi/               # Automation via REST API → README.md
```

**Note:** Directories marked with `→ README.md` contain detailed documentation in their respective README files.

---

## Course Modules

### 1. Python Basics

**Location:** [`Python Basics/`](Python_Basics/)

**Objective:** Python fundamentals for automation: classes, modules, data structures.

**Content:**

- Object-oriented programming (basic and advanced classes)
- Mathematical operations and attribute management
- Module and import management
- Data structures: dictionaries and lists

**Scripts:** `main.py`, `class_oper_basic_math.py`, `class_oper_advance_math.py`, `class_basic_attr.py`

---

### 2. Data Manipulation (JSON/YAML)

#### JSON

**Location:** [`json/`](json/)

**Content:**

- `manage_json.py`: `JsonHandler` class for JSON serialization/deserialization
- `diccionario.py`: Sample data structures
- `devices.json`: Generated JSON file

**Techniques:** `json.dump()`, `json.load()`, `json.dumps()`, `json.loads()`

#### YAML

**Location:** [`yaml/`](yaml/)

**Content:**

- `manage_yaml.py`: `YamlHandler` class for YAML reading
- `file.yaml`: YAML file example

**Advantage:** Better readability, comment support, standard format in Ansible.

---

### 3. Data Modeling

**Location:** [`Modelado/`](Modelado/) → **[See complete README](Modelado/README.md)**

**Objective:** Advanced infrastructure modeling with JSON Schema validation and YAML reuse.

**Content:**

- YAML infrastructure data models
- JSON Schema validation (draft-07)
- Reuse techniques: anchors (`&`), aliases (`*`), merge keys (`<<:`)
- Validation scripts: `main_schema.py`, `main_reutilizacion.py`
- Progressive examples with models and schemas

**Use cases:** Centralized Source of Truth, configuration validation, automation input.

---

### 4. Netmiko Automation

#### Example 1: Fundamentals

**Location:** [`Netmiko/ejemplo1/`](Netmiko/ejemplo1/) → **[See complete README](Netmiko/ejemplo1/README.md)**

**Topics:** SSH connections, show commands, parsing with TextFSM, analysis with CiscoConfParse, performance optimization, reusable `NetmikoInicial` class.

**Scripts:** `netmiko_eje1.py` (basics), `netmiko_eje2.py` (TextFSM), `netmiko_eje3.py` (optimization), `netmiko_eje4.py` (CiscoConfParse), `integrador1.py`

#### Example 2: Advanced Configuration

**Location:** [`Netmiko/ejemplo2/`](Netmiko/ejemplo2/) → **[See complete README](Netmiko/ejemplo2/README.md)**

**Topics:** Configuration with `send_config_set()` and `send_config_from_file()`, Jinja2 templates, multiline commands, error validation, `ConfigurationClass` class.

**Scripts:** `netmiko_eje1.py` through `netmiko_eje4.py`, `integrador2.py`, templates in `templates/`

#### Simulation: Professional Implementation

**Location:** [`Netmiko/sim_caso/`](Netmiko/sim_caso/) → **[See complete README](Netmiko/sim_caso/README.md)**

**Description:** Modular and scalable end-to-end solution for configuring multiple devices.

**Components:**

- `main.py`: Main orchestrator
- `class_device_config.py`: SSH connection management
- `class_create_configs.py`: Jinja2 template rendering
- `modelo_datos.yaml`: Centralized Source of Truth
- Templates for VLANs, access/trunk interfaces

**Flow:** Read model → Generate configs → Connect SSH → Apply → Validate → Save

---

### 5. Ansible Automation

#### Example 1: Variables and Queries

**Location:** [`Ansible/ejemplo1/`](Ansible/ejemplo1/) → **[See complete README](Ansible/ejemplo1/README.md)**

**Topics:** Inventories, data models, JSON Schema validation, variable manipulation, `hostvars`, Jinja2 filters, show commands on Cisco IOS.

**Components:** `inventario.ini`, `modelo_datos.yaml`, `validador_modelo.json`, playbooks 1-3, `host_vars/`, `group_vars/`

**Collections:** `cisco.ios`, `ansible.netcommon`

#### Example 2: Programming Structures

**Location:** [`Ansible/ejemplo2/`](Ansible/ejemplo2/) → **[See complete README](Ansible/ejemplo2/README.md)**

**Topics:** Conditionals (`when`), loops (`loop`), error handling (`block/rescue/always`), reusable tasks (`include_tasks`), shared variables.

**Components:** `ansible.cfg`, `tasks/validate.yaml`, `tasks/timestamp.yaml`, playbooks 1-6

#### Example 3: Ansible Vault and Templates

**Location:** [`Ansible/ejemplo3/`](Ansible/ejemplo3/) → **[See complete README](Ansible/ejemplo3/README.md)**

**Topics:** Credential encryption with Ansible Vault, Jinja2 templates, YAML anchors/aliases, configuration generation and application, conditional handlers.

**Components:** `group_vars/cisco_ios/vault.yaml`, `modelo/modelo.yaml`, `templates/`, `play_create_codigo.yaml`, `play_config_devices.yaml`

**Workflow:** Generate configs → Review → Apply to devices (with `--vault-password-file`)

#### Simulation: Enterprise Solution

**Location:** [`Ansible/sim_caso/`](Ansible/sim_caso/) → **[See complete README](Ansible/sim_caso/README.md)**

**Description:** Complete enterprise implementation with high availability, automated documentation.

**Architecture:**

- 2 Core Switches (EIGRP AS 10, VRRP)
- 2 Access Switches + 1 Datacenter
- 3 VLANs (Engineering, Production, Finance)

**Components:**

- `modelo_datos/modelo.yaml`: Complete Source of Truth
- Templates for configuration (trunk, access, VLANs, SVIs, EIGRP) and documentation
- Playbooks: `play_create_codigo.yaml`, `play_config_devices.yaml`, `play_create_documentacion.yaml`
- Reusable tasks, JSON Schema validation

**Features:** Complete IaC, high availability (VRRP, EIGRP), automatic validation, auto-generated technical documentation.

**Flow:** Generate configs → Apply to devices → Generate documentation

---

### 6. Automation with REST API

**Location:** [`RestApi/`](RestApi/) → **[See full README](RestApi/README.md)**

**Objective:** Solve the same course problem over HTTP instead of SSH, with the API as the device interface.

**Topics:** `requests` client with session and retries, token authentication, TLS verification, status codes, and declarative reconciliation with `--dry-run` and drift removal.

**Components:**

- `rest_clase.py`: `RestClient` class — login, reusable session, error handling
- `mock_server.py`: controller simulator (FastAPI), to work without real hardware
- `rest_eje1.py`, `rest_eje2.py`, `rest_eje3.py`: progressive examples
- `integrador3.py`: integrator that reconciles device state against `modelo_datos.yaml`

**How to run it:** start `mock_server.py` in one terminal and run the examples in another. No lab required.

---

## Requirements and Configuration

### General Requirements

- **Python:** 3.12 or higher
- **System:** Linux, macOS, Windows (WSL recommended)
- **Package manager:** uv (recommended)

### Dependencies by Technology

**Netmiko:**

```toml
netmiko >= 4.6.0
ciscoconfparse >= 1.9.52
jinja2 >= 3.1.6
pyyaml >= 6.0.3
```

**Ansible:**

```toml
ansible >= 12.2.0
ansible-pylibssh >= 1.3.0
jsonschema >= 4.25.1
```

**Ansible Collections:**

```bash
ansible-galaxy collection install cisco.ios ansible.netcommon
```

**Modeling:**

```toml
jsonschema >= 4.25.1
pyyaml >= 6.0.3
```

### Quick Installation

**With uv (recommended):**

```bash
cd Netmiko/ejemplo1  # or any project
uv sync
```

---

## Usage Guide

### Learning Path

1. **Python Basics** → Fundamentals
2. **json/ and yaml/** → Data manipulation
3. **Modelado/** → Validation and Source of Truth
4. **Netmiko/ejemplo1/** → Connections and commands
5. **Netmiko/ejemplo2/** → Configuration with templates
6. **Netmiko/sim_caso/** → Complete implementation
7. **Ansible/ejemplo1/** → Variables and queries
8. **Ansible/ejemplo2/** → Programming structures
9. **Ansible/ejemplo3/** → Vault and templates
10. **Ansible/sim_caso/** → Enterprise solution

### Best Practices

- **Virtual environments:** One per project, avoid global installations
- **Security:** Ansible Vault for credentials, don't version `.vault-pass`
- **Version control:** Frequent commits, appropriate `.gitignore`
- **Testing:** Test in lab, validate models, backup first

---

## Additional Resources

**Documentation:**

- [Ansible](https://docs.ansible.com/) | [Netmiko](https://github.com/ktbyers/netmiko) | [Jinja2](https://jinja.palletsprojects.com/) | [JSON Schema](https://json-schema.org/) | [CiscoConfParse](https://ciscoconfparse.readthedocs.io/)

**Tools:**

- **Editor:** VS Code (extensions: Python, Ansible, YAML, Jinja2)
- **Emulators:** GNS3, EVE-NG, Cisco CML, Containerlab

**Community:**

- [Ansible Galaxy](https://galaxy.ansible.com/) | [Network to Code Slack](https://networktocode.slack.com/) | [r/networking](https://www.reddit.com/r/networking/) | [r/ansible](https://www.reddit.com/r/ansible/)

---

## Important Notes

- Each subdirectory with examples includes its own **detailed README.md**
- `pyproject.toml` files define specific dependencies for each project
- Simulations integrate all module concepts
- Material designed for academic and educational use

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: December 2025  
