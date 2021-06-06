"""
Code for use in debugging. 
IMPORTANT: check the configuration options at the start of the file.

Author: Dana Nau <nau@umd.edu>
Feb 8, 2021
"""

import sys


################################################################################
# Configuration options: 

# If we're reading input from a terminal, let the code have pauses for paging.
# You can override this by changing the value of allow_pauses below.
if sys.stdin.isatty():
    allow_pauses = True
else:
    allow_pauses = False

# If the user is using IPython, assume that if they call the debugger,
# they'll want IPython's debugger.
# You can override this by changing the value of use_ipython below.
if 'IPython' in sys.modules:
    use_ipython = True
else:
    use_ipython = False

################################################################################


# Choose which debugger to use
if use_ipython:
    from IPython import embed
    from IPython.terminal.debugger import set_trace
else:
    from pdb import set_trace


def check_result(actual,expected):
    """
    Check whether a function has returned the correct value. Arguments:
      - actual: the value that you want to check
      - expected: the value that you want 'actual' to have
    If actual != expected, check_result raises an exception. 
    Otherwise, it prints a message saying the comparison was successful.
    """
    if actual != expected:
        raise Exception("Actual result differs from expected result.")
    elif actual != None:     # whence expected is also None
        print('check_result> The result is as expected.\n')


def pause():
    """
    If the global variable allow_pauses is true, then pause and wait for
    the user to decide whether to continue execution or enter the debugger.
    Otherwise, just continue.
    """
    if allow_pauses:
        typing = input(">>> Type Enter to continue, or d to debug: ")
        if typing == 'd': 
            print('            ===========================================')
            print("            Type 'c' or 'continue' to exit the debugger")
            print('            ===========================================')
            set_trace()
#         elif use_ipython and typing == 'e':
#             print('            ===========================')
#             print("            Type 'exit' to exit ipython")
#             print('            ===========================')
#             embed()
        else:
            print('=======================================================================')
    else:
        print('Continuing.')

