#!/usr/bin/env python
# coding: utf-8

import pympi

def make_content(eafob, tier_ref, tier_align):
    list_ref = eafob.get_annotation_data_for_tier(tier_ref)
    list_Mft = eafob.get_annotation_data_for_tier(tier_align)

    H = []
    H2 = []
    for i in list_ref:
        H.append(i[1])

    for i in list_Mft:
        H2.append(i[1])

    dict_ = {}
    for h in H:
        dict_var = {}
        list_var = []

        for i in range(0, 40):
            var = h + i
            varneg = h - i
            list_var.append((h, varneg))
            list_var.append((h, var))

        for value, key in list_var:
            dict_var.setdefault(key, []).append(value)

        dict_.update(dict_var)

    Mft = []
    for i in list_Mft:
        var = i[1]
        if var in dict_.keys():
            i = (i[0], dict_[var][0], i[2])
        Mft.append(i)

    list_Mft2 = []
    for i in Mft:
        x = [i[0], i[1], i[2]]
        list_Mft2.append(x)

    for i in list_Mft2:
        if i[0] != list_Mft2[list_Mft2.index(i) - 1][1]:
            i[0] = list_Mft2[list_Mft2.index(i) - 1][1]
        list_Mft2[0][0] = 0

    content = []
    for i in list_Mft2:
        tuple_ = (i[0], i[1], i[2])
        content.append(tuple_)

    return content


def annotation(eafob, tier_name, content):
    eafob.add_tier(tier_name)
    for i in content:
        t1 = int(i[0])
        t2 = int(i[1])
        value = str(i[2])
        eafob.add_annotation(tier_name, t1, t2, value)


def EafAlign(path_in, path_out, tier_ref, tier_align, tier_name):
    fichier = path_in
    eafob = pympi.Elan.Eaf(fichier)
    Mft = make_content(eafob, tier_ref, tier_align)
    annotation(eafob, tier_name, Mft)
    pympi.Elan.to_eaf(path_out, eafob)