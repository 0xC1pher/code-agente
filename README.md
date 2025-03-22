```markdown
# Guía Única de Configuración y Uso del MultiAIEditor

```
██████╗ ███████╗███████╗██╗  ██╗    ██████╗  ██████╗ ████████╗
██╔══██╗██╔════╝██╔════╝██║  ██║    ██╔══██╗██╔═══██╗╚══██╔══╝
██║  ██║█████╗  ███████╗███████║    ██████╔╝██║   ██║   ██║   
██║  ██║██╔══╝  ╚════██║██╔══██║    ██╔══██╗██║   ██║   ██║   
██████╔╝███████╗███████║██║  ██║    ██████╔╝╚██████╔╝   ██║   
╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
```

**Versión 2.1.0 - 2025-03-22**

---

## Tabla de Contenidos
1. [Instalación y Dependencias](#1-instalación-y-dependencias)  
2. [Variables de Entorno](#2-variables-de-entorno)  
3. [Lanzamiento del Programa](#3-lanzamiento-del-programa)  
4. [Comandos Universales](#4-comandos-universales)  
5. [Configuración Avanzada](#5-configuración-avanzada)  
6. [Flujos de Trabajo](#6-flujos-de-trabajo)  
7. [Ejemplos de Uso Avanzado](#7-ejemplos-de-uso-avanzado)  
8. [Flujo de Trabajo](#8-flujo-de-trabajo)  
9. [Historial de Versiones](#9-historial-de-versiones)  

---

## 1. Instalación y Dependencias
Configura tu entorno para usar el **MultiAIEditor** con estos pasos sencillos.

### 1.1 Requisitos del Sistema
- **Sistema Operativo:** Linux, MacOS o Windows (WSL2 recomendado para Windows).

### 1.2 Crear Entorno Virtual
Usa un entorno virtual para mantener las dependencias aisladas.

```bash
# Linux/Mac
python -m venv .aienv && source .aienv/bin/activate

# Windows
python -m venv .aienv && .aienv\Scripts\activate
```

### 1.3 Instalar Dependencias
Instala las librerías necesarias con el archivo `requirements.txt`.

```bash
echo "anthropic==0.25.1
openai==1.12.0
python-dotenv==1.0.0
gradio_client==0.15.0
termcolor==2.4.0
tqdm==4.66.2
rich==13.7.0" > requirements.txt && pip install -r requirements.txt
```

---

## 2. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto para configurar las claves API y otras opciones.

```bash
# ARCHIVO .env - Colocar en la raíz del proyecto
OPENAI_API_KEY="sk-tu_clave_openai_32caracteres"
ANTHROPIC_API_KEY="sk-ant-tu_clave_claude_96caracteres"
LOG_LEVEL="DEBUG"  # Opciones: DEBUG, INFO, WARNING, ERROR
AUTO_SAVE_INTERVAL="300"  # Segundos entre autoguardados
```

- **OPENAI_API_KEY:** Clave para usar modelos de OpenAI.  
- **ANTHROPIC_API_KEY:** Clave para modelos de Anthropic (Claude).  
- **LOG_LEVEL:** Nivel de detalle en los logs.  
- **AUTO_SAVE_INTERVAL:** Frecuencia de autoguardado en segundos.

---

## 3. Lanzamiento del Programa
El **MultiAIEditor** ofrece varios modos de ejecución según tus necesidades.

### 3.1 Modo Básico (Interfaz Simple)
Para una experiencia minimalista.

```bash
python main.py --simple-ui
```

### 3.2 Modo Avanzado (Interfaz Enriquecida)
Con más opciones y una interfaz mejorada.

```bash
python main.py --rich-ui --model gpt-4 --provider openai
```

### 3.3 Modo Desarrollo (Logs Detallados)
Ideal para depuración y desarrollo.

```bash
python main.py --dev-mode --log-level DEBUG
```

---

## 4. Comandos Universales
Interactúa con el agente DeepSeek mediante comandos específicos para gestionar proyectos, archivos y configuraciones.

### 4.1 Tabla de Comandos Principales

| Comando            | Sintaxis                              | Ejemplo                                  | Descripción                              |
|--------------------|---------------------------------------|------------------------------------------|------------------------------------------|
| `::switch_provider` | `::switch_provider <nombre>`          | `::switch_provider claude`               | Cambia el proveedor (openai/claude/deepseek) |
| `::model_config`    | `::model_config <param>=<valor>`      | `::model_config temp=0.7`                | Ajusta parámetros del modelo             |
| `::file_create`     | `::file_create <ruta> "<contenido>"`  | `::file_create app.py "print('Hola')"`   | Crea un archivo con contenido            |
| `::file_edit`       | `::file_edit <ruta> <old> <new>`      | `::file_edit config.yaml dev prod`       | Edita un archivo de forma segura         |
| `::project_init`    | `::project_init <nombre>`             | `::project_init mi-proyecto`             | Inicializa la estructura del proyecto    |
| `::undo_last`       | `::undo_last`                         |                                          | Deshace la última operación              |
| `::export_session`  | `::export_session <nombre>`           | `::export_session sesion1`               | Guarda el estado actual de la sesión     |

### 4.2 Comandos de Depuración
Verifica el sistema y genera reportes con estos comandos.

```bash
# Ver estado del sistema
::system_status

