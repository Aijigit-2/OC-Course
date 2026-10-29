#!/usr/bin/env python3
import ast
import operator
import os
from pathlib import Path

REQUEST = Path("/tmp/os_calc_request")
RESPONSE = Path("/tmp/os_calc_response")
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


def main() -> None:
    for path in (REQUEST, RESPONSE):
        if path.exists():
            raise SystemExit(f"Удалите старый FIFO: {path}")
        os.mkfifo(path, 0o600)
    print(f"FIFO-сервер готов: {REQUEST}", flush=True)
    try:
        while True:
            with REQUEST.open("r", encoding="utf-8") as stream:
                expression = stream.readline().strip()
            if not expression:
                continue
            try:
                answer = "bye" if expression == "quit" else calculate(expression)
            except Exception as error:
                answer = f"ERROR: {error}"
            with RESPONSE.open("w", encoding="utf-8") as stream:
                stream.write(answer + "\n")
            print(f"{expression} => {answer}", flush=True)
            if expression == "quit":
                return
    finally:
        REQUEST.unlink(missing_ok=True)
        RESPONSE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
