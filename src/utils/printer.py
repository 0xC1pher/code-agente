def colorize(text, color):
    colors = {
        "reset": "\033[0m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }
    return f"{colors[color]}{text}{colors['reset']}"


class Printer:
    # ANSI escape sequences for colors
    colors = {
        "reset": "\033[0m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }

    def __init__(self, identifier=None):
        self.identifier = identifier

    def _color_text(self, text, color):
        return f"{self.colors[color]}{text}{self.colors['reset']}"

    def print_colored(self, *args, color="reset", sep=" ", end="\n", flush=False):
        if self.identifier:
            print(f"[{self.identifier}] ", end="")
        colored_texts = [self._color_text(str(arg), color) for arg in args]
        print(sep.join(colored_texts), end=end, flush=flush)
        return ""

    def red(self, *args, sep=" ", end="\n", flush=False):
        self.print_colored(*args, color="red", sep=sep, end=end, flush=flush)

    def green(self, *args, sep=" ", end="\n", flush=False):
        self.print_colored(*args, color="green", sep=sep, end=end, flush=flush)

    def yellow(self, *args, sep=" ", end="\n", flush=False):
        self.print_colored(*args, color="yellow", sep=sep, end=end, flush=flush)

    def blue(self, *args, sep=" ", end="\n", flush=False):
        self.print_colored(*args, color="blue", sep=sep, end=end, flush=flush)

    def magenta(self, *args, sep=" ", end="\n", flush=False):
        self.print_colored(*args, color="magenta", sep=sep, end=end, flush=flush)

    def cyan(self, *args, sep=" ", end="\n", flush=False):
        self.print_colored(*args, color="cyan", sep=sep, end=end, flush=flush)

    def white(self, *args, sep=" ", end="\n", flush=False):
        self.print_colored(*args, color="white", sep=sep, end=end, flush=flush)

    def user_output(self, text):
        """Imprime texto del usuario en cian con formato Markdown"""
        print(self._color_text("Usuario: ", "cyan") + colorize(text, "cyan"))

    def agent_output(self, text):
        """Imprime texto del agente en blanco con formato Markdown"""
        print(self._color_text("Agente: ", "white") + colorize(text, "white"))

    def title_output(self, text):
        """Imprime títulos en verde con formato Markdown"""
        print(self._color_text(text, "green"))

    def markdown_output(self, text):
        """Imprime texto formateado en Markdown"""
        print(text)
