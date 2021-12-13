import pympi
import re

def ConlluContent(eafob,
                  ref_tier,
                  id_tier,
                  lemmaToken_tier,
                  morphoToken_tier,
                  feats_tier,
                  pos_tier):

    # création de liste de tuple à partir des tiers utiles
    list_Mft = eafob.get_annotation_data_for_tier(ref_tier)
    list_ref = eafob.get_annotation_data_for_tier(id_tier)
    list_motSP = eafob.get_annotation_data_for_tier(lemmaToken_tier)
    list_mbSP = eafob.get_annotation_data_for_tier(morphoToken_tier)
    list_geSP = eafob.get_annotation_data_for_tier(feats_tier)
    list_rxSP = eafob.get_annotation_data_for_tier(pos_tier)

    ###################################################################################
    # segmentation et metadata #text_en
    ###################################################################################

    # identification et segmentation des unités maximales à partir des traductions
    # identification et balisage
    p_list = []
    list_unitMax = []
    for i in list_Mft:
        string = i[2]
        string = string.strip(" ")

        if string.endswith("§") == False:
            p_list.append(i)

        if string.endswith('§') == True:
            p_list.append(i)
            p_list.append("$")

    # segmentation
    sous_list = []
    for i in p_list:
        if i != "$":
            sous_list.append(i)
        else:
            list_unitMax.append(sous_list)
            sous_list = []

    # remise en forme selon la nouvelle segmentation et création de #text_en
    text_en = buildMetadata(list_unitMax)

    # création d'une liste temporaire contenant les times codes initiaux des unités maximales
    # (nécessaire pour la segmentation de toutes les listes)
    list_temp = []
    for i in text_en:
        list_temp.append(i[0])

    ###################################################################################
    # metadata tokenized_text
    ###################################################################################

    # conversion de la liste de tuples en liste de liste (plus pratique pour le traitement)
    list_mot = tupleToList(list_motSP)

    for i in list_mot:
        if re.search(r"[0-9]", i[2]):
            list_mot[list_mot.index(i) - 1][1] = i[1]
            list_mot.remove(i)

    # mise en forme de la liste Mots
    Mots = miseEnForme(list_temp, list_mot)

    # création liste métadonnées #tokenized_text (tokenization lexical)
    tokenized_text = buildMetadata(Mots)

    ###################################################################################
    # metadata #sent_id
    ###################################################################################

    # mise en forme de la liste Sent
    IDs = miseEnForme(list_temp, list_ref)

    # création liste métadonnées #sent_id
    nameNumRef = list_ref[0][2].rstrip('001')
    sent_id = []
    for textMax in IDs:
        num = textMax[0][2].split(nameNumRef)[1] + '-' + textMax[len(textMax) - 1][2].split(nameNumRef)[1]
        s = nameNumRef + num
        sent_id.append((textMax[0][0], textMax[len(textMax) - 1][1], s))

    ###################################################################################
    # colonne FORM et metadata #text
    ###################################################################################

    # conversion de la liste de tuples en liste de liste (plus pratique pour le traitement)
    list_token = tupleToList(list_mbSP)

    # suppression des vides
    for i in list_token:
        if i[2] == '':
            list_token[list_token.index(i) - 1][1] = i[1]
            list_token.remove(i)

    # mise en forme des tokens à partir de la tier mb@SP

    # alignement time code 2
    list_token = alignTimeCode(list_token)

    # mise en forme de la liste FORM
    FORM = miseEnForme(list_temp, list_token)

    # création liste de metadonnées text (tokenization morphologique)
    text = buildMetadata(FORM)

    ###################################################################################
    # colonne UD_Features
    ###################################################################################
    # mise en forme des traits morpho-syntaxiques à partir de la tier ge@SP

    # conversion de la liste de tuples en liste de liste (plus pratique pour le traitement)
    list_feats = tupleToList(list_geSP)

    for i in list_feats:
        if i[2] == "." or i[2] == "":
            list_feats[list_feats.index(i)][2] = 'PUNCT'

    # alignement time code 2
    list_feats = alignTimeCode(list_feats)

    # mise en forme de la liste FEATS
    FEATS = miseEnForme(list_temp, list_feats)

    ###################################################################################
    # colonne UPOS
    ###################################################################################
    # mise en forme des parties du discours à partir de la tier rx@SP
    list_POS = tupleToList(list_rxSP)

    for i, j in zip(list_POS, list_token):
        if i[2] == "." or i[2] == "":
            list_POS[list_POS.index(i)][2] = 'PUNCT'
        elif i[2] == "?":
            list_POS[list_POS.index(i)][2] = 'PUNCT'
            list_token[list_token.index(j)][2] = "?"

    # alignement time code 2
    list_POS = alignTimeCode(list_POS)

    # mise en forme de la liste POS
    POS = miseEnForme(list_temp, list_POS)


    ###################################################################################
    # colonne MISC
    ###################################################################################

    # déplacement de l'annotation de traduction dans la colonne MISC depuis la colonne FEATS
    MISC = []
    sous_list = []
    for feat in FEATS:
        for i in feat:
            if re.search(r"([a-z])\\([A-Z])", i[2]):
                f = i[2]
                feat[feat.index(i)] = [i[0], i[1], f.split('\\')]
            elif re.search(r"([A-Z])~([a-z])", i[2]):
                f = i[2]
                feat[feat.index(i)] = [i[0], i[1], f.split('~')]

    for feat, pos in zip(FEATS, POS):
        for i, j in zip(feat, pos):
            if type(i[2]) != list:
                if str(i[2]).islower():
                    GE = str(preprocess_MISC_Value(i[2]))
                    RX = str(preprocess_MISC_Value(j[2]))
                    sous_list.append([i[0], i[1],
                                      'Gloss= ' + str(i[2]) + '|AlignBegin= ' + str(i[0]) + '|AlignEnd= ' + str(
                                          i[1]) + '|GE= ' + str(GE) + '|RX= ' + str(RX)])
                    feat[feat.index(i)] = [i[0], i[1], '_']
                elif str(i[2]).istitle() and str(i[2]).startswith('-') == False:
                    GE = preprocess_MISC_Value(i[2])
                    RX = preprocess_MISC_Value(j[2])
                    sous_list.append([i[0], i[1],
                                      'ProperName= ' + str(i[2]) + '|AlignBegin= ' + str(i[0]) + '|AlignEnd= ' + str(
                                          i[1]) + '|GE= ' + str(GE) + '|RX= ' + str(RX)])
                    feat[feat.index(i)] = [i[0], i[1], '_']
                else:
                    GE = preprocess_MISC_Value(i[2])
                    RX = preprocess_MISC_Value(j[2])
                    sous_list.append([i[0], i[1],
                                      'AlignBegin= ' + str(i[0]) + '|AlignEnd= ' + str(i[1]) + '|GE= ' + str(
                                          GE) + '|RX= ' + str(RX)])

            elif str(i[2][0]).islower():
                GE = preprocess_MISC_Value(i[2][1])
                RX = preprocess_MISC_Value(j[2])
                sous_list.append([i[0], i[1],
                                  'Gloss= ' + str(i[2][0]) + '|AlignBegin= ' + str(i[0]) + '|AlignEnd= ' + str(
                                      i[1]) + '|GE= ' + str(GE) + '|RX= ' + str(RX)])
                feat[feat.index(i)] = [i[0], i[1], str(i[2][1])]

            elif str(i[2][1]).islower():
                GE = preprocess_MISC_Value(i[2][0])
                RX = preprocess_MISC_Value(j[2])
                sous_list.append([i[0], i[1],
                                  'Gloss= ' + str(i[2][1]) + '|AlignBegin= ' + str(i[0]) + '|AlignEnd= ' + str(
                                      i[1]) + '|GE= ' + str(GE) + '|RX= ' + str(RX)])
                feat[feat.index(i)] = [i[0], i[1], str(i[2][0])]

            elif re.search(r"([A-Z])~([a-z])", i[2][0]):
                f = i[2][0]
                f = f.split('~')

                if str(f[1]).islower():
                    GE = preprocess_MISC_Value(i[2])
                    RX = preprocess_MISC_Value(j[2])
                    sous_list.append([i[0], i[1],
                                      'Gloss= ' + str(f[1]) + '|AlignBegin= ' + str(i[0]) + '|AlignEnd= ' + str(
                                          i[1])] + '|GE= ' + str(GE) + '|RX= ' + str(RX))
                    feat[feat.index(i)] = [i[0], i[1], str(f[0]) + "." + str(i[2][1])]
            else:
                GE = preprocess_MISC_Value(i[2])
                RX = preprocess_MISC_Value(j[2])
                sous_list.append([i[0], i[1], 'AlignBegin= ' + str(i[0]) + '|AlignEnd= ' + str(i[1]) + '|GE= ' + str(
                    GE) + '|RX= ' + str(RX)])

        MISC.append(sous_list)
        sous_list = []

    return text_en, text, tokenized_text, FORM, FEATS, POS, MISC, sent_id

