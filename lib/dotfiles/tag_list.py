class TagList():
    def __init__(self):
        self._chosen_tags = []

    def is_tagged(self, word):
        return word.lower() in [tag.lower() for tag in self._chosen_tags]

    def add(self, tag):
        tag = tag.strip()
        if not tag:
            return
        if self.is_tagged(tag):
            return
        self._chosen_tags.append(tag)

    def add_all(self, collection):
        for tag in collection:
            self.add(tag)

    def remove(self, word):
        self._chosen_tags = [
            tag for tag in self._chosen_tags if tag.lower() != word.lower()]

    def remove_all(self, collection):
        for tag in collection:
            self.remove(tag)

    def get(self):
        return self._chosen_tags

    def __len__(self):
        return len(self._chosen_tags)
