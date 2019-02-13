import pickle
from daba.storage import Storage

class StorageTests:
   def prepare(self):
      try:
         f = open('temp.db', 'r+b')
      except:
         f = open('temp.db', 'x+b')
      self.storage = Storage(f)

   def run(self):
      self.prepare()
      self.test_write_read()
      self.test_root_write_read()

   # Test writing and reading
   def test_write_read(self):
      data = pickle.dumps([1, 2, 3])
      address = self.storage.write(data)

      read_data = self.storage.read(address)
      assert read_data == data

      arr = pickle.loads(read_data)
      assert arr == [1, 2, 3]

   # Test root writing and reading
   def test_root_write_read(self):
      data = pickle.dumps([1, 2, 3])
      address = self.storage.write_root(data)

      read_address = self.storage.read_root_address()
      read_data = self.storage.read(read_address)
      assert read_data == data

      arr = pickle.loads(read_data)
      assert arr == [1, 2, 3]

if __name__ == '__main__':
      StorageTests().run()