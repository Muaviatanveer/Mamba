from lark import Transformer

class PhpGenerator(Transformer):
    def number(self, args): return str(args[0])
    def string(self, args): return str(args[0])
    def var(self, args): return f"${args[0]}"
    def add(self, args): return f"({args[0]} + {args[1]})"
    def sub(self, args): return f"({args[0]} - {args[1]})"
    def mul(self, args): return f"({args[0]} * {args[1]})"
    def div(self, args): return f"({args[0]} / {args[1]})"
    def gt(self, args): return f"({args[0]} > {args[1]})"
    def lt(self, args): return f"({args[0]} < {args[1]})"
    def eq(self, args): return f"({args[0]} == {args[1]})"
    def ne(self, args): return f"({args[0]} != {args[1]})"
    def var_assign(self, args): return f"${args[0]} = {args[1]};"
    def print_stmt(self, args): return f"echo {args[0]} . \"\\n\";"
    def expr_stmt(self, args): return f"{args[0]};"
    def assert_stmt(self, args): return f"assert({args[0]});"
    def test_stmt(self, args): return f"// Test: {args[0]}\necho \"Running Test: \" . {args[0]} . \"\\n\"; {args[1]}"
    def block(self, args):
        body = "\n    ".join([str(a) for a in args if a is not None])
        return f"{{\n    {body}\n}}"
    def return_stmt(self, args): return f"return {args[0]};"
    def if_stmt(self, args):
        cond, body = args[0], args[1]
        if len(args) > 2 and args[2] is not None:
            return f"if ({cond}) {body} else {args[2]}"
        return f"if ({cond}) {body}"
    def while_stmt(self, args): return f"while ({args[0]}) {args[1]}"
    def try_stmt(self, args):
        return f"try {args[0]} catch (Exception ${args[1]}) {args[2]}"
    def map_pair(self, args):
        key = str(args[0])
        if not key.startswith('"'): key = f'"{key}"'
        return f"{key} => {args[1]}"
    def map(self, args):
        pairs = ", ".join([str(a) for a in args if a is not None])
        return f"[{pairs}]"
    def list(self, args):
        items = ", ".join([str(a) for a in args if a is not None])
        return f"[{items}]"
    def index_access(self, args): return f"{args[0]}[{args[1]}]"
    def dot_call(self, args):
        obj, method = str(args[0]), str(args[1])
        call_args = ", ".join([str(a) for a in args[2:] if a is not None])
        if obj == "file" and method == "read": return f"file_get_contents({call_args})"
        if obj == "file" and method == "write": return f"file_put_contents({call_args})"
        if obj == "http" and method == "get": return f"file_get_contents({call_args})"
        if obj == "env" and method == "get": return f"(getenv({call_args}) ? getenv({call_args}) : \"\")"
        if obj == "json" and method == "stringify": return f"json_encode({call_args})"
        if obj == "json" and method == "parse": return f"json_decode({call_args}, true)"
        if obj == "req" and method == "body": return "file_get_contents('php://input')"
        if obj == "req" and method == "query": return f"(isset($_GET[{call_args}]) ? $_GET[{call_args}] : \"\")"
        if obj == "req" and method == "header": return f"(isset($_SERVER['HTTP_' . strtoupper(str_replace('-', '_', {call_args}))]) ? $_SERVER['HTTP_' . strtoupper(str_replace('-', '_', {call_args}))] : \"\")"
        if obj == "db" and method == "open": return f"new PDO('sqlite:' . {call_args})"
        if obj == "db" and method == "query":
            parsed_args = [str(a) for a in args[2:] if a is not None]
            if len(parsed_args) > 1:
                return f"$stmt = $mamba_global_db->prepare({parsed_args[0]}); $stmt->execute({parsed_args[1]});"
            return f"$mamba_global_db->exec({call_args})"
        if obj == "str" and method == "upper": return f"strtoupper({call_args})"
        if obj == "str" and method == "lower": return f"strtolower({call_args})"
        if obj == "str" and method == "replace": return f"str_replace({call_args})"
        if obj == "str" and method == "len": return f"strlen({call_args})"
        if obj == "arr" and method == "push": return f"array_push({call_args})"
        if obj == "arr" and method == "contains": return f"in_array({call_args})"
        if obj == "arr" and method == "join": return f"implode({call_args})"
        if obj == "arr" and method == "len": return f"count({call_args})"
        if obj == "map" and method == "has": return f"array_key_exists({call_args})"
        if obj == "map" and method == "remove": return f"unset({call_args})"
        return f"${obj}->{method}({call_args})"
    def route_def(self, args):
        method, path, body = args[0], args[1], args[2]
        return f"header('Access-Control-Allow-Origin: *'); header('Access-Control-Allow-Headers: Content-Type'); if (isset($_SERVER['REQUEST_METHOD']) && $_SERVER['REQUEST_METHOD'] === '{method}' && parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) === {path}) {body}"
    def fn_def(self, args):
        fn_name = str(args[0])
        params = [f"${p}" for p in args[1:-1] if p is not None]
        params_str = ", ".join(params)
        body = args[-1]
        return f"function {fn_name}({params_str}) {body}"
    def fn_call(self, args):
        fn_name = str(args[0])
        call_args = ", ".join([str(a) for a in args[1:] if a is not None])
        return f"{fn_name}({call_args})"
    def start(self, args):
        statements = "\n    ".join([str(s) for s in args if s is not None])
        return f"<?php\n{statements}\n?>"