class PrecedenceGraph:
    def __init__(self):
        self.groups = {}
        self.lower = {}
        self.higher = {}
        self.nodes = []
        self.members = {}
        
    def copy(self):
        new = PrecedenceGraph()
        new.groups = {name: set(members) for name, members in self.groups.items()}

        new.lower = {name: set(lows) for name, lows in self.lower.items()}
        new.higher = {name: set(highs) for name, highs in self.higher.items()}

        new.nodes = list(self.nodes)

        new.members = {name: set(members) for name, members in self.members.items()}

        return new

    
    def update(self, other):
        self.groups = {name: set(members) for name, members in other.groups.items()}

        self.lower = {name: set(lows) for name, lows in other.lower.items()}
        self.higher = {name: set(highs) for name, highs in other.higher.items()}

        new_nodes = []
        for node in other.nodes:
            if node not in self.nodes:
                new_nodes.append(node)
        self.nodes.extend(new_nodes)

        self.members.update({name: set(members) for name, members in other.members.items()})
        
    
    def group(self, name, low=None, high=None):
        if name not in self.groups:
            group = set()
            self.groups[name] = group
        else:
            group = self.groups[name]
        self.add_node(name)
        if low is not None: # group that is lower than me
            self.add_sub(name, low)
        if high is not None: # group that is higher than me
            self.add_dom(name, high)
            
    def add_sub(self, high, low):
        if high not in self.lower:
            self.lower[high] = set()
        self.lower[high].add(low)
        if low not in self.higher:
            self.higher[low] = set()
        self.higher[low].add(high)
    
    def add_dom(self, low, high):
        if high not in self.lower:
            self.lower[high] = set()
        self.lower[high].add(low)
        if low not in self.higher:
            self.higher[low] = set()
        self.higher[low].add(high)
        
    
    def add_node(self, group_name):
        if group_name not in self.nodes:
            self.nodes.append(group_name)
            
    def add_members(self, group, *members):
        for member in members:
            self.groups[group].add(member)
            
    def sort_group_names(self):
        order = []
        for group in self.nodes:
            pos = 0
            while pos < len(order):
                before = order[:pos]
                after = order[pos:]
                if any(lower in after for lower in self.lower.get(group, [])):
                    pos += 1
                    continue
                if any(higher in before for higher in self.higher.get(group, [])):
                    pos += 1
                    continue
                break
            order.insert(pos, group)
        
        return order
    
    def sort_groups(self):
        groups = []
        for name in self.sort_group_names():
            groups.append(self.groups[name])
        return list(reversed(groups))
        
        
                
        