#!/usr/bin/env python3
import sys
from pathlib import Path

REQUEST = Path("/tmp/os_calc_request")
RESPONSE = Path("/tmp/os_calc_response")
expression = " ".join(sys.argv[1:]) or "2 + 2 * 2"
with REQUEST.open("w", encoding="utf-8") as stream:
    stream.write(expression + "\n")
with RESPONSE.open("r", encoding="utf-8") as stream:
    print(stream.readline().strip())
