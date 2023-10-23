import io
import re
import sys

from enum import Enum

import warnings
warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")

class CodeExecutionStatus(Enum):
    NOT_CODE = 0
    SUCCESS = 1
    ERROR = 2
    TIMEOUT = 3


class CodeExecutor:
    def __init__(self):
        pass

    def execute(self, code_string):
        if "import " in code_string:
            regex = r"```python\n(.*?)\n```"
            matches = re.findall(regex, code_string, re.DOTALL)
            if not matches:
                matches = re.findall(r"```\n(.*?)\n```", code_string, re.DOTALL)

            if not matches:
                matches = [code_string]

            if type(matches) == list:
                code_string = matches[0]
            else:
                code_string = matches

            output_buffer = io.StringIO()
            original_stdout = sys.stdout
            try:
                sys.stdout = output_buffer
                import warnings
                warnings.filterwarnings("ignore")
                exec(code_string, globals())
                warnings.filterwarnings("default")
                printed_output = output_buffer.getvalue()

                return {
                    "status": CodeExecutionStatus.SUCCESS,
                    "output": printed_output,
                }
            except Exception as e:
                # Restore the original standard output

                return {
                    "status": CodeExecutionStatus.ERROR,
                    "output": str(e),
                }
            finally:
                sys.stdout = original_stdout

        else:
            return {
                "status": CodeExecutionStatus.NOT_CODE,
                "output": None,
            }
