import os
import uuid

print(os.urandom(12).hex())
print(uuid.uuid4().hex)