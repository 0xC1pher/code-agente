import os
import re
import sys
import json
import inspect
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import argparse
from termcolor import colored
from pathlib import Path
import logging

# Configurar logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Attempt to import necessary libraries, handling potential ImportErrors
try:
    import anthropic
except ImportError as e:
    print(f"Error: The 'anthropic' library is not installed. Please install it using: pip install anthropic")
    anthropic = None
try:
    import openai
except ImportError as e:
    print(f"Error: The 'openai' library is not installed. Please install it using: pip install openai")
    openai = None
try:
    from termcolor import colored
except ImportError as e:
    print(f"Error: The 'termcolor' library is not installed. Please install it using: pip install termcolor")
    colored = lambda x, y: x
try:
    from gradio_client import Client
except ImportError as e:
    print(f"Error: The 'gradio_client' library is not installed. Please install it using: pip install gradio_client")
    Client = None

# ====================
# Configuración inicial
# ====================
load_dotenv()

# ================ NUEVAS CLASES Y MÉTODOS ================
class ProjectAnalyzer:
    """Analiza proyectos incompletos y sugiere mejoras"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.architecture_rules = {
            'clean_architecture': ['core', 'infra', 'ui'],
            'mvc': ['models', 'views', 'controllers']
        }

    def calculate_completion(self) -> dict:
        """Calcula porcentaje de completado y componentes faltantes"""
        total_files = 0
        analyzed_files = 0
        missing_components = set()

        if not self.project_path.exists():
            print(colored(f"Error: El directorio '{self.project_path}' no existe.", "red"))
            return {"completion": 0, "missing_components": []}

        for root, dirs, files in os.walk(self.project_path):
            total_files += len(files)
            for rule_name, expected_dirs in self.architecture_rules.items():
                for expected_dir in expected_dirs:
                    if expected_dir not in dirs:
                        missing_components.add(expected_dir)

        completion = (total_files - len(missing_components)) / total_files * 100 if total_files > 0 else 0
        return {"completion": round(completion, 2), "missing_components": list(missing_components)}

    def detect_architecture(self) -> str:
        """Identifica patrones arquitectónicos en el proyecto"""
        detected_architectures = []

        if not self.project_path.exists():
            print(colored(f"Error: El directorio '{self.project_path}' no existe.", "red"))
            return "Desconocida"

        for rule_name, expected_dirs in self.architecture_rules.items():
            if all((self.project_path / d).exists() for d in expected_dirs):
                detected_architectures.append(rule_name)

        return detected_architectures[0] if detected_architectures else "Desconocida"

class NaturalLanguageInterpreter:
    """
    Interpreta comandos en lenguaje natural y los traduce a acciones técnicas.
    """

    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        logging.debug(f"NaturalLanguageInterpreter initialized with project_path: {self.project_path}")

    def parse_command(self, text: str) -> Dict[str, Optional[str]]:
        """Convierte un comando en lenguaje natural a una estructura de acción"""
        text_lower = text.lower()

        # Regular expressions for more flexible parsing
        list_files_regex = re.compile(
            r"(lista|ver|mostrar)\s+(los|el)?\s*(archivos|contenido)\s+(de|del|en)?\s+(directorio|carpeta)\s+([\w./-]+)",
            re.IGNORECASE
        )
        view_file_regex = re.compile(
            r"(ver|mostrar)\s+(el\s+)?archivo\s+([\w./-]+)",
            re.IGNORECASE
        )
        analyze_regex = re.compile(r"(analiza|revisa)\s+(el\s+)?proyecto", re.IGNORECASE)

        if analyze_regex.search(text_lower):
            return {"action": "analyze_project"}
        elif "calcula" in text_lower and "completado" in text_lower:
            return {"action": "calculate_completion"}
        elif "detecta" in text_lower and "arquitectura" in text_lower:
            return {"action": "detect_architecture"}
        elif match := list_files_regex.search(text):
            path = match.group(6).strip()
            return {"action": "list_files", "path": path}
        elif match := view_file_regex.search(text):
            path = match.group(3).strip()
            return {"action": "view", "path": path}
        else:
            return {"action": "unknown", "message": "No se pudo interpretar el comando."}

    def execute_command(self, command: Dict[str, Optional[str]]) -> None:
        """Ejecuta la acción basada en la estructura del comando interpretado."""
        action = command.get("action")
        if action == "analyze_project":
            logging.debug("Ejecutando análisis del proyecto...")
        elif action == "calculate_completion":
            logging.debug("Calculando el completado del proyecto...")
        elif action == "detect_architecture":
            logging.debug("Detectando la arquitectura del proyecto...")
        elif action == "list_files":
            path = command.get("path", self.project_path)
            logging.debug(f"Listando archivos en: {path}")
        elif action == "view":
            path = command.get("path")
            logging.debug(f"Mostrando contenido del archivo: {path}")
        else:
            logging.info("Comando desconocido o no soportado.")

class DatabaseManager:
    """Gestiona operaciones de bases de datos"""

    def generate_migration(self, schema_changes: str):
        """Crea migraciones desde descripciones naturales"""
        print("DatabaseManager.generate_migration() - Implementación pendiente")
        return "Migration generation not implemented"

    def execute(self, intent: Dict) -> str:
        """Ejecuta una operación de base de datos basada en la intención."""
        print("DatabaseManager.execute() - Implementación pendiente")
        return "DB execution not implemented"

class ArchitectureManager:
    """Implementa patrones arquitectónicos"""

    def apply_pattern(self, pattern_name: str):
        """Crea estructura de directorios y archivos base"""
        print("ArchitectureManager.apply_pattern() - Implementación pendiente")
        return f"Applied {pattern_name} - Not implemented"

class BaseAIProvider:
    """Clase base para proveedores de IA"""

    def __init__(self, model: str, api_key: str = None):
        self.model = model
        self.api_key = api_key
        self.conversation_history = []
        self.tools = []
        self.file_backups = {}
        self.system_prompt = self._base_system_prompt()
        # Nuevas dependencias
        self.analyzer = ProjectAnalyzer("project")
        self.interpreter = NaturalLanguageInterpreter()
        self.db_manager = DatabaseManager()
        self.arch_manager = ArchitectureManager()

    def _base_system_prompt(self) -> str:
        """Prompt base para todos los proveedores"""
        try:
            with open("prompt.md", "r") as f:
                return f.read()
        except FileNotFoundError:
            return """Eres un asistente de codificación experto y proactivo. Tu objetivo es ayudar al usuario a modificar y gestionar archivos de código de manera eficiente. Tienes acceso a las siguientes herramientas:

