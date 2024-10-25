from django import forms


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
