# -*- coding: UTF-8 -*-

def getYears(model):
    "Gets all years with data from a model.anio"

    years = model.objects.values_list('anio').order_by('anio').distinct('anio')
    return [x[0] for x in years]


def glue(inicial, final, key, actualizado=[]):
    "Glues together two different lists of 'asignado' and 'ejecutado' of dictionaries using a chosen key"

    merged = {}

    # cast as lists
    actualizado = list(actualizado)
    inicial = list(inicial)
    final = list(final)

    # changes 'asignado' to 'actualizado' #FIXME why not fix this at origin?
    for item in actualizado:
        item['actualizado'] = item.pop('asignado')

    # do glue
    for item in inicial+final+actualizado:
        if item[key] in merged:
            merged[item[key]].update(item)
        else:
            merged[item[key]] = item
    glued = [val for (_, val) in merged.items()]

    # checks all required keys have a value (0 if none)
    required = ('ejecutado', 'actualizado', 'asignado')
    for item in glued:
        for r in required:
            if not r in item:
                item[r] = 0

    return glued


def superglue(data=(), key='id', default=0):
    "Glues together different lists of dictionaries using a common key"

    alldata = []
    for datum in data:
        # cast as lists
        datum = list(datum)
        alldata = alldata + datum

    # do glue
    nonkeys = []
    merged = {}
    for item in alldata:
        if item[key] in merged:
            merged[item[key]].update(item)
        else:
            merged[item[key]] = item
        for field, value in item.iteritems():
            if field <> key and field not in nonkeys:
                nonkeys.append(field)
    glued = [val for (_, val) in merged.items()]

    # checks all required keys have a value (default if none)
    required = nonkeys
    for item in glued:
        for r in required:
            if not r in item:
                item[r] = default

    return glued


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"

    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

