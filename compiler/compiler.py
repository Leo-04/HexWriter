import ast

from compiler.regexparser import Parser
import struct
import compiler.consts as consts


class Compiler(Parser):
    def __init__(self, text_encode="UTF-8", pad_size=4):
        Parser.__init__(self, consts.REGEX)

        self.pad_defs = consts.PAD_DEFS
        self.pad_size = pad_size
        self.text_encode = text_encode

    def compile(self, text: str) -> bytes:
        """Takes in a string and compiles it to binary data"""

        tokens = self.scan(text, remove=["white_space", "comment"])

        defs = {}
        pad_size = self.pad_size
        pad_defs = self.pad_defs.copy()

        byte_array = bytes()
        
        for token in tokens:
            if token.group == "def":
                eq_at = token.string.find("=")
                defs[token.string[1:eq_at]] = self.compile(token.string[eq_at+1:])
            
            elif token.group == "pad":
                pad_type = token.string[1:-1].lower()

                if pad_type.isdigit():
                    pad_size = int(pad_type)
                elif pad_type not in pad_defs:
                    raise ValueError(pad_type, token.line)
                else:
                    pad_size = pad_defs[pad_type]
            
            elif token.group == "sizedef":
                eq_at = token.string.find("=")
                pad_defs[token.string[1:eq_at]] = int(token.string[eq_at+1:])
            
            elif token.group == "int":
                num = int(token.string)
                byte_array += num.to_bytes(((num.bit_length() + 7) // 8) if pad_size is None else pad_size, "big", signed=True)
            
            elif token.group == "hex":
                num = int(token.string[1:], 16)
                byte_array += num.to_bytes(((num.bit_length() + 7) // 8) if pad_size is None else pad_size, "big", signed=True)
            
            elif token.group == "bin":
                num = int(token.string.replace(" ", "").replace("_", ""), 2)
                byte_array += num.to_bytes(((num.bit_length() + 7) // 8) if pad_size is None else pad_size, "big", signed=True)
            
            elif token.group == "float":
                byte_array += struct.pack(">" + ("d" if pad_size is None or pad_size > 4 else "f"), float(token.string))

            elif token.group == "var":
                byte_array += defs[token.string]

            elif token.group == "str":
                byte_array += ast.literal_eval(token.string).encode(self.text_encode)

            else:
                raise TypeError(token.group)
        return byte_array
