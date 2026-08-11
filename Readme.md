# Automatización de Redes - UTN-FRC Academia de Cisco

**Autor:** Ed Scrimaglia  
**Institución:** Universidad Tecnológica Nacional - Facultad Regional Córdoba  
**Curso:** Network Automation Engineer  
**Fecha de Creación:** 2 de Diciembre del 2025  

---

## Descripción General

Este repositorio contiene el material práctico completo del curso de Automatización de Redes, organizado en módulos progresivos que van desde fundamentos de Python hasta implementaciones empresariales de Infrastructure as Code (IaC) con Ansible y Netmiko.

**Enfoque pedagógico:** Cada módulo incluye ejemplos incrementales, casos de uso reales y simulacros integradores que preparan para escenarios profesionales en gestión y automatización de redes empresariales.

---

## Estructura del Proyecto

```tree
Codigo/
├── Python_Basics/         # Fundamentos de programación Python
├── json/                  # Manipulación de archivos JSON
├── yaml/                  # Manipulación de archivos YAML
├── Modelado/              # Modelado y validación de datos → README.md
├── Netmiko/               # Automatización con Netmiko
│   ├── ejemplo1/          # Comandos básicos y TextFSM → README.md
│   ├── ejemplo2/          # Configuración con templates Jinja2 → README.md
│   └── sim_caso/          # Simulacro integrador → README.md
├── Ansible/               # Automatización con Ansible
│   ├── ejemplo1/          # Variables y comandos show → README.md
│   ├── ejemplo2/          # Estructuras de programación → README.md
│   ├── ejemplo3/          # Ansible Vault y templates → README.md
│   ├── sim_caso/          # Simulacro empresarial completo → README.md
│   └── ssh-config/        # Config SSH para equipos con algoritmos legacy
└── RestApi/               # Automatización vía REST API → README.md
```

**Nota:** Los directorios marcados con `→ README.md` contienen documentación detallada en sus respectivos archivos README.

---

## Módulos del Curso

### 1. Python Basics

**Ubicación:** [`Python Basics/`](Python_Basics/)

**Objetivo:** Fundamentos de Python para automatización: clases, módulos, estructuras de datos.

**Contenido:**

- Programación orientada a objetos (clases básicas y avanzadas)
- Operaciones matemáticas y manejo de atributos
- Gestión de módulos e importaciones
- Estructuras de datos: diccionarios y listas

**Scripts:** `main.py`, `class_oper_basic_math.py`, `class_oper_advance_math.py`, `class_basic_attr.py`

---

### 2. Manipulación de Datos (JSON/YAML)

#### JSON

**Ubicación:** [`json/`](json/)

**Contenido:**

- `manage_json.py`: Clase `JsonHandler` para serialización/deserialización JSON
- `diccionario.py`: Estructuras de datos de ejemplo
- `devices.json`: Archivo JSON generado

**Técnicas:** `json.dump()`, `json.load()`, `json.dumps()`, `json.loads()`

#### YAML

**Ubicación:** [`yaml/`](yaml/)

**Contenido:**

- `manage_yaml.py`: Clase `YamlHandler` para lectura de YAML
- `file.yaml`: Ejemplo de archivo YAML

**Ventaja:** Mayor legibilidad, soporte de comentarios, formato estándar en Ansible.

---

### 3. Modelado de Datos

**Ubicación:** [`Modelado/`](Modelado/) → **[Ver README completo](Modelado/README.md)**

**Objetivo:** Modelado avanzado de infraestructuras con validación JSON Schema y reutilización YAML.

**Contenido:**

- Modelos de datos de infraestructura YAML
- Validación con JSON Schema (draft-07)
- Técnicas de reutilización: anchors (`&`), aliases (`*`), merge keys (`<<:`)
- Scripts de validación: `main_schema.py`, `main_reutilizacion.py`
- Ejemplos progresivos con modelos y esquemas

**Casos de uso:** Source of Truth centralizado, validación de configuraciones, input para automatización.

---

### 4. Automatización con Netmiko

#### Ejemplo 1: Fundamentos

**Ubicación:** [`Netmiko/ejemplo1/`](Netmiko/ejemplo1/) → **[Ver README completo](Netmiko/ejemplo1/README.md)**

