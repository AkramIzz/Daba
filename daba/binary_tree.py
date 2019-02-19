from .logical import ValueRef, LogicalBase

import pickle

class Node:
   def __init__(self, key, value_ref, left_ref, right_ref):
      self.key = key
      self.value_ref = value_ref
      self.left_ref = left_ref
      self.right_ref = right_ref

class NodeRef(ValueRef):
   def load(self, bytes):
      key, value_addr, left_addr, right_addr = pickle.loads(bytes)
 
      left_ref = None
      if left_addr is not None:
         left_ref = NodeRef(address=left_addr)
      right_ref = None 
      if right_addr is not None:
         right_ref = NodeRef(address=right_addr)

      self.value = Node(
         key, ValueRef(address=value_addr), left_ref, right_ref
      )
   
   def serialize(self):
      left_addr = None
      if self.value.left_ref is not None:
         left_addr = self.value.left_ref.address
      right_addr = None
      if self.value.right_ref is not None:
         right_addr = self.value.right_ref.address
         
      return pickle.dumps(
         (self.value.key, self.value.value_ref.address, left_addr, right_addr)
      )

class BinaryTree(LogicalBase):
   RootRefClass = NodeRef

   def _set(self, node_ref, key, value_ref):
      new_node = None
      if node_ref is None:
         new_node = Node(key, value_ref, None, None)
      elif key == node_ref.value.key:
         new_node = Node(key, value_ref, node_ref.value.left_ref, node_ref.value.right_ref)
      elif key > node_ref.value.key:
         new_node = Node(node_ref.value.key, node_ref.value.value_ref,
            node_ref.value.left_ref,
            self._set(self._retrieve(node_ref.value.right_ref), key, value_ref))
      else:
         new_node = Node(node_ref.value.key, node_ref.value.value_ref,
            self._set(self._retrieve(node_ref.value.left_ref), key, value_ref),
            node_ref.value.right_ref)
      return NodeRef(value=new_node)

   def _get(self, node_ref, key):
      if node_ref is None:
         return None
      
      if key == node_ref.value.key:
         return node_ref.value.value_ref
      elif key > node_ref.value.key:
         return self._get(self._retrieve(node_ref.value.right_ref), key)
      else:
         return self._get(self._retrieve(node_ref.value.left_ref), key)

   def _delete(self, node_ref, key):
      if node_ref is None:
         raise KeyError('key', key, 'not found')
      
      new_node = None
      if key == node_ref.value.key:
         if node_ref.value.left_ref or node_ref.value.right_ref:
            new_node = self._merge(self._retrieve(node_ref.value.left_ref),
               self._retrieve(node_ref.value.right_ref))
      elif key > node_ref.value.key:
         new_node = Node(node_ref.value.key, node_ref.value.value_ref,
            node_ref.value.left_ref,
            self._delete(self._retrieve(node_ref.value.right_ref), key))
      else:
         new_node = Node(node_ref.value.key, node_ref.value.value_ref,
            self._delete(self._retrieve(node_ref.value.left_ref), key),
            node_ref.value.right_ref)
      if new_node is None:
         return None
      return NodeRef(value=new_node)

   def _merge(self, left_ref, right_ref):
      new_node = None
      if left_ref is not None and right_ref is not None:
         left_max_ref = self._get_max_ref(left_ref)
         new_left_ref = self._delete(left_ref, left_max_ref.key)
         new_node = Node(left_max_ref.value.key, left_max_ref.value.value_ref,
            new_left_ref, right_ref)
      elif left_ref is not None:
         new_node = Node(left_ref.value.key, left_ref.value.value_ref,
            left_ref.value.left_ref, left_ref.value.right_ref)
      elif right_ref is not None:
         new_node = Node(right_ref.value.key, right_ref.value.value_ref,
            right_ref.value.left_ref, right_ref.value.right_ref)
      return new_node

   def _get_max_ref(self, node_ref):
      while node_ref.value.right_ref is not None:
         node_ref = self._retrieve(node_ref.value.right_ref)
      return node_ref

   def _prepare_to_store(self, node_ref):
      if node_ref is None or node_ref.address is not None:
         return

      self._prepare_to_store(node_ref.value.left_ref)
      self._prepare_to_store(node_ref.value.right_ref)

      self._store_value_ref(node_ref.value.value_ref)
      self._store_value_ref(node_ref)
      
   def print(self):
      self.print_node(self.root_ref)

   def print_node(self, node_ref, preprint=''):
      if node_ref is None:
         return
      print(preprint, end=' ')
      print('key:', node_ref.value.key)
      self.print_node(self._retrieve(node_ref.value.left_ref), preprint=preprint+' '*4)
      self.print_node(self._retrieve(node_ref.value.right_ref), preprint=preprint+' '*4)