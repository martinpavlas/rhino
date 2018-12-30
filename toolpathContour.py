import Rhino
import rhinoscriptsyntax as rs


def getToolpathParameters():

    # get curves to generate the toolpaths for
    objects = rs.GetObjects("Select Curves", 4, True, True)
    rs.SelectObjects(objects)

    # get mode of operation
    myoptions = ["Inside", "Outside"]
    mode = rs.GetString("Choose an option", "", myoptions)
    if mode is None:
        mode == "Inside"

    # get total depth
    totalDepth = rs.GetDistance()

    # get depth per pass
    passDepth = rs.GetReal("Depth of the pass")

    # get diameter of the tool
    toolDiameter = rs.GetReal("Diameter of the tool")

    return objects, mode, totalDepth, passDepth, toolDiameter


def prepareToolpaths(objects, mode, totalDepth, passDepth, toolDiameter):

    # this is the starting point for milling all contours
    startPoint = [0, 0, 20]

    for id in objects:
        plane = rs.CurvePlane(id)

        # place point inside or outside the object (it is needed for the offset)
        if mode == "Inside" :
            point = rs.CurveAreaCentroid(id)[0]
        else :
            point = rs.XformCPlaneToWorld([10000,10000,0], plane)

        rs.CurrentLayer("toolpaths")

        tempCurve = rs.OffsetCurve(id, point, toolDiameter / 2.0, plane.ZAxis)
        #rs.ObjectLayer(tempCurve, "gcode")

        passPoint = rs.CurveStartPoint(tempCurve)


        objId = rs.AddLine(startPoint, [passPoint.X, passPoint.Y, 5])
        rs.ObjectName(objId, 0)

        objId = rs.AddLine([passPoint.X, passPoint.Y, 5], [passPoint.X, passPoint.Y, 0])
        rs.ObjectName(objId, 1)


        lastPass = False
        passNr = 1
        pathSegmentNr = 2
        prevDepth = 0

        while True:

            depth = passNr * passDepth

            # if the depth is lower, set it to max and mark for last pass
            if depth >= totalDepth:
                depth = totalDepth
                lastPass = True

            objId = rs.AddLine([passPoint.X, passPoint.Y, -prevDepth], [passPoint.X, passPoint.Y, -depth])
            rs.ObjectName(objId, pathSegmentNr)
            pathSegmentNr = pathSegmentNr + 1
            prevDepth = depth

            # add the toolpath and move it to current depth
            toolpathCurve = rs.CopyObject(tempCurve)
            rs.MoveObject(toolpathCurve, [0, 0, -depth])
            rs.ObjectName(toolpathCurve, pathSegmentNr)

            passNr = passNr + 1
            pathSegmentNr = pathSegmentNr + 1

            if lastPass == True:
                break


        # add the exit move
        objId = rs.AddLine([passPoint.X, passPoint.Y, -depth], [passPoint.X, passPoint.Y, 20])
        rs.ObjectName(objId, pathSegmentNr)


        # remove the helper curve
        rs.DeleteObject(tempCurve)



if __name__=="__main__":
    objects, mode, totalDepth, passDepth, toolDiameter = getToolpathParameters()
    prepareToolpaths(objects, mode, totalDepth, passDepth, toolDiameter)
