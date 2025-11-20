from kivy.uix.image import Image

class ProportionalImage(Image):
    def __init__(self, source, fixed_height=50, **kwargs):
        super().__init__(source=source, allow_stretch=True, keep_ratio=True, **kwargs)
        self.fixed_height = fixed_height
        self.size_hint_y = None
        self.height = fixed_height
        self.size_hint_x = None
        self.width = fixed_height  # valor temporal
        self.bind(texture=self._update_width)

    def _update_width(self, *args):
        if self.texture and self.texture.size[1] > 0:
            iw, ih = self.texture.size
            self.width = iw * (self.fixed_height / ih)
