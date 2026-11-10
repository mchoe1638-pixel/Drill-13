"""Pico2D 공 던지기 게임"""

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
ROW_IDLE_RIGHT = 3  # 서 있는 모습(오른쪽). 줄 번호는 맨 아랫줄이 0

# 프레임 끝에서 쉬는 시간(초)
FRAME_DELAY = 0.01


class Ground:
    """화면 아래쪽에 깔린 잔디 땅"""

    def __init__(self) -> None:
        self.image = load_image(GROUND_IMAGE)

    def draw(self) -> None:
        # 가로 중앙, 화면 맨 아래에 붙여서 그림
        self.image.draw(CANVAS_W // 2, self.image.h // 2)


class Player:
    """초록 모자를 쓴 플레이어"""

    def __init__(self) -> None:
        self.image = load_image(PLAYER_IMAGE)
        self.x = CANVAS_W // 2
        self.y = GROUND_Y  # 발바닥 위치

    def draw(self) -> None:
        # 서 있는 모습(오른쪽을 봄)의 첫 프레임
        left = SHEET_BORDER
        bottom = SHEET_BORDER + ROW_IDLE_RIGHT * SPRITE_SIZE
        center_y = self.y + SPRITE_SIZE // 2 - SPRITE_FOOT_GAP  # 발바닥 -> 칸 중심
        self.image.clip_draw(left, bottom, SPRITE_SIZE, SPRITE_SIZE, self.x, center_y)


# reset_world()에서 만드는 게임 객체
ground: Ground
player: Player


def handle_events() -> bool:
    """이벤트를 처리한다. 계속 실행하면 True, 종료하면 False"""
    for event in get_events():
        if event.type == SDL_QUIT:  # 창 닫기 버튼
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


def reset_world() -> None:
    """게임 객체를 만든다 (이미지를 읽어야 해서 open_canvas() 뒤에 호출)"""
    global ground, player
    ground = Ground()
    player = Player()


def update_world(dt: float) -> None:
    """모든 객체를 dt초만큼 갱신한다 (아직 움직이는 객체 없음)"""


def render_world() -> None:
    clear_canvas()  # 연한 회색 격자 배경까지 같이 그려짐
    ground.draw()
    player.draw()
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
