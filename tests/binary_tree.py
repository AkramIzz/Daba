import pickle
from daba.storage import Storage
from daba.binary_tree import BinaryTree

class BinaryTreeTests:
   def prepare(self):
      try:
         f = open('new.db', 'r+b')
      except:
         f = open('new.db', 'x+b')
      self.store = Storage(f)
      self.init_tree()
   
   def init_tree(self):
      self.tree = BinaryTree(self.store)

   def run(self):
      self.prepare()
      self.set((
         ("key", "value"),
         ("test", "true"),
         ("foo", "bar")
      ))
      self.commit()
      self.init_tree()
      self.set((
         ("key", "new_value"),
         ("k", "v"),
         ("fiz", "buz")
      ))
      self.test_delete(("k","foo"), ("value", "bar"))
      self.commit()
      self.init_tree()
      self.test_get((
         ("key", "new_value"),
         ("test", "true"),
         ("foo", None),
         ("k", None),
         ("fiz", "buz")
      ))

   def set(self, key_value_pairs):
      for key, value in key_value_pairs:
         self.tree.set(key, value)

   def commit(self):
      self.tree.commit()

   def test_delete(self, keys, not_keys):
      for key in keys:
         assert self.tree.delete(key) == True
      for key in not_keys:
         assert self.tree.delete(key) == False

   def test_get(self, key_value_pairs):
      for key, value in key_value_pairs:
         assert value == self.tree.get(key)

if __name__ == '__main__':
      BinaryTreeTests().run()