import sys
import os
import yaml

dct = yaml.load(os.environ["CHARTS"])
# print(os.environ)
print(dct)