def tupleToList(list_tier):
    listDeList = []
    for i in list_tier:
        x = [i[0], i[1], i[2]]
        listDeList.append(x)
    return listDeList

def listsToTuples (list_token, list_mb, list_feats, list_ge, list_POS, list_rx):
    # reconversion sous la forme de liste de tuple (à voir si vraiment utile puisque pas de réécriture dans le .eaf)
    for i in list_token:
        tuple_ = (i[0], i[1], i[2])
        list_mb.append(tuple_)

    for i in list_feats:
        tuple_ = (i[0], i[1], i[2])
        list_ge.append(tuple_)

    for i in list_POS:
        tuple_ = (i[0], i[1], i[2])
        list_rx.append(tuple_)

def buildMetadata(metadatas):
    mdata = []
    for unitMax in metadatas:
        s = ' '.join([str(unit[2]) for unit in unitMax])
        mdata.append((unitMax[0][0], unitMax[len(unitMax) - 1][1], s))
    return mdata

def alignTimeCode(list_):
    for i in list_[:-1]:
        if i[1] != list_[list_.index(i) + 1][0]:
            i[1] = list_[list_.index(i) + 1][0]
    return list_

def miseEnForme(list_temp, list_element):
    list_text = []
    for i in list_element:
        if i == list_element[len(list_element) - 1]:
            list_text.append("#")
        else:
            if i[1] in list_temp:
                list_text.append(i)
                list_text.append("#")
            else:
                list_text.append(i)

    sous_list = []
    list_out = []
    for i in list_text:
        if i != "#":
            sous_list.append(i)
        else:
            list_out.append(sous_list)
            sous_list = []
    return list_out