1. view - Ver el contenido de un archivo. Úsala para entender el archivo antes de hacer cambios.
    Parámetros: 'path' (obligatorio)
    Ejemplo: {"command": "view", "path": "mi_archivo.txt"}

2. str_replace - Reemplazar texto exacto en un archivo. Asegúrate de que el 'old_str' coincide exactamente con el texto que se va a reemplazar, incluyendo espacios y sangría.
    Parámetros: 'path' (obligatorio), 'old_str' (obligatorio), 'new_str' (obligatorio)
    Ejemplo: {"command": "str_replace", "path": "mi_archivo.txt", "old_str": "texto antiguo", "new_str": "texto nuevo"}

3. create - Crear un nuevo archivo.
    Parámetros: 'path' (obligatorio)
    Ejemplo: {"command": "create", "path": "nuevo_archivo.txt"}

4. insert - Insertar texto en una línea específica de un archivo.
    Parámetros: 'path' (obligatorio), 'insert_line' (obligatorio), 'new_str' (obligatorio). Ejemplo: {"command": "insert", "path": "mi_archivo.txt", "insert_line": 5, "new_str": "nuevo texto"}

5. undo_edit - Deshacer la última edición realizada en un archivo.
    Parámetros: 'path' (obligatorio). Ejemplo: {"command": "undo_edit", "path": "mi_archivo.txt"}

6. list_files - Listar los archivos en un directorio. Útil para explorar la estructura del proyecto.
   Parámetros: 'path' (obligatorio)
    Ejemplo: {"command": "list_files", "path": "src"}

7. delete_file - Eliminar un archivo existente
    Parámetros: 'path' (obligatorio)
    Ejemplo: {"command": "delete_file", "path": "mi_archivo.txt"}

8. create_directory - Crear un nuevo directorio
    Parámetros: 'path' (obligatorio)
    Ejemplo: {"command": "create_directory", "path": "src/nuevo_dir"}

9. procesar_comando - Procesa comandos en lenguaje natural para operaciones de archivos, bases de datos y arquitectura

Workflow Obligatorio:

1.  **Antes de cualquier modificación:** Siempre debes utilizar la herramienta 'view' para comprender el contenido actual del archivo y asegurarte de que conoces la estructura existente.

