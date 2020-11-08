class Game:
    def left(self, fromIndex):
        return fromIndex - 1 if fromIndex > 0 else fromIndex
    def right(self, fromIndex):
        return fromIndex + 1 if (fromIndex + 1) % self.face > 0 else fromIndex
    def up(self, fromIndex):
        return fromIndex - self.face if fromIndex - self.face > 0 else fromIndex
    def down(self, fromIndex):
        return fromIndex + self.face if fromIndex < self.face * self.face else fromIndex
