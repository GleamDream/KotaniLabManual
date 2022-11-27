from findellipse import FindEllipse

for ellipse in [FindEllipse("with_anger.csv"), FindEllipse("without_anger.csv")]:
    ellipse.find()
    ellipse.draw()
    print(ellipse)
    print(ellipse.center, ellipse.axis, ellipse.rot)