2.  **Ayuda proactiva:** Si el usuario parece indeciso u no está seguro de cómo proceder, ofrécele sugerencias específicas basadas en el contexto. Por ejemplo, si listó los archivos en un directorio, pregunta qué archivo le gustaría ver.

3.  **Precisión en 'str_replace':**  Enfatiza la importancia de que el 'old_str' coincida exactamente con el texto que se va a reemplazar, incluyendo espacios y sangría.

4.  **Confirmación antes de editar:**  Siempre debes confirmar con el usuario los cambios que vas a realizar antes de ejecutar cualquier comando de edición (str_replace, create, insert) en modo interactivo.

5.  **Guiar al usuario:** Siempre debes preguntar qué archivo quiere ver o modificar y guiarlo paso a paso en el workflow. Pregúntale qué tarea intenta realizar y ofrece orientación específica.

6. **Preguntar al usuario**: después de cada acción, y antes de realizar otras, pregunta al usuario cual será la siguiente acción y qué archivo se va a usar

7. **Modo Autónomo**: En modo autónomo, puedes crear, modificar y eliminar archivos y directorios automáticamente basándote en el análisis del proyecto y los requisitos dados.
"""

    def add_to_history(self, role: str, content: Any):
        """Añade mensaje al historial"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def _handle_tools(self, tool_use: Any) -> str:
        """Manejo unificado de herramientas"""
        if tool_use['name'] == 'text_editor':
            tool_calls = tool_use['function']['arguments']
            tool_calls = json.loads(tool_calls)
            command = tool_calls['command']
            path = tool_calls['path']

            if command == "view":
                return self._view_file(path)
            elif command == "str_replace":
                old_str = tool_calls['old_str']
                new_str = tool_calls['new_str']
                return self._replace_in_file(path, old_str, new_str)
            elif command == "create":
                return self._create_file(path)
            elif command == "insert":
                insert_line = tool_calls['insert_line']
                new_str = tool_calls['new_str']
                return self._insert_in_file(path, insert_line, new_str)
            elif command == "undo_edit":
                return self._undo_last_edit(path)
            elif command == "list_files":
                return self._list_files_in_directory(path)
            elif command == "delete_file":
                return self._delete_file(path)
            elif command == "create_directory":
                return self._create_directory(path)
        return "Comando no reconocido"

    def process_natural_command(self, user_input: str) -> Dict:
        """Procesa comandos en lenguaje natural"""
        intent = self.interpreter.parse_command(user_input)
        if intent['action'] == 'analyze_project':
            result = self.analyzer.calculate_completion()
            return {"content": [{"text": f"Análisis del proyecto: {result}"}]}
        elif intent['action'] == 'detect_architecture':
            arch = self.analyzer.detect_architecture()
            return {"content": [{"text": f"Arquitectura detectada: {arch}"}]}
        elif intent['action'] == 'list_files':
            path = intent.get("path", ".")
            result = self._list_files_in_directory(path)
            return {"content": [{"text": result}]}
        elif intent['action'] == 'view':
            path = intent.get("path", ".")
            result = self._view_file(path)
            return {"content": [{"text": result}]}
        elif intent['action'] == 'db_operation':
            return {"content": [{"text": self.db_manager.execute(intent)}]}
        elif intent['action'] == 'arch_operation':
            return {"content": [{"text": self.arch_manager.apply_pattern(intent['pattern'])}]}
        else:
            return {"content": [{"text": intent.get("message", "Comando no reconocido.")}]}

    def _view_file(self, path: str) -> str:
        """Ver contenido del archivo"""
        try:
            with open(path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: Archivo no encontrado: {path}"
        except Exception as e:
            return f"Error al leer el archivo: {str(e)}"

    def _create_file(self, path: str) -> str:
        """Crear nuevo archivo"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'w').close()
            return f"Archivo '{path}' creado exitosamente."
        except Exception as e:
            return f"Error al crear el archivo: {str(e)}"

    def _replace_in_file(self, path: str, old_str: str, new_str: str) -> str:
        """Reemplazar texto en el archivo"""
        if path not in self.file_backups:
            self.file_backups[path] = self._view_file(path)

        try:
            with open(path, 'r') as file:
                content = file.read()
            updated_content = content.replace(old_str, new_str)
            with open(path, 'w') as file:
                file.write(updated_content)
            return f"Reemplazado '{old_str}' con '{new_str}' en '{path}'."
        except Exception as e:
            return f"Error al reemplazar en el archivo: {str(e)}"

    def _insert_in_file(self, path: str, insert_line: int, new_str: str) -> str:
        """Insertar texto en una línea específica"""
        if path not in self.file_backups:
            self.file_backups[path] = self._view_file(path)

        try:
            with open(path, 'r') as file:
                lines = file.readlines()
            
            if 0 <= insert_line <= len(lines):
                lines.insert(insert_line, new_str + '\n')
                with open(path, 'w') as file:
                    file.writelines(lines)
                return f"Insertado en la línea {insert_line} en '{path}'."
            return "Número de línea inválido."
        except Exception as e:
            return f"Error al insertar en el archivo: {str(e)}"

    def _undo_last_edit(self, path: str) -> str:
        """Deshacer la última edición"""
        if path in self.file_backups:
            try:
                with open(path, 'w') as file:
                    file.write(self.file_backups[path])
                del self.file_backups[path]
                return f"Edición deshecha en '{path}'."
            except Exception as e:
                return f"Error al deshacer la edición: {str(e)}"

    def _list_files_in_directory(self, path: str) -> str:
        """Listar archivos en un directorio."""
        try:
            if not os.path.isdir(path):
                return f"Error: Directorio no encontrado: {path}"
            files = os.listdir(path)
            return f"Archivos en el directorio '{path}':\n" + "\n".join(files)
        except Exception as e:
            return f"Error listando archivos: {str(e)}"

    def _delete_file(self, path: str) -> str:
        """Eliminar un archivo"""
        try:
            if os.path.exists(path):
                if path not in self.file_backups:
                    self.file_backups[path] = self._view_file(path)
                os.remove(path)
                return f"Archivo '{path}' eliminado exitosamente."
            return f"Error: Archivo no encontrado: {path}"
        except Exception as e:
            return f"Error al eliminar el archivo: {str(e)}"

    def _create_directory(self, path: str) -> str:
        """Crear un nuevo directorio"""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Directorio '{path}' creado exitosamente."
        except Exception as e:
            return f"Error al crear el directorio: {str(e)}"

    def _backup_file(self, path: str):
        """Crear respaldo de un archivo"""
        if os.path.exists(path) and path not in self.file_backups:
            with open(path, 'r') as file:
                self.file_backups[path] = file.read()

    def _process_code_blocks(self, response: str):
        """Detecta bloques de código y los escribe en archivos"""
        code_blocks = self._extract_code_blocks(response)
        for block in code_blocks:
            try:
                if block['filename'] and block['code']:
                    self._write_code_file(block['filename'], block['code'])
            except Exception as e:
                print(colored(f"❌ Error escribiendo archivo: {str(e)}", "red"))

    def _extract_code_blocks(self, text: str) -> List[Dict]:
        """Extrae bloques de código marcados con ```file:ruta/archivo"""
        code_blocks = []
        current_block = None
        lines = text.split('\n')
        
        for line in lines:
            if line.strip().startswith('```file:'):
                if current_block:
                    code_blocks.append(current_block)
                filename = line.split(':')[1].strip().replace('```', '')
                current_block = {'filename': filename, 'code': []}
            elif line.strip().startswith('```'):
                if current_block:
                    current_block['code'] = '\n'.join(current_block['code'])
                    code_blocks.append(current_block)
                    current_block = None
            elif current_block:
                current_block['code'].append(line)
        
        if current_block:
            current_block['code'] = '\n'.join(current_block['code'])
            code_blocks.append(current_block)
            
        return code_blocks

    def _write_code_file(self, filepath: str, content: str) -> None:
        """Escribe el contenido en el archivo especificado"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Verificar si el archivo existe
            if os.path.exists(filepath):
                self._backup_file(filepath)
                mode = 'w'  # Sobreescribir en modo autónomo
            else:
                mode = 'w'  # Crear nuevo
            
            with open(filepath, mode, encoding='utf-8') as f:
                f.write(content)
            
            print(colored(f"✓ Archivo actualizado: {filepath}", "green"))
            
        except Exception as e:
            print(colored(f"❌ Error escribiendo {filepath}: {str(e)}", "red"))

    def _handle_file_ops(self, intent: dict) -> Dict:
        return {"content": [{"text": "Implement file operations"}]}

class ClaudeProvider(BaseAIProvider):
    """Implementación para Claude 3"""

    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        if anthropic is None:
            self.client = None
            print(colored("Anthropic client will not be initialized due to missing library.", "yellow"))
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        self.system_prompt = """Eres un desarrollador de software experto con 10 años de experiencia. 
        Tu principal objetivo es aplicar los diseños y arquitectura definidos por el Arquitecto de Software (otro modelo de IA). 
        Debes ser preciso al modificar archivos, verificar que el código sea correcto y comunicarte con el usuario para confirmar las acciones a realizar. 
        Tienes acceso a las siguientes herramientas:

1. view - Ver el contenido de un archivo.
2. str_replace - Reemplazar texto exacto en un archivo.
3. create - Crear un nuevo archivo.
4. insert - Insertar texto en una línea específica de un archivo.
5. undo_edit - Deshacer la última edición realizada en un archivo.
6. list_files - Listar los archivos en un directorio.
7. delete_file - Eliminar un archivo existente
8. create_directory - Crear un nuevo directorio
"""

    def generate_response(self, user_input: str) -> Dict:
        """Generar respuesta usando Claude"""
        if self.client is None:
            return {"content": [{"text": "Anthropic library not installed."}]}
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_input}],
            tools=[{"type": "function", "function": {"name": "text_editor",
                                                    "description": "Herramientas de edición de texto",
                                                    "parameters": {
                                                        "type": "object",
                                                        "properties": {
                                                            "command": {"type": "string", "enum": ["view", "str_replace", "create", "insert", "undo_edit", "list_files", "delete_file", "create_directory"]},
                                                            "path": {"type": "string", "description": "The path or directory to use"},
                                                            "old_str": {"type": "string", "description": "The string to find and replace"},
                                                            "new_str": {"type": "string", "description": "The string to replace with"},
                                                            "insert_line": {"type": "integer", "description": "The line number to insert at"}
                                                        },
                                                        "required": ["command", "path"]
                                                    }
                                                    }}]
        )
        response_dict = {"content": [{"text": message.content[0].text}]}
        self._process_code_blocks(message.content[0].text)
        return response_dict

class OpenAiProvider(BaseAIProvider):
    """Implementación para OpenAI"""

    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        if openai is None:
            self.client = None
            print(colored("OpenAI client will not be initialized due to missing library.", "yellow"))
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
        self.system_prompt = """Eres un desarrollador de software experto con 10 años de experiencia.
        Tu principal objetivo es implementar los diseños y arquitectura definidos por el Arquitecto de Software (otro modelo de IA).
        Debes ser preciso al modificar archivos, verificar que el código sea correcto y comunicarte con el usuario para confirmar las acciones a realizar.
        Tienes acceso a las siguientes herramientas:

1. view - Ver el contenido de un archivo.
2. str_replace - Reemplazar texto exacto en un archivo.
3. create - Crear un nuevo archivo.
4. insert - Insertar texto en una línea específica de un archivo.
5. undo_edit - Deshacer la última edición realizada en un archivo.
6. list_files - Listar los archivos en un directorio.
7. delete_file - Eliminar un archivo existente
8. create_directory - Crear un nuevo directorio
"""

    def generate_response(self, user_input: str) -> Dict:
        """Generar respuesta usando OpenAI"""
        if self.client is None:
            return {"content": [{"text": "OpenAI library not installed."}]}
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._format_messages(user_input),
            tools=self._get_tools_schema()
        )
        response_text = response.choices[0].message.content
        self._process_code_blocks(response_text)
        return {"content": [{"text": response_text}]}

    def _format_messages(self, user_input: str) -> List[Dict]:
        """Formatea los mensajes para la API de OpenAI."""
        messages = [{"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}]
        return messages

    def _get_tools_schema(self) -> List[Dict]:
        """Estructura de herramientas para OpenAI"""
        return [{
            "type": "function",
            "function": {
                "name": "text_editor",
                "description": "Operaciones de edición de archivos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "enum": ["view", "str_replace", "create", "insert", "undo_edit", "list_files", "delete_file", "create_directory"]},
                        "path": {"type": "string", "description": "The path or directory to use"},
                        "old_str": {"type": "string", "description": "The string to find and replace"},
                        "new_str": {"type": "string", "description": "The string to replace with"},
                        "insert_line": {"type": "integer", "description": "The line number to insert at"}
                    },
                    "required": ["command", "path"]
                }
            }
        }]

class DeepSeekProvider(BaseAIProvider):
    """Implementación para DeepSeek"""

    def __init__(self, model: str, api_key: str = None):
        super().__init__(model, api_key)
        if Client is None:
            self.client = None
            print(colored("DeepSeek client will not be initialized due to missing gradio_client library.", "yellow"))
        else:
            try:
                self.client = Client("reasoning-course/deepseek-ai-DeepSeek-R1-Distill-Qwen-32B")
            except Exception as e:
                print(colored(f"Error initializing DeepSeek client: {e}", "red"))
                self.client = None

        self.system_prompt += "\nVersión: DeepSeek - Editor Técnico"

    def generate_response(self, user_input: str) -> Dict:
        """Generar respuesta usando DeepSeek"""
        if self.client is None:
            return {"content": [{"text": "DeepSeek client not initialized due to missing gradio_client library or initialization error."}]}
        
        full_message = f"{self.system_prompt}\n{user_input}"
        if self.client is not None:
           response = self.client.predict(
                message=full_message,
                api_name="/chat"
           )
           self._process_code_blocks(response)
           return {"content": [{"text": response}]}
        return {"content":[{"text":"DeepSeek model missing"}]}

class GeminiProvider(BaseAIProvider):
    """Implementación para Gemini"""

    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        self.system_prompt = """Eres un arquitecto de software experto con 10 años de experiencia en la creación de aplicaciones robustas y escalables.
        Tu objetivo principal es analizar la estructura general del proyecto de software, identificar patrones de diseño existentes, detectar posibles problemas y ofrecer sugerencias para mejorar la arquitectura.
        Después del análisis, deberás entregarle el proyecto y sus componentes al desarrollador de software para que continue trabajando con el.

        Como arquitecto de software, puedo ayudarte a planificar, diseñar, analizar y evaluar la arquitectura de sistemas de software. Aquí hay algunas áreas específicas en las que puedo ofrecer orientación y apoyo:

1. Análisis de requisitos y diseño de la arquitectura:
2. Selección de patrones de diseño y arquitecturas:
3. Evaluación y mejora de la calidad de la arquitectura:
4. Definición de la estrategia de integración:
5. Documentación de la arquitectura:
"""

    def generate_response(self, user_input: str) -> Dict:
        """Generar respuesta usando Gemini"""
        response = self.process_natural_command(user_input)
        self._process_code_blocks(response['content'][0]['text'])
        return response

class MultiAIEditor:
    """Sistema unificado de edición con múltiples proveedores"""

    def __init__(self, provider: str, model: str):
        self.providers = {}
        self.model = model
        self.autonomous_mode = False
        self.project_path = "project"

        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if anthropic is not None and anthropic_api_key:
            self.providers["claude"] = ClaudeProvider(model=model, api_key=anthropic_api_key)
        if openai is not None and openai_api_key:
            self.providers["openai"] = OpenAiProvider(model=model, api_key=openai_api_key)
        if Client is not None:
            self.providers["deepseek"] = DeepSeekProvider(model=model, api_key="")
        if gemini_api_key:
            self.providers["gemini"] = GeminiProvider(model=model, api_key=gemini_api_key)

        if not self.providers:
            print(colored("No AI providers are available due to missing libraries or API keys.", "red"))
            self.active_provider = None
            self.architect_provider = None
            self.developer_provider = None
            self.current_provider = None
        else:
            self.current_provider = provider
            self.active_provider = self.providers[self.current_provider]
            self.architect_provider = self.providers.get("gemini")
            self.developer_provider = self.providers.get("openai") or self.providers.get("claude") or self.providers.get("deepseek")

            if not self.developer_provider and not self.architect_provider:
                print(colored("No Developer or Architect found", "red"))

        self.history = []
        if not os.path.exists(self.project_path):
           os.mkdir(self.project_path)

    def switch_provider(self, provider: str):
        """Cambiar proveedor activo"""
        if provider in self.providers:
            self.current_provider = provider
            self.active_provider = self.providers[provider]
            print(f"Proveedor cambiado a: {provider}")
        else:
            print("Proveedor no válido")

    def switch_model(self, model: str):
        """Cambiar el modelo para el proveedor actual"""
        if self.active_provider is not None:
            self.active_provider.model = model
            print(f"Model switched to {model} for {self.current_provider}.")
        else:
            print(colored("No AI provider is active.", "red"))

    def switch_mode(self, mode: str):
        """Switches between interactive and autonomous modes"""
        if mode.lower() == "autonomous":
            self.autonomous_mode = True
            print("Switching to autonomous mode.")
        elif mode.lower() == "interactive":
            self.autonomous_mode = False
            print("Switching to interactive mode.")
        else:
            print("Invalid mode")

    def interactive_session(self):
        """Sesión interactiva mejorada"""
        if not self.providers:
            print(colored("No AI providers are available. Please install the necessary libraries and API keys.", "red"))
            return

        print(colored("=" * 20 + " Editor Multi-IA " + "=" * 20, "cyan"))
        print("Proveedores disponibles: " + " | ".join(self.providers.keys()))

        while True:
            user_input = input(colored("\nTu: ", "green"))
            if user_input.lower() == "exit":
                break
            if user_input.startswith("switch "):
                new_provider = user_input.split(" ")[1]
                self.switch_provider(new_provider)
                continue
            if user_input.startswith("switch_model "):
                new_model = user_input.split(" ")[1]
                self.switch_model(new_model)
                continue
            if user_input.startswith("switch_mode "):
                new_mode = user_input.split(" ")[1]
                self.switch_mode(new_mode)
                continue
            self._process_command(user_input)

    def _process_command(self, command: str):
        """Método modificado para soportar ambos modos"""
        if self.autonomous_mode:
            self._process_autonomous(command)
        else:
            try:
                if not self.active_provider:
                    print(colored("No AI provider is active.", "red"))
                    return

                response = self.active_provider.generate_response(command)

                if hasattr(response, 'tool_uses') and self.current_provider != "deepseek":
                    for tool in response.tool_uses:
                        result = self.active_provider._handle_tools(tool)
                        self._handle_tool_result(result)

                self._display_response(response, command)
                self._update_history(command, response)

            except Exception as e:
                print(colored(f"Error: {str(e)}", "red"))

    def _process_autonomous(self, command: str):
        """Procesamiento autónomo mejorado"""
        print("Starting Autonomous Processing...")

        if not self.architect_provider:
            print(colored("Warning: No Architect (Gemini) provider available. Using developer for all tasks.", "yellow"))
            architect_response = self.active_provider.generate_response(command)
            self._display_response(architect_response, command)
            return

        print(colored("Architect (Gemini) is analyzing the project...", "cyan"))
        analysis_result = self.architect_provider.generate_response("Analiza el proyecto")
        print(colored("Analysis from Architect:", "cyan"))
        self._display_response(analysis_result, "Analiza el proyecto")

        print(colored("Arquitecto está generando plan de acción...", "cyan"))
        action_plan_prompt = f"Based on your analysis, provide a detailed plan including specific file creations, modifications, and deletions:\n{analysis_result.get('content',[])[0]['text']}"
        action_plan_response = self.architect_provider.generate_response(action_plan_prompt)
        print(colored("Architect action Plan", "cyan"))
        self._display_response(action_plan_response, action_plan_prompt)

        if not self.developer_provider:
            print(colored("No developer provider was found", "red"))
            return

        print(colored("The developer will execute the action plan", "yellow"))
        for content in action_plan_response['content']:
            if isinstance(content, dict) and 'text' in content:
                dev_response = self.developer_provider.generate_response(content['text'])
                self._display_response(dev_response, content['text'])

    def _display_response(self, response: Dict, command: str):
        """Mostrar respuesta formateada"""
        print(colored("\n🤖 Asistente:", "blue"))

        first_prompt = "1. ¿Quieres ver el contenido del archivo? (comando: view, parametro: path)\n2. ¿Hay otro directorio o archivo que necesites explorar?\n3. Indicar los cambios que te gustaría realizar en el archivo."
        list_files_prompt = "Ahora, ¿qué archivo de la lista te gustaría examinar (comando view) o qué acción deseas realizar?"

        for content in response['content']:
            if isinstance(content, dict) and 'text' in content:
                response_text = content['text']
                if "Files in directory" in response_text:
                    print(response_text + "\n" + list_files_prompt)
                else:
                    print(response_text + "\n" + (first_prompt if not self.autonomous_mode else ""))
            elif hasattr(content, 'text'):
                print(content.text + "\n" + (first_prompt if not self.autonomous_mode else ""))
            elif isinstance(content, dict):
                print(content.get('text', '') + "\n" + (first_prompt if not self.autonomous_mode else ""))

    def _update_history(self, command: str, response: Dict):
        """Actualizar historial de conversación"""
        self.history.append({
            "input": command,
            "output": response,
            "provider": self.current_provider
        })

    def _handle_tool_result(self, result: str):
        """Manejar resultados de herramientas"""
        print(colored("\n⚙️ Resultado de herramienta:", "yellow"))
        print(result)

# ====================
# Funciones principales
# ====================
def main():
    """Función principal ejecutando el editor mejorado"""
    parser = argparse.ArgumentParser(description="MultiAIEditor - A text editor that uses multiple AI providers.")
    parser.add_argument("--provider", type=str, default="openai", help="The AI provider to use (claude, openai, deepseek, gemini).")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo", help="The model to use for the provider.")

    args = parser.parse_args()

    try:
        editor = MultiAIEditor(args.provider, args.model)
        editor.interactive_session()
    except KeyboardInterrupt:
        print(colored("\nOperación cancelada por el usuario", "yellow"))
    except Exception as e:
        print(colored(f"Error crítico: {str(e)}", "red"))

if __name__ == "__main__":
    with open("prompt.md", "w") as f:
        f.write("""Eres un arquitecto de software, experto en backend, con 10 anos de experiencia en el desarrollo de aplicaciones web, pwa, spa.

Tu objetivo principal es guiar al usuario a través del proceso de edición de código, ayudándolo a planificar los cambios, usar las herramientas disponibles y confirmar cada paso. Debes ofrecer ayuda proactiva, anticipando las necesidades del usuario y guiándolo en cada etapa. Recuerda que el usuario puede no estar familiarizado con las herramientas o el workflow.
Tienes acceso a las siguientes herramientas de edición de texto:

1. view - Ver contenido de archivo.  Úsala para entender el archivo antes de hacer cambios. Es obligatorio usar este comando antes de cualquier otro comando de edicion.
    Parámetros: 'path' (obligatorio). Ejemplo: {"command": "view", "path": "mi_archivo.txt"}

2. str_replace - Reemplazar texto exacto en un archivo.  Asegúrate de que el 'old_str' coincide exactamente con el texto existente, incluyendo espacios y sangría.
    Parámetros: 'path' (obligatorio), 'old_str' (obligatorio), 'new_str' (obligatorio). Ejemplo: {"command": "str_replace", "path": "mi_archivo.txt", "old_str": "texto antiguo", "new_str": "texto nuevo"}

3. create - Crear un nuevo archivo.
    Parámetros: 'path' (obligatorio). Ejemplo: {"command": "create", "path": "nuevo_archivo.txt"}

4. insert - Insertar texto en una línea específica de un archivo.
    Parámetros: 'path' (obligatorio), 'insert_line' (obligatorio), 'new_str' (obligatorio). Ejemplo: {"command": "insert", "path": "mi_archivo.txt", "insert_line": 5, "new_str": "nuevo texto"}

5. undo_edit - Deshacer la última edición realizada en un archivo.
    Parámetros: 'path' (obligatorio). Ejemplo: {"command": "undo_edit", "path": "mi_archivo.txt"}

6. list_files - Listar los archivos en un directorio. Útil para explorar la estructura del proyecto.
    Parámetros: 'path' (obligatorio). Ejemplo: {"command": "list_files", "path": "src"}

7. delete_file - Eliminar un archivo existente
    Parámetros: 'path' (obligatorio)
    Ejemplo: {"command": "delete_file", "path": "mi_archivo.txt"}

8. create_directory - Crear un nuevo directorio
    Parámetros: 'path' (obligatorio)
    Ejemplo: {"command": "create_directory", "path": "src/nuevo_dir"}

Workflow Obligatorio:

1.  **Antes de cualquier modificación:** Siempre debes utilizar la herramienta 'view' para comprender el contenido actual del archivo y asegurarte de que conoces la estructura existente.

2.  **Ayuda proactiva:** Si el usuario parece indeciso u no está seguro de cómo proceder, ofrécele sugerencias específicas basadas en el contexto. Por ejemplo, si listó los archivos en un directorio, pregunta qué archivo le gustaría ver.

3.  **Precisión en 'str_replace':**  Enfatiza la importancia de que el 'old_str' coincida exactamente con el texto que se va a reemplazar, incluyendo espacios y sangría.

4.  **Confirmación antes de editar:**  Siempre debes confirmar con el usuario los cambios que vas a realizar antes de ejecutar cualquier comando de edición (str_replace, create, insert) en modo interactivo.

5.  **Guiar al usuario:** Siempre debes preguntar qué archivo quiere ver o modificar y guiarlo paso a paso en el workflow. Pregúntale qué tarea intenta realizar y ofrece orientación específica.

6. **Preguntar al usuario**: después de cada acción, y antes de realizar otras, pregunta al usuario cual será la siguiente acción y qué archivo se va a usar

7. **Modo Autónomo**: En modo autónomo, puedes crear, modificar y eliminar archivos y directorios automáticamente basándote en el análisis del proyecto y los requisitos dados. Usa bloques de código con ```file:ruta/archivo para especificar archivos a crear o modificar.
""")
    main()
