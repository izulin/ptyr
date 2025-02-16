from __future__ import annotations

from pygame.locals import *

PLAYER_1_CONTROLS = dict(
    forward=K_w,
    backward=K_s,
    left_turn=K_a,
    right_turn=K_d,
    left_strafe=K_q,
    right_strafe=K_e,
    shoot=K_x,
    secondary=K_z,
)

PLAYER_2_CONTROLS = dict(
    forward=K_i,
    backward=K_k,
    left_turn=K_j,
    right_turn=K_l,
    left_strafe=K_u,
    right_strafe=K_o,
    shoot=K_COMMA,
    secondary=K_m,
)
