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

   def _prepare_to_store(self, node_ref):
      if node_ref is None or node_ref.address is not None:
         return

      self._prepare_to_store(node_ref.value.left_ref)
      self._prepare_to_store(node_ref.value.right_ref)

      self._store_value_ref(node_ref.value.value_ref)
      self._store_value_ref(node_ref)
      
   def print(self):
      self.print_node(self.root_ref)

   def print_node(self, node_ref):
      if node_ref is None:
         return
      print('key:', node_ref.value.key, ' value:', node_ref.value.value)
      self.print_node(node_ref.value.left_ref)
      self.print_node(node_ref.value.right_ref)