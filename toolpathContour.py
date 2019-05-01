import Rhino
import scriptcontext
import rhinoscriptsyntax as rs


feedrateCutting = 1800
feedratePlunge  = int(feedrateCutting / 3)
feedrateRetract = feedrateCutting
feedrateMove    = 6000
safetyHeight    = 5



def setSegmentId(objId, segmentId):
        rs.SetUserText(objId, "SegmentId", str(segmentId))
        rs.ObjectName(objId, segmentId)


def setFeedrate(objId, feedrate):
        rs.SetUserText(objId, "Feedrate", str(feedrate))


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
    objectNr = 1
    pathSegmentNr = 1
    lastPoint = []

    for id in objects:
        plane = rs.CurvePlane(id)

        # place point inside or outside the object (it is needed for the offset)
        if mode == "Inside" :
            point = rs.CurveAreaCentroid(id)[0]
        else :
            point = rs.XformCPlaneToWorld([10000,10000,0], plane)


        tempCurve = rs.OffsetCurve(id, point, toolDiameter / 2.0, plane.ZAxis)

        if not tempCurve:
            print "Tool cannot do this toolpath"
            return False

        passPoint = rs.CurveStartPoint(tempCurve)

        if objectNr > 1:
            objId = rs.AddLine(lastPoint, [passPoint.X, passPoint.Y, safetyHeight])
            setSegmentId(objId, pathSegmentNr)
            pathSegmentNr = pathSegmentNr + 1
            setFeedrate(objId, feedrateMove)

        objId = rs.AddLine([passPoint.X, passPoint.Y, safetyHeight], [passPoint.X, passPoint.Y, 0])
        setSegmentId(objId, pathSegmentNr)
        pathSegmentNr = pathSegmentNr + 1
        setFeedrate(objId, feedratePlunge)

        if objectNr == 1:
            labelId = rs.AddTextDot(toolpathName, [passPoint.X, passPoint.Y, safetyHeight])
            rs.SetUserText(labelId, "LayerId", rs.LayerId("Toolpaths::" + pathLayerName))


        lastPass = False
        passNr = 1
        prevDepth = 0

        while True:

            depth = passNr * passDepth

            # if the depth is lower, set it to max and mark for last pass
            if depth >= totalDepth:
                depth = totalDepth
                lastPass = True

            objId = rs.AddLine([passPoint.X, passPoint.Y, -prevDepth], [passPoint.X, passPoint.Y, -depth])
            setSegmentId(objId, pathSegmentNr)
            setFeedrate(objId, feedratePlunge)
            pathSegmentNr = pathSegmentNr + 1
            prevDepth = depth

            # add the toolpath and move it to current depth
            toolpathCurve = rs.CopyObject(tempCurve)
            rs.MoveObject(toolpathCurve, [0, 0, -depth])
            setSegmentId(toolpathCurve, pathSegmentNr)
            setFeedrate(toolpathCurve, feedrateCutting)

            passNr = passNr + 1
            pathSegmentNr = pathSegmentNr + 1

            if lastPass == True:
                break


        # add the exit move
        lastPoint = [passPoint.X, passPoint.Y, safetyHeight]
        objId = rs.AddLine([passPoint.X, passPoint.Y, -depth], lastPoint)
        setSegmentId(objId, pathSegmentNr)
        setFeedrate(objId, feedrateRetract)
        pathSegmentNr = pathSegmentNr + 1



        # remove the helper curve
        rs.DeleteObject(tempCurve)

        objectNr = objectNr + 1

    return True


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

    #
    # create Toolpaths parent layer if not present
    #
    if not rs.IsLayer("Toolpaths"):
        rs.AddLayer("Toolpaths")

    #
    # run form to collect data about the toolpath operation
    #
    objects, mode, totalDepth, passDepth, toolDiameter = getToolpathParameters()

    #
    # add sublayer for the new toolpath
    #
    nrOfPaths = rs.LayerChildCount("Toolpaths")
    pathLayerName = "path%03d" % nrOfPaths
    rs.AddLayer(name="Toolpaths::" + pathLayerName, color=[255, 0, 0])
    rs.CurrentLayer(pathLayerName)

    #
    # generate the toolpath
    #
    rc = prepareToolpaths(pathLayerName, objects, mode, totalDepth, passDepth, toolDiameter)

    #
    # remove toolpath layer if the operation failed
    #
    if rc == False:
        print "Removing layer"
        rs.CurrentLayer("Toolpaths")
        rs.DeleteLayer("Toolpaths::" + pathLayerName)

    #
    # enable Layer change event listener
    #
    func = layerChangeEvent
    scriptcontext.sticky["MyLayerChangeEvent"] = func
    Rhino.RhinoDoc.LayerTableEvent += func
