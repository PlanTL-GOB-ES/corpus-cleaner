class StringFilter:

    def filter(self, text: str) -> bool:
        raise NotImplementedError

    def __call__(self, text: str) -> bool:
        return self.filter(text)
