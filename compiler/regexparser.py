import re


class Parser:
    def __init__(self, patterns, error_name="miss_match_error"):
        if type(patterns) == dict:
            patterns = list(patterns.items())

        self.regex = re.compile(
            "|".join(
                [
                    '(?P<%s>%s)' % (re.escape(name),
                                    (
                                        regex
                                        if type(regex != re.Pattern)
                                        else regex.pattern)
                                    ) for name, regex in patterns
                ]
            ) + "|(?P<%s>.)" % error_name)

        self.error_name = error_name

    def scan(self, string, remove=None, ignore_errors=False):
        """Scans a string with the compiled regex finding matches and returning them, removing any groups specified"""

        if remove is None:
            remove = []
        tokens = []

        for match in self.regex.finditer(string):
            if not match:
                continue

            span = match.span()
            if span[0] == span[1]:
                continue

            match_dict = match.groupdict()
            if len([name for name in match_dict if match_dict[name] is not None]) != 1:
                raise NotImplementedError()

            if match.lastgroup == self.error_name and not ignore_errors:
                raise Parser.Error(match)

            if match.lastgroup not in remove:
                tokens.append(Parser.Match(match))

        return tokens

    class Error(Exception):
        def __init__(self, match):
            self.match = match
            Exception.__init__(self, self.what())

        def what(self):
            return "Miss Match Error at position %s: %s" % (
                self.match.start(),
                repr(self.match.group())
            )

    class Match:
        def __init__(self, match):
            self.match = match

        def __str__(self):
            return self.string

        def __repr__(self):
            return self.group + "{" + repr(self.string)[1:-1] + "}"

        @property
        def group(self):
            return self.match.lastgroup

        @property
        def start(self):
            return self.match.start()

        @property
        def end(self):
            return self.match.end()

        @property
        def string(self):
            return self.match.group()

        @property
        def base_string(self):
            return self.match.string

        @property
        def line(self):
            return self.match.string[:self.start].count("\n") + 1

        @property
        def endline(self):
            return self.match.string[:self.end].count("\n") + 1


def anyof(*arr):
    """Turns an array of options into a regex"""

    return "(" + ("|".join(re.escape(i) for i in arr)) + ")"
