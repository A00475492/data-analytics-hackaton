from shapely.geometry import Point, Polygon

southend = [
    (-63.614826,44.640886),
    (-63.574588,44.652858),
    (-63.559801,44.626083),
    (-63.567749,44.617745)
]

northend = [
    (-63.630485,44.663642),
    (-63.615618,44.676056),
    (-63.575051,44.652723),
    (-63.591396,44.647097)
]

westend = [
    (-63.588618,44.643578),
    (-63.607104,44.638424),
    (-63.628977,44.646552),
    (-63.627678,44.662298),
    (-63.615576,44.660706)
]

claytonPark = [
    (-63.628379,44.662314),
    (-63.629647,44.646338),
    (-63.673048,44.634274),
    (-63.678797,44.682118),
    (-63.636067,44.661021),
    (-63.651316,44.654683)
]

bedford = [
    (-63.664021,44.707641),
    (-63.690181,44.693556),
    (-63.733227,44.721437),
    (-63.701555,44.758669),
    (-63.626118,44.758184),
    (-63.602142,44.740991),
    (-63.619883,44.704135),
    (-63.662164,44.729871),
]

dartmouth = [
    (-63.524870,44.633227),
    (-63.652676,44.703871),
    (-63.557749,44.740637),
    (-63.495074,44.681758)
]

rockingham = [
    (-63.636139,44.681758),
    (-63.649734,44.664301),
    (-63.654688,44.663228),
    (-63.685458,44.693914),
    (-63.661598,44.703464),
    (-63.631104,44.663729)
]



def findRegion(location):
    point = Point(location['lng'], location['lat'])
    if Polygon(southend).contains(point):
        return "South End Halifax"
    elif Polygon(northend).contains(point):
        return "North End Halifax"
    elif Polygon(westend).contains(point):
        return "West End Halifax"
    elif Polygon(claytonPark).contains(point):
        return "Clayton Park"
    elif Polygon(bedford).contains(point):
        return "Bedford"
    elif Polygon(dartmouth).contains(point):
        return "Dartmouth"
    elif Polygon(rockingham).contains(point):
        return "Rockingham"
    else:
        return "Outer Halifax"