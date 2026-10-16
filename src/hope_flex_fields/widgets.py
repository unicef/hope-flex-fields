from typing import Any

from django import forms

from hope_flex_fields.references import flex_file_src


class FlexImageInput(forms.ClearableFileInput):
    """Render a file-typed flex field whose value is a reference, not a file.

    ``ClearableFileInput`` expects the initial value to be a ``FieldFile`` it can
    take a ``url`` from. Here it is a plain reference string, so both the test
    for an existing value and the preview URL go through the reference helpers.
    """

    template_name = "flex_fields/flex_image_widget.html"

    def is_initial(self, value: Any) -> bool:
        return bool(value)

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        context["widget"]["image_src"] = flex_file_src(value)
        return context


class Base64ImageInput(FlexImageInput):
    """Deprecated: superseded by :class:`FlexImageInput`, kept for one release.

    It inherits the new rendering, which already handles inline ``data:`` URIs, so
    that a project can swap the field type and migrate its data in either order.
    """


class JavascriptEditor(forms.Textarea):
    template_name = "flex_fields/editor.html"

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", "midnight")
        toolbar = kwargs.pop("toolbar", True)
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "js-editor"
        self.attrs["theme"] = theme
        self.attrs["toolbar"] = toolbar

    class Media:
        css = {
            "all": (
                "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/theme/midnight.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/display/fullscreen.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/fold/foldgutter.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/lint/lint.min.css",
                # "codemirror/codemirror.css",
                # "codemirror/fullscreen.css",
                # "codemirror/midnight.css",
                # "codemirror/foldgutter.css",
            )
        }
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/display/placeholder.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/edit/closebrackets.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/edit/trailingspace.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/fold/foldcode.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/fold/foldgutter.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/fold/brace-fold.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/fold/indent-fold.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/fold/indent-fold.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/hint/javascript-hint.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/lint/javascript-lint.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/mode/javascript/javascript.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/lint/lint.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/selection/active-line.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/addon/display/fullscreen.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/jshint/2.13.6/jshint.min.js",
            # "cm.js",
            # "codemirror/codemirror.js",
            # "codemirror/javascript.js",
            # "codemirror/fullscreen.js",
            # "codemirror/active-line.js",
            # "codemirror/foldcode.js",
            # "codemirror/foldgutter.js",
            # "codemirror/indent-fold.js",
        )
