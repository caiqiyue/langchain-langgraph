import uuid

memory_id = str(uuid.uuid4())
memory = {"user" : "你好，我叫木羽"}
in_memory_store.put(namespace_for_memory, memory_id,  memory)