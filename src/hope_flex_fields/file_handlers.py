from django.core.files.uploadedfile import UploadedFile


def parse_xlsx(f: UploadedFile):
    import python_calamine

    workbook = python_calamine.CalamineWorkbook.from_filelike(f)  # type: ignore[arg-type]
    rows = iter(workbook.get_sheet_by_index(0).to_python())
    headers = list(map(str, next(rows)))
    for row in rows:
        yield dict(zip(headers, row))


HANDLERS = {".xlsx": parse_xlsx}
