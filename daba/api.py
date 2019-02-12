from .storage import Storage
from .binary_tree import BinaryTree

class Daba:
   def __init__(self, dbfile):
      self._storage = Storage(dbfile)
      self._tree = BinaryTree(self._storage)

   def commit(self):
      pass

   def __getitem__(self, key):
      pass

   def __setitem__(self, key, value):
      pass

   def __delitem__(self, key):
      pass