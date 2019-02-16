import os
import struct
import portalocker

class Storage:
   # > means big-endian order (network order), std. size and alignment
   # Q means Unsigned long long
   INTEGER_FORMAT = ">Q"
   # the standard size of unsigned long long
   INTEGER_SIZE = 8
   # root address is stored at the beginning of the file
   # the root block is 8 bytes in size
   ROOT_BLOCK_SIZE = 8
   
   def __init__(self, file):
      self._file = file
      self._locked = False
      self._ensure_root_block()
   
   def write(self, data):
      self._file.seek(0, os.SEEK_END)
      address = self._file.tell()
      self._write_int(len(data))
      self._file.write(data)
      return address

   def write_root_address(self, address):
      self._file.seek(0)
      self._write_int(address)

   def read(self, address):
      self._file.seek(address)
      length = self._read_int()
      data = self._file.read(length)
      return data

   def read_root_address(self):
      self._file.seek(0)
      address = self._read_int()
      
      if address == 0:
         return None
      return address

   def _ensure_root_block(self):
      self.lock()
      self._file.seek(0, os.SEEK_END)
      if self._file.tell() >= self.ROOT_BLOCK_SIZE:
         # root block exists. No furthur actions needed
         return
         
      self._file.write(b'\x00' * self.ROOT_BLOCK_SIZE)
      self.unlock()

   def _write_int(self, integer):
      bytes = struct.pack(self.INTEGER_FORMAT, integer)
      self._file.write(bytes)

   def _read_int(self):
      bytes = self._file.read(self.INTEGER_SIZE)
      return struct.unpack(self.INTEGER_FORMAT, bytes)[0]

   def lock(self):
      self._locked = True
      portalocker.lock(self._file, portalocker.LOCK_EX)

   def unlock(self):
      self._locked = False
      self._file.flush()
      portalocker.unlock(self._file)

   def is_locked(self):
      return self._locked