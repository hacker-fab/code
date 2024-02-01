# coding=utf-8
# =============================================================================
# Copyright (c) 2001-2023 FLIR Systems, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================

# J. Kent Wirant
# Hacker Fab
# Flir Camera Module

from camera.camera_module import *
from pyspin import PySpin

# for the time being, leave unimplemented in public repos
class FlirCamera(CameraModule, PySpin.ImageEventHandler):
    __camera_system__ = None
    __camera_list__ = None
    __camera_nodemap__ = None
    __camera_nodemap_tldevice__ = None
    __selected_camera__ = None
    __processor__ = None

    __image_format__ = 'mono8'

    __stream_image__ = None


    def __init__(self):
        PySpin.ImageEventHandler.__init__(self)
        self.__processor__ = PySpin.ImageProcessor()
        self.__processor__.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)


    # set to None if no callback desired
    def setSingleCaptureCallback(self, callback):
        self.__singleCaptureCallback__ = callback


    # set to None if no callback desired
    def setStreamCaptureCallback(self, callback):
        self.__streamCaptureCallback__ = callback


    # TODO
    # camera configuration functions (e.g. 'exposure_time', 'gain', 'image_format', etc.)
    def getSetting(self, settingName):
        return None


    # TODO
    def setSetting(self, settingName, settingValue): # returns true on success
        return False


    # TODO
    def getAvailableResolutions(self, mode=None):
        return None


    # TODO
    def getResolution(self, mode=None):
        return None


    # TODO
    def setResolution(self, resolution, mode=None): # returns true on success
        return False


    # camera interfacing functions
    # TODO
    def singleImageReady(self): # returns bool
        return False


    def streamImageReady(self): # returns bool
        return self.__stream_image__ != None and not self.__stream_image__.IsIncomplete()


    # TODO
    def getSingleCaptureImage(self):
        return None


    def getStreamCaptureImage(self):
        if self.streamImageReady():
            return (self.__stream_image__, self.__stream_image__.shape, self.__image_format__)
        else:
            return None


    def isOpen(self): # returns bool
        return self.__selected_camera__ != None and self.__selected_camera__.IsValid()


    def open(self): # returns true on success
        # Retrieve singleton reference to system object
        self.__camera_system__ = PySpin.System.GetInstance()

        # Retrieve list of cameras from the system
        self.__camera_list__ = self.__camera_system__.GetCameras()
        num_cameras = self.__camera_list__.GetSize()

        # Finish if there are no cameras
        if num_cameras == 0:
            print("No cameras connected.")
            self.close()
            return False

        # Run on first camera
        self.__selected_camera__ = self.__camera_list__[0]

        try:
            # Retrieve TL device nodemap
            self.__camera_nodemap_tldevice__ = self.__selected_camera__.GetTLDeviceNodeMap()

            # Initialize camera
            self.__selected_camera__.Init()

            # Retrieve GenICam nodemap
            self.__camera_nodemap__ = self.__selected_camera__.GetNodeMap()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            self.close()
            return False
        
        # Register Event Handler
        self.__selected_camera__.RegisterEventHandler(self)

        return True
        

    def close(self): # returns true on success
        # deinitialize camera and release any resources allocated to it
        if self.__selected_camera__ != None:
            self.stopStreamCapture()
            # Unregister Event Handler
            self.__selected_camera__.UnegisterEventHandler(self)
            self.__selected_camera__.DeInit()
            del self.__selected_camera__
            self.__selected_camera__ = None

        # clear camera list
        if self.__camera_list__ != None:
            self.__camera_list__.Clear()
            self.__camera_list__ = None

        # release system instance
        if self.__camera_system__ != None:
            self.__camera_system__.ReleaseInstance()
            self.__camera_system__ = None

        self.__camera_nodemap__ = None
        self.__camera_nodemap_tldevice__ = None

        self.__invalidateImages__()        

        return True


    # TODO
    def startSingleCapture(self): # returns true on success
        return False


    # TODO: callback setup
    def startStreamCapture(self): # returns true on success
        try:
            # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
            node_acquisition_mode = PySpin.CEnumerationPtr(self.__camera_nodemap__.GetNode('AcquisitionMode'))
            if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsReadable(node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            # set up callback here? Pyspin.ImageEventHandler?

            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
            self.__selected_camera__.BeginAcquisition()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        return True


    # TODO
    def stopSingleCapture(self): # returns true on success
        return False


    def stopStreamCapture(self): # returns true on success
        if self.__selected_camera__ != None:
            if self.__selected_camera__.IsStreaming():
                self.EndAcquisition()
                return True
        return False


    # TODO: more of this
    # camera description functions
    def getDeviceInfo(self, parameterName):
        match parameterName:
            case 'vendor':
                return "Flir"
            case 'name':
                return "Flir Camera"
            case other:
                return None


    # overrides member function PySpin.ImageEventHandler.OnImageEvent(self, image)
    def OnImageEvent(self, image):
        if not image.IsIncomplete():
            # TODO: support more image formats
            self.__stream_image__ = self.__processor__.Convert(image, PySpin.PixelFormat_Mono8).GetNDArray()
            image.Release()
        
            # TODO: test for stream or single capture mode
            if self.__streamCaptureCallback__ != None:
                self.__streamCaptureCallback__(self.__stream_image__, self.__stream_image__.shape, self.__image_format__)


    def __invalidateImages__(self):
        if self.__stream_image__ != None:
            del self.__stream_image__
            self.__stream_image__ = None
