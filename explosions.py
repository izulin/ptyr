from assets import LargeExplosion1, LargeExplosion2
from groups import ALL_EXPLOSIONS
from objects import AnimatedDrawable, NoControl, HasTimer, MovingObject


class PlayerExplosion(AnimatedDrawable, HasTimer, NoControl, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    TTL = 1000
    IMAGE = (LargeExplosion1, LargeExplosion2)

    def __init__(self, *args, **kwargs):
        super().__init__(ALL_EXPLOSIONS, *args, **kwargs)
        assert self.ttl == self._image.animation_time


class MineExplosion(AnimatedDrawable, HasTimer, NoControl, MovingObject):
    DRAG = 0.0
    ANGULAR_DRAG = 0.0

    TTL = 1000
    IMAGE = (LargeExplosion1.scale_by(2), LargeExplosion2.scale_by(2))

    def __init__(self, *args, **kwargs):
        super().__init__(ALL_EXPLOSIONS, *args, **kwargs)
        assert self.ttl == self._image.animation_time
