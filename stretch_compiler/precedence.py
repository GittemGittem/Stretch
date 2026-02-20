class PrecedenceGraph:
    def __init__(self):
        self.lower = {}
        self.higher = {}
        self.nodes = set()

    def add_operator(self, op):
        self.nodes.add(op)

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
        incoming = {operator: len(self.lower.get(operator, [])) for operator in self.nodes}
        queue = [operator for operator in self.nodes if incoming[operator] == 0]
        result = []

        while queue:
            operator = queue.pop()
            result.append(operator)

            for higher in self.higher.get(operator, []):
                incoming[higher] -= 1
                if incoming[higher] == 0:
                    queue.append(higher)
        return result