def preprocess_MISC_Value(annot):
    ele = re.split('(\W)', annot)

    while '' in ele:
        ele.remove('')

    for j in ele:
        if j != '=' and j != '.' and j != '\\' and j != '~' and j != '-':
            if j.islower():
                ele[ele.index(j)] = j
            else:
                ele[ele.index(j)] = '[' + j + ']'

    ele = ''.join(ele)

    return ele

def makeConllu(
        path_in,
        ref_tier,
        id_tier,
        lemmaToken_tier,
        morphoToken_tier,
        feats_tier,
        pos_tier):

    fichier = path_in
    eafob = pympi.Elan.Eaf(fichier)

    text_en, text, tokenized_text, FORM, FEATS, POS, MISC, sent_id = ConlluContent(eafob,
                                                                             ref_tier,
                                                                             id_tier,
                                                                             lemmaToken_tier,
                                                                             morphoToken_tier,
                                                                             feats_tier,
                                                                             pos_tier)

    # écriture dans le fichier de sortie
    fichier = fichier.rstrip("\.eaf").lstrip("C:/Users/ziane/py/stageM2/beja/align//.")
    with open("C:/Users/ziane/py/stageM2/beja/output/" + fichier + ".conllu", "w", encoding='utf-8') as file:
        comp = 0
        for sent_id, trad, text, tokenized, form, feat, pos, misc in zip(sent_id, text_en, text, tokenized_text, FORM, FEATS, POS,
                                                                          MISC):
            comp += 1
            file.write("# sent_id = " + sent_id[2] + '\n')
            file.write("# text = " + text[2] + '\n')
            file.write("# phonetic_text = " + tokenized[2] + '\n')
            if trad[2].endswith('and §'):
                x = re.sub('and §$', '[and]', trad[2])
                file.write("# text_en = " + x + '\n')
            else:
                file.write("# text_en = " + trad[2].rstrip('§') + '\n')

            # file.write("\n")
            id_token = 0
            for t, f, p, m in zip(form, feat, pos, misc):
                id_token += 1
                # print(id_token, t[2], f[2], p[2])
                file.write(str(id_token) + '\t'
                           + str(t[2]) + '\t'
                           + '_' + '\t'
                           + '_' + '\t'
                           + str(p[2]) + '\t'
                           + str(f[2]) + '\t'
                           + '_' + '\t'
                           + '_' + '\t'
                           + '_' + '\t'
                           + str(m[2]) + '\n')
            file.write("\n")