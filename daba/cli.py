import sys
import os

import daba

USAGE_ERR = 1
KEY_ERR = 2

def usage():
   print(
"""
Usage:
   python3 -m daba.cli DBNAME get KEY
   python3 -m daba.cli DBNAME set KEY VALUE
   python3 -m daba.cli DBNAME delete KEY VALUE
"""
   )

def main(argc, argv):
   if 4 < argc < 5:
      usage()
      exit(USAGE_ERR)
   
   # Extract argv into seperate variables
   dbname, verb, key, value = (argv[1:] + [None])[:4]

   if verb not in ('get', 'set', 'delete'):
      usage()
      exit(USAGE_ERR)
   
   db = daba.connect(dbname)
   try:
      if verb == 'get':
         print(db[key])
      elif verb == 'set':
         db[key] = value
         db.commit()
      elif verb == 'delete':
         del db[key]
         db.commit()
   except KeyError as ke:
      print(ke, file=sys.stderr)
      exit(KEY_ERR)

if __name__ == '__main__':
   main(len(sys.argv), sys.argv)