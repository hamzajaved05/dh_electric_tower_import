import os

class Line(object):
    def __init__(self, p1, p2):
        self.line = [p1, p2]
    
    def jsonify(self):
        return self.line

    def get_hash(self):
        hash = 0
        for p in self.line:
            for c in p:
                hash += 32 * c
        return hash

    def __repr__(self):
        return f"line from {self.line[0]} to {self.line[1]}"