import json

from UI.window import Window
from UI.tkmenu import TkMenu
from UI.colorizertext import ColorizerText
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import askokcancel, showerror

from compiler.compiler import Compiler
from compiler.decompiler import Decompiler
from compiler.regexparser import Parser


class App:
    def __init__(self, style_path):
        self.win = Window("Hex Writer", self.close)
        self.file = None

        try:
            self.win.option_readfile(style_path)
        except:
            pass

        self.text = ColorizerText(self.win, font="consolas 12")
        self.menu = TkMenu(self.win,
                           ("New", "<Control-o>", self.new),
                           ("Open", "<Control-o>", self.open),
                           ("Load", "<Control-l>", self.load),
                           None,
                           ("Save", "<Control-s>", self.save),
                           ("Save As", "<Control-Shift-S>", self.save),
                           None,
                           ("Compile", "<Control-p>", self.compile)
                           )

        self.menu.pack(side="top", fill="x")
        self.text.pack(fill="both", expand=True)

    def close(self):
        """Closes the window"""

        if not self.new():
            self.win.destroy()

    def run(self):
        """Goes into the event loop"""

        self.win.mainloop()

    def new(self):
        """Create a blank document"""

        if self.file is not None or self.text.get("1.0", "end-1c") != "":
            if not askokcancel("", "Any unsaved data will be lost"):
                return 1

        self.file = None
        self.text.delete("1.0", "end")
        self.win.title("")

    def open(self):
        """Opens a file"""

        file = askopenfilename()

        if file:

            if self.new():
                return

            with open(file, "r") as fp:
                text = fp.read()

            self.text.insert("end", text)

            self.file = file
            self.win.title(file)

    def load(self):
        """Ask to open a binary file and a rules.json file"""

        file = askopenfilename()
        if not file:
            return
        rules_file = askopenfilename()

        if not rules_file:
            return

        hw = Decompiler("utf-8", 4)

        try:
            rules = json.load(open(rules_file))
        except Exception as err:
            showerror("", "Cannot open file: "+ str(rules_file)+"\nReason: " + str(err))
            return

        try:
            with open(file, "rb") as fp:
                binary = fp.read()
        except Exception as err:
            showerror("", "Cannot open file:" + str(file) + "\nReason:" + str(err))
            return

        header = hw.get_header(rules)

        try:
            string, index = hw.decompile(rules, binary)

            if index != len(binary):
                string += "\n" + (" ".join("#" + hex(byte)[2:] for byte in binary[index:]))

            if self.new():
                return

            self.text.insert("1.0", header + "\n" + string)

        except NameError as err:
            showerror("", "Cannot find varname: " + str(err))
        except TypeError as err:
            showerror("", "Cannot find width: " + str(err))

    def save(self):
        """Saves the current file, if there is no current file, it call saveas"""

        if self.file is None:
            return self.saveas()

        if self.file is not None:
            with open(self.file, "w") as fp:
                fp.write(self.text.get("1.0", "end"))

    def saveas(self):
        """Ask the user to save a file"""

        file = asksaveasfilename()

        if file:
            self.file = file
            self.win.title(file)
            self.save()

    def compile(self):
        """Compiles the string to binary data, then ask the user to save the file"""

        string = self.text.get("1.0", "end")
        hw = Compiler("UTF-8", 4)

        try:
            byte_array = hw.compile(string)

            output = asksaveasfilename()

            if output:
                try:
                    with open(output, "wb") as fp:
                        fp.write(byte_array)
                except Exception as err:
                    showerror("", "Could not write to file: " + str(output) + "\nReason:" + str(err))

        except Parser.Error as err:
            showerror("", "Unexpected " + repr(err.match.string) + " on line " + err.match.line)
        except TypeError as err:
            showerror("", "Unexpected group type:" + str(err))
        except ValueError as err:
            err = err.args
            showerror("", "Unknown padding type: " + repr(err[0]) + " on line " + err[1])
