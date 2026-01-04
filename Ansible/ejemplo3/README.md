# Network Configuration Automation with Ansible

**Author:** Ed Scrimaglia  
**Version:** 1.0  
**Creation Date:** December 12, 2025  
**Project:** Ansible Vault example project

## Project Description

This project implements a complete network automation solution using Ansible to manage Cisco IOS devices. The project follows an **Infrastructure as Code (IaC)** approach and uses **Ansible Vault** for secure credential management.

### Main Features

- Automated configuration of access interfaces on Cisco switches
- Secure credential management with Ansible Vault
- Configuration generation through Jinja2 templates
- Centralized data model for the entire infrastructure

## Network Architecture

The project manages a network infrastructure that includes:

### Managed Devices

| Device | Management IP | Group | Function |
|--------|---------------|-------|----------|
| SW-Bld_A | 10.2.0.10X | cisco_ios_access_bsas | Access Switch - Building A |
| SW-Bld_B | 10.2.0.10X | cisco_ios_access_cba | Access Switch - Building B |
| SW-Data_Center | 10.2.0.10X | cisco_ios_datacenter | Data Center Switch |
| SW-CORE_1 | 10.2.0.10X | cisco_ios_core | Main Core Switch |
| SW-CORE_2 | 10.2.0.10X | cisco_ios_core | Secondary Core Switch |

### Configured VLANs

| VLAN ID | Name | Gateway | Usage |
|---------|------|---------|-------|
| 10 | Ingenieria | 192.168.10.254 | Engineering department users |
| 20 | Produccion | 192.168.20.254 | Production department users |
| 30 | Finanzas | 192.168.30.254 | Finance servers and users |

## Project Structure

```tree
ejemplo4/
├── README.md                          # This file
├── pyproject.toml                     # Project dependencies (Python/Ansible)
│
├── inventario/
│   └── inventario.ini                 # Network device inventory
│
├── group_vars/
│   └── cisco_ios/
│       └── vault.yaml                 # Credentials encrypted with Ansible Vault
│
├── modelo/
│   └── modelo.yaml                    # Infrastructure data model
│
├── templates/
│   └── inter_access_cfg.j2            # Jinja2 template for access interfaces
│
├── configs/                           # Generated configuration files
│   ├── SW-Bld_A_int_access.cfg
│   └── SW-Bld_B_int_access.cfg
│
└── playbooks/ (in project root)
    ├── .vault-pass                    # Vault password (DO NOT VERSION!)
    ├── play_create_codigo.yaml        # Playbook to generate configurations
    └── play_config_devices.yaml       # Playbook to apply configurations
```

## Main Components

### 1. Inventory (`inventario/inventario.ini`)

Defines all network devices organized by groups and their connection variables:

- **Switch groups:**
  - `cisco_ios_access_bsas` - Access switches in Buenos Aires
  - `cisco_ios_access_cba` - Access switches in Córdoba
  - `cisco_ios_core` - Core network switches
  - `cisco_ios_datacenter` - Datacenter switches

- **Global variables:**
  - Connection: `ansible.netcommon.network_cli`
  - User: `netsim`
  - Network OS: `cisco.ios.ios`
  - Authentication: Password (no SSH public key)

### 2. Ansible Vault (`group_vars/cisco_ios/vault.yaml`)

Stores encrypted credentials for the `cisco_ios` group:

```yaml
ansible_password: [ENCRYPTED]
ansible_become_password: [ENCRYPTED]
```

**Command to view content:**

```bash
ansible-vault view group_vars/cisco_ios/vault.yaml --vault-password-file .vault-pass
```

### 3. Data Model (`modelo/modelo.yaml`)

Centralized file that defines the entire network infrastructure using the **Source of Truth** pattern:

**Structure:**

- **Metadata:** Project information
- **hosts_groups:** Host group mapping
- **infra_spec.devices:** Detailed specification for each device
  - Management (IP, interface)
  - Physical interfaces and SVIs
  - VLANs
  - Routing (for core switches)

**Features:**

- Uses YAML anchors (`&`) and aliases (`<<: *`) for configuration reusability
- Defines interface templates: `int_trunk_access`, `int_trunk_core`, `int_access`, `int_svi`

### 4. Jinja2 Template (`templates/inter_access_cfg.j2`)

Template that generates access interface configuration for Cisco IOS:

```jinja
!
{% for interface in interfaces -%}
{% if interface.mode == "access" -%}
interface {{ interface.name }}
  description {{ interface.description }}
  switchport mode {{ interface.mode }}
  switchport access vlan {{ interface.vlan }}
!
{% endif -%}
{% endfor -%}
```

**Generated output** (example for SW-Bld_A):

```text
!
interface GigabitEthernet1/1
  description Conexion a PC_ING_1
  switchport mode access
  switchport access vlan 10
!
interface GigabitEthernet1/2
  description Conexion a PC_PROD_1
  switchport mode access
  switchport access vlan 20
!
```

## Playbooks

### Playbook 1: `play_create_codigo.yaml`

**Purpose:** Generate configuration files from Jinja2 templates

**Process:**

