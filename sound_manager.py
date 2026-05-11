"""
sound_manager.py - Hệ thống quản lý âm thanh cho PathFinder TD
================================================================
Môn   : IT003 - Cấu trúc dữ liệu và Giải thuật
Trường: Đại học Công nghệ Thông tin (UIT)

Mô tả:
    Module này tạo và quản lý toàn bộ hiệu ứng âm thanh (SFX) cho game.
    Tất cả âm thanh được **tổng hợp bằng code** (synthesize) sử dụng
    numpy sine/square waves, KHÔNG cần file .wav/.mp3 bên ngoài.

    Pygame.mixer được dùng để phát âm thanh real-time.

Cách dùng:
    import sound_manager
    sound_manager.init()          # Gọi sau pygame.init()
    sound_manager.play_shoot('archer')
    sound_manager.play_enemy_death()
"""

import math
import numpy as np
import pygame

# ─── Trạng thái module ─────────────────────────────────────────────
_initialized = False
_sounds: dict[str, pygame.mixer.Sound] = {}
_volume = 0.5
_muted = False


# ─── Hàm tổng hợp âm thanh ────────────────────────────────────────

def _make_sound(samples_array):
    """
    Chuyển numpy array (float64, mono, giá trị -1..1) thành pygame.mixer.Sound.

    Tham số:
        samples_array (np.ndarray): Mảng mẫu âm thanh float64, giá trị trong [-1, 1].

    Trả về:
        pygame.mixer.Sound: Đối tượng Sound có thể phát.
    """
    samples_16 = np.clip(samples_array * 32767, -32768, 32767).astype(np.int16)
    stereo = np.column_stack((samples_16, samples_16))
    return pygame.mixer.Sound(buffer=stereo.tobytes())


def _sine(freq, duration, sample_rate=44100):
    """
    Tạo sóng sine đơn giản.

    Tham số:
        freq        (float): Tần số (Hz).
        duration    (float): Thời lượng (giây).
        sample_rate (int)  : Tần số lấy mẫu (mặc định 44100).

    Trả về:
        np.ndarray: Mảng mẫu float64 trong [-1, 1].
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * math.pi * freq * t)


def _square(freq, duration, sample_rate=44100):
    """
    Tạo sóng vuông (square wave).

    Tham số:
        freq        (float): Tần số (Hz).
        duration    (float): Thời lượng (giây).
        sample_rate (int)  : Tần số lấy mẫu.

    Trả về:
        np.ndarray: Mảng mẫu float64 trong [-1, 1].
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sign(np.sin(2 * math.pi * freq * t))


def _noise(duration, sample_rate=44100):
    """
    Tạo nhiễu trắng (white noise).

    Tham số:
        duration    (float): Thời lượng (giây).
        sample_rate (int)  : Tần số lấy mẫu.

    Trả về:
        np.ndarray: Mảng mẫu float64 trong [-1, 1].
    """
    return np.random.uniform(-1, 1, int(sample_rate * duration))


def _envelope(samples, attack=0.01, decay=0.05, sustain_level=0.7, release=0.1):
    """
    Áp dụng đường bao ADSR (Attack-Decay-Sustain-Release) lên tín hiệu.

    Giúp âm thanh tự nhiên hơn bằng cách thay đổi biên độ theo thời gian.

    Tham số:
        samples       (np.ndarray): Mảng mẫu âm thanh.
        attack        (float)     : Thời gian tăng biên độ (giây).
        decay         (float)     : Thời gian giảm xuống sustain (giây).
        sustain_level (float)     : Mức biên độ duy trì (0–1).
        release       (float)     : Thời gian tắt dần (giây).

    Trả về:
        np.ndarray: Mảng mẫu đã áp dụng envelope.
    """
    n = len(samples)
    sr = 44100
    env = np.ones(n)

    a_samples = int(attack * sr)
    d_samples = int(decay * sr)
    r_samples = int(release * sr)

    a_samples = min(a_samples, n)
    if a_samples > 0:
        env[:a_samples] = np.linspace(0, 1, a_samples)

    d_end = min(a_samples + d_samples, n)
    if d_samples > 0 and a_samples < n:
        env[a_samples:d_end] = np.linspace(1, sustain_level,
                                           d_end - a_samples)

    if d_end < n:
        env[d_end:max(n - r_samples, d_end)] = sustain_level

    r_start = max(n - r_samples, 0)
    if r_samples > 0 and r_start < n:
        env[r_start:] = np.linspace(env[r_start] if r_start > 0 else sustain_level,
                                    0, n - r_start)

    return samples * env


