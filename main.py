"""Pico2D 공 던지기 게임"""

import math

from pico2d import *

# 화면 크기
CANVAS_W = 800
CANVAS_H = 600

# 에셋 파일 이름
GROUND_IMAGE = "grass.png"
PLAYER_IMAGE = "animation_sheet.png"

# 땅 윗면 높이 (캐릭터의 발과 공이 닿는 곳)
GROUND_Y = 54

# 플레이어 스프라이트 시트: 100x100 칸, 가장자리에 투명 테두리 1px
SHEET_BORDER = 1
SPRITE_SIZE = 100
SPRITE_FOOT_GAP = 13  # 칸 바닥에서 발바닥까지 빈 공간
# 서 있는 모습이 들어 있는 줄 (줄 번호는 맨 아랫줄이 0)
ROW_IDLE_LEFT = 2
ROW_IDLE_RIGHT = 3
PRONE_LIFT = 15  # 눕힌 그림의 중심이 땅에서 떠 있어야 하는 높이

# 플레이어 이동
PLAYER_SPEED = 300  # 초당 이동 거리(픽셀)
PLAYER_HALF_W = 20  # 화면 밖으로 나가지 않게 하는 몸 반폭

# 공 크기 (Ball의 size 값)
BALL_SMALL = 1
BALL_BIG = 2
BALL_IMAGES = {BALL_SMALL: "ball21x21.png", BALL_BIG: "ball41x41.png"}
BALL_DIAMETER = {BALL_SMALL: 21, BALL_BIG: 41}  # 공 지름(픽셀)
BALL_SPEED = 400  # 던진 공의 가로 속도(픽셀/초)

# 공이 나가는 위치: 몸 중심에서 앞쪽으로 떨어진 거리, 땅에서 올라간 높이
THROW_FRONT_STAND = 35
THROW_HEIGHT_STAND = 45
THROW_FRONT_PRONE = 50
THROW_HEIGHT_PRONE = 22

# 프레임 끝에서 쉬는 시간(초)
FRAME_DELAY = 0.01