**Temas:** Conexiones SSH, comandos show, parseo con TextFSM, análisis con CiscoConfParse, optimización de rendimiento, clase reutilizable `NetmikoInicial`.

**Scripts:** `netmiko_eje1.py` (básicos), `netmiko_eje2.py` (TextFSM), `netmiko_eje3.py` (optimización), `netmiko_eje4.py` (CiscoConfParse), `integrador1.py`

#### Ejemplo 2: Configuración Avanzada

**Ubicación:** [`Netmiko/ejemplo2/`](Netmiko/ejemplo2/) → **[Ver README completo](Netmiko/ejemplo2/README.md)**

**Temas:** Configuración con `send_config_set()` y `send_config_from_file()`, templates Jinja2, comandos multilínea, validación de errores, clase `ConfigurationClass`.

**Scripts:** `netmiko_eje1.py` a `netmiko_eje4.py`, `integrador2.py`, templates en `templates/`

#### Simulacro: Implementación Profesional

**Ubicación:** [`Netmiko/sim_caso/`](Netmiko/sim_caso/) → **[Ver README completo](Netmiko/sim_caso/README.md)**

**Descripción:** Solución end-to-end modular y escalable para configurar múltiples dispositivos.

**Componentes:**

- `main.py`: Orquestador principal
- `class_device_config.py`: Gestión de conexiones SSH
- `class_create_configs.py`: Renderizado de templates Jinja2
- `modelo_datos.yaml`: Source of Truth centralizado
- Templates para VLANs, interfaces access/trunk

**Flujo:** Leer modelo → Generar configs → Conectar SSH → Aplicar → Validar → Guardar

---

### 5. Automatización con Ansible

#### Ejemplo 1: Variables y Consultas

**Ubicación:** [`Ansible/ejemplo1/`](Ansible/ejemplo1/) → **[Ver README completo](Ansible/ejemplo1/README.md)**

**Temas:** Inventarios, modelos de datos, validación JSON Schema, manipulación de variables, `hostvars`, filtros Jinja2, comandos show en Cisco IOS.

**Componentes:** `inventario.ini`, `modelo_datos.yaml`, `validador_modelo.json`, playbooks 1-3, `host_vars/`, `group_vars/`

**Colecciones:** `cisco.ios`, `ansible.netcommon`

#### Ejemplo 2: Estructuras de Programación

**Ubicación:** [`Ansible/ejemplo2/`](Ansible/ejemplo2/) → **[Ver README completo](Ansible/ejemplo2/README.md)**

**Temas:** Condicionales (`when`), loops (`loop`), manejo de errores (`block/rescue/always`), tareas reutilizables (`include_tasks`), variables compartidas.

**Componentes:** `ansible.cfg`, `tasks/validate.yaml`, `tasks/timestamp.yaml`, playbooks 1-6

#### Ejemplo 3: Ansible Vault y Templates

**Ubicación:** [`Ansible/ejemplo3/`](Ansible/ejemplo3/) → **[Ver README completo](Ansible/ejemplo3/README.md)**

**Temas:** Encriptación de credenciales con Ansible Vault, templates Jinja2, YAML anchors/aliases, generación y aplicación de configuraciones, handlers condicionales.

**Componentes:** `group_vars/cisco_ios/vault.yaml`, `modelo/modelo.yaml`, `templates/`, `play_create_codigo.yaml`, `play_config_devices.yaml`

**Workflow:** Generar configs → Revisar → Aplicar a dispositivos (con `--vault-password-file`)

#### Simulacro: Solución Empresarial

**Ubicación:** [`Ansible/sim_caso/`](Ansible/sim_caso/) → **[Ver README completo](Ansible/sim_caso/README.md)**

**Descripción:** Implementación empresarial completa con alta disponibilidad, documentación automatizada.

**Arquitectura:**

- 2 Switches Core (EIGRP AS 10, VRRP)
- 2 Switches Acceso + 1 Datacenter
- 3 VLANs (Ingeniería, Producción, Finanzas)

**Componentes:**

- `modelo_datos/modelo.yaml`: Source of Truth completo
- Templates para configuración (trunk, access, VLANs, SVIs, EIGRP) y documentación
- Playbooks: `play_create_codigo.yaml`, `play_config_devices.yaml`, `play_create_documentacion.yaml`
- Tasks reutilizables, validación JSON Schema

