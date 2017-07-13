#!/bin/python
# -*- coding: utf-8 *-

import re


def add_line_number(source):
    '''
    给列表的每个元素加上行号
    :param source: 列表
    '''
    text = []
    i = 0
    for line in source:
        i += 1
        text.append("%d:%s" %(i, line))
    return text
