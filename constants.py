# constants.py

# global constants
PLAYER_X = 400.0
PLAYER_Y = 300.0
MOVE_SPEED = 7.0  # make sure defines MOVE_SPEED there
BULLET_SPEED = 9.5 # bullet speed (pixels/s)
BULLET_LIFETIME = 3000 # bullet lifetime (ms)
SHOOT_COOLDOWN = 250  # shoot cooldown (ms)
F_KEY_COOLDOWN = 15000  # F key cooldown (ms)
ENERGY_RECOVERY_RATE = 2  # energy recovery rate (energy/s)
GAME_OVER_DELAY = 1500  # game over delay (ms)
HALL_WIDTH = None
HALL_HEIGHT = None

# global variables
BULLETS = [] # list of bullets
LAST_SHOT_TIME = 0 # last time bullet was shot
LAST_F_KEY_TIME = 0 # last time F key was pressed