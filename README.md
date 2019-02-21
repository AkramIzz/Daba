# Daba
A key-value database that (mostly) adheres to the ACID properties, namely the atomicity, isolation and durability properties.

# Usage
## CLI
The CLI provide three operations, getting, setting, and deleting a key
```
python3 -m daba.cli DBNAME get KEY
python3 -m daba.cli DBNAME set KEY VALUE
python3 -m daba.cli DBNAME delete KEY
```
## API
The interface of the database is similar to a dictionary with few minor differences.
Fisrt we need to connect to the database
```python3
import daba
db = daba.connect(DBNAME)
```
Then we can use the `db` object like a normal dictionary, except that after setting or deleting a key we need to commit our changes
```python3
db[key] = value # sets the key
print(db[key]) # prints `value` but the transaction is not commited yet
db.commit() # now other database transactions can see our changes
del db[key] # deletes the key
print(db[key]) # None, but other database transactions can still read it and get `value`
# Oh no what have I done!
db.rollback() # discards the transaction
print(db[key]) # prints `value`
```

# How It Works
## The ValueRef Class
a value in the database is represented in memory in one of two ways:
1. It's address in the database file. That is we don't know what the value is but we know that it's stored in the database and we know how to retrieve it.
2. The value itself. That is we know the value and may even know the address of the value in the database file.

Something to keep in mind is that the way a value is represented in memory represents it's status regarding whether it's commited to the database or not. More on this later.

## The Storage
The way the database file is structured is very simple.
Each write operation does three things:
1. Determine the address the data will be written to. The address is simply the file object's pointer.
2. write the length of the data in bytes to the file using a fixed width int (8 bytes).
3. write the data and return the address from step 1.

A read operation is the opposite; it takes an address and returns the data.
1. Seek to the address
2. read the length of the data (8 byte int)
3. read the data and return it

All that is left is some address to start from, and that is what the root block is. The root block is always stored at address 0 and contains an address (8 bytes int) to the root.
The storage itself doesn't care about what's stored in the root, it only provide it as a header.

## The Logical Layer and Database Operations
This is where all the action happens. The in memory representation of the key-value store is an immutable binary-tree, which it's nodes inherets the ValueRef class.
The node itself becomes the value of the NodeRef class and is only retrieved when needed. A node has a key, value_ref for the value associated with the key, left_ref, and right_ref members. All the *_ref members are ValueRef objects.

Getting, setting, and deleting a value is very straight forward. When a new value is added to the tree or updated, a new reference (NodeRef object) is created holding the new value in a new node.
A commit walks the tree and stores any reference with no address assigned to it.

# ACID
## Atomicity
The database transactions are atomic. A transaction is either successfully commited or not. No transaction can corrupt the database even if a failure happens while writing to disk.
This is ensured with two things:
1. Any write operation is done in a new unused address. No modification happens to the already stored values in the database file.
2. Root address (in the root block) is only modified after we guaranteed that all the values from a transaction are written and the new root is written too.

This way even if a failure happens, the root address in the root block still points to the old root (last successful transaction) and the old root and all the values it points to (directly or indirectly) are untouched.

## Consistency
The current implementation doesn't provide any consistency mechanics or constraints. But the user of the database (the programmer) can always inforce his own constraints.
Thus it's not of a high priority to implement consistency property.

## Isolation
Only one database write transaction can be executing at a time, though read operations can be performed during a transaction.
Thus the database implements a read commited isolation level in it's current implementation. A future addition will provide serializable isolation level.

## Durablity
A commited transaction is never lost. This is for the same reasons that this database provide atomicity.
