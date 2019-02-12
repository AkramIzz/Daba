from .api import Daba

def connect(dbname):
   try:
      dbfile = open(dbname, 'r+b')
   except:
      dbfile = open(dbname, 'x+b')
   return Daba(dbfile)