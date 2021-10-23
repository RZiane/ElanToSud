def makeCorresp(table_conv):
    # création du dictionnaire à partir du tableau de conversion des gloses
    gloses = open(table_conv)
    dict_gloses = {}
    for i in gloses:
        i = i.split(";")
        dict_gloses[i[4]] = [i[3], i[0], i[1], i[2]]
    return dict_gloses

def makeDicts(table_pos, table_feats, table_dep):
    # création du dictionnaire de UPOS
    UD_pos = open(table_pos, table_feats, table_dep)
    dict_UD_pos = {}
    for i in UD_pos:
        i = i.split(";")
        dict_UD_pos[i[1].rstrip('\n')] = [i[0].rstrip('\n')]

    # création du dictionnaire de feats
    UD_feats = open()
    dict_UD_feats = {}
    for i in UD_feats:
        i = i.split(";")
        dict_UD_feats[i[0].rstrip('\n')] = [i[1].rstrip('\n')]

    # création du dictionnaire de dépendances
    UD_dep = open()
    dict_UD_dep = {}
    for i in UD_dep:
        i = i.split(";")
        dict_UD_dep[i[0].rstrip('\n')] = [i[1].rstrip('\n')]

    return dict_UD_pos, dict_UD_feats, dict_UD_dep

def conversion(fichier):
    # création des dictionnaires de conversions
    dict_gloses = makeCorresp("conv_gloses.csv")
    dict_UD_pos, dict_UD_feats, dict_UD_dep = makeDicts("UD_pos.csv", "UD_feats.csv", "UD_dep.csv")

    with open(fichier, "w", encoding="utf-8") as out:
        # iteration des lignes du fichier conllu en evitant les métadonnées
        for i in corpus:
            XPOS = []
            XFEATS = []
            UPOS = []
            UFEATS = []
            UDEP = []
            XDEP = []
            if len(i) == 1:
                pass
            elif i.startswith('#') == False:
                i = i.split('\t')
                POS = i[4].split('.')
                FEATS = i[5].split('.')

                # conversion des pos
                for an in POS:
                    an = an.lstrip("=").lstrip("-").rstrip("=").rstrip("-")
                    if an in dict_gloses.keys():
                        var = dict_gloses[an][1]
                        varF = dict_gloses[an][2]
                        varD = dict_gloses[an][3]

                        if varD in dict_UD_dep.keys():
                            var2 = str(dict_UD_dep[varD])
                            UDEP.append(var2.lstrip("['").rstrip("']"))
                            XDEP.append(an)

                        elif varF in dict_UD_feats.keys():
                            var2 = str(dict_UD_feats[varF])

                            if var2.lstrip("['").rstrip("']") in UFEATS:
                                pass
                            else:
                                UFEATS.append(var2.lstrip("['").rstrip("']"))
                                XFEATS.append(an)

                            if var != '_':
                                var3 = str(dict_UD_pos[var])
                                UPOS.append(var3.lstrip("['").rstrip("']"))
                                XPOS.append(an)

                        elif var in dict_UD_pos.keys():
                            var2 = str(dict_UD_pos[var])
                            UPOS.append(var2.lstrip("['").rstrip("']"))
                            XPOS.append(an)

                # conversion des feats
                for an in FEATS:
                    an = an.lstrip("=").lstrip("-").rstrip("=").rstrip("-")
                    if an in dict_gloses.keys():
                        var = dict_gloses[an][1]
                        varF = dict_gloses[an][2]
                        varD = dict_gloses[an][3]
                        if varF in dict_UD_feats.keys():
                            var2 = str(dict_UD_feats[varF])
                            if var2.lstrip("['").rstrip("']") in UFEATS:
                                pass
                            else:
                                UFEATS.append(var2.lstrip("['").rstrip("']"))
                                XFEATS.append(an)

                            if var != '_':
                                var3 = str(dict_UD_pos[var])
                                UPOS.append(var3.lstrip("['").rstrip("']"))
                                XPOS.append(an)

                        elif varD in dict_UD_dep.keys():
                            var3 = str(dict_UD_dep[varD])
                            UDEP.append(var3.lstrip("['").rstrip("']"))
                            XDEP.append(an)

                # preparation des etiquettes
                # #colonne UPOS
                if len(UPOS) == 2:
                    i[3] = UPOS[0]
                else:
                    i[3] = ''.join(UPOS)

                # #colonne XPOS
                i[4] = ', '.join(XPOS)

                # #colonne Feats
                if len(UFEATS) == 0:
                    i[5] = '_'
                else:
                    i[5] = '|'.join(UFEATS)

                # #colonne Misc
                try:
                    FEATS.remove('_')
                except:
                    pass

                if len(POS) != 0 and len(FEATS) != 0:
                    i[9] = "GE= " + ','.join(FEATS) + "|" + "RX= " + ','.join(POS) + "|" + i[9].rstrip('\n')
                elif len(POS) == 0 and len(FEATS) != 0:
                    i[9] = "GE= " + ','.join(FEATS) + "|" + i[9].rstrip('\n')
                elif len(FEATS) == 0 and len(POS) != 0:
                    i[9] = "RX= " + ','.join(POS) + "|" + i[9].rstrip('\n')
                else:
                    i[9] = i[9].rstrip('\n')

                if 'ProperName=' in str(i[9]):
                    i[3] = 'PROPN'
                    i[4] = 'NP'

                if i[3] == '':
                    i[3] = '_'
                    i[4] = '_'

            # Ecriture dans le fichier de sortie
            print(i)

            try:
                if i.startswith('# sent_id =') == True and '001-' in i:
                    out.write(i)
                elif i.startswith('# sent_id =') == True:
                    out.write('\n')
                    out.write(i)
                elif i.startswith('#') == True:
                    out.write(i)
            except:
                out.write('\t'.join(i) + '\n')
