import pickle

class ValueRef:
   def __init__(self, value=None, address=None):
      self.value = value
      self.address = address

   def load(self, bytes):
      self.value = pickle.loads(bytes)
   
   def serialize(self):
      return pickle.dumps(self.value)

class LogicalBase:
   def __init__(self, storage):
      self.root_ref = None
      self._storage = storage
   
   def set(self, key, value):
      if not self._storage.is_locked():
         self._retrieve_root()
         self._storage.lock()
      self.root_ref = self._set(self.root_ref, key, ValueRef(value=value))

   def get(self, key):
      self._retrieve_root()
      return self._retrieve(self._get(self.root_ref, key)).value

   def commit(self):
      if self.root_ref is not None and self.root_ref.address is None:
         self._prepare_to_store(self.root_ref)
         self._storage.write_root_address(self.root_ref.address)
      
      self._storage.unlock()
      self.root_ref = None

   def _retrieve_root(self):
      address = self._storage.read_root_address()
      if address is None:
         self.root_ref = None
         return

      if self.root_ref is None or self.root_ref.address != address:
         self.root_ref = self.RootRefClass(address=address)
         self._retrieve(self.root_ref)
      

   def _retrieve(self, value_ref):
      if value_ref is None or value_ref.value is not None:
         return value_ref
      bytes = self._storage.read(value_ref.address)
      value_ref.load(bytes)
      return value_ref

   def _store_value_ref(self, value_ref):
      if value_ref.address is not None:
         return

      address = self._storage.write(value_ref.serialize())
      value_ref.address = address