1. Reads data model from `modelo/modelo.yaml`
2. Executes on `cisco_ios` group (access switches)
3. Extracts device interfaces from model
4. Renders the `inter_access_cfg.j2` template
5. Saves result in `configs/{{ hostname }}_int_access.cfg`

**Usage:**

```bash
ansible-playbook -i inventario/inventario.ini ./play_create_codigo.yaml --vault-password-file ./.vault-pass
```

**Output:**

- `configs/SW-Bld_A_int_access.cfg`
- `configs/SW-Bld_B_int_access.cfg`

### Playbook 2: `play_config_devices.yaml`

**Purpose:** Apply generated configurations to real devices

**Process:**

1. Reads data model from `modelo/modelo.yaml`
2. Executes on `cisco_ios` group
3. Reads generated configuration file for each device
4. Applies configuration using `cisco.ios.ios_config` module
5. If there are changes, executes handler to save configuration

**Features:**

- Requires authentication via Ansible Vault
- Only saves if there are changes (conditional handler)
- Secure SSH connection with password authentication

## Usage Guide

1. **`.vault-pass` file** in root directory with vault password

### Complete Workflow

#### Step 1: Generate Configurations

```bash
ansible-playbook -i inventario/inventario.ini ./play_create_codigo.yaml --vault-password-file ./.vault-pass
```

**Verify output:**

```bash
cat configs/SW-Bld_A_int_access.cfg
cat configs/SW-Bld_B_int_access.cfg
```

#### Step 2: Apply Configurations to Devices

```bash
ansible-playbook -i inventario/inventario.ini ./play_config_devices.yaml --vault-password-file ./.vault-pass
```

### Inventory Verification

```bash
# List all hosts
ansible-inventory -i ./inventario/inventario.ini --list --vault-password-file .vault-pass

# View specific host variables (with decrypted vault)
ansible-inventory -i ./inventario/inventario.ini \
  --host SW-Bld_A \
  --vault-password-file .vault-pass
```

## Ansible Vault Management

### Create vault file

```bash
ansible-vault create group_vars/cisco_ios/vault.yaml --vault-password-file .vault-pass
```

### Edit vault file

```bash
ansible-vault edit group_vars/cisco_ios/vault.yaml --vault-password-file .vault-pass
```

### View vault content

```bash
ansible-vault view group_vars/cisco_ios/vault.yaml --vault-password-file .vault-pass
```

### Change vault password

```bash
ansible-vault rekey group_vars/cisco_ios/vault.yaml
```

### Expected vault content

```yaml
ansible_password: password
ansible_become_password: password
```

## Troubleshooting

### Problem 1: SSH Authentication Error

**Error:**

```text
Failed to authenticate public key: Access denied for 'publickey'
```

**Solution:**
Make sure `inventario.ini` is configured with:

```ini
[cisco_ios:vars]
ansible_ssh_common_args="-o PubkeyAuthentication=no -o PreferredAuthentications=password"
```

### Problem 2: Vault variables not loading

**Error:** Ansible cannot connect, credentials not found

**Solution:**
Run playbooks from the **project root directory**, not from subdirectories:

```bash
cd /path/to/ejemplo4
ansible-playbook play_config_devices.yaml -i inventario/inventario.ini --vault-password-file .vault-pass
```

### Problem 3: Vault-pass file not found

**Error:**

```text
ERROR! The vault password file ./.vault-pass was not found
```

**Solution:**
Create the `.vault-pass` file with the password:

```bash
echo "your_vault_password" > .vault-pass
chmod 600 .vault-pass
```

### Problem 4: cisco.ios module not found

**Error:**

```text
ERROR! couldn't resolve module/action 'cisco.ios.ios_config'
```

**Solution:**

```bash
ansible-galaxy collection install cisco.ios
```

## Implemented Best Practices

### 1. Infrastructure as Code (IaC)

- All network configuration is defined in the data model
- Version control with Git
- Reproducible in any environment

### 2. Data and Logic Separation

- Centralized data model (`modelo.yaml`)
- Reusable templates (`inter_access_cfg.j2`)
- Simple and readable playbooks

### 3. Security

- Credentials encrypted with Ansible Vault
- `.vault-pass` file not versioned (add to `.gitignore`)
- Password authentication without exposed SSH keys

### 4. Idempotency

- Playbooks can be executed multiple times without adverse effects
- Only saves changes if there are modifications

### 5. DRY (Don't Repeat Yourself)

- Use of YAML anchors and aliases for reusability
- Jinja2 templates for code generation
- Centralized variables

## Project Workflow

```text
┌──────────────────┐
│  modelo.yaml     │  ← Source of Truth
│  (Data)          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Jinja2 Template  │
│ (Logic)          │
└────────┬─────────┘
         │
         ▼ play_create_codigo.yaml
┌──────────────────┐
│ Configs/*.cfg    │  ← Generated configurations
└────────┬─────────┘
         │
         ▼ play_config_devices.yaml
┌──────────────────┐
│ Network          │  ← Cisco IOS Switches
│ Devices          │
└──────────────────┘
```

## References

- [Ansible Documentation](https://docs.ansible.com/)
- [Cisco IOS Collection](https://galaxy.ansible.com/cisco/ios)
- [Ansible Vault Guide](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: December 2025
