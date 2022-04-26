import sys
import os
import yaml

dct = yaml.safe_load(sys.argv)
print(os.environ)
print(dct)