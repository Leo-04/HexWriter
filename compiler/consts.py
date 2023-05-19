PAD_DEFS = {
    "byte": 1,
    "ubyte": 1,
    "short": 2,
    "ushort": 2,
    "int": 4,
    "uint": 4,
    "long": 8,
    "ulong": 8,
    "big": 16,
    "ubig": 16,
    
    "i8": 1,
    "u8": 1,
    "i16": 2,
    "u16": 2,
    "i32": 4,
    "u32": 4,
    "i64": 8,
    "u64": 8,
    "i128": 16,
    "u128": 16,
}

# Find this in colorizer.py in IdleLib
_stringprefix = r"(?i:r|u|f|fr|rf|b|br|rb)?"
_sqstring = _stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
_dqstring = _stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
_sq3string = _stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
_dq3string = _stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'

REGEX = {
    "def": r"\$[a-zA-Z_][a-zA-Z_0-9]*\=.*",
    "sizedef": r"\@[a-zA-Z_][a-zA-Z_0-9]*\=[0-9]+",
    "pad": r"\[[^\]]*\]",
    "int": r"(\+|\-)[0-9]+",
    "hex": r"\#[a-fA-F0-9]+",
    "float": r"[0-9]*\.[0-9]*",
    "bin": r"([01]( |_)*)+",
    "var": r"[a-zA-Z_][a-zA-Z_0-9]*",
    "str": "(" + ("|".join([_sq3string, _dq3string, _sqstring, _dqstring])) + ")",
    "comment": r"\/\*(\*(?!\/)|[^*])*\*\/",
    "white_space": r"[\s]*",
}
