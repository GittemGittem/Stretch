class Stack(list):
    def push(self, value):
        list.append(self, value)
    def pull(self, index=-1):
        return list.pop(self, index)
    def peek(self, index=-1):
        if abs(index) <= len(self):
            return self[index]
        return None
    def peek_if(self, type, index=-1):
        if isinstance(self.peek(index), type):
            return self[index]
        return None
    def pull_if(self, type = None):
        val = self.peek()
        if type is None:
            if len(self) > 0:
                self.pull()
            return val
        elif isinstance(val, type):
            self.pull()
            return val
        return None
    def pull_only(self, type):
        val = self.peek()
        if isinstance(val, type):
            self.pull()
            return val
        raise TypeError()
    def insert(self, value, index=0):
        list.insert(self, index, value)
    
    def __repr__(self):
        return f"[{", ".join([str(item) for item in self])}]"


class Group(tuple): pass
