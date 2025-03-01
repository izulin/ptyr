from __future__ import annotations
import pygame as pg



PLAYER_1_CONTROLS = dict(
    forward=pg.K_w,
    backward=pg.K_s,
    left_turn=pg.K_a,
    right_turn=pg.K_d,
    left_strafe=pg.K_q,
    right_strafe=pg.K_e,
    shoot=pg.K_x,
    secondary=pg.K_z,
)

PLAYER_2_CONTROLS = dict(
    forward=pg.K_i,
    backward=pg.K_k,
    left_turn=pg.K_j,
    right_turn=pg.K_l,
    left_strafe=pg.K_u,
    right_strafe=pg.K_o,
    shoot=pg.K_COMMA,
    secondary=pg.K_m,
)
