from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int

    def before(self, other: "Position") -> bool:
        if self.y == other.y:
            return self.x < other.x
        return self.y < other.y


@dataclass
class HighlightedZone:
    start: Position = None
    end: Position = None

    def clear(self):
        self.start = None
        self.end = None

    def empty(self):
        return self.start is None
