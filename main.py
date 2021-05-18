import os
import re
import glob
import shutil
from PIL import Image

in_dir = os.path.normpath('img/**/*')
dirname = os.path.dirname(__file__)
error_dir = "error"

def splitfn(fn):
    path, fn = os.path.split(fn)
    name, ext = os.path.splitext(fn)
    return path, name, ext

def get_concat_resize_h(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif (((im1.height > im2.height) and resize_big_image) or
          ((im1.height < im2.height) and not resize_big_image)):
        _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height), resample=resample)
    im = Image.new('RGB', (_im1.width + _im2.width, _im1.height))
    im.paste(_im1, (0, 0))
    im.paste(_im2, (_im1.width, 0))
    return im

def get_concat_resize_v(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.width == im2.width:
        _im1 = im1
        _im2 = im2
    elif (((im1.width > im2.width) and resize_big_image) or
          ((im1.width < im2.width) and not resize_big_image)):
        _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((im1.width, int(im2.height * im1.width / im2.width)), resample=resample)
    im = Image.new('RGB', (_im1.width, _im1.height + _im2.height))
    im.paste(_im1, (0, 0))
    im.paste(_im2, (0, _im1.height))
    return im

def validate_file(file):
    pattern = re.compile('(_front)|(front)|(_back)|(back)')
    if not pattern.findall(file):
        shutil.move(file, error_dir)
    return file

def main():
    file_list = {}
    for file in glob.iglob(in_dir, recursive=True):
        validate_file(file)
        path, fname, ext = splitfn(file)

        #TODO: @fer IndexError: list index out of range
        parts = fname.split('_')
        item = dict(
            base = parts[0],
            ftype = parts[1],
            ext = ext,
            loc = file
        )

        if parts[0] in file_list.keys():
            file_list[parts[0]].append(item)
        else:
            file_list[parts[0]] = [item]

    for item in file_list.values():
        if item[0]['base'] == item[1]['base']:
            i1 = Image.open(dirname + '\\' + item[0]['loc'])
            i2 = Image.open(dirname + '\\' + item[1]['loc'])
            ov = os.path.join(dirname + '\\out\\' + (item[0]['base'] + '_v' + item[0]['ext']))
            oh = os.path.join(dirname + '\\out\\' + (item[0]['base'] + '_h' + item[0]['ext']))
            get_concat_resize_v(i1, i2).save(ov)
            get_concat_resize_h(i1, i2).save(oh)

if __name__ == "__main__":
    main()
