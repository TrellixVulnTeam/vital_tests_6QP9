import pathlib
str_fileAddres = "/Users/pankaj/abc.txt"
fileAddres = pathlib.Path(str_fileAddres)
fileAddres2 = pathlib.Path('D:/Pycharm Projects/spectra-synthesizer/src/specsiser/database/lines_data.xlsx')
print(1, fileAddres.suffix)
print(2, fileAddres.name)
print(3, fileAddres.parent)
print(4, fileAddres.parts)
print(5, pathlib.Path(str_fileAddres).with_suffix('.db'))
print(6, fileAddres2.is_file())
print(7, fileAddres2.parent.exists())
print(8, fileAddres.as_posix())
print(9, fileAddres.stem)

if False:
    pathlib.Path('/tmp/sub1/sub2').mkdir(parents=True, exist_ok=True)