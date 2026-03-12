class PrecedenceGraph:
    __slots__ = ("order", "groups")
    def __init__(self):
        self.order = []
        self.groups = {}
    
    
    def update(self, other):
        for group in other.groups:
            if group not in self.groups:
                self.groups[group] = set(other.groups[group])
        
        
        for name in other.order:
            if name not in self.order:
                self.order.append(name)
            else:
                self.order.remove(name)
                idx = other.order.index(name)
                if idx == 0:
                    self.order.insert(0, name)
                else:
                    prev = other.order[idx - 1]
                    if prev in self.order:
                        pos = self.order.index(prev) + 1
                    else:
                        pos = len(self.order)
                    self.order.insert(pos, name)
    
    def set_group(self, name, low = None):
        if name in self.order:
            self.order.remove(name)
        if low is None:
            self.order.append(name)
        else:
            index = self.order.index(low)
            self.order.insert(index, name)
        if name not in self.groups:
            self.groups[name] = set()
    def add_member(self, group_name, symbol):
        self.groups[group_name].add(symbol)
        
    
    def __iter__(self):
        for group in self.order:
            yield self.groups[group]

