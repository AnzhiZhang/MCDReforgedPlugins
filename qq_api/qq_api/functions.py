# -*- coding: utf-8 -*-
import os


def touch_folder(path: str) -> None:
    """
    Touch a folder, create it if not exists.
    :param path: Folder path.
    :return: None.
    """
    if not os.path.isdir(path):
        os.makedirs(path)


def version_compare(v1, v2):
    """Compare two versions."""
    def split_version(v):
        return tuple([int(x) for x in v.split('-')[0].split('.')])

    def cmp(a, b):
        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    v1 = split_version(v1)
    v2 = split_version(v2)
    for i in range(min(len(v1), len(v2))):
        if v1[i] != v2[i]:
            return cmp(v1[i], v2[i])
    else:
        return cmp(len(v1), len(v2))
