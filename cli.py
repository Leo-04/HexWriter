import sys
import os
import json
from compiler.compiler import Compiler, Parser
from compiler.decompiler import Decompiler


def handle_argv(argv):
    """Handles command line arguments and returns the arguments"""

    files = []
    encoding = "UTF-8"
    dps = 4
    output = None
    decompile_rules = None

    # Check if next argument is a value
    output_next = False
    encoding_next = False
    dps_next = False
    decompile_next = False

    for arg in argv:
        if arg in ["/out", "--out", "-out", "-o", "/o"]:
            output_next = True

        elif arg in ["/decompile", "--decompile", "-decompile", "-d", "/d"]:
            decompile_next = True

        elif arg in ["/encoding", "-encoding", "--encoding", "-e", "/e"]:
            encoding_next = True

        elif arg in ["/default_pad_size", "-default_pad_size", "--default_pad_size", "-dps", "/dps"]:
            dps_next = True

        elif arg in ["/help", "-help", "--help", "-h", "/h", "/?"]:
            print("Command line options:")
            print("\t/out --out -out -o /o")
            print("\t\tSpecifies the output file")
            print("\t/encoding --encoding -encoding -e /e")
            print("\t\tSpecifies the encoding of string literals")
            print("\t/default_pad_size --default_pad_size -default_pad_size -dps /dps")
            print("\t\tSpecifies the default pad size")
            print("\t/decompile --decompile -decompile -d /d")
            print("\t\tDecompiles binary back into hw script with a set of rules")
            print("\t/help --help -help -h /h /?")
            print("\t\tShows this dialog")


        elif decompile_next:
            decompile_rules = arg

        elif output_next:
            output = arg

        elif encoding_next:
            try:
                "".encode(arg)
                encoding = arg
            except:
                print("Unknown encoding:", arg)
                return None, None, None, None, None

        elif dps_next:
            if arg.isdigit():
                dps = int(arg)
            else:
                print("default pad size must be an integer")
                return None, None, None, None, None

        elif os.path.isfile(os.path.abspath(arg)):
            files.append(arg)

        else:
            print("Unknown command option:", arg)
            print("Use --help to get a list of options")
            return None, None, None, None, None

    return files, output, encoding, dps, decompile_rules


def command_line_interface():
    """Takes the command line parameter and executes them"""

    files, output, encoding, dps, decompile_rules = handle_argv(sys.argv[1:])
    if files is None:
        return

    if len(files) == 0:
        handle_argv(["-help"])
        return

    # Check if we are decompiling
    if decompile_rules is None:
        # We are compiling

        hw = Compiler(encoding, dps)

        string = ""

        for file in files:
            try:
                with open(file) as fp:
                    string += fp.read()
            except Exception as err:
                print("Unable to open file:", file)
                print("Error:", err)

        try:
            byte_array = hw.compile(string)

            if output is None:
                print(str(byte_array)[2:-1])
            else:
                try:
                    with open(output, "wb") as fp:
                        fp.write(byte_array)
                except Exception as err:
                    print("Could not write to file", output)
                    print("Error:", err)

        except Parser.Error as err:
            print("Unexpected", repr(err.match.string), "on line", err.match.line)
        except TypeError as err:
            print("Unexpected group type:", err)
        except ValueError as err:
            err = err.args
            print("Unknown padding type:", repr(err[0]), "on line", err[1])

    else:
        # we are decompiling

        hw = Decompiler(encoding, dps)

        try:
            rules = json.load(open(decompile_rules))
        except Exception as err:
            print("Cannot open file:", decompile_rules)
            print(err)
            return

        print(hw.get_header(rules))

        for file in files:
            try:
                with open(file, "rb") as fp:
                    binary = fp.read()
            except:
                print("Cannot open file:", file)
                continue

            try:
                string, index = hw.decompile(rules, binary)

                # append the left over bytes
                if index != len(binary):
                    string += "\n" + (" ".join("#" + hex(byte)[2:] for byte in binary[index:]))

                print(string)

            except NameError as err:
                print("Cannot find varname:", err)
            except TypeError as err:
                print("Cannot find width:", err)


if __name__ == "__main__":
    command_line_interface()
