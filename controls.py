from __future__ import annotations

import pygame as pg

PLAYER_1_CONTROLS = {
    "forward": pg.K_w,
    "backward": pg.K_s,
    "left_turn": pg.K_a,
    "right_turn": pg.K_d,
    "left_strafe": pg.K_q,
    "right_strafe": pg.K_e,
    "shoot": pg.K_x,
    "secondary": pg.K_z,
}

PLAYER_2_CONTROLS = {
    "forward": pg.K_t,
    "backward": pg.K_g,
    "left_turn": pg.K_f,
    "right_turn": pg.K_h,
    "left_strafe": pg.K_r,
    "right_strafe": pg.K_y,
    "shoot": pg.K_v,
    "secondary": pg.K_b,
}

PLAYER_3_CONTROLS = {
    "forward": pg.K_i,
    "backward": pg.K_k,
    "left_turn": pg.K_j,
    "right_turn": pg.K_l,
    "left_strafe": pg.K_u,
    "right_strafe": pg.K_o,
    "shoot": pg.K_COMMA,
    "secondary": pg.K_m,
}

PLAYER_4_CONTROLS = {
    "forward": pg.K_LEFTBRACKET,
    "backward": pg.K_QUOTE,
    "left_turn": pg.K_SEMICOLON,
    "right_turn": pg.K_BACKSLASH,
    "left_strafe": pg.K_p,
    "right_strafe": pg.K_RIGHTBRACKET,
    "shoot": pg.K_SLASH,
    "secondary": pg.K_RSHIFT,
}
