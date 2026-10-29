#!/usr/bin/env python3
import ast
import operator
from pathlib import Path
import socket
import threading

SOCKET = Path("/tmp/os_calc.sock")
OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.UAdd: operator.pos, ast.USub: operator.neg,
}


def calculate(expression: str) -> str:
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](visit(node.operand))
        raise ValueError("разрешены только числа и арифметические операции")
    return str(visit(ast.parse(expression, mode="eval")))


def handle(connection: socket.socket) -> None:
    with connection, connection.makefile("rwb") as stream:
        expression = stream.readline().decode().strip()
        try:
            answer = calculate(expression)
        except Exception as error:
            answer = f"ERROR: {error}"
        stream.write((answer + "\n").encode())
        print(f"{expression} => {answer}", flush=True)


def main() -> None:
    SOCKET.unlink(missing_ok=True)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        server.bind(str(SOCKET))
        server.listen()
        print(f"Unix-сокет готов: {SOCKET}", flush=True)
        while True:
            connection, _ = server.accept()
            threading.Thread(target=handle, args=(connection,), daemon=True).start()
    finally:
        server.close()
        SOCKET.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
