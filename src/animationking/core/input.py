"""
Terminal raw mode controller and non-blocking key reader.
Safely manages alternate screen buffer vs. native terminal mode,
disables line auto-wrap, and controls cursor visibility.
"""

import atexit
import os
import select
import shutil
import signal
import sys
import termios
import tty
from types import FrameType, TracebackType
from typing import Any, ClassVar

from animationking.core.config import AppConfig

KEY_UP = "KEY_UP"
KEY_DOWN = "KEY_DOWN"
KEY_LEFT = "KEY_LEFT"
KEY_RIGHT = "KEY_RIGHT"
KEY_PAGE_UP = "KEY_PAGE_UP"
KEY_PAGE_DOWN = "KEY_PAGE_DOWN"
KEY_HOME = "KEY_HOME"
KEY_END = "KEY_END"
KEY_ENTER = "KEY_ENTER"
KEY_SPACE = "KEY_SPACE"
KEY_ESC = "KEY_ESC"
KEY_BACKSPACE = "KEY_BACKSPACE"
KEY_TAB = "KEY_TAB"


class TerminalController:
    """Manages raw mode, altscreen vs. native terminal buffer, cursor visibility, and teardown."""

    _instance: ClassVar["TerminalController | None"] = None

    def __init__(self) -> None:
        self.orig_termios: list[Any] | None = None
        self.is_raw: bool = False
        self.in_altscreen: bool = False
        self.is_tty: bool = sys.stdin.isatty() and sys.stdout.isatty()
        self._buffer: bytearray = bytearray()

    @classmethod
    def get(cls) -> "TerminalController":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def enter(self, use_altscreen: bool | None = None) -> None:
        if use_altscreen is None:
            use_altscreen = AppConfig.get().altscreen
        else:
            AppConfig.get().altscreen = use_altscreen

        if not self.is_tty:
            return
        if self.is_raw:
            self.set_altscreen(use_altscreen)
            return

        try:
            self.orig_termios = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            self.is_raw = True

            if use_altscreen:
                sys.stdout.write("\033[?1049h\033[?25l\033[?7l\033[2J\033[H")
                self.in_altscreen = True
            else:
                # Native terminal buffer: keep in main screen buffer
                sys.stdout.write("\033[?25l\033[?7l\033[2J\033[H")
                self.in_altscreen = False
            sys.stdout.flush()

            atexit.register(self.restore)
            signal.signal(signal.SIGINT, self._sig_handler)
            signal.signal(signal.SIGTERM, self._sig_handler)
        except Exception:
            pass

    def set_altscreen(self, enabled: bool) -> None:
        """Dynamically switch between Alternate Screen Buffer and Native Terminal mode."""
        AppConfig.get().altscreen = enabled
        if not self.is_tty or not self.is_raw:
            return
        if enabled == self.in_altscreen:
            return
        try:
            if enabled:
                sys.stdout.write("\033[?1049h\033[?25l\033[?7l\033[2J\033[H")
                self.in_altscreen = True
            else:
                sys.stdout.write("\033[?1049l\033[?25l\033[?7l\033[2J\033[H")
                self.in_altscreen = False
            sys.stdout.flush()
        except Exception:
            pass

    def toggle_altscreen(self) -> bool:
        """Toggle between altscreen and native terminal buffer."""
        new_mode = not AppConfig.get().altscreen
        self.set_altscreen(new_mode)
        return new_mode

    def restore(self) -> None:
        if not self.is_raw:
            return
        try:
            if self.in_altscreen:
                # Re-enable auto-wrap, show cursor, restore main screen buffer, reset colors
                sys.stdout.write("\033[0m\033[?7h\033[?25h\033[?1049l")
            else:
                # Native terminal mode: place cursor at bottom row cleanly and restore attributes
                _, rows = shutil.get_terminal_size((80, 24))
                sys.stdout.write(f"\033[{rows};1H\033[0m\033[?7h\033[?25h\r\n")
            sys.stdout.flush()
            if self.orig_termios is not None and self.is_tty:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.orig_termios)
        except Exception:
            pass
        finally:
            self.is_raw = False
            self.in_altscreen = False
            self._buffer.clear()

    def _sig_handler(self, sig: int, frame: FrameType | None) -> None:
        self.restore()
        sys.exit(0)

    def read_key(self) -> str | None:
        """
        Non-blocking read of a single key press or arrow escape sequence.
        Reads raw bytes directly from the file descriptor without buffering issues.
        """
        if not self.is_tty or not self.is_raw:
            return None

        fd = sys.stdin.fileno()

        while True:
            rlist, _, _ = select.select([fd], [], [], 0)
            if not rlist:
                break
            try:
                chunk = os.read(fd, 64)
                if not chunk:
                    break
                self._buffer.extend(chunk)
            except OSError:
                break

        if not self._buffer:
            return None

        if self._buffer[0] == 0x1B:
            if len(self._buffer) == 1:
                rlist, _, _ = select.select([fd], [], [], 0.025)
                if rlist:
                    try:
                        chunk = os.read(fd, 64)
                        if chunk:
                            self._buffer.extend(chunk)
                    except OSError:
                        pass

            if len(self._buffer) == 1:
                self._buffer.pop(0)
                return KEY_ESC

            buf_bytes = bytes(self._buffer)

            if len(self._buffer) >= 3:
                seq3 = buf_bytes[:3]
                if seq3 in (b"\x1b[A", b"\x1bOA"):
                    del self._buffer[:3]
                    return KEY_UP
                if seq3 in (b"\x1b[B", b"\x1bOB"):
                    del self._buffer[:3]
                    return KEY_DOWN
                if seq3 in (b"\x1b[C", b"\x1bOC"):
                    del self._buffer[:3]
                    return KEY_RIGHT
                if seq3 in (b"\x1b[D", b"\x1bOD"):
                    del self._buffer[:3]
                    return KEY_LEFT
                if seq3 in (b"\x1b[H", b"\x1bOH"):
                    del self._buffer[:3]
                    return KEY_HOME
                if seq3 in (b"\x1b[F", b"\x1bOF"):
                    del self._buffer[:3]
                    return KEY_END

            if len(self._buffer) >= 4:
                seq4 = buf_bytes[:4]
                if seq4 == b"\x1b[5~":
                    del self._buffer[:4]
                    return KEY_PAGE_UP
                if seq4 == b"\x1b[6~":
                    del self._buffer[:4]
                    return KEY_PAGE_DOWN
                if seq4 == b"\x1b[1~":
                    del self._buffer[:4]
                    return KEY_HOME
                if seq4 == b"\x1b[4~":
                    del self._buffer[:4]
                    return KEY_END
                if seq4 == b"\x1b[3~":
                    del self._buffer[:4]
                    return KEY_BACKSPACE

            if len(self._buffer) >= 3 and self._buffer[1] in (ord("["), ord("O")):
                for idx in range(2, min(8, len(self._buffer))):
                    ch_code = self._buffer[idx]
                    if 0x40 <= ch_code <= 0x7E:
                        del self._buffer[: idx + 1]
                        if ch_code == ord("A"):
                            return KEY_UP
                        if ch_code == ord("B"):
                            return KEY_DOWN
                        if ch_code == ord("C"):
                            return KEY_RIGHT
                        if ch_code == ord("D"):
                            return KEY_LEFT
                        if ch_code == ord("H"):
                            return KEY_HOME
                        if ch_code == ord("F"):
                            return KEY_END
                        return KEY_ESC
                if len(self._buffer) < 8:
                    return None

            self._buffer.pop(0)
            return KEY_ESC

        b = self._buffer.pop(0)
        if b in (ord("\r"), ord("\n")):
            return KEY_ENTER
        if b == ord(" "):
            return KEY_SPACE
        if b in (0x7F, 0x08):
            return KEY_BACKSPACE
        if b == ord("\t"):
            return KEY_TAB
        if b == 0x03:  # Ctrl+C
            return "q"
        try:
            return chr(b)
        except Exception:
            return None


class TerminalSession:
    """Context manager for terminal setup and safe cleanup."""

    def __init__(self, use_altscreen: bool | None = None) -> None:
        self.use_altscreen = use_altscreen

    def __enter__(self) -> TerminalController:
        TerminalController.get().enter(self.use_altscreen)
        return TerminalController.get()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        TerminalController.get().restore()
