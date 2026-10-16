import typing

if typing.TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile


def parse_xlsx(f: "UploadedFile"):
    import python_calamine  # noqa

    workbook = python_calamine.CalamineWorkbook.from_filelike(f)  # type: ignore[arg-type]
    rows = iter(workbook.get_sheet_by_index(0).to_python())
    headers = list(map(str, next(rows)))
    for row in rows:
        yield dict(zip(headers, row, strict=True))


HANDLERS = {".xlsx": parse_xlsx}
