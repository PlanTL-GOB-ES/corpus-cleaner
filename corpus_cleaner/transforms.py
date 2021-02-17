class StringTransform:

    def transform(self, text: str) -> str:
        raise NotImplementedError

    def __call__(self, text: str) -> str:
        return self.transform(text)
