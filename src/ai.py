import os
import inspect
import json
from abc import ABC, abstractmethod
from typing import Literal, List, Dict, Any, AsyncGenerator, Optional, Callable
from pydantic import BaseModel
import aiohttp  # For asynchronous HTTP requests

from src.utils.tools import get_tools
from src.utils.printer import Printer

printer = Printer(identifier="AI")

class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    text: str
    images: List[str] = []  # For OpenRouter multi-modal
    tool_calls: List[Dict] = []
    tool_call_id: str = ""

class AIProvider(ABC):
    def __init__(self, model: str, api_key: str, agent_id: str = None):
        self.model = model
        self.api_key = api_key
        self.messages: List[Message] = []  # Initialize messages list
        self.tools: List[Callable] = []  # Callable functions
        self.config: Dict[str, Any] = {}
        self.agent_id = agent_id

    @abstractmethod
    async def complete(self, message: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def stream(self, message: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    def add_message(self, message: Message):
        self.messages.append(message)

    def set_tools(self):
         self.tools = get_tools()

class ProviderImports:
    openai = None
    groq = None
    mistralai = None
    google = None
    
    def __init__(self):
        try:
            from openai import OpenAI
            self.openai = OpenAI
        except ImportError:
            pass
            
        try:
            from groq import Groq
            self.groq = Groq
        except ImportError:
            pass
            
        try:
            from mistralai.client import MistralClient
            self.mistralai = MistralClient
        except ImportError:
            pass
            
        try:
            import google.generativeai as genai
            self.google = genai
        except ImportError:
            pass

provider_imports = ProviderImports()

class OpenAIClient(AIProvider):
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None, agent_id: str = None):
        if not provider_imports.openai:
            raise ImportError("OpenAI no instalado. Ejecute: pip install openai")
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.tools_map = {}
        self.tools = []
        self.messages = []
        self.config = {
            "temperature": 0.5,
            "max_tokens": 1000,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }
        super().__init__(model, api_key, agent_id)

    def append(self, messages: List[Message]):
        converted = []
        for msg in messages:
            new_msg = {
                "role": msg.role,
                "content": [{"type": "text", "text": msg.text}],
            }
            if msg.tool_calls:
                new_msg["tool_calls"] = [{
                    "id": tc.get('id', ''),
                    "type": "function",
                    "function": {
                        "name": tc.get('function', {}).get('name', ''),
                        "arguments": tc.get('function', {}).get('arguments', '')
                    }
                } for tc in msg.tool_calls]
            if msg.tool_call_id:
                new_msg["tool_call_id"] = msg.tool_call_id
            converted.append(new_msg)
        self.messages.extend(converted)
        return self.messages

    async def complete(self, model: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=self.messages,
            tools=self.tools,
            **self.config
        )
        msg = response.choices[0].message
        generated = Message(
            role="assistant",
            text=msg.content or "",
            tool_calls=[tc.model_dump() for tc in msg.tool_calls] if msg.tool_calls else []
        )
        self.append([generated])
        
        if await self.process_tool_calls(generated.tool_calls):
            return await self.complete(model)
        return generated.text

    async def stream(self, model: str) -> AsyncGenerator[str, None]:
        response = self.client.chat.completions.create(
            model=model,
            messages=self.messages,
            tools=self.tools,
            stream=True,
            **self.config
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
                
        if full_response:
            self.append([Message(role="assistant", text=full_response)])

    def set_tools(self):
        self.tools = get_tools()
        self.tools_map = {tool.__name__: tool for tool in self.tools}

    async def process_tool_calls(self, tool_calls: List[Dict]) -> bool:
        if not tool_calls:
            return False
            
        results = []
        for tc in tool_calls:
            func_name = tc['function']['name']
            args = json.loads(tc['function']['arguments'])
            
            if func_name in self.tools_map:
                tool_function = self.tools_map[func_name]
                result = await tool_function(**args)  # Call the function
                results.append(Message(
                    role="tool",
                    text=str(result), # convert to string
                    tool_call_id=tc['id']
                ))
        
        if results:
            self.append(results)
            return True
        return False

    def text_to_speech(self, text: str, voice: str, file_path: str):
        from openai import OpenAI
        client = OpenAI()
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(file_path)

class GroqClient(AIProvider):
    def __init__(self, model: str, api_key: str, agent_id: str = None):
        if not provider_imports.groq:
            raise ImportError("Groq no instalado. Ejecute: pip install groq")
        from groq import Groq
        self.client = Groq(api_key=api_key)
        self.tools_map = {}
        self.tools = []
        self.messages = []
        self.config = {"temperature": 0.5, "max_tokens": 1000}
        super().__init__(model, api_key, agent_id)

    def append(self, messages: List[Message]):
        self.messages.extend([{
            "role": msg.role,
            "content": msg.text,
            **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
            **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {})
        } for msg in messages])

    async def complete(self, model: str) -> str:
        response = self.client.chat.completions.create(
            messages=self.messages,
            model=model,
            tools=self.tools,
            **self.config
        )
        return response.choices[0].message.content

    async def stream(self, model: str) -> AsyncGenerator[str, None]:
        response = self.client.chat.completions.create(
            messages=self.messages,
            model=model,
            tools=self.tools,
            stream=True,
            **self.config
        )
        for chunk in response:
            yield chunk.choices[0].delta.content or ""

    def set_tools(self):
        self.tools = get_tools()
        self.tools_map = {tool.__name__: tool for tool in self.tools}

    async def process_tool_calls(self, tool_calls: List[Dict]) -> bool:
        # Implementación similar a OpenAI
        return False

    def text_to_speech(self, text: str, voice: str, file_path: str):
        raise NotImplementedError("Groq no soporta text-to-speech")

class MistralClient(AIProvider):
    def __init__(self, model: str, api_key: str, agent_id: str = None):
        if not provider_imports.mistralai:
            raise ImportError("Mistral no instalado. Ejecute: pip install mistralai")
        from mistralai.client import MistralClient as MistralAI
        self.client = MistralAI(api_key=api_key)
        self.tools_map = {}
        self.tools = []
        self.messages = []
        self.config = {"temperature": 0.5, "max_tokens": 1000}
        super().__init__(model, api_key, agent_id)

    def append(self, messages: List[Message]):
        self.messages.extend([{
            "role": msg.role,
            "content": msg.text
        } for msg in messages])

    async def complete(self, model: str, agent_id: str = None) -> str:
        if agent_id:
             chat_response = self.client.chat(
                model=model,
                messages=self.messages,
                #tools=self.tools,
                 agent_id=agent_id,
                **self.config
             )
        else:
            chat_response = self.client.chat(
                model=model,
                messages=self.messages,
                tools=self.tools,
                **self.config
        )
        return chat_response.choices[0].message.content

    async def stream(self, model: str) -> AsyncGenerator[str, None]:
        response = self.client.chat_stream(
            model=model,
            messages=self.messages,
            tools=self.tools,
            **self.config
        )
        for chunk in response:
            yield chunk.choices[0].delta.content or ""

    def set_tools(self):
         self.tools = get_tools()
         self.tools_map = {tool.__name__: tool for tool in self.tools}

    async def process_tool_calls(self, tool_calls: List[Dict]) -> bool:
        # Implementación similar a OpenAI
        return False

    def text_to_speech(self, text: str, voice: str, file_path: str):
        raise NotImplementedError("Mistral no soporta text-to-speech")

class GeminiClient(AIProvider):
    def __init__(self, model: str, api_key: str, agent_id: str = None):
        if not provider_imports.google:
            raise ImportError("Gemini no instalado. Ejecute: pip install google-generativeai")
        import google.generativeai as genai
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model)
        self.messages: List[Message] = []  # Initialize messages list
        self.config = {"temperature": 0.5}
        super().__init__(model, api_key, agent_id)

    def add_message(self, message: Message):
        self.messages.append(message)

    async def complete(self, prompt: str) -> str:
        response = self.client.generate_content(
            contents=[{
                "parts": [{"text": prompt}]
            }]
        )
        return response.text

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        response = self.client.generate_content(
            contents=[{
                "parts": [{"text": prompt}]
            }],
            stream=True
        )
        for chunk in response:
            yield chunk.text or ""

    def set_tools(self):
        self.tools = get_tools()
        self.tools_map = {tool.__name__: tool for tool in self.tools}

    async def process_tool_calls(self, tool_calls: List[Dict]) -> bool:
        return False  # Implementación base