# Generar reporte técnico en HTML
::generate_report --format html

# Probar conexión con todos los proveedores
::test_connection --provider all
```

---

## 5. Configuración Avanzada
Personaliza el agente editando el archivo `settings.json`.

### 5.1 Ejemplo de `settings.json`

```json
{
  "auto_save": true,
  "backup_strategy": "incremental",
  "model_defaults": {
    "openai": {
      "temperature": 0.7,
      "max_tokens": 2000,
      "stream": true
    },
    "claude": {
      "max_tokens": 4000,
      "system_prompt": "professional_coder"
    }
  },
  "security": {
    "encrypt_files": true,
    "audit_log": "./logs/audit.log"
  }
}
```

- **auto_save:** Activa o desactiva el autoguardado.  
- **backup_strategy:** Define la estrategia de respaldo (ejemplo: "incremental").  
- **model_defaults:** Configuraciones por defecto para cada proveedor.  
- **security:** Opciones de seguridad como encriptación y logs de auditoría.

---

## 6. Flujos de Trabajo
Ejemplos prácticos para usar el **MultiAIEditor** en tareas comunes.

### 6.1 Inicializar y Editar un Proyecto

```bash
::project_init mi-proyecto
::file_create mi-proyecto/src/main.py "def main():\n    print('Hola Mundo')"
::file_edit mi-proyecto/src/main.py print('Hola Mundo') print('Bienvenido al Sistema')"
::export_session proyecto_inicial
```

### 6.2 Modo Mantenimiento
Ejecuta tareas de optimización y reparación.

```bash
python main.py --maintenance
```

**Opciones Disponibles:**  
1. Reconstruir índices de búsqueda.  
2. Verificar integridad de archivos.  
3. Optimizar base de datos local.  
4. Limpiar caché temporal.

---

## 7. Ejemplos de Uso Avanzado
Configura el agente para roles específicos, como un **Ingeniero de Software Senior**.

### 7.1 Rol: Ingeniero de Software Senior

#### Stack Tecnológico
```python
{
  "lenguajes": ["Python", "TypeScript", "Go"],
  "frameworks": ["FastAPI", "React", "TensorFlow"],
  "infraestructura": ["Docker", "Kubernetes", "AWS"]
}
```

#### Directrices de Desarrollo
1. Aplicar principios SOLID.  
2. Escribir tests unitarios.  
3. Usar documentación Swagger.  
4. Implementar logs estructurados.

#### Ejemplo de Código
```python
# app/api/v1/users.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str

@router.post("/users")
async def create_user(user: UserCreate):
    """Crea un nuevo usuario con validación"""
    # Lógica de negocio aquí
    return {"status": "user_created"}
```

#### Restricciones de Seguridad
- Validar todos los inputs.  
- Encriptar datos sensibles.  
- Limitar tasa de acceso.  
- Realizar auditorías diarias.

---

## 8. Flujo de Trabajo
Visualiza cómo interactúan el usuario, el agente y el sistema con este diagrama de secuencia.

```mermaid
sequenceDiagram
    Usuario->>Agente: "Necesito mejorar la seguridad de la API"
    Agente->>Sistema: Analiza estructura actual (project/)
    Sistema->>Agente: Detecta 2 endpoints sin autenticación
    Agente->>Usuario: "Recomiendo: 1. JWT en /users 2. OAuth en /admin. ¿Qué prefieres?"
    Usuario->>Agente: "Implementa JWT primero"
    Agente->>Sistema: Genera código base + tests
    Sistema->>Agente: Muestra diff con cambios propuestos
    Agente->>Usuario: "Confirmas estos cambios? (Ver detalles técnicos)"
    Usuario->>Agente: "Sí, pero explica el flujo de tokens"
    Agente->>Usuario: Explicación técnica simplificada + diagrama
```

---

## 9. Historial de Versiones

### Versión 2.1.0 - 2025-03-18
- **Nuevas Características:**  
  - Soporte para modelos Claude 3.  
  - Sistema de plugins integrado.  
  - Optimización de memoria.  
  - Corrección de vulnerabilidades (CVE-2024-1234).  
- **Mejoras:**  
  - Carga de prompts desde archivos (`prompt.md` y `requerimientos.md`).  
  - Procesamiento mejorado de requerimientos iniciales.  
  - Nuevo sistema de construcción de contexto.  
  - Mejor manejo de respuestas y comandos.  
  - Sistema de impresión de historial actualizado.

## 10. Script 

- | `::* code-agen.py`  |
- | `::* main.py`       |
- | `::* main2.py`      |
---
