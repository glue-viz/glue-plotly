from functools import wraps

import pytest

try:
    import pytest_mpl  # noqa: F401
    import pytest_playwright  # noqa: F401
    HAS_VISUAL_TEST_DEPS = True
except ImportError:
    HAS_VISUAL_TEST_DEPS = False


class PngFigure:

    def __init__(self, png_bytes):
        self._png_bytes = png_bytes

    def savefig(self, filename_or_fileobj, *args, **kwargs):
        if isinstance(filename_or_fileobj, str):
            with open(filename_or_fileobj, "wb") as f:
                f.write(self._png_bytes)
        else:
            filename_or_fileobj.write(self._png_bytes)


def html_screenshot_test(*args, **kwargs):

    tolerance = kwargs.pop("tolerance", 0)
    wait = kwargs.pop("wait", 200)
    width = kwargs.pop("width", 1280)
    height = kwargs.pop("height", 720)

    def decorator(test_function):
        @pytest.mark.skipif("not HAS_VISUAL_TEST_DEPS")
        @pytest.mark.mpl_image_compare(
            tolerance=tolerance,
            deterministic=True,
            **kwargs
        )
        @wraps(test_function)
        def test_wrapper(tmp_path, page, *args, **kwargs):
            path = test_function(tmp_path, page, *args, **kwargs)
            page.set_viewport_size({"width": width, "height": height})
            page.goto(f"file:{path}")
            page.wait_for_timeout(wait)

            return PngFigure(page.screenshot())

        return test_wrapper

    # If the decorator was used without any arguments, the only positional
    # argument will be the test to decorate so we do the following:
    if len(args) == 1:
        return decorator(*args)

    return decorator
