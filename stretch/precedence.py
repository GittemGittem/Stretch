class PrecedenceGraph:
    def __init__(self):
        self.lower = {}
        self.higher = {}
        self.nodes = []

    def add_operator(self, op):
        if op not in self.nodes:
            self.nodes.append(op)

    def add(self, operator, low=None, high=None):
        self.add_operator(operator)
        if low is not None:
            self.add_sub(operator, low)
        if high is not None:
            self.add_dom(operator, high)
    
    def add_dom(self, low, high):
        self.add_operator(low)
        self.add_operator(high)

        self.higher.setdefault(low, set()).add(high)
        self.lower.setdefault(high, set()).add(low)

    def add_sub(self, high, low):
        self.add_dom(low, high)

    def sort(self):
        order = []
        for op in self.nodes:
            pos = 0
            while pos < len(order):
                before = order[:pos]
                after = order[pos:]
                if any(l in after for l in self.lower.get(op, [])):
                    pos += 1
                    continue
                if any(h in before for h in self.higher.get(op, [])):
                    pos += 1
                    continue
                break
            order.insert(pos, op)
        return order
    
    def update(self, other): # Add all nodes
        for op in other.nodes:
            self.add_operator(op) # Add all dominance (low < high) relationships
        for low, highs in other.higher.items():
            for high in highs:
                self.add_dom(low, high)
        for high, lows in other.lower.items():
            for low in lows:
                self.add_sub(high, low)

    def copy(self):
        instance = PrecedenceGraph()
        instance.nodes = self.nodes[:]
        instance.lower = {symbol: set(lower) for symbol, lower in self.lower.items()}
        instance.higher = {symbol: set(higher) for symbol, higher in self.higher.items()}
        return instance
    