**Características:** IaC completo, alta disponibilidad (VRRP, EIGRP), validación automática, documentación técnica autogenerada.

**Flujo:** Generar configs → Aplicar a dispositivos → Generar documentación

---

### 6. Automatización con REST API

**Ubicación:** [`RestApi/`](RestApi/) → **[Ver README completo](RestApi/README.md)**

**Objetivo:** Resolver el mismo problema del curso sobre HTTP en lugar de SSH, con la API como interfaz del equipo.

**Temas:** Cliente `requests` con sesión y reintentos, autenticación por token, verificación TLS, códigos de estado, y reconciliación declarativa con `--dry-run` y eliminación de deriva.

**Componentes:**

- `rest_clase.py`: clase `RestClient` — login, sesión reutilizable, manejo de errores
- `mock_server.py`: simulador de controlador (FastAPI), para trabajar sin equipo real
- `rest_eje1.py`, `rest_eje2.py`, `rest_eje3.py`: ejemplos progresivos
- `integrador3.py`: integrador que reconcilia el estado del equipo contra `modelo_datos.yaml`

**Cómo correrlo:** levantar `mock_server.py` en una terminal y ejecutar los ejemplos en otra. No hace falta laboratorio.

---

## Requisitos y Configuración

### Requisitos Generales

- **Python:** 3.12 o superior
- **Sistema:** Linux, macOS, Windows (WSL recomendado)
- **Gestor de paquetes:**  uv (recomendado)

### Dependencias por Tecnología

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

**Colecciones Ansible:**

```bash
ansible-galaxy collection install cisco.ios ansible.netcommon
```

**Modelado:**

```toml
jsonschema >= 4.25.1
pyyaml >= 6.0.3
```

### Instalación Rápida

**Con uv (recomendado):**

```bash
cd Netmiko/ejemplo1  # o cualquier proyecto
uv sync
```

---

## Guía de Uso

### Ruta de Aprendizaje

1. **Python Basics** → Fundamentos
2. **json/ y yaml/** → Manipulación de datos
3. **Modelado/** → Validación y Source of Truth
4. **Netmiko/ejemplo1/** → Conexiones y comandos
5. **Netmiko/ejemplo2/** → Configuración con templates
6. **Netmiko/sim_caso/** → Implementación completa
7. **Ansible/ejemplo1/** → Variables y consultas
8. **Ansible/ejemplo2/** → Estructuras de programación
9. **Ansible/ejemplo3/** → Vault y templates
10. **Ansible/sim_caso/** → Solución empresarial

### Mejores Prácticas

- **Entornos virtuales:** Uno por proyecto, evitar instalaciones globales
- **Seguridad:** Ansible Vault para credenciales, no versionar `.vault-pass`
- **Versionamiento:** Commits frecuentes, `.gitignore` apropiado
- **Testing:** Probar en laboratorio, validar modelos, backups previos

---

## Recursos Adicionales

**Documentación:**

- [Ansible](https://docs.ansible.com/) | [Netmiko](https://github.com/ktbyers/netmiko) | [Jinja2](https://jinja.palletsprojects.com/) | [JSON Schema](https://json-schema.org/) | [CiscoConfParse](https://ciscoconfparse.readthedocs.io/)

**Herramientas:**

- **Editor:** VS Code (extensiones: Python, Ansible, YAML, Jinja2)
- **Emuladores:** GNS3, EVE-NG, Cisco CML, Containerlab

**Comunidad:**

- [Ansible Galaxy](https://galaxy.ansible.com/) | [Network to Code Slack](https://networktocode.slack.com/) | [r/networking](https://www.reddit.com/r/networking/) | [r/ansible](https://www.reddit.com/r/ansible/)

---

## Notas Importantes

- Cada subdirectorio con ejemplos incluye su propio **README.md detallado**
- Los `pyproject.toml` definen dependencias específicas de cada proyecto
- Los simulacros integran todos los conceptos del módulo
- Material diseñado para uso académico y educativo

## Licencia

Proyecto educativo - UTN-FRC Academia Cisco - Network Automation Engineer Course

---

**Última actualización**: Diciembre 2025  
