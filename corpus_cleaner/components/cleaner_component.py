from corpus_cleaner.cleaner import GlobalConfig


class CleanerComponent:
    pass


class LegacyCleanerComponent:

    def __init__(self, config: GlobalConfig):
        self.debug = config.debug