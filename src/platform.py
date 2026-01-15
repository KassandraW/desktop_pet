import win32gui

class Platform:
    def __init__(self, rect, kind, owner=None):
        self.rect = rect
        self.kind = kind # "window" - "pet" - "ground"
        self.owner = owner # hwnd or Pet or None

    def update(self):
        if self.kind == "window":
            try:
                l, t, r, _ = win32gui.GetWindowRect(self.owner)
                self.rect.update(l, t - 1, r - l, 2)
            except win32gui.error:
                return False  # window closed → platform invalid
        
        elif self.kind == "pet":
            pet = self.owner
            self.rect.update(
                pet.rect.left,
                pet.rect.top - 1,
                pet.rect.width,
                2
            )
        return True
