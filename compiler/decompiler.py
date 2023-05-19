import struct
import re
import compiler.consts as consts


class Reader:
    def __init__(self, type_, fmt="h", length=1, var_name=None):
        self.type = type_
        self.length = length
        self.var_name = var_name
        self.fmt = fmt

    def __str__(self):
        """Converts to human-readable form"""

        return "[" + self.type + ("" if self.length is None else ":" + str(self.length)) + "]" + (
            self.fmt if self.fmt is not None else "") + (" " + self.var_name if self.var_name else "")

    def __repr__(self):
        """Converts to human-readable form"""
        return self.__str__()


class Decompiler:
    def __init__(self, text_encode="UTF-8", pad_size=4):
        self.regex = re.compile(r"\[([^:\]]*)\s*(:\s*[^\]]*)?\](x|h|d|b|f|s|c|\!|\?)?\s*(\$[a-zA-Z0-9_]+)?")
        self.text_encode = text_encode
        self.pad_size = pad_size

    def read_format(self, format_string):
        """Converts a format string into a array of Reader classes"""

        if type(format_string) == str:
            format_string = [s.strip() for s in re.split("\\n|;", format_string)]

        reader = []

        for string in format_string:
            for item in self.regex.finditer(string):
                name, size, fmt, var = item.groups()
                if size is not None:
                    size = size[1:]

                    if size.isdigit():
                        size = int(size)

                if var is not None:
                    var = var.strip()

                if name.isdigit():
                    name = int(name)

                reader.append(Reader(name, fmt, size, var))

        return reader

    def decompile(self, rules, binary, indent=0):
        """Decompiles binary data back to input string by following a set of rules"""

        readers = self.read_format(rules["format"])

        def_vars = {}
        index = 0
        string = ""
        indent_string = " " * (4 * indent)

        for code in readers:
            if code.type in rules["sizes"]:
                n_bytes = rules["sizes"][code.type]

            elif type(code.type) == int:
                n_bytes = code.type

            elif code.type in consts.PAD_DEFS:
                n_bytes = consts.PAD_DEFS[code.type]

            elif code.type in rules["structs"]:
                new_rules = rules.copy()
                new_rules["format"] = rules["structs"][code.type]

                for n in range(self.get_var(code.length, def_vars)):
                    s, i = self.decompile(new_rules, binary[index:], indent=indent + 1)

                    index += i
                    string += indent_string + s
                continue

            elif code.fmt == "?":
                n_bytes = 0
            else:
                raise TypeError(code.type)

            byte_array = binary[index: index + n_bytes]

            if code.fmt == "f":
                for n in range(self.get_var(code.length, def_vars)):
                    value = struct.unpack('>' + ("d" if size > 4 else "f"), byte_array)[0]
                    string += indent_string + "[" + str(code.type) + "] " + str(value) + "\n"

                    index += n_bytes

            elif code.fmt == "b":
                for n in range(self.get_var(code.length, def_vars)):
                    as_str = ''.join(bin(byte)[2:] for byte in byte_array)
                    string += indent_string + "[" + str(code.type) + "] " + as_str + "\n"

                    index += n_bytes

            elif code.fmt == "?":
                defs_ = {int(s.split("=", 1)[0]): s.split("=", 1)[1] for s in code.type.split(",")}
                var_ = def_vars[code.var_name]

                new_rules = rules.copy()
                new_rules["format"] = rules["structs"][defs_[var_]]

                for n in range(self.get_var(code.length, def_vars)):
                    s, i = self.decompile(new_rules, binary[index:], indent=indent + 1)

                    index += i
                    string += indent_string + s
                    continue

            elif code.fmt in ["h", "x"]:
                for n in range(self.get_var(code.length, def_vars)):
                    as_str = ''.join(hex(byte)[2:] for byte in byte_array)
                    string += indent_string + "[" + str(code.type) + "] #" + as_str + "\n"

                    index += n_bytes

            elif code.fmt in ["c", "s"]:
                n_bytes = n_bytes * self.get_var(code.length, def_vars)
                byte_array = binary[index: index + n_bytes]
                index += n_bytes

                s = byte_array.decode(self.text_encode)

                string += indent_string + repr(s) + "\n"

            elif code.fmt in ["d", None]:
                for n in range(self.get_var(code.length, def_vars)):
                    as_int = int.from_bytes(byte_array, "big", signed=True)
                    string += indent_string + "[" + str(code.type) + "] " + ("-" if as_int < 0 else "+") + str(
                        as_int) + "\n"

                    index += n_bytes

            elif code.fmt == "!":
                for n in range(self.get_var(code.length, def_vars)):
                    as_int = int.from_bytes(byte_array, "big", signed=True)
                    as_hex = ''.join(hex(byte)[2:] for byte in byte_array)

                    if str(as_int) in rules["defines"]:
                        value = str(rules["defines"][str(as_int)])

                    elif "#" + as_hex in rules["defines"]:
                        value = str(rules["defines"]["#" + as_hex])

                    else:
                        value = "[" + str(code.type) + "] " + ("-" if as_int < 0 else "+") + str(as_int)

                    string += indent_string + value + "\n"
                    index += n_bytes

            else:
                raise 1234

            if code.var_name:
                def_vars[code.var_name] = int.from_bytes(byte_array, "big", signed=True)

        return string, index

    def get_header(self, rules):
        """Get the string header from a set of rules"""

        string = ""

        for def_ in rules["defines"]:
            string += "$" + rules["defines"][def_] + "="

            if def_[0] == "#":
                string += str(def_) + "\n"
            elif def_[0] in "+-":
                value = int(def_)
                string += ("-" if value < 0 else "+") + str(value) + "\n"

        for size in rules["sizes"]:
            string += "@" + size + "=" + str(rules["sizes"][size]) + "\n"

        return string

    def get_var(self, s, def_vars):
        """Finds a variable from a dictionary or returns the integer representation of a string"""

        if s is None:
            return 1
        elif s in def_vars:
            return def_vars[s]
        elif s.isdigit():
            return int(s)
        else:
            raise NameError(s)
