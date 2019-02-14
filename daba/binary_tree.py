import pickle

class StringRef:
   def __init__(self, value=None, address=None):
      self.value = value
      self.address = address

   def load(self, bytes):
      self.value = pickle.loads(bytes)
   
   def serialize(self):
      return pickle.dumps(self.value)

class Node:
   def __init__(self, key, value_ref, left_ref, right_ref):
      self.key = key
      self.value_ref = value_ref
      self.left_ref = left_ref
      self.right_ref = right_ref

class NodeRef:
   def __init__(self, value=None, address=None):
      self.value = value
      self.address = address
   
   def load(self, bytes):
      key, value_addr, left_addr, right_addr = pickle.loads(bytes)
 
      left_ref = None
      if left_addr is not None:
         left_ref = NodeRef(address=left_addr)
      right_ref = None 
      if right_addr is not None:
         right_ref = NodeRef(address=right_addr)

      self.value = Node(
         key,
         StringRef(address=value_addr),
         left_ref,
         right_ref
      )
   
   def serialize(self):
      left_addr = None
      if self.value.left_ref is not None:
         left_addr = self.value.left_ref.address
      right_addr = None
      if self.value.right_ref is not None:
         right_addr = self.value.right_ref.address
         
      return pickle.dumps((
         self.value.key,
         self.value.value_ref.address,
         left_addr,
         right_addr
      ))

class BinaryTree:
   def __init__(self, storage):
      self._storage = storage
      self.root_ref = None

   def set(self, key, value):
      self._retrieve_root()
      self.root_ref = self._set(self.root_ref, key, StringRef(value=value))
      self.commit()

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

   def get(self, key):
      self._retrieve_root()
      return self._retrieve(self._get(self.root_ref, key)).value

   def _get(self, node_ref, key):
      if node_ref is None:
         return None
      
      if key == node_ref.value.key:
         return node_ref.value.value_ref
      elif key > node_ref.value.key:
         return self._get(self._retrieve(node_ref.value.right_ref), key)
      else:
         return self._get(self._retrieve(node_ref.value.left_ref), key)

   def _retrieve_root(self):
      if self.root_ref is not None:
         return
      address = self._storage.read_root_address()
      if address is None:
         self.root_ref = None
         return
      self.root_ref = NodeRef(address=address)
      self._retrieve(self.root_ref)

   def _retrieve(self, value_ref):
      if value_ref is None or value_ref.value is not None:
         return value_ref
      bytes = self._storage.read(value_ref.address)
      value_ref.load(bytes)
      return value_ref

   def commit(self):
      if self.root_ref is None or self.root_ref.address is not None:
         return
      self._prepare_to_store(self.root_ref)
      self._storage.write_root_address(self.root_ref.address)

   def _prepare_to_store(self, node_ref):
      if node_ref is None or node_ref.address is not None:
         return

      self._prepare_to_store(node_ref.value.left_ref)
      self._prepare_to_store(node_ref.value.right_ref)

      self._store_value_ref(node_ref.value.value_ref)
      self._store_value_ref(node_ref)
      
   def _store_value_ref(self, value_ref):
      if value_ref.address is not None:
         return

      address = self._storage.write(value_ref.serialize())
      value_ref.address = address

   def print(self):
      self.print_node(self.root_ref)

   def print_node(self, node_ref):
      if node_ref is None:
         return
      print('key:', node_ref.value.key, ' value:', node_ref.value.value)
      self.print_node(node_ref.value.left_ref)
      self.print_node(node_ref.value.right_ref)