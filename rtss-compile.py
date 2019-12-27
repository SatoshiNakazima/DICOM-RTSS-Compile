
# coding: utf-8

import cv2
import os
import numpy as np
import glob
import sys
import re
import pydicom



maskpath=""
dcmpath=""
rtss=""

def dcmfile_rename_uid(dcmpath):
    for i in os.listdir(dcmpath):
        if pydicom.misc.is_dicom(dcmpath+i):     
            data=pydicom.dcmread(os.path.join(dcmpath, i),force=True) 
            filename=data.SOPInstanceUID
            os.rename(dcmpath+i,dcmpath+filename+'.dcm')


def maskfile_rename_uid(dcmpath,maskpath):
    dcmlist=[]
    for i in os.listdir(dcmpath):
        if pydicom.misc.is_dicom(dcmpath+i):    
            data=pydicom.dcmread(os.path.join(dcmpath, i),force=True) 
            filename=data.SOPInstanceUID
            dcmlist.append(filename)
        maskpathlist=sorted(glob.glob(os.path.join(maskpath,'*.png')))
    for n in range(len(maskpathlist)):
            newname=dcmlist[n]+'.png'
            os.rename(maskpathlist[n],maskpath +newname)


def get_contour_dict(maskpath,dcmpath):
    contourdict={}
    n=0
    for img in os.listdir(imgpath):
        imge= cv2.imread(imgpath+img,cv2.IMREAD_GRAYSCALE )
        ret,thresh = cv2.threshold(imge,127,255,0) 
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        for i in contours:
            a=i.tolist()
            contourdict[img[0:-4]]=a 
    Zdict={}
    for i in os.listdir(dcmpath):
        if pydicom.misc.is_dicom(dcmpath+i):     #dicomであるか
            data=pydicom.dcmread(os.path.join(dcmpath, i),force=True)    
            Zdict[i[0:-4]] = float(data.ImagePositionPatient[2])
    XYZdict={}
    for i in range(len(contourdict)):
        filename=list(contourdict.keys())[i]
        for v in contourdict[filename]:
            n=len(contourdict[filename])
            XYZlist=[]
            for j in range (n):
                XYZlist.append(float(contourdict[filename][j][0][0])-128)#128
                XYZlist.append(float(contourdict[filename][j][0][1])-128)
                XYZlist.append(float(Zdict[filename]))
                XYZdict[filename]=XYZlist
    return XYZdict


def write_position(rtss,XYZdict):
    rtss =  pydicom.dcmread(rtss)
    n=0
    for i in XYZdict.keys():
        rtss.ROIContourSequence[0].ContourSequence[n].ContourImageSequence[0].ReferencedSOPInstanceUID=i
        rtss.ROIContourSequence[0].ContourSequence[n].ContourData=XYZdict[i]
        rtss.ROIContourSequence[0].ContourSequence[n].NumberOfContourPoints=int(len(XYZdict[i])/3)
        rtss.ROIContourSequence[0].ContourSequence[n].ContourGeometricType='CLOSED_PLANAR'
        n+=1
    print(n)
    for i in  reversed(range(n,len(rtss.ROIContourSequence[0].ContourSequence))):
        del rtss.ROIContourSequence[0].ContourSequence[i]
    return rtss