class OpenAIRouterProvider(AIProvider):
    def __init__(self, model: str, api_key: str, http_referer: str, x_title: str, agent_id: str = None):
        super().__init__(model, api_key, agent_id)
        self.http_referer = http_referer
        self.x_title = x_title
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def complete(self, message: str) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.http_referer,  # Required for OpenRouter
                "X-Title": self.x_title,  # Optional
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": message}],  # Simple text message
            }

            async with session.post(self.api_url, headers=headers, json=data) as response:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                json_response = await response.json()
                return json_response["choices"][0]["message"]["content"]

    async def stream(self, message: str) -> AsyncGenerator[str, None]:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.http_referer,  # Required for OpenRouter
                "X-Title": self.x_title,  # Optional
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": message}],
                "stream": True
            }

            async with session.post(self.api_url, headers=headers, json=data) as response:
                response.raise_for_status()
                async for chunk in response.content.iter_any():
                    try:
                        chunk_str = chunk.decode('utf-8')
                        # OpenRouter sends newlines as complete messages
                        for line in chunk_str.splitlines():
                            if line.strip():  # Ignore empty lines
                                yield line
                    except UnicodeDecodeError:
                        # Handle non-UTF-8 encoded data if necessary
                        print("Warning: Could not decode chunk as UTF-8")
                        continue
    def set_tools(self):
         self.tools = get_tools()
         self.tools_map = {tool.__name__: tool for tool in self.tools}

    async def process_tool_calls(self, tool_calls: List[Dict]) -> bool:
        # Implementación similar a OpenAI
        return False

    def text_to_speech(self, text: str, voice: str, file_path: str):
        raise NotImplementedError("Gemini no soporta text-to-speech")

class ProviderFactory:
    @staticmethod
    def create_provider(provider_name: str, model: str, api_key: str, agent_id: str = None, **kwargs):
        if provider_name == "openai":
            return OpenAIClient(model, api_key, **kwargs, agent_id=agent_id)
        elif provider_name == "mistral":
            return MistralClient(model, api_key, **kwargs, agent_id=agent_id)
        if provider_name == "openrouter":
            return OpenAIRouterProvider(model, api_key, kwargs.get("http_referer", ""), kwargs.get("x_title", ""), agent_id=agent_id, **kwargs)
        elif provider_name == "gemini":
            return GeminiClient(model, api_key, **kwargs, agent_id=agent_id)
        elif provider_name == "groq":
            return GroqClient(model, api_key, **kwargs, agent_id=agent_id)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

def toolify(func):
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    sig = inspect.signature(func)
    params = {
        p.name: {"type": type_map.get(p.annotation, "string")}
        for p in sig.parameters.values()
    }
    required = [p.name for p in sig.parameters.values() if p.default == inspect.Parameter.empty]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": params,
                "required": required,
                "additionalProperties": False
            }
        }
    }
