import sys
import os
import yaml

dct = yaml.load(sys.argv[1])
# print(os.environ)
print(dct)