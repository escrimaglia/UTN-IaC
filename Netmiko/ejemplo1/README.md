# Proyecto Netmiko - Ejemplos de Automatización de Redes Cisco

## Descripción del Proyecto

Este proyecto contiene una colección de scripts Python que demuestran el uso de **Netmiko** para la automatización de dispositivos de red Cisco. El proyecto incluye ejemplos progresivos que van desde comandos básicos hasta implementaciones más avanzadas utilizando parseo de configuraciones con **TextFSM** y **CiscoConfParse**.

## Información del Proyecto

**Autor:** Ed Scrimaglia  
**Versión:** 1.0  
**Fecha de Creación:** 6 de Septiembre de 2025
**Descripción**: Primer ejemplo Netmiko

## Dependencias

El proyecto utiliza las siguientes bibliotecas principales:

- **netmiko** (>=4.6.0): Biblioteca multi-vendor para simplificar conexiones SSH a dispositivos de red
- **ciscoconfparse** (>=1.9.52): Biblioteca para parsear y analizar configuraciones de dispositivos Cisco

Estas dependencias se encuentran definidas en el archivo `pyproject.toml`.

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

## Estructura del Proyecto

```tree
ejemplo1/
├── pyproject.toml          # Configuración del proyecto y dependencias
├── netmiko_clase.py        # Clase principal NetmikoInicial con métodos reutilizables
├── netmiko_eje1.py         # Ejemplo 1: Comandos básicos
├── netmiko_eje2.py         # Ejemplo 2: Uso de TextFSM
├── netmiko_eje3.py         # Ejemplo 3: Parámetros de optimización
├── netmiko_eje4.py         # Ejemplo 4: CiscoConfParse
├── integrador1.py          # Ejemplo integrador usando la clase NetmikoInicial
└── textfsm/                # Template TextFSM propio (capitulo 9 §9.4)
    ├── cisco_ios_show_interfaces_trunk.textfsm
    ├── salida_trunk.txt    # Salida real, versionada como caso de prueba
    └── probar_template.py  # Prueba el template contra el archivo, sin equipo
```

## Descripción de los Scripts

### 1. `netmiko_clase.py` - Clase NetmikoInicial

Implementa una clase Python que encapsula las funcionalidades más comunes de Netmiko:

**Métodos principales:**

- `connect(device_params)`: Establece conexión SSH con el dispositivo
- `enable_mode(connection)`: Entra en modo privilegiado
- `config_mode(connection)`: Entra en modo de configuración global
- `get_prompt(connection)`: Obtiene el prompt actual del dispositivo
- `send_command(connection, command, expect_string, use_textfsm)`: Envía comandos al dispositivo
- `connection_status(connection)`: Verifica el estado de la conexión
- `parse_running_config(config_output)`: Parsea la configuración usando CiscoConfParse
- `disconnect(connection)`: Cierra la conexión

**Características:**

- Manejo robusto de excepciones
- Soporte para TextFSM
- Parseo automático de configuraciones con CiscoConfParse
- Extracción de interfaces y direcciones IP

### 2. `netmiko_eje1.py` - Comandos Básicos

**Objetivo**: Demostrar el uso básico de Netmiko para conectarse a un dispositivo Cisco y ejecutar comandos.

**Conceptos cubiertos:**

- Establecimiento de conexión SSH
- Verificación del estado de la conexión con `is_alive()`
- Navegación entre modos (usuario → privilegiado → configuración)
- Obtención y análisis del prompt con `find_prompt()`
- Envío de comandos con `send_command()`
- Uso del parámetro `expect_string` para control de salida
- Cierre correcto de la conexión

**Comandos ejecutados:**

- `show ip interface brief`

### 3. `netmiko_eje2.py` - Uso de TextFSM

**Objetivo**: Demostrar el parseo automático de salidas de comandos usando TextFSM.

**Conceptos cubiertos:**

- Uso del parámetro `use_textfsm=True` para parseo automático
- Procesamiento de salidas estructuradas (listas de diccionarios)
- Extracción de información específica (versión de IOS)
- Validación del tipo de datos retornados

**Comandos ejecutados:**

- `show version` (con parseo TextFSM)

**Ventajas de TextFSM:**

- Convierte salidas de texto plano en datos estructurados
- Facilita la extracción de información específica
- Permite procesamiento programático de datos

### 3b. `textfsm/` - Escribir un template propio

**Objetivo**: Escribir un template TextFSM cuando el comando no tiene uno en `ntc-templates`.

`use_textfsm=True` funciona porque alguien escribió el template. `ntc-templates` 7.7.0 trae 127
templates para `cisco_ios`, pero **`show interfaces trunk` no está entre ellos**: el comando existe
en IOS, la plantilla no. Este directorio lo resuelve.

La dificultad del comando es que devuelve **cuatro tablas con el mismo encabezado `Port`** en una
sola salida. Un template de una sola regla las trata como una y devuelve seis filas para dos
interfaces —cada una repetida tres veces, provenientes de tablas que significan cosas distintas— sin
ningún campo que permita distinguirlas. La solución es una máquina de estados, que es lo que TextFSM
es.

**Probarlo, sin equipo ni laboratorio:**

```bash
cd textfsm
uv run python probar_template.py
```

```text
['PORT', 'VLANS_PERMITIDAS']
[
  {
    "PORT": "Gi0/1",
    "VLANS_PERMITIDAS": "10,20"
  },
  {
    "PORT": "Gi0/2",
    "VLANS_PERMITIDAS": "10,20"
  }
]

-> OK: 2 filas, como se esperaba
```

El script compara contra el resultado esperado y devuelve código de salida 1 si no coincide, así que
sirve como test en un pipeline. `salida_trunk.txt` es el caso de prueba: el día que una actualización
de IOS cambie el formato, esto falla acá y no en producción.

**Enchufarlo a Netmiko.** La trampa está en el orden de búsqueda: si `NET_TEXTFSM` está definida,
gana, y los 127 templates comunitarios **dejan de verse**. Agregar un template propio así arregla un
comando y rompe los otros ciento veintisiete. La receta que no rompe nada es copiar el set completo y
sumarle el propio:

```bash
uv run python -c "import ntc_templates, os; \
  print(os.path.join(os.path.dirname(ntc_templates.__file__), 'templates'))"

cp -r /ruta/que/imprimio/arriba ~/mis-templates
cp textfsm/cisco_ios_show_interfaces_trunk.textfsm ~/mis-templates/
export NET_TEXTFSM=~/mis-templates
```

Y declararlo en el `index` de ese directorio. Las entradas se prueban de arriba hacia abajo, así que
esta va **antes** que la de `show interfaces status`:

```text
cisco_ios_show_interfaces_trunk.textfsm, .*, cisco_ios, sh[[ow]] int[[erfaces]] tr[[unk]]
```

> ⚠️ El template está verificado contra `salida_trunk.txt`, no contra un equipo. Si los switches
> escriben `GigabitEthernet0/1` en lugar de `Gi0/1`, la regex `(\S+)` los toma igual, pero conviene
> regenerar `salida_trunk.txt` con la salida real del laboratorio.

Ver el capítulo 9 §9.4 del libro para la explicación completa: los modificadores de `Value`, las
acciones de regla, y por qué TextFSM no puede hacer joins.

### 4. `netmiko_eje3.py` - Optimización de Rendimiento

**Objetivo**: Demostrar el uso de parámetros de optimización para mejorar el rendimiento de las conexiones.

**Conceptos cubiertos:**

- Parámetro `global_delay_factor`: Ajusta los tiempos de espera globalmente
  - Valores bajos (0.1): Mayor velocidad, útil con conexiones estables
  - Valores altos (1.5): Mayor estabilidad, útil con conexiones lentas
- Alternativa `fast_cli=True` para conexiones rápidas
- Iteración sobre múltiples dispositivos con diferentes configuraciones
- Comparación de rendimiento

**Comandos ejecutados:**

- `show version` (con diferentes configuraciones de delay)

**Mejores prácticas:**

- Usar `global_delay_factor=0.1` o `fast_cli=True` para laboratorios
- Usar valores más altos en entornos de producción o conexiones inestables

### 5. `netmiko_eje4.py` - CiscoConfParse

**Objetivo**: Demostrar el parseo avanzado de configuraciones usando CiscoConfParse.

**Conceptos cubiertos:**

- Obtención de `running-config`
- Conversión de salida a lista de líneas con `splitlines()`
- Creación de objeto `CiscoConfParse`
- Búsqueda de objetos de configuración con expresiones regulares
- Búsqueda de objetos hijos (child objects)
- Dos métodos de búsqueda:
  1. `re_search_children()`: Busca hijos dentro de un objeto padre
  2. `find_child_objects()`: Busca relaciones padre-hijo específicas

**Comandos ejecutados:**

- `show running-config`

**Análisis realizado:**

- Extracción de todas las interfaces
- Identificación de direcciones IP asignadas a cada interfaz
- Detección de interfaces sin IP

### 6. `integrador1.py` - Implementación con Clase

**Objetivo**: Demostrar el uso de la clase `NetmikoInicial` para una implementación limpia y reutilizable.

**Conceptos cubiertos:**

- Instanciación de la clase `NetmikoInicial`
- Uso de métodos encapsulados
- Validación de estado de conexión
- Procesamiento de comandos con y sin TextFSM
- Parseo de configuración con el método de la clase
- Salida formateada en JSON

**Funcionalidad:**