class Ground:
    """화면 아래쪽에 깔린 잔디 땅"""

    def __init__(self) -> None:
        self.image = load_image(GROUND_IMAGE)

    def draw(self) -> None:
        # 가로 중앙, 화면 맨 아래에 붙여서 그림
        self.image.draw(CANVAS_W // 2, self.image.h // 2)


class Ball:
    """축구공. size는 BALL_SMALL(작은 공) 또는 BALL_BIG(큰 공)"""

    images: dict[int, Image] = {}  # 크기별 이미지 (처음 필요할 때 한 번만 읽음)

    def __init__(self, x: float, y: float, vx: float, size: int) -> None:
        if size not in Ball.images:
            Ball.images[size] = load_image(BALL_IMAGES[size])
        self.image = Ball.images[size]
        self.x = x
        self.y = y
        self.vx = vx  # 가로 속도(픽셀/초)
        self.radius = BALL_DIAMETER[size] / 2

    def update(self, dt: float) -> None:
        self.x += self.vx * dt

    def is_off_screen(self) -> bool:
        return self.x + self.radius < 0 or self.x - self.radius > CANVAS_W

    def draw(self) -> None:
        self.image.draw(self.x, self.y)


class Player:
    """초록 모자를 쓴 플레이어"""

    def __init__(self) -> None:
        self.image = load_image(PLAYER_IMAGE)
        self.x = CANVAS_W // 2
        self.y = GROUND_Y  # 발바닥 위치
        self.face_dir = 1  # 바라보는 방향 (1: 오른쪽, -1: 왼쪽)
        self.is_prone = False  # 엎드려 있는가
        self.left_held = False  # 왼쪽 방향키를 누르고 있는가
        self.right_held = False  # 오른쪽 방향키를 누르고 있는가
        self.ball_size = BALL_SMALL  # 던질 공의 크기

    @property
    def held_dir(self) -> int:
        """눌려 있는 방향키가 가리키는 방향 (-1: 왼쪽, 0: 없음, 1: 오른쪽)"""
        if self.left_held and self.right_held:
            return self.face_dir  # 둘 다 누르면 나중에 누른 쪽
        return int(self.right_held) - int(self.left_held)

    @property
    def move_dir(self) -> int:
        """실제 이동 방향. 엎드려 있으면 움직이지 않는다"""
        return 0 if self.is_prone else self.held_dir

    def handle_event(self, event: Event) -> None:
        """방향키 눌림/뗌을 기록하고 바라보는 방향과 자세를 정한다"""
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        is_down = event.type == SDL_KEYDOWN
        if event.key == SDLK_LEFT:
            self.left_held = is_down
            if is_down:
                self.face_dir = -1
        elif event.key == SDLK_RIGHT:
            self.right_held = is_down
            if is_down:
                self.face_dir = 1
        elif event.key == SDLK_DOWN and is_down:
            self.is_prone = True  # 엎드림
        elif event.key == SDLK_UP and is_down:
            self.is_prone = False  # 다시 일어섬
        if self.held_dir != 0:  # 한쪽 키만 남아 있으면 그쪽을 바라봄
            self.face_dir = self.held_dir

    def throw_ball(self) -> Ball:
        """바라보는 방향으로 공을 던진다. 엎드려 있으면 더 낮은 곳에서 나간다"""
        if self.is_prone:
            front, height = THROW_FRONT_PRONE, THROW_HEIGHT_PRONE
        else:
            front, height = THROW_FRONT_STAND, THROW_HEIGHT_STAND
        x = self.x + self.face_dir * front
        y = self.y + height
        return Ball(x, y, self.face_dir * BALL_SPEED, self.ball_size)

    def update(self, dt: float) -> None:
        x = self.x + self.move_dir * PLAYER_SPEED * dt
        # 화면 밖으로 나가지 않게 막음
        self.x = max(PLAYER_HALF_W, min(x, CANVAS_W - PLAYER_HALF_W))

    def draw(self) -> None:
        # 서 있는 모습의 첫 프레임 (바라보는 방향에 맞는 줄)
        row = ROW_IDLE_RIGHT if self.face_dir > 0 else ROW_IDLE_LEFT
        bottom = SHEET_BORDER + row * SPRITE_SIZE
        clip = (SHEET_BORDER, bottom, SPRITE_SIZE, SPRITE_SIZE)  # 왼쪽, 아래, 너비, 높이
        if self.is_prone:
            # 90도 눕혀서 엎드린 모습으로 그림 (머리가 바라보는 쪽)
            angle = -self.face_dir * math.pi / 2
            y = self.y + PRONE_LIFT
            self.image.clip_composite_draw(
                *clip, angle, "", self.x, y, SPRITE_SIZE, SPRITE_SIZE
            )
        else:
            y = self.y + SPRITE_SIZE // 2 - SPRITE_FOOT_GAP  # 발바닥 -> 칸 중심
            self.image.clip_draw(*clip, self.x, y)


# reset_world()에서 만드는 게임 객체
ground: Ground
player: Player
balls: list[Ball]  # 지금 날아다니는 공들


def handle_events() -> bool:
    """이벤트를 처리한다. 계속 실행하면 True, 종료하면 False"""
    for event in get_events():
        if event.type == SDL_QUIT:  # 창 닫기 버튼
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_z:
            balls.append(player.throw_ball())
        player.handle_event(event)
    return True


def reset_world() -> None:
    """게임 객체를 만든다 (이미지를 읽어야 해서 open_canvas() 뒤에 호출)"""
    global ground, player, balls
    ground = Ground()
    player = Player()
    balls = []


def update_world(dt: float) -> None:
    """모든 객체를 dt초만큼 갱신한다"""
    global balls
    player.update(dt)
    for ball in balls:
        ball.update(dt)
    # 화면 밖으로 나간 공은 지움
    balls = [ball for ball in balls if not ball.is_off_screen()]


def render_world() -> None:
    clear_canvas()  # 연한 회색 격자 배경까지 같이 그려짐
    ground.draw()
    player.draw()
    for ball in balls:
        ball.draw()
    update_canvas()


def main() -> None:
    open_canvas(CANVAS_W, CANVAS_H)
    reset_world()

    running = True
    prev_time = get_time()
    while running:
        now = get_time()
        dt = now - prev_time  # 지난 프레임 이후 흐른 시간(초)
        prev_time = now

        running = handle_events()
        update_world(dt)
        render_world()
        delay(FRAME_DELAY)

    close_canvas()


if __name__ == "__main__":
    main()
