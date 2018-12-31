import Rhino
import scriptcontext
import rhinoscriptsyntax as rs


def setSegmentId(objId, segmentId):
        rs.SetUserText(objId, "SegmentId", str(segmentId))
        rs.ObjectName(objId, segmentId)


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


def prepareToolpaths(toolpathName, objects, mode, totalDepth, passDepth, toolDiameter):

    for id in objects:
        plane = rs.CurvePlane(id)

        # place point inside or outside the object (it is needed for the offset)
        if mode == "Inside" :
            point = rs.CurveAreaCentroid(id)[0]
        else :
            point = rs.XformCPlaneToWorld([10000,10000,0], plane)


        tempCurve = rs.OffsetCurve(id, point, toolDiameter / 2.0, plane.ZAxis)
        #rs.ObjectLayer(tempCurve, "gcode")

        passPoint = rs.CurveStartPoint(tempCurve)

        objId = rs.AddLine([passPoint.X, passPoint.Y, 5], [passPoint.X, passPoint.Y, 0])
        setSegmentId(objId, 1)
        labelId = rs.AddTextDot(toolpathName, [passPoint.X, passPoint.Y, 5])
        rs.SetUserText(labelId, "LayerId", rs.LayerId("Toolpaths::" + pathLayerName))


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
            setSegmentId(objId, pathSegmentNr)
            pathSegmentNr = pathSegmentNr + 1
            prevDepth = depth

            # add the toolpath and move it to current depth
            toolpathCurve = rs.CopyObject(tempCurve)
            rs.MoveObject(toolpathCurve, [0, 0, -depth])
            setSegmentId(toolpathCurve, pathSegmentNr)

            passNr = passNr + 1
            pathSegmentNr = pathSegmentNr + 1

            if lastPass == True:
                break


        # add the exit move
        objId = rs.AddLine([passPoint.X, passPoint.Y, -depth], [passPoint.X, passPoint.Y, 5])
        setSegmentId(objId, pathSegmentNr)


        # remove the helper curve
        rs.DeleteObject(tempCurve)


def layerChangeEvent(sender, e):
    toolpaths = rs.LayerChildren("Toolpaths")
    layerId = "";

    for toolpath in toolpaths:
        layerId = rs.LayerId(toolpath)

        for textDotId in rs.ObjectsByType(8192):
            toolpathName = rs.TextDotText(textDotId)

            if rs.GetUserText(textDotId, "LayerId") == layerId:
                newToolpathName = toolpath.split("::")[1]
                print "Renaming ", toolpathName, " to ", newToolpathName
                rs.TextDotText(textDotId, newToolpathName)


if __name__=="__main__":

    #
    # disable Layer change event listener
    #
    if scriptcontext.sticky.has_key("MyLayerChangeEvent"):
        func = scriptcontext.sticky["MyLayerChangeEvent"]
        Rhino.RhinoDoc.LayerTableEvent -= func
        scriptcontext.sticky.Remove("MyLayerChangeEvent")

    objects, mode, totalDepth, passDepth, toolDiameter = getToolpathParameters()
    nrOfPaths = rs.LayerChildCount("Toolpaths")
    pathLayerName = "path%03d" % nrOfPaths
    rs.AddLayer(name="Toolpaths::" + pathLayerName, color=[255, 0, 0])
    rs.CurrentLayer(pathLayerName)
    prepareToolpaths(pathLayerName, objects, mode, totalDepth, passDepth, toolDiameter)

    #
    # enable Layer change event listener
    #
    func = layerChangeEvent
    scriptcontext.sticky["MyLayerChangeEvent"] = func
    Rhino.RhinoDoc.LayerTableEvent += func
