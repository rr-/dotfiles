class TagList:
    def __init__(self):
        self._chosen_tags = []
        self._index = {}

    def add(self, tag):
        if not str(tag).strip() or tag in self:
            return
        self._chosen_tags.append(tag)
        self._index[str(tag).lower()] = tag

    def add_all(self, collection):
        for tag in collection:
            self.add(tag)

    def remove(self, tag):
        self._chosen_tags = [
            other_tag
            for other_tag in self._chosen_tags
            if str(other_tag).lower() != str(tag).lower()]
        del self._index[str(tag).lower()]

    def remove_all(self, collection):
        for tag in collection:
            self.remove(tag)

    def __getitem__(self, tag):
        return self._index.get(str(tag).lower(), None)

    def __iter__(self):
        return self._chosen_tags.__iter__()

    def __len__(self):
        return len(self._chosen_tags)

    def __contains__(self, tag):
        return str(tag).lower() in self._index
