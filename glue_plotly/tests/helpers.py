from functools import wraps
import pytest

try:
    import pytest_mpl  # noqa: F401
    import pytest_playwright  # noqa: F401
    HAS_VISUAL_TEST_DEPS = True
except:
    HAS_VISUAL_TEST_DEPS = False


def screenshot_when(page):
    screenshot = page.screenshot()
    return screenshot


class PngFigure:

    def __init__(self, png_bytes):
        self._png_bytes = png_bytes

    def savefig(self, filename_or_fileobj, *args, **kwargs):
        if isinstance(filename_or_fileobj, str):
            with open(filename_or_fileobj, 'wb') as f:
                f.write(self._png_bytes)
        else:
            filename_or_fileobj.write(self._png_bytes)


def html_screenshot_test(*args, **kwargs):

    tolerance = kwargs.get("tolerance", 0)

    def decorator(test_function):
        @pytest.mark.skipif("not HAS_VISUAL_TEST_DEPS")
        @pytest.mark.mpl_image_compare(
            tolerance=tolerance, **kwargs
        )
        @wraps(test_function)
        def test_wrapper(tmp_path, page, *args, **kwargs):
            path = test_function(tmp_path, page, *args, **kwargs)
            width = kwargs.get("width", 1280)
            height = kwargs.get("height", 720)
            page.set_viewport_size({"width": width, "height": height})
            page.goto(path)

            screenshot = page.screenshot()
            return PngFigure(screenshot)

        return test_wrapper

    # If the decorator was used without any arguments, the only positional
    # argument will be the test to decorate so we do the following:
    if len(args) == 1:
        return decorator(*args)

    return decorator