def _fade_out(samples, fade_time=0.05):
    """
    Áp dụng fade-out cuối tín hiệu.

    Tham số:
        samples   (np.ndarray): Mảng mẫu.
        fade_time (float)     : Thời gian fade (giây).

    Trả về:
        np.ndarray: Mảng mẫu đã fade.
    """
    n = len(samples)
    fade_samples = int(44100 * fade_time)
    fade_samples = min(fade_samples, n)
    if fade_samples > 0:
        samples[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    return samples


# ─── Tạo từng loại SFX ────────────────────────────────────────────

def _synth_shoot_archer():
    """Tổng hợp âm thanh bắn cung – tiếng 'twang' ngắn cao."""
    s = _sine(880, 0.08) * 0.3 + _sine(1320, 0.08) * 0.2
    s += _noise(0.08) * 0.05
    return _make_sound(_envelope(s, attack=0.002, decay=0.03,
                                 sustain_level=0.1, release=0.04))


def _synth_shoot_cannon():
    """Tổng hợp âm thanh bắn pháo – tiếng 'boom' trầm."""
    boom = _sine(80, 0.2) * 0.5 + _sine(40, 0.2) * 0.3
    boom += _noise(0.2) * 0.15
    return _make_sound(_envelope(boom, attack=0.005, decay=0.08,
                                 sustain_level=0.15, release=0.1))


def _synth_shoot_mage():
    """Tổng hợp âm thanh phép thuật – tiếng 'shimmer' ma thuật."""
    t = np.linspace(0, 0.15, int(44100 * 0.15), endpoint=False)
    freq_sweep = 600 + 800 * t / 0.15
    s = np.sin(2 * math.pi * freq_sweep * t) * 0.3
    s += _sine(1200, 0.15) * 0.15
    s += _noise(0.15) * 0.03
    return _make_sound(_envelope(s, attack=0.01, decay=0.05,
                                 sustain_level=0.2, release=0.08))


def _synth_enemy_hit():
    """Tổng hợp âm thanh quái bị trúng đạn – tiếng 'thud' nhẹ."""
    s = _sine(300, 0.06) * 0.3 + _noise(0.06) * 0.1
    return _make_sound(_envelope(s, attack=0.002, decay=0.02,
                                 sustain_level=0.05, release=0.03))


def _synth_enemy_death():
    """Tổng hợp âm thanh quái chết – tiếng nổ nhỏ."""
    s = _sine(200, 0.15) * 0.25 + _sine(100, 0.15) * 0.2
    s += _noise(0.15) * 0.15
    return _make_sound(_envelope(s, attack=0.005, decay=0.06,
                                 sustain_level=0.1, release=0.08))


def _synth_base_hit():
    """Tổng hợp âm thanh quái chạm căn cứ – cảnh báo nguy hiểm."""
    s = _sine(180, 0.3) * 0.3 + _square(90, 0.3) * 0.15
    s += _noise(0.3) * 0.08
    return _make_sound(_envelope(s, attack=0.01, decay=0.1,
                                 sustain_level=0.15, release=0.15))


def _synth_build():
    """Tổng hợp âm thanh xây tháp – tiếng 'clink' xây dựng."""
    s = _sine(523, 0.05) * 0.25
    s2 = _sine(659, 0.05) * 0.25
    s3 = _sine(784, 0.05) * 0.25
    combined = np.concatenate([s, s2, s3])
    return _make_sound(_envelope(combined, attack=0.005, decay=0.03,
                                  sustain_level=0.15, release=0.05))


def _synth_sell():
    """Tổng hợp âm thanh bán tháp – tiếng coin drop."""
    s = _sine(784, 0.04) * 0.2
    s2 = _sine(523, 0.06) * 0.2
    combined = np.concatenate([s, s2])
    return _make_sound(_envelope(combined, attack=0.005, decay=0.02,
                                  sustain_level=0.1, release=0.04))


def _synth_wave_start():
    """Tổng hợp âm thanh bắt đầu wave – tiếng kèn ngắn."""
    notes = [523, 659, 784]
    parts = []
    for f in notes:
        parts.append(_envelope(_sine(f, 0.1) * 0.25,
                                attack=0.005, decay=0.03,
                                sustain_level=0.15, release=0.04))
    return _make_sound(np.concatenate(parts))


def _synth_wave_complete():
    """Tổng hợp âm thanh hoàn thành wave – fanfare ngắn."""
    notes = [523, 659, 784, 1047]
    parts = []
    for f in notes:
        parts.append(_envelope(_sine(f, 0.12) * 0.2,
                                attack=0.01, decay=0.04,
                                sustain_level=0.1, release=0.06))
    return _make_sound(np.concatenate(parts))


def _synth_button_click():
    """Tổng hợp âm thanh click button – 'tick' nhẹ."""
    s = _sine(1000, 0.03) * 0.15 + _noise(0.03) * 0.03
    return _make_sound(_fade_out(s, 0.01))


def _synth_victory():
    """Tổng hợp nhạc chiến thắng – melody vui vẻ."""
    melody = [523, 587, 659, 784, 1047, 1047, 784, 1047]
    parts = []
    for f in melody:
        part = _sine(f, 0.15) * 0.2 + _sine(f * 2, 0.15) * 0.05
        parts.append(_envelope(part, attack=0.01, decay=0.04,
                                sustain_level=0.12, release=0.06))
    return _make_sound(np.concatenate(parts))


def _synth_game_over():
    """Tổng hợp nhạc thua cuộc – melody buồn giảm dần."""
    melody = [392, 349, 330, 262]
    parts = []
    for i, f in enumerate(melody):
        dur = 0.2 + i * 0.05
        part = _sine(f, dur) * (0.2 - i * 0.03)
        parts.append(_envelope(part, attack=0.01, decay=0.08,
                                sustain_level=0.1, release=0.1))
    return _make_sound(np.concatenate(parts))


def _synth_no_gold():
    """Tổng hợp âm thanh không đủ vàng – buzzer ngắn."""
    s = _square(200, 0.1) * 0.12
    return _make_sound(_envelope(s, attack=0.005, decay=0.04,
                                  sustain_level=0.06, release=0.05))


# ─── API công khai ─────────────────────────────────────────────────

def init():
    """
    Khởi tạo hệ thống âm thanh.

    **Phải gọi sau pygame.init() và pygame.mixer.init().**

    Tạo tất cả sound effects bằng cách tổng hợp (synthesize)
    sóng sine, sóng vuông, và nhiễu trắng.
    """
    global _initialized, _sounds

    if _initialized:
        return

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    except pygame.error:
        print("[SoundManager] Không thể khởi tạo mixer – tắt âm thanh")
        _initialized = True
        return

    _sounds['shoot_archer'] = _synth_shoot_archer()
    _sounds['shoot_cannon'] = _synth_shoot_cannon()
    _sounds['shoot_mage']   = _synth_shoot_mage()
    _sounds['enemy_hit']    = _synth_enemy_hit()
    _sounds['enemy_death']  = _synth_enemy_death()
    _sounds['base_hit']     = _synth_base_hit()
    _sounds['build']        = _synth_build()
    _sounds['sell']         = _synth_sell()
    _sounds['wave_start']   = _synth_wave_start()
    _sounds['wave_complete'] = _synth_wave_complete()
    _sounds['button_click'] = _synth_button_click()
    _sounds['victory']      = _synth_victory()
    _sounds['game_over']    = _synth_game_over()
    _sounds['no_gold']      = _synth_no_gold()

    set_volume(_volume)

    _initialized = True
    print(f"[SoundManager] Đã tổng hợp {len(_sounds)} hiệu ứng âm thanh")


def _play(name):
    """
    Phát âm thanh theo tên.

    Tham số:
        name (str): Tên key trong dict _sounds.
    """
    if _muted or not _initialized:
        return
    sound = _sounds.get(name)
    if sound:
        sound.play()


def play_shoot(tower_type='archer'):
    """
    Phát âm thanh bắn theo loại tháp.

    Tham số:
        tower_type (str): 'archer', 'cannon', hoặc 'mage'.
    """
    _play(f'shoot_{tower_type}')


def play_enemy_hit():
    """Phát âm thanh quái bị trúng đạn."""
    _play('enemy_hit')


def play_enemy_death():
    """Phát âm thanh quái chết."""
    _play('enemy_death')


def play_base_hit():
    """Phát âm thanh quái chạm căn cứ."""
    _play('base_hit')


def play_build():
    """Phát âm thanh xây tháp thành công."""
    _play('build')


def play_sell():
    """Phát âm thanh bán tháp."""
    _play('sell')


def play_wave_start():
    """Phát âm thanh bắt đầu wave mới."""
    _play('wave_start')


def play_wave_complete():
    """Phát âm thanh hoàn thành wave."""
    _play('wave_complete')


def play_button_click():
    """Phát âm thanh click nút bấm."""
    _play('button_click')


def play_victory():
    """Phát nhạc chiến thắng."""
    _play('victory')


def play_game_over():
    """Phát nhạc thua cuộc."""
    _play('game_over')


def play_no_gold():
    """Phát âm thanh không đủ vàng."""
    _play('no_gold')


def set_volume(level):
    """
    Đặt âm lượng cho tất cả sound effects.

    Tham số:
        level (float): Mức âm lượng từ 0.0 (tắt) đến 1.0 (tối đa).
    """
    global _volume
    _volume = max(0.0, min(1.0, level))
    for sound in _sounds.values():
        sound.set_volume(_volume)


def toggle_mute():
    """
    Bật/tắt âm thanh.

    Trả về:
        bool: True nếu đang tắt tiếng (muted).
    """
    global _muted
    _muted = not _muted
    return _muted


def is_muted():
    """
    Kiểm tra trạng thái tắt tiếng.

    Trả về:
        bool: True nếu đang tắt tiếng.
    """
    return _muted
