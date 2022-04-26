import sys
import os
import yaml

dct = yaml.load(sys.argv[1], Loader=yaml.FullLoader)
# print(os.environ)
print(dct)