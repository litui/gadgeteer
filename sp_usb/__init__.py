class GadgetManager:
    def __init__(self) -> None:

        pass

    @property
    def active(self):
        if self._active:
            return self._active.type_name
        return None

    @active.setter
    def active(self, type):
        pass
