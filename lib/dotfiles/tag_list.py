class TagList():
    def __init__(self):
        self._chosen_tags = []
        self._index = set()

    def add(self, tag):
        if not str(tag).strip() or tag in self:
            return
        self._chosen_tags.append(tag)
        self._index.add(str(tag).lower())

    def add_all(self, collection):
        for tag in collection:
            self.add(tag)

    def remove(self, tag):
        self._chosen_tags = [
            t for t in self._chosen_tags \
                if str(t).lower() != str(tag).lower()]
        self._index.remove(str(tag).lower())

    def remove_all(self, collection):
        for tag in collection:
            self.remove(tag)

    def __iter__(self):
        return self._chosen_tags.__iter__()

    def __len__(self):
        return len(self._chosen_tags)

    def __contains__(self, word):
        return str(word).lower() in self._index
