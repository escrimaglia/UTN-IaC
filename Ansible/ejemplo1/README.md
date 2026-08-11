# Proyecto de Automatización de Redes con Ansible

**Autor:** Ed Scrimaglia  
**Versión:** 0.1.0  
**Descripción:** Manipulación y uso de variables en Ansible  
**Fecha de Creación:** 28 de noviembre de 2025

## Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Requisitos](#-requisitos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Inventario](#-inventario)
- [Modelo de Datos](#-modelo-de-datos)
- [Playbooks](#-playbooks)
- [Variables](#-variables)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Uso](#-uso)

## Descripción General

Este proyecto implementa automatización de configuración y consulta de dispositivos de red Cisco IOS utilizando Ansible. Incluye ejemplos de:

- Ejecución de comandos show en dispositivos Cisco IOS
- Gestión de variables y datos estructurados
- Validación de modelos de datos con JSON Schema
- Uso de templates Jinja2 para formateo de salidas
- Configuración de VLANs e interfaces

## Requisitos

### Dependencias Python

El proyecto requiere Python 3.12 o superior. Las dependencias se gestionan mediante `pyproject.toml`:

```toml
- ansible >= 12.2.0
- jsonschema >= 4.25.1
```

### Colecciones Ansible Necesarias

```bash
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install ansible.netcommon
```

## Estructura del Proyecto

```tree
ejemplo1/
├── pyproject.toml              # Definición del proyecto y dependencias
├── inventario.ini              # Inventario de dispositivos de red
├── playbook1.yaml              # Consultas a dispositivos Cisco IOS
├── playbook2.yaml              # Visualización y manipulación de variables
├── playbook3.yaml              # Uso de hosts dinámicos desde modelo de datos
├── modelo_datos/
│   └── modelo_datos.yaml       # Modelo de datos de la infraestructura
├── json_files/
│   └── validador_modelo.json   # JSON Schema para validación
├── host_vars/
│   ├── SW-Bld_A.yaml          # Variables específicas del host
│   └── SW-Bld_B.yaml          # Variables específicas del host
└── group_vars/
    └── cisco_ios.yaml          # Variables del grupo cisco_ios
```

## Inventario

El archivo `inventario.ini` define la infraestructura de red organizada en grupos:

### Grupos Definidos

- **`cisco_ios_access_bsas`**: Switches de acceso en Buenos Aires
  - SW-Bld_A (10.2.0.10X)

- **`cisco_ios_access_cba`**: Switches de acceso en Córdoba
  - SW-Bld_B (10.2.0.10X)

- **`cisco_ios_datacenter`**: Switches del datacenter
  - SW-Data_Center (10.2.0.10X)

- **`cisco_ios_core`**: Switches de core
  - SW-CORE_1 (10.2.0.10X)

- **`cisco_ios`**: Grupo padre que agrupa todos los dispositivos Cisco IOS

### Variables Globales

```ini
[all:vars]
ansible_connection=ansible.netcommon.network_cli
```

## Modelo de Datos

El archivo `modelo_datos/modelo_datos.yaml` contiene la definición estructurada de la infraestructura:

### Estructura del Modelo

```yaml
modelo:
  metadatos:
    proyecto: "Ejemplos de palybooks para manejo de variables"
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
          # ... credenciales y configuración SSH
        interfaces:
          # ... definición de interfaces trunk y access
        vlans:
          # ... definición de VLANs
        config_spec:
          # ... especificaciones de configuración
```

### Validación con JSON Schema

El archivo `json_files/validador_modelo.json` define un esquema JSON Schema (draft-07) que valida:

- Metadatos del proyecto (nombre, versión, autor, fecha)
- Especificaciones de dispositivos
- Configuración de management (IP, interfaz)
- Parámetros de conexión (tipo, host, credenciales)
- Interfaces (nombre, descripción, modo access/trunk, VLANs)
- Formatos de direcciones IP (IPv4/IPv6)

## Playbooks

### playbook1.yaml - Consultas a Dispositivos

**Propósito:** Ejecutar comandos show en dispositivos Cisco IOS

**Características:**

- Dos plays separados para dispositivos de acceso y core
- Ejecuta `show ip interface brief`
- Muestra la salida formateada

**Ejecución:**

```bash
ansible-playbook -i inventario.ini playbook1.yaml
```

**Hosts objetivo:**

- Play 1: `cisco_ios` (todos los dispositivos)
- Play 2: `cisco_ios_core` (solo core)

### playbook2.yaml - Visualización de Variables

**Propósito:** Demostrar diferentes técnicas de manipulación y visualización de variables

**Características:**

- Carga del modelo de datos desde archivo YAML
- Visualización de dispositivos en formato JSON
- Lectura y validación con JSON Schema
- Creación de variables con `set_fact`
- Acceso a `hostvars` y variables del sistema

**Ejecución:**

```bash
ansible-playbook -i inventario.ini playbook2.yaml
```

**Técnicas demostradas:**

```yaml
# Formateo con Jinja2
msg: |
  {% for device in modelo.infra_spec.devices -%}
  {{ device }}
  {% endfor -%}

# Lectura de JSON Schema
msg: "{{ lookup('file', schema_path) | from_json }}"

# Definición de variables
set_fact:
  mis_devices: "{{ modelo.infra_spec.devices }}"

# Acceso a hostvars
var: hostvars[inventory_hostname]

# Acceso directo a los metadatos del modelo
var: modelo.metadatos

# Formateo personalizado de metadatos
msg: "Proyecto: {{ modelo.metadatos.proyecto }}, Version: {{ modelo.metadatos.version }}"

# Variables del sistema que Ansible expone por host
var: hostvars[inventory_hostname].playbook_dir
```

---

### playbook3.yaml - Hosts Dinámicos

**Propósito:** Usar variables del modelo de datos para definir hosts objetivo dinámicamente

**Características:**

- El parámetro `hosts` se obtiene del modelo de datos
- Ejecuta comandos en dispositivos definidos en `modelo.infra_spec.hosts_group`
- Visualiza interfaces de cada dispositivo

**Ejecución:**

```bash
ansible-playbook -i inventario.ini playbook3.yaml
```

**Nota importante:** El uso de hosts dinámicos puede causar errores en `--syntax-check` ya que las variables no están disponibles en tiempo de validación.

## Variables

### Variables de Grupo (`group_vars/cisco_ios.yaml`)

Variables comunes para todos los dispositivos Cisco IOS:

```yaml
ansible_network_os: cisco.ios.ios
ansible_user: netsim
ansible_become: true
ansible_become_method: ansible.netcommon.enable
ansible_become_password: password
```

### Variables de Host (`host_vars/`)

Credenciales específicas por dispositivo:

```yaml
# SW-Bld_A.yaml
ansible_password: password

# SW-Bld_B.yaml
ansible_password: password
```

### Variables del Modelo de Datos

Accesibles mediante `vars_files`:

```yaml
vars_files:
  - "./modelo_datos/modelo_datos.yaml"
```

Acceso en tareas:

- `modelo.metadatos.proyecto`
- `modelo.metadatos.autor`
- `modelo.infra_spec.devices`
- `modelo.infra_spec.hosts_group`

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd ejemplo1
```

### 2. Configurar Entorno Python

Usando `uv` (recomendado):

```bash
uv sync
```

### 3. Instalar Colecciones Ansible

```bash
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install ansible.netcommon
```

### 4. Configurar Credenciales

Editar archivos en `host_vars/` y `group_vars/` con las credenciales apropiadas.

### 5. Verificar Conectividad

```bash
ansible -i inventario.ini all -m ping
```

## Uso

### Ejecutar Consultas Básicas

```bash
ansible-playbook -i inventario.ini playbook1.yaml
```

### Explorar Variables

```bash
ansible-playbook -i inventario.ini playbook2.yaml
```

### Usar Hosts Dinámicos

```bash
ansible-playbook -i inventario.ini playbook3.yaml
```

### Validación de Sintaxis

```bash
ansible-playbook --syntax-check playbook1.yaml
```

### Modo Dry-Run

```bash
ansible-playbook -i inventario.ini playbook1.yaml --check
```

### Ejecutar en Hosts Específicos

```bash
ansible-playbook -i inventario.ini playbook1.yaml --limit SW-Bld_A
```

### Modo Verboso

```bash
ansible-playbook -i inventario.ini playbook1.yaml -vvv
```

## Conceptos Clave Demostrados

### 1. Organización de Inventario

- Grupos jerárquicos
- Variables de grupo y host
- Parámetros de conexión específicos de red

### 2. Modelo de Datos

- Separación de datos y lógica
- Validación con JSON Schema
- Estructura reutilizable

### 3. Manejo de Variables

- `vars_files` para carga de datos externos
- `set_fact` para variables dinámicas
- `hostvars` para acceso a variables de otros hosts
- Templates Jinja2 para formateo

### 4. Módulos de Red

- `cisco.ios.ios_command` para comandos show
- Registro de salidas con `register`
- Visualización con `ansible.builtin.debug`

### 5. Técnicas Avanzadas

- Hosts dinámicos desde variables
- Delegación de tareas
- Control de bucles con `loop_control`
- Formateo de salida con filtros (`to_nice_json`, `from_yaml`)

## Notas Importantes

1. **Seguridad:** Las credenciales en este proyecto son de ejemplo. En producción, usar Ansible Vault.

2. **Hosts Dinámicos:** El uso de variables en el parámetro `hosts` puede causar fallos en `--syntax-check`.

3. **Conexión de Red:** Los playbooks requieren conectividad SSH a los dispositivos Cisco IOS.

4. **JSON Schema:** La validación del modelo de datos asegura consistencia en la estructura.

5. **Loop Control:** El uso de `label` en `loop_control` reduce verbosidad en la salida.

## Troubleshooting

### Problemas de Conexión SSH

```bash
# Verificar conectividad
ansible -i inventario.ini all -m ping -vvv

# Verificar variables
ansible-inventory -i inventario.ini --list
```

### Variables No Disponibles

```bash
# Verificar que vars_files esté correctamente definido
# Verificar que el path al modelo de datos sea correcto
# Usar delegate_to: localhost para variables locales
```

## Referencias

- [Documentación Ansible](https://docs.ansible.com/)
- [Cisco IOS Collection](https://docs.ansible.com/ansible/latest/collections/cisco/ios/)
- [JSON Schema Draft 07](https://json-schema.org/draft-07/schema)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

## Licencia

Proyecto educativo - UTN-FRC Academia Cisco - Network Automation Engineer Course

---

**Última actualización**: Diciembre 2025
