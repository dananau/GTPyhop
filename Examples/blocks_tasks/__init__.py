"""
Generic initialization file for a GTPyhop example domain
Author: Dana Nau <nau@umd.edu>
June 3, 2021
"""

import sys
sys.path.append('../')      # kludge to make gtpyhop available

import gtpyhop

# This avoids hard-coding the domain name, making the code more portable
domain_name = __package__
the_domain = gtpyhop.Domain(domain_name)

from .methods import *
from .actions import *
from .examples import *

def main():
    # If we've changed to some other domain, this will change us back.
    print(f"Changing current domain to {domain_name}, if it isn't that already.")
    gtpyhop.current_domain = the_domain
    run_examples()      # defined in the .examples file

print('-----------------------------------------------------------------------')
print(f"Created '{gtpyhop.current_domain}'. To run the examples, type this:")
print(f'{domain_name}.main()')

###############################################################################
# It's tempting to make the following call to main() unconditional, to run the
# examples without making the user type an extra command. But if we do this
# and an error occurs while main() is executing, we get a situation in which
# the actions, methods, and examples files have been imported but the module
# hasn't been - which causes problems if we try to import the module again.
###############################################################################

if __name__=="__main__":
    main()
