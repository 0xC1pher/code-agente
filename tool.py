import os
import re
from termcolor import colored
from dotenv import load_dotenv
from gradio_client import Client

class DeepSeekAgent:
    def __init__(self, model_url="reasoning-course/deepseek-ai-DeepSeek-R1-Distill-Qwen-32B", base_dir="."):
        """Inicializa el agente DeepSeek con el cliente API y el directorio base."""
        self.client = Client(model_url)
        self.max_tokens = 4000
        self.base_dir = base_dir
        self.project_dir = os.path.join(base_dir, "project")
        self.requirements = self._read_requirements()
        self.system_prompt = """Eres un arquitecto y desarrollador de software experto con 10 años de experiencia en crear aplicaciones robustas y escalables. Tu objetivo es crear, actualizar y gestionar archivos y directorios de forma autónoma basándote en los requerimientos del usuario y el estado del proyecto. Tienes acceso a las siguientes herramientas:

1. view - Ver el contenido de un archivo.
   Parámetros: 'path' (requerido)
   Ejemplo: {"command": "view", "path": "mi_archivo.txt"}

2. str_replace - Reemplazar texto exacto en un archivo.
   Parámetros: 'path' (requerido), 'old_str' (requerido), 'new_str' (requerido)
   Ejemplo: {"command": "str_replace", "path": "mi_archivo.txt", "old_str": "texto viejo", "new_str": "texto nuevo"}

3. create - Crear un nuevo archivo.
   Parámetros: 'path' (requerido), 'file_text' (requerido)
   Ejemplo: {"command": "create", "path": "nuevo_archivo.txt", "file_text": "contenido"}

4. insert - Insertar texto en una línea específica de un archivo.
   Parámetros: 'path' (requerido), 'insert_line' (requerido), 'new_str' (requerido)
   Ejemplo: {"command": "insert", "path": "mi_archivo.txt", "insert_line": 5, "new_str": "texto nuevo"}

5. undo_edit - Deshacer la última edición en un archivo.
   Parámetros: 'path' (requerido)
   Ejemplo: {"command": "undo_edit", "path": "mi_archivo.txt"}

6. list_files - Listar archivos en un directorio.
   Parámetros: 'path' (requerido)
   Ejemplo: {"command": "list_files", "path": "src"}

7. delete_file - Eliminar un archivo existente.
   Parámetros: 'path' (requerido)
   Ejemplo: {"command": "delete_file", "path": "mi_archivo.txt"}

8. create_directory - Crear un nuevo directorio.
   Parámetros: 'path' (requerido)
   Ejemplo: {"command": "create_directory", "path": "src/nuevo_dir"}

9. delete_directory - Eliminar un directorio existente.
   Parámetros: 'path' (requerido)
   Ejemplo: {"command": "delete_directory", "path": "src/viejo_dir"}

10. process_code_blocks - Procesar bloques de código para crear o actualizar archivos automáticamente.

Además, puedes:
- Leer el archivo 'requerimientos.md' en el directorio 'project' para entender los requerimientos del proyecto.
- Analizar el proyecto para determinar el porcentaje de completitud e identificar tareas pendientes.
- Detectar las tecnologías utilizadas en el proyecto.

Flujo de trabajo:
1. **Analizar Requerimientos:** Lee 'requerimientos.md' y comprende los requerimientos del usuario.
2. **Analizar Estado del Proyecto:** Determina el porcentaje de completitud e identifica tareas pendientes.
3. **Planificar Acciones:** Decide las acciones necesarias para completar las tareas pendientes sin duplicar trabajo existente.
4. **Ejecutar Acciones:** Usa las herramientas disponibles para crear, actualizar o eliminar archivos y directorios según sea necesario.
5. **Verificar Cambios:** Asegúrate de que los cambios estén alineados con los requerimientos y las mejores prácticas.
6. **Reportar Resultados:** Informa al usuario sobre las acciones tomadas y los pasos adicionales necesarios.

Debes asegurarte de que todas las acciones sean precisas y sigan los principios de código limpio y arquitectura limpia. Si los requerimientos del usuario son vagos, pide aclaraciones. En modo interactivo, confirma cambios significativos con el usuario. En modo autónomo, procede según el análisis y la planificación."""
        self.conversation_history = []
        self.file_backups = {}
        self.autonomous_mode = False  # Modo interactivo por defecto

    def _read_requirements(self):
        """Lee y parsea el archivo requerimientos.md de forma flexible."""
        req_path = os.path.join(self.project_dir, "requerimientos.md")
        if not os.path.exists(req_path):
            return [{"task": "Crear archivo de requerimientos inicial", "completed": False}]
        try:
            with open(req_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                return [{"task": "Definir requerimientos del proyecto", "completed": False}]
            tasks = re.findall(r'^[-\*]\s+(.*)', content, re.MULTILINE)
            if not tasks:
                # Si no hay formato de lista, asumir que cada línea no vacía es una tarea
                tasks = [line.strip() for line in content.split('\n') if line.strip()]
            return [{"task": task, "completed": False} for task in tasks] or [{"task": "Clarificar requerimientos", "completed": False}]
        except Exception as e:
            return {"error": f"Error al leer 'requerimientos.md': {str(e)}"}

    def _list_files(self, path, format_output=True):
        """Lista archivos en un directorio de manera recursiva."""
        try:
            if not os.path.isdir(path):
                return f"Error: Directorio no encontrado: {path}"
            file_list = []
            for root, _, files in os.walk(path):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), path)
                    file_list.append(rel_path)
            if format_output:
                return f"Archivos en '{path}':\n" + "\n".join(file_list) if file_list else "  - Ninguno"
            return file_list
        except Exception as e:
            return f"Error al listar archivos: {str(e)}"

    def _analyze_project_completion(self):
        """Analiza el proyecto para determinar el porcentaje de completitud con inferencias."""
        requirements = self._read_requirements()
        if "error" in requirements:
            return requirements
        project_files = self._list_files(self.project_dir, format_output=False)
        if isinstance(project_files, str):  # Error case
            return {"error": project_files}

        completed, pending = [], []

        # Inferir tareas si los requerimientos son vagos
        if not requirements or all(r["task"] in ["Clarificar requerimientos", "Definir requerimientos del proyecto"] for r in requirements):
            inferred_tasks = []
            if project_files:
                inferred_tasks.append({"task": "Estructura inicial creada", "completed": True})
            else:
                inferred_tasks.append({"task": "Crear estructura inicial", "completed": False})
            if any(f.endswith(".py") for f in project_files):
                inferred_tasks.append({"task": "Iniciar archivo principal Python", "completed": True})
            requirements = inferred_tasks

        for req in requirements:
            task_keywords = re.split(r'\s+', req["task"].lower())
            task_completed = False
            for file in project_files:
                if any(keyword in file.lower() for keyword in task_keywords):
                    task_completed = True
                    break
            if task_completed:
                req["completed"] = True
                completed.append(req["task"])
            else:
                pending.append(req["task"])

        total_reqs = len(requirements)
        completed_count = len(completed)
        completion_percentage = (completed_count / total_reqs) * 100 if total_reqs > 0 else (10 if project_files else 0)

        return {
            "completion_percentage": round(completion_percentage, 2),
            "completed": completed,
            "pending": pending,
            "files": project_files
        }

    def _identify_technologies(self):
        """Identifica tecnologías basándose en extensiones y contenido."""
        tech_stack = set()
        project_files = self._list_files(self.project_dir, format_output=False)
        if isinstance(project_files, str):  # Error case
            return ["Desconocido"]
        for file in project_files:
            if file.endswith(".py"): tech_stack.add("Python")
            elif file.endswith(".js"): tech_stack.add("JavaScript")
            elif file.endswith(".java"): tech_stack.add("Java")
            elif file == "package.json": tech_stack.add("Node.js")
            elif file == "requirements.txt": tech_stack.add("Python")
            elif file == "pom.xml": tech_stack.add("Java (Maven)")
            elif file == "composer.json": tech_stack.add("PHP (Composer)")
            elif file == "Gemfile": tech_stack.add("Ruby (Rails)")
        return list(tech_stack) if tech_stack else ["Desconocido"]

    def _generate_project_status_response(self, project_analysis, tech_stack):
        """Genera una respuesta detallada con sugerencias específicas."""
        response = "**Estado del Proyecto Actual**\n\n"
        response += f"- **Porcentaje de completitud:** {project_analysis['completion_percentage']}%\n"
        response += f"- **Tecnologías identificadas:** {', '.join(tech_stack)}\n"
        response += "- **Archivos presentes:**\n" + "\n".join(f"  - {f}" for f in project_analysis['files']) + "\n"
        response += "- **Tareas completadas:**\n" + ("\n".join(f"  - {t}" for t in project_analysis['completed']) or "  - Ninguna") + "\n"
        response += "- **Tareas pendientes:**\n" + ("\n".join(f"  - {t}" for t in project_analysis['pending']) or "  - Ninguna") + "\n"
        if project_analysis['files'] and not project_analysis['completed']:
            response += "\n**Sugerencia:** Hay archivos presentes pero no se alinean con los requerimientos. Considera actualizar 'requerimientos.md' o vincular los archivos existentes a tareas específicas."
        elif tech_stack != ["Desconocido"]:
            response += f"\n**Sugerencia:** Dado que se detectaron {', '.join(tech_stack)}, podrías comenzar definiendo módulos o funcionalidades específicas."
        else:
            response += "\n**Sugerencia:** El proyecto está vacío. Considera crear la estructura inicial y definir requerimientos."
        return response

    def chat(self):
        """Inicia una sesión de chat interactivo."""
        print(colored("="*10 + " Agente DeepSeek Interactivo " + "="*10, "cyan"))
        print(colored("Escribe 'exit' para salir, 'history' para ver el historial, 'switch_mode' para cambiar de modo", "cyan"))

        while True:
            user_input = input(colored("Tú: ", "green"))

            if user_input.lower() == "exit":
                print(colored("¡Adiós! 👋", "cyan"))
                break

            if user_input.lower() == "history":
                self._print_history()
                continue

            if user_input.lower() == "switch_mode":
                self.autonomous_mode = not self.autonomous_mode
                mode = "autónomo" if self.autonomous_mode else "interactivo"
                print(colored(f"Cambiado a modo {mode}.", "cyan"))
                continue

            final_response = self._process_message(user_input)
            self._print_assistant_response(final_response)

    def _process_message(self, user_message):
        """Procesa el mensaje del usuario con manejo de herramientas."""
        self.conversation_history.append({"role": "user", "content": user_message})

        try:
            user_message_lower = user_message.lower()
            if "status del proyecto" in user_message_lower or "estado del proyecto" in user_message_lower:
                project_analysis = self._analyze_project_completion()
                if "error" in project_analysis:
                    response = f"**Error:** {project_analysis['error']}"
                else:
                    tech_stack = self._identify_technologies()
                    response = self._generate_project_status_response(project_analysis, tech_stack)
            elif "lista los archivos" in user_message_lower or "mostrar archivos" in user_message_lower:
                files = self._list_files(self.project_dir, format_output=True)
                response = files if "Error" in files else f"**Archivos en '{self.project_dir}':**\n{files}"
            else:
                full_prompt = self._build_full_prompt()
                response = self.client.predict(message=full_prompt, api_name="/chat")
                response = str(response)

            self.conversation_history.append({"role": "assistant", "content": response})

            if self.autonomous_mode:
                self._process_autonomous(response)
            else:
                while self._has_tool_commands(response):
                    tool_commands = self._extract_tool_commands(response)
                    for command in tool_commands:
                        tool_result = self._handle_tool_use(command)
                        self.conversation_history.append({"role": "user", "content": f"RESULTADO DE HERRAMIENTA: {tool_result}"})
                        follow_up_prompt = self._build_full_prompt()
                        response = self.client.predict(message=follow_up_prompt, api_name="/chat")
                        self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            print(colored(f"❌ Error: {str(e)}", "red"))
            return "Ocurrió un error al procesar tu solicitud."

    def _build_full_prompt(self):
        """Construye el contexto completo de la conversación."""
        prompt = self.system_prompt + "\n\n"
        for msg in self.conversation_history:
            role = "Usuario" if msg['role'] == "user" else "Asistente"
            prompt += f"{role}: {msg['content']}\n"
        return prompt

    def _has_tool_commands(self, response):
        """Verifica si la respuesta contiene comandos de herramientas."""
        return "COMMAND:" in response

    def _extract_tool_commands(self, response):
        """Extrae comandos de la respuesta."""
        commands = []
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith("COMMAND:"):
                cmd_str = line[len("COMMAND:"):].strip()
                cmd_parts = cmd_str.split(' ', 1)
                if len(cmd_parts) >= 2:
                    command_name = cmd_parts[0]
                    params = self._parse_parameters(cmd_parts[1])
                    commands.append({"name": command_name, "input": params})
        return commands

    def _parse_parameters(self, param_str):
        """Parsea los parámetros de un comando."""
        params = {}
        parts = param_str.split('--')
        for part in parts[1:]:
            part = part.strip()
            if ' ' in part:
                key, value = part.split(' ', 1)
                params[key.strip()] = value.strip().strip('"')
        return params

    def _handle_tool_use(self, command):
        """Maneja los comandos de herramientas."""
        tool_name = command['name']
        params = command['input']

        if tool_name == "view":
            return self._view_file(params.get('path'))
        elif tool_name == "str_replace":
            return self._replace_in_file(params.get('path'), params.get('old_str'), params.get('new_str'))
        elif tool_name == "create":
            return self._create_file(params.get('path'), params.get('file_text'))
        elif tool_name == "insert":
            return self._insert_in_file(params.get('path'), int(params.get('insert_line')), params.get('new_str'))
        elif tool_name == "undo_edit":
            return self._undo_edit(params.get('path'))
        elif tool_name == "list_files":
            return self._list_files(params.get('path'), format_output=True)
        elif tool_name == "delete_file":
            return self._delete_file(params.get('path'))
        elif tool_name == "create_directory":
            return self._create_directory(params.get('path'))
        elif tool_name == "delete_directory":
            return self._delete_directory(params.get('path'))
        else:
            return f"Comando desconocido: {tool_name}"

    def _process_autonomous(self, response):
        """Procesa respuestas en modo autónomo."""
        self._process_code_blocks(response)

    def _process_code_blocks(self, response):
        """Detecta y escribe bloques de código en archivos."""
        code_blocks = self._extract_code_blocks(response)
        for block in code_blocks:
            try:
                if block['filename'] and block['code']:
                    self._write_code_file(block['filename'], block['code'])
            except Exception as e:
                print(colored(f"❌ Error al escribir archivo: {str(e)}", "red"))

    def _extract_code_blocks(self, text):
        """Extrae bloques de código marcados con ```file:ruta/al/archivo."""
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

    def _write_code_file(self, filepath, content):
        """Escribe contenido en el archivo especificado."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            if os.path.exists(filepath):
                self._backup_file(filepath)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(colored(f"✓ Archivo actualizado: {filepath}", "green"))
        except Exception as e:
            print(colored(f"❌ Error al escribir {filepath}: {str(e)}", "red"))

    # ========== Operaciones con Archivos ==========
    def _view_file(self, file_path, view_range=None):
        """Ver el contenido de un archivo."""
        try:
            if not os.path.exists(file_path):
                return f"Error: Archivo no encontrado: {file_path}"
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if view_range:
                start = max(0, view_range[0] - 1)
                end = view_range[1] if view_range[1] <= len(lines) else len(lines)
                lines = lines[start:end]
            result = "".join(f"{i + 1}: {line}" for i, line in enumerate(lines))
            return result
        except Exception as e:
            return f"Error al ver archivo: {str(e)}"

    def _create_file(self, file_path, file_text):
        """Crear un nuevo archivo."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if os.path.exists(file_path):
                return f"Error: El archivo ya existe: {file_path}"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_text)
            return f"Archivo creado exitosamente: {file_path}"
        except Exception as e:
            return f"Error al crear archivo: {str(e)}"

    def _replace_in_file(self, file_path, old_str, new_str):
        """Reemplazar texto en un archivo."""
        try:
            if not os.path.exists(file_path):
                return f"Error: Archivo no encontrado: {file_path}"
            self._backup_file(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            count = content.count(old_str)
            if count != 1:
                return f"Error: Encontradas {count} ocurrencias (debe ser exactamente 1)"
            new_content = content.replace(old_str, new_str, 1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"Texto reemplazado exitosamente en {file_path}"
        except Exception as e:
            return f"Error al reemplazar texto: {str(e)}"

    def _insert_in_file(self, file_path, insert_line, new_str):
        """Insertar texto en una línea específica."""
        try:
            if not os.path.exists(file_path):
                return f"Error: Archivo no encontrado: {file_path}"
            self._backup_file(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if insert_line > len(lines):
                return f"Error: Línea {insert_line} fuera de rango ({len(lines)} líneas)"
            lines.insert(insert_line - 1, new_str + '\n' if not new_str.endswith('\n') else new_str)
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return f"Insertado exitosamente en la línea {insert_line} de {file_path}"
        except Exception as e:
            return f"Error al insertar texto: {str(e)}"

    def _undo_edit(self, file_path):
        """Deshacer la última edición en un archivo."""
        try:
            if file_path not in self.file_backups:
                return f"Error: No hay respaldo para {file_path}"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.file_backups[file_path])
            del self.file_backups[file_path]
            return f"Restaurado exitosamente {file_path}"
        except Exception as e:
            return f"Error al deshacer edición: {str(e)}"

    def _delete_file(self, path):
        """Eliminar un archivo."""
        try:
            if os.path.exists(path):
                self._backup_file(path)
                os.remove(path)
                return f"Archivo '{path}' eliminado exitosamente."
            return f"Error: Archivo no encontrado: {path}"
        except Exception as e:
            return f"Error al eliminar archivo: {str(e)}"

    def _create_directory(self, path):
        """Crear un nuevo directorio."""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Directorio '{path}' creado exitosamente."
        except Exception as e:
            return f"Error al crear directorio: {str(e)}"

    def _delete_directory(self, path):
        """Eliminar un directorio."""
        try:
            if os.path.exists(path):
                os.rmdir(path)
                return f"Directorio '{path}' eliminado exitosamente."
            return f"Error: Directorio no encontrado: {path}"
        except Exception as e:
            return f"Error al eliminar directorio: {str(e)}"

    def _backup_file(self, file_path):
        """Crear respaldo antes de editar."""
        try:
            if file_path not in self.file_backups and os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self.file_backups[file_path] = f.read()
        except Exception:
            pass

    # ========== Funciones de Interfaz ==========
    def _print_assistant_response(self, response):
        """Imprime la respuesta formateada."""
        print(colored("\n🤖 DeepSeek:", "blue"))
        print(colored(response, "blue"))
        print(colored("-"*40, "cyan"))

    def _print_history(self):
        """Imprime el historial de la conversación."""
        print(colored("\n" + "="*10 + " Historial " + "="*10, "cyan"))
        for msg in self.conversation_history:
            color = "green" if msg['role'] == "user" else "blue"
            prefix = "Tú: " if msg['role'] == "user" else "IA: "
            print(colored(prefix + msg['content'], color))
        print(colored("="*30 + "\n", "cyan"))

def main():
    """Punto de entrada principal."""
    try:
        load_dotenv()
        agent = DeepSeekAgent()
        agent.chat()
    except KeyboardInterrupt:
        print(colored("\n¡Adiós!", "cyan"))
    except Exception as e:
        print(colored(f"Error fatal: {e}", "red"))

if __name__ == "__main__":
    main()
