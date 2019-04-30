import rhinoscriptsyntax as rs
import Rhino
import math



#Function to find direction of Offset, Works on normal of curve.  User must set normal for specified task
def Offset_Direction(curve_sel):
    crv_centroid=rs.CurveAreaCentroid(curve_sel)
    off_direct=crv_centroid[0]
    return off_direct

#Offsets curve by distance until curve is too small
def Offset_total():
    off_dist=rs.GetReal("Enter distance of offsets",2.5)
    off_dist=abs(off_dist)
    curve_sel=rs.GetObject("Select curve")
    off_direct=Offset_Direction(curve_sel)

    #off_direct=rs.GetPoint("Pick point")
    new_curve=rs.OffsetCurve(curve_sel, off_direct, off_dist)
    #get curve area  for safety break if offset goes outside (it would be infinite)
    if rs.IsCurveClosed(curve_sel):
        curve_sel_area=rs.CurveArea(curve_sel)
        print(curve_sel_area)
        new_curve_area=rs.CurveArea(new_curve)
        print(new_curve_area)
    i=0
    # while curve_sel_area > new_curve_area and new_curve !=None:
    while i < 20:
        print "iterating"
        curve_sel=new_curve

        print curve_sel, off_direct, off_dist

        new_curve=rs.OffsetCurve(curve_sel, off_direct, off_dist)

        if new_curve is None:
            print "Is none"
            break

        if rs.IsCurve(new_curve):
          if len(new_curve) > 1:
              print ">1"
              rs.DeleteObjects(new_curve)
              break
        else:
            print "It is not curve anymore"
            break

        i = i + 1

if __name__=="__main__":
    Offset_total()
