# Collections

Mamba provides ergonomic standard functions for working with complex data collections.

## Arrays

Arrays in Mamba represent ordered lists of items. The `arr` module provides core manipulation methods.

### Creating Arrays
```mamba
let fruits = ["Apple", "Banana"]
```

### Modifying Arrays
```mamba
# Appends item to array
arr.push(fruits, "Orange")

# Removes the last item from array
arr.pop(fruits)
```

### Reading Arrays
```mamba
# Checks if an item exists
let has_banana = arr.contains(fruits, "Banana")

# Formats array into a joined string
let joined = arr.join(fruits, " | ")
# Result: "Apple | Banana | Orange"
```

---

## HashMaps

HashMaps (Dictionaries) represent key-value pairs. The `map` module handles key operations.

### Creating HashMaps
```mamba
let user = {
    "name": "Alex",
    "age": 25
}
```

### Reading and Indexing
```mamba
# Direct access via key
let username = user["name"]

# Check if a key exists safely
if map.has(user, "name") {
    print("Name is present.")
}
```

### Modifying HashMaps
```mamba
# Removes a key from the map
map.remove(user, "temp_key")
```
