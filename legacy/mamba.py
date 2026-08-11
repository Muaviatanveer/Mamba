import sys
from lark import Lark
from lark.visitors import Interpreter

class Scope:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Mamba Runtime Error: Variable '{name}' is not defined.")

    def set(self, name, value):
        self.vars[name] = value

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class MambaInterpreter(Interpreter):
    def __init__(self):
        super().__init__()
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.functions = {}

    def number(self, tree):
        val = tree.children[0].value
        return float(val) if '.' in val else int(val)

    def string(self, tree):
        return tree.children[0].value[1:-1]

    def var(self, tree):
        return self.current_scope.get(tree.children[0].value)

    def list(self, tree):
        return [self.visit(child) for child in tree.children]

    def index_access(self, tree):
        var_name = tree.children[0].value
        idx = int(self.visit(tree.children[1]))
        arr = self.current_scope.get(var_name)
        return arr[idx]

    def add(self, tree):
        left = self.visit(tree.children[0])
        right = self.visit(tree.children[1])
        if isinstance(left, str) or isinstance(right, str):
            return str(left) + str(right)
        return left + right

    def sub(self, tree):
        return self.visit(tree.children[0]) - self.visit(tree.children[1])

    def mul(self, tree):
        return self.visit(tree.children[0]) * self.visit(tree.children[1])

    def div(self, tree):
        return self.visit(tree.children[0]) / self.visit(tree.children[1])

    def gt(self, tree):
        return self.visit(tree.children[0]) > self.visit(tree.children[1])

    def lt(self, tree):
        return self.visit(tree.children[0]) < self.visit(tree.children[1])

    def eq(self, tree):
        return self.visit(tree.children[0]) == self.visit(tree.children[1])

    def ne(self, tree):
        return self.visit(tree.children[0]) != self.visit(tree.children[1])

    def var_assign(self, tree):
        var_name = tree.children[0].value
        val = self.visit(tree.children[1])
        self.current_scope.set(var_name, val)

    def print_stmt(self, tree):
        val = self.visit(tree.children[0])
        print(val)

    def block(self, tree):
        for stmt in tree.children:
            self.visit(stmt)

    def fn_def(self, tree):
        fn_name = tree.children[0].value
        params = [c.value for c in tree.children[1:-1]]
        body_block = tree.children[-1]
        self.functions[fn_name] = (params, body_block)

    def fn_call(self, tree):
        fn_name = tree.children[0].value
        arg_values = [self.visit(arg) for arg in tree.children[1:]]

        # Built-in Standard Library Functions
        if fn_name == "len":
            return len(arg_values[0])
        if fn_name == "input":
            prompt = arg_values[0] if arg_values else ""
            return input(prompt)
        if fn_name == "str":
            return str(arg_values[0])
        if fn_name == "int":
            return int(arg_values[0])

        if fn_name not in self.functions:
            raise NameError(f"Mamba Runtime Error: Function '{fn_name}' is not defined.")

        params, body_block = self.functions[fn_name]

        if len(params) != len(arg_values):
            raise TypeError(f"Mamba Runtime Error: '{fn_name}' expects {len(params)} args, got {len(arg_values)}")

        old_scope = self.current_scope
        self.current_scope = Scope(parent=self.global_scope)
        for name, val in zip(params, arg_values):
            self.current_scope.set(name, val)

        result = None
        try:
            self.visit(body_block)
        except ReturnException as ret:
            result = ret.value
        finally:
            self.current_scope = old_scope

        return result

    def return_stmt(self, tree):
        val = self.visit(tree.children[0])
        raise ReturnException(val)

    def if_stmt(self, tree):
        condition = self.visit(tree.children[0])
        if condition:
            self.visit(tree.children[1])
        elif len(tree.children) > 2:
            self.visit(tree.children[2])

    def while_stmt(self, tree):
        while self.visit(tree.children[0]):
            self.visit(tree.children[1])

def start_repl():
    print("========================================")
    print("   🐍 Mamba v0.2 Interactive Shell     ")
    print("   Type 'exit' to quit.                 ")
    print("========================================")

    with open('grammar.lark', 'r') as g_file:
        grammar = g_file.read()

    parser = Lark(grammar, parser='lalr')
    interpreter = MambaInterpreter()

    while True:
        try:
            line = input("mamba > ")
            if line.strip() == "exit":
                print("Goodbye!")
                break
            if not line.strip():
                continue
            tree = parser.parse(line)
            interpreter.visit(tree)
        except Exception as e:
            print(f"Error: {e}")

def run_mamba(filename):
    with open('grammar.lark', 'r') as g_file:
        grammar = g_file.read()

    parser = Lark(grammar, parser='lalr')

    with open(filename, 'r') as code_file:
        code = code_file.read()

    tree = parser.parse(code)
    interpreter = MambaInterpreter()
    interpreter.visit(tree)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        start_repl()
    else:
        run_mamba(sys.argv[1])