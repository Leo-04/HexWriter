from tkinter import *
from compiler.regexparser import Parser
from compiler.consts import REGEX


class ColorizerText(Text):
    def __init__(self, master, **kwargs):
        Text.__init__(self, master, **kwargs)

        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

        self.bind("<<TextModified>>", self.colorize)
        self.parser = Parser(REGEX)

        self.tag_config("def", foreground="white")
        self.tag_config("sizedef", foreground="white")
        self.tag_config("pad", foreground="blue")
        self.tag_config("int", foreground="orange")
        self.tag_config("float", foreground="orange")
        self.tag_config("var", foreground="purple")
        self.tag_config("str", foreground="green")
        self.tag_config("comment", foreground="dark grey")
        self.tag_config("miss_match_error", background="red")

    def _proxy(self, command, *args):
        """Proxy callback"""

        cmd = (self._orig, command) + args
        try:
            result = self.tk.call(cmd)
        except Exception as err:
            # This is needed as when you press CTRL+A then CTRL+V it crashes
            print(cmd, err)
            return

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

    def colorize(self, event=None):
        """Scans through text and highlights all found words"""

        text = self.get("1.0", "end")

        tokens = self.parser.scan(text, remove=["white_space"], ignore_errors=True)

        for tag in REGEX:
            self.tag_remove(tag, "1.0", "end")
        self.tag_remove("miss_match_error", "1.0", "end")

        for token in tokens:
            self.tag_add(token.group, "1.0+%sc" % token.start, "1.0+%sc" % token.end)