1. Establece conexión con el dispositivo
2. Valida el estado de la conexión
3. Entra en modo privilegiado
4. Ejecuta comandos con parseo TextFSM
5. Obtiene y parsea la configuración
6. Cierra la conexión limpiamente

**Ventajas del enfoque orientado a objetos:**

- Código más organizado y mantenible
- Reutilización de lógica común
- Manejo centralizado de errores
- Fácil extensión de funcionalidades

## Configuración de Dispositivos

Antes de ejecutar los scripts, debes configurar los parámetros de conexión en cada archivo:

```python
device = {
    'device_type': 'cisco_ios',
    'host': 'X.X.X.X',        # Dirección IP del dispositivo
    'username': 'xxxx',       # Usuario SSH
    'password': 'xxxx',       # Contraseña
    'ssh_config_file': '~/.ssh/config'  # Archivo de configuración SSH (opcional)
}
```

### Parámetros Adicionales Disponibles

- `global_delay_factor`: Factor de multiplicación para los delays (default: 1)
- `fast_cli`: Modo rápido para conexiones estables (boolean)
- `timeout`: Timeout para la conexión inicial (segundos)
- `secret`: Contraseña para modo enable (si es diferente)

## Uso

### Ejecutar ejemplos individuales

```bash
# Ejemplo 1: Comandos básicos
python netmiko_eje1.py

# Ejemplo 2: TextFSM
python netmiko_eje2.py

# Ejemplo 3: Optimización
python netmiko_eje3.py

# Ejemplo 4: CiscoConfParse
python netmiko_eje4.py

# Ejemplo integrador con clase
python integrador1.py
```

### Usar la clase en tus propios scripts

```python
from netmiko_clase import NetmikoInicial

device_params = {
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "password"
}

net = NetmikoInicial()
conn = net.connect(device_params)
net.enable_mode(conn)
output = net.send_command(conn, "show version", use_textfsm=True)
net.disconnect(conn)
```

## Funcionalidades Principales

### 1. Gestión de Conexiones

- Conexión SSH automática
- Verificación de estado
- Manejo de timeouts y errores de autenticación
- Cierre seguro de conexiones

### 2. Navegación de Modos

- Modo usuario (USER EXEC)
- Modo privilegiado (PRIVILEGED EXEC)
- Modo de configuración global (CONFIG)
- Detección automática del modo actual

### 3. Ejecución de Comandos

- Comandos show
- Soporte para expect_string personalizado
- Parseo automático con TextFSM
- Parseo de configuraciones con CiscoConfParse

### 4. Análisis de Configuraciones

- Extracción de interfaces
- Identificación de direcciones IP
- Análisis de relaciones padre-hijo en configuraciones
- Búsqueda con expresiones regulares

## Manejo de Errores

Todos los scripts implementan manejo de excepciones para:

- `NetmikoTimeoutException`: Timeout en la conexión
- `NetmikoAuthenticationException`: Errores de autenticación
- `Exception`: Errores genéricos de Netmiko

La clase `NetmikoInicial` proporciona mensajes de error descriptivos para facilitar el debugging.

## Mejores Prácticas

1. **Seguridad**:
   - No hardcodear credenciales en el código
   - Usar variables de entorno o archivos de configuración
   - Configurar SSH keys cuando sea posible

2. **Rendimiento**:
   - Usar `fast_cli=True` o `global_delay_factor=0.1` en laboratorios
   - Ajustar timeouts según la latencia de red
   - Cerrar siempre las conexiones

3. **Código**:
   - Usar la clase `NetmikoInicial` para código reutilizable
   - Implementar manejo de errores robusto
   - Validar estados antes de ejecutar comandos

4. **Parseo**:
   - Usar TextFSM para comandos show estándar
   - Usar CiscoConfParse para análisis de configuraciones complejas
   - Validar el tipo de dato retornado antes de procesarlo

## Recursos Adicionales

- [Documentación oficial de Netmiko](https://github.com/ktbyers/netmiko)
- [Documentación de CiscoConfParse](https://github.com/mpenning/ciscoconfparse)
- [TextFSM Templates](https://github.com/networktocode/ntc-templates)

## Troubleshooting

### Problema: Timeout al conectar

**Solución**: Verificar conectividad de red y aumentar el parámetro `timeout`

### Problema: Error de autenticación

**Solución**: Verificar credenciales y que SSH esté habilitado en el dispositivo

### Problema: TextFSM no parsea la salida

**Solución**: Verificar que exista un template para el comando y versión de IOS

### Problema: CiscoConfParse no encuentra objetos

**Solución**: Revisar las expresiones regulares y la estructura de la configuración

## Licencia

Proyecto educativo - UTN-FRC Academia Cisco - Network Automation Engineer Course

---

**Última actualización**: Diciembre 2025
