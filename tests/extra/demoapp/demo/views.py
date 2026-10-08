from django.http import HttpResponse


def flex_file(request, pk):
    """Stand in for the view a project serves file payloads from.

    The library only builds the URL; serving the bytes and deciding who may read
    them is left to the project, which is why this lives in the demo app.
    """
    return HttpResponse("payload of %s" % pk, content_type="text/plain")
