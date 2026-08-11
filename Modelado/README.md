# Modelado de Datos para Automatización de Red

Este proyecto demuestra técnicas de modelado de datos YAML y validación con JSON Schema para automatización de infraestructura de red.

## Descripción

El proyecto incluye ejemplos de:

- Modelado de datos de infraestructura de red en formato YAML
- Validación de datos usando JSON Schema
- Reutilización de código en YAML usando anchors y aliases
- Scripts Python para validación automatizada

## Estructura del Proyecto

```
├── main_schema.py           # Script principal de validación
├── main_reutilizacion.py   # Script para demostrar reutilización YAML
├── modelo_datos.yaml       # Modelo principal de infraestructura
├── modelo_schema.json      # Schema de validación principal
├── ejemplo1_datos.yaml     # Ejemplo básico de metadatos
├── ejemplo1_schema.json    # Schema para ejemplo básico
├── ejemplo2_datos.yaml     # Ejemplo de dispositivos de red
├── ejemplo2_schema.json    # Schema para dispositivos
├── ejemplo3_datos.yaml     # Ejemplo que FALLA a proposito (additionalProperties)
├── ejemplo3_schema.json    # Schema restrictivo: maxLength, pattern, minimum/maximum
├── reutilizacion_a.yaml    # Ejemplo de merge keys (<<)
├── reutilizacion_b.yaml    # Ejemplo de anchors y aliases
├── reutilizacion_c.yaml    # Merge keys aplicados a parametros de conexion
├── pyproject.toml          # Configuración del proyecto
└── .python-version         # Versión de Python requerida
```

## Requisitos

- Python 3.12+
- Dependencias (definidas en [pyproject.toml](pyproject.toml)):
  - `jsonschema>=4.25.1`
  - `pyyaml>=6.0.3`

## Instalación

```bash
# Instalar dependencias
uv add jsonschema pyyaml
```

## Uso

### Validación de Modelos de Datos

Use el script [`main_schema.py`](main_schema.py) para validar modelos YAML contra esquemas JSON:

```bash
# Validar modelo principal
python main_schema.py modelo_datos.yaml modelo_schema.json

# Validar ejemplos
python main_schema.py ejemplo1_datos.yaml ejemplo1_schema.json
python main_schema.py ejemplo2_datos.yaml ejemplo2_schema.json
```

### Explorar Reutilización de Código YAML

Use el script [`main_reutilizacion.py`](main_reutilizacion.py) para ver ejemplos de reutilización:

```bash
# Ejemplo de merge keys
python main_reutilizacion.py reutilizacion_a.yaml

# Ejemplo de anchors y aliases
python main_reutilizacion.py reutilizacion_b.yaml
```

## Ejemplos de Modelado

### 1. Modelo Principal ([modelo_datos.yaml](modelo_datos.yaml))

Modelo completo de infraestructura de red que incluye:

- **Metadatos**: Información del proyecto, versión, autor
- **Dispositivos**: Switches con configuración de management y conectividad
- **Interfaces**: Configuración detallada de puertos (access/trunk)
- **VLANs**: Definición de redes virtuales
- **Especificaciones de configuración**: Templates y archivos de configuración

### 2. Ejemplos Básicos

- **[ejemplo1_datos.yaml](ejemplo1_datos.yaml)**: Modelo simple con metadatos básicos
- **[ejemplo2_datos.yaml](ejemplo2_datos.yaml)**: Modelo de dispositivos con IPs IPv4/IPv6
- **[ejemplo3_datos.yaml](ejemplo3_datos.yaml)**: **está diseñado para NO validar.** Su esquema usa
  restricciones más finas (`maxLength`, `pattern`, `minimum`/`maximum`) y cierra el objeto con
  `additionalProperties: false`; el dato trae un `fecha_creacion` que el esquema no declara.
  Al validarlo se obtiene:

  ```text
  -> El modelo de datos es inválido:
  Additional properties are not allowed ('fecha_creacion' was unexpected)
  Path: []
  Validator: additionalProperties
  ```

  El objetivo del ejercicio es ver **cómo se lee un error de validación**: qué validador falló, en qué
  ruta y por qué. Que falle no es un bug del repositorio.

### 3. Reutilización de Código YAML

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

#### Anchors y Aliases ([reutilizacion_b.yaml](reutilizacion_b.yaml))

```yaml
commands: &base_commands
  - Iniciando
  - Ejecutando tarea principal
  - Finalizado

job1:
  steps: *base_commands
```

#### Merge Keys aplicados a la conexión ([reutilizacion_c.yaml](reutilizacion_c.yaml))

El caso realista, y el eslabón entre los dos ejemplos anteriores y el modelo de verdad: los
parámetros de conexión se declaran una vez y cada dispositivo solo aporta su `host`.

```yaml
datos_devices: &common_devices
  device_type: cisco_ios
  user: admin
  password: secret
  global_delay_factor: 2

devices:
  - host: 10.1.1.1
    <<: *common_devices
  - host: 10.1.1.2
    <<: *common_devices
```

Con cuarenta dispositivos, cambiar el `global_delay_factor` es editar **una** línea.

## Esquemas de Validación

Los archivos JSON Schema definen las reglas de validación:

- **[modelo_schema.json](modelo_schema.json)**: Schema completo para infraestructura
- **[ejemplo1_schema.json](ejemplo1_schema.json)**: Schema básico para metadatos
- **[ejemplo2_schema.json](ejemplo2_schema.json)**: Schema para dispositivos de red

### Características de Validación

- Tipos de datos (string, integer, boolean, array, object)
- Formatos específicos (date, ipv4, ipv6)
- Restricciones de longitud y rango
- Campos requeridos y opcionales
- Validación de enums y patrones

## Funcionalidades

### Script de Validación ([main_schema.py](main_schema.py))

- Carga y valida archivos YAML contra esquemas JSON
- Proporciona mensajes de error detallados
- Soporte para validación de formatos (IP, fechas)
- Manejo de errores con paths específicos

### Script de Reutilización ([main_reutilizacion.py](main_reutilizacion.py))

- Demuestra técnicas de reutilización en YAML
- Carga y muestra la estructura resultante
- Útil para entender anchors, aliases y merge keys

## Casos de Uso

Este proyecto es útil para:

1. **Automatización de Red**: Modelar configuraciones de switches y routers
2. **Gestión de Infraestructura**: Definir topologías de red de forma estructurada
3. **Validación de Configuraciones**: Asegurar consistencia en modelos de datos
4. **Documentación de Red**: Mantener inventarios estructurados de dispositivos
5. **Plantillas de Configuración**: Generar configuraciones a partir de modelos

## Beneficios del Modelado

- **Consistencia**: Esquemas garantizan estructura uniforme
- **Validación**: Detección temprana de errores
- **Reutilización**: Evita duplicación de código
- **Mantenibilidad**: Estructura clara y documentada
- **Escalabilidad**: Fácil adición de nuevos dispositivos

## Contribución

Para contribuir al proyecto:

1. Asegúrese de validar todos los modelos antes de commit
2. Mantenga la documentación actualizada
3. Siga las convenciones de nomenclatura existentes
4. Incluya tests para nuevas funcionalidades

## Autor

Ed Scrimaglia - Curso de Network Automation, UTN Academia