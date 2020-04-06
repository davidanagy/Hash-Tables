# '''
# Linked List hash table key/value pair
# '''
class LinkedPair:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class HashTable:
    '''
    A hash table that with `capacity` buckets
    that accepts string keys
    '''
    def __init__(self, capacity, max_load=0.7, min_load=0.2):
        self.capacity = capacity  # Number of buckets in the hash table
        self.storage = [None] * capacity
        self.size = 0 # Number of keys total; need this to calculate the load factor
        self.was_resized = False # Change to true after resizing once
        self.max_load = max_load # Maximum load factor allowed
        self.min_load = min_load # Minimum load factor allowed


    def _hash(self, key):
        '''
        Hash an arbitrary key and return an integer.

        You may replace the Python hash with DJB2 as a stretch goal.
        '''
        return hash(key)


    def _hash_djb2(self, key):
        '''
        Hash an arbitrary key using DJB2 hash

        OPTIONAL STRETCH: Research and implement DJB2
        '''
        # Consulted this source: http://www.cse.yorku.ca/~oz/hash.html
        # as well as the code Grant wrote in class.
        # The site is confusing because it has both "33 ^ str[i]" and
        # "33 + c", but further researched showed the latter seems to be correct.
        if type(key) is str:
            bytes_key = key.encode()
            hash_value = 5381
            for char in bytes_key:
                hash_value = hash_value * 33 + char
            return hash_value
        # If the key is an int, just return it
        elif type(key) is int:
            return key
        # If the key is a float, convert to an int
        elif type(key) is float:
            return int(key)
        else:
            raise ValueError('Key must be a string, int, or float')


    def _hash_mod(self, key):
        '''
        Take an arbitrary key and return a valid integer index
        within the storage capacity of the hash table.
        '''
        return self._hash_djb2(key) % self.capacity


    def insert(self, key, value, auto_resize=True):
        '''
        Store the value with the given key.

        # Part 1: Hash collisions should be handled with an error warning. (Think about and
        # investigate the impact this will have on the tests)

        # Part 2: Change this so that hash collisions are handled with Linked List Chaining.

        Fill this in.
        '''
        # Get the proper index number in storage by using the hash_mod method
        index = self._hash_mod(key)
        # If there isn't a linked list at the proper location,
        # create a new one and put it into storage.
        if not self.storage[index]:
            new_node = LinkedPair(key, value)
            self.storage[index] = new_node
        else:
            # Otherwise, loop through all the nodes in the linked list
            # to look for one that matches the key.
            node = self.storage[index]
            value_set = False
            while node:
                # Define "prev_node". This will be used if we end up
                # adding a new node.
                prev_node = node
                if key == node.key:
                    # If you find a match, replace its value with the new one.
                    node.value = value
                    # Define "value_set" as True because we successfully set the value.
                    value_set = True
                    break
                else:
                    # If the current node isn't a match, do the same
                    # for the next node.
                    node = node.next
            if not value_set:
                # If value_set is False, that means that the key didn't
                # already exist. So make a new node and add it after the last
                # one in the current chain.
                # Because we only define prev_node when we do an iteration, that means
                # that once "node" ends up as "None", the above loop will end and
                # "prev_node" will be the last existing node in the chain.
                new_node = LinkedPair(key, value)
                prev_node.next = new_node

        # Increase size by one
        self.size += 1
        # Run the auto_resize method if the "auto_resize" argument is True.
        # (See the "resize" or "halve_capacity" methods below to see why
        # this is necessary.)
        if auto_resize:
            self.auto_resize()


    def remove(self, key):
        '''
        Remove the value stored with the given key.

        Print a warning if the key is not found.

        Fill this in.
        '''
        # Find the proper index number and the node that matches it.
        index = self._hash_mod(key)
        node = self.storage[index]
        # Pre-define prev_node and key_found.
        prev_node = None
        key_found = False
        # Run the loop while "node" is not None.
        while node:
            if node.key == key:
                # If we find the key,
                if not prev_node:
                    # and if the key was in the first node
                    # in the linked list,
                    # then delete the first node while
                    # keeping all the others.
                    self.storage[index] = node.next
                else:
                    # Otherwise, if the key is not in the first node,
                    # remove it from the list while keeping
                    # all the other nodes.
                    prev_node.next = node.next
                key_found = True
                break
            else:
                # Otherwise, continue looping through the chain.
                prev_node = node
                node = node.next
        if not key_found:
            # If we didn't find the key, raise an error.
            raise KeyError('key not found')
        else:
            # If we found the key, reduce the size by one and auto-resize.
            self.size -= 1
            self.auto_resize()


    def retrieve(self, key):
        '''
        Retrieve the value stored with the given key.

        Returns None if the key is not found.

        Fill this in.
        '''
        # Similar logic to the delete method above.
        index = self._hash_mod(key)
        node = self.storage[index]
        key_found = False
        while node:
            if node.key == key:
                key_found = True
                return node.value
            else:
                node = node.next
        if not key_found:
            return None


    def resize(self):
        '''
        Doubles the capacity of the hash table and
        rehash all key/value pairs.

        Fill this in.
        '''
        self.capacity *= 2
        # Set size to 0, since we'll be starting out with an empty storage
        # and adding the old key/value pairs in one by one.
        self.size = 0
        old_storage = self.storage
        self.storage = [None] * self.capacity
        for i in range(len(old_storage)):
            node = old_storage[i]
            while node:
                # Insert each key/value pair into the new storage individually.
                # But we want to avoid auto-resizing until after we finish copying
                # over all the nodes, so set the auto_resize argument to be False.
                self.insert(node.key, node.value, auto_resize=False)
                node = node.next
        # The instructions say to only auto-resize after it's been resized once.
        # So once we resize, set the "was_resized" property to True.
        self.was_resized = True
        # Continue resizing until the load factor is within the requested range.
        self.auto_resize()


    def halve_capacity(self):
        '''
        Halves the capacity of the hash table and
        rehash all key/value pairs.
        '''
        # Same as the above; we just halve the capacity instead.
        # (Use floor division to ensure the result remains an integer.)
        self.capacity = self.capacity // 2
        self.size = 0
        old_storage = self.storage
        self.storage = [None] * self.capacity
        for i in range(len(old_storage)):
            node = old_storage[i]
            while node:
                self.insert(node.key, node.value, auto_resize=False)
                node = node.next
        self.auto_resize()


    def auto_resize(self):
        '''
        Double capacity when the load factor is above max_load;
        halve capacity when the load factor is below min_load.
        '''
        # I used this to learn about load factors:
        # https://www.geeksforgeeks.org/load-factor-and-rehashing/
        # The commented-out print statements were used for error-checking.
        if self.was_resized:
            load_factor = self.size / self.capacity
            #print(f'size: {self.size}, capacity: {self.capacity}')
            #print(f'load factor: {load_factor}')
            if load_factor > self.max_load:
                #print('Double capacity')
                self.resize()
            elif load_factor < self.min_load:
                if self.capacity > 1:
                    #print('Halve capacity')
                    self.halve_capacity()
                else:
                    # If the capacity is at 1, halving it will give us 0.
                    # That's bad, so let's keep it at 1.
                    pass
                    #print('Capacity at minimum')


if __name__ == "__main__":
    ht = HashTable(2)

    ht.insert("line_1", "Tiny hash table")
    ht.insert("line_2", "Filled beyond capacity")
    ht.insert("line_3", "Linked list saves the day!")

    print("")

    # Test storing beyond capacity
    print(ht.retrieve("line_1"))
    print(ht.retrieve("line_2"))
    print(ht.retrieve("line_3"))

    # Test resizing
    old_capacity = len(ht.storage)
    ht.resize()
    new_capacity = len(ht.storage)

    print(f"\nResized from {old_capacity} to {new_capacity}.\n")

    # Test if data intact after resizing
    print(ht.retrieve("line_1"))
    print(ht.retrieve("line_2"))
    print(ht.retrieve("line_3"))

    print("")
