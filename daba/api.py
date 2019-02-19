from .storage import Storage
from .binary_tree import BinaryTree

class Daba:
   def __init__(self, dbfile):
      self._storage = Storage(dbfile)
      self._tree = BinaryTree(self._storage)

   def commit(self):
      self._tree.commit()

   def __getitem__(self, key):
      return self._tree.get(key)

   def __setitem__(self, key, value):
      self._tree.set(key, value)

   def __delitem__(self, key):
      self._tree.delete(key)