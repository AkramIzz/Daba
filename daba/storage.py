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
      self._ensure_root_block()
   
   def write(self, data):
      # lock before determining address
      # to ensure no two processes get the same address
      self._lock()
      self._file.seek(0, os.SEEK_END)
      address = self._file.tell()
      self._write_int(len(data))
      self._file.write(data)
      self._unlock()
      return address

   def write_root_address(self, address):
      self._file.seek(0)
      self._lock()
      self._write_int(address)
      self._unlock()

   def read(self, address):
      self._file.seek(address)
      length = self._read_int()
      data = self._file.read(length)
      return data

   def read_root_address(self):
      self._file.seek(0)
      # lock on read because this part is mutable
      # and another process could be changing it
      self._lock()
      address = self._read_int()
      self._unlock()
      if address == 0:
         return None
      return address

   def _ensure_root_block(self):
      self._file.seek(0, os.SEEK_END)
      if self._file.tell() >= self.ROOT_BLOCK_SIZE:
         # root block exists. No furthur actions needed
         return
         
      self._lock()
      self._file.write(b'\x00' * self.ROOT_BLOCK_SIZE)
      self._unlock()

   def _write_int(self, integer):
      bytes = struct.pack(self.INTEGER_FORMAT, integer)
      self._file.write(bytes)

   def _read_int(self):
      bytes = self._file.read(self.INTEGER_SIZE)
      return struct.unpack(self.INTEGER_FORMAT, bytes)[0]

   def _lock(self):
      portalocker.lock(self._file, portalocker.LOCK_EX)

   def _unlock(self):
      self._file.flush()
      portalocker.unlock(self._file)
