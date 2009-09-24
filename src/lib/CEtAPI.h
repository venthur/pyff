// ---------------------------------------------------------------------------- 
//
// Copyright (C) 2009, alea technologies gmbh
//
// ----------------------------------------------------------------------------
//
//      Author: Martin Werner
//
// ----------------------------------------------------------------------------

// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the CETAPI_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// CETAPI_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.

#ifdef CETAPI_EXPORTS
#define CETAPI_API __declspec(dllexport)
#else
#define CETAPI_API __declspec(dllimport)
#endif

#ifndef Py_CODECREGISTRY_H
#define Py_CODECREGISTRY_H
#ifdef __cplusplus
extern "C" {
#endif


struct _aleaData
{
	//Raw Data
	long rawDataTimestamp;
	double intelligazeX;
	double intelligazeY;
	double gazePositionXLeftEye;
	double gazePositionYLeftEye;
	double gazePositionConfidenceLeftEye;
	double pupilDiameterLeftEye;
	double gazePositionXRightEye;
	double gazePositionYRightEye;
	double gazePositionConfidenceRightEye;
	double pupilDiameterRightEye;
	//Event Data
	int eventID;
	long eventDataTimestamp;
	long duration;
	double positionX;
	double positionY;
	double dispersionX;
	double dispersionY;
	double confidence;
};

typedef struct _aleaData ALEADATA;

//exported Methods
CETAPI_API int __stdcall Open();

CETAPI_API void __stdcall Close();

CETAPI_API int __stdcall Version(long* major, long* minor, long* build, long* device);

CETAPI_API int __stdcall IsOpen(short* open);

// Parameter location:
// 0 = Full -> outer points are 5% off the monitor border
// 1 = Center -> outer points are 20% off the monitor border
// 2 = Bottom -> points are located in the lower half of the monitor
//
// Parameter eye: 
// 0 = calibrate both eyes
// 1 = calibrate left, track both eyes (“glass eye”)
// 2 = calibrate right, track both eyes (“glass eye”)
// 3 = calibrate and track left eye ( “pirate eye” )
// 4 = calibrate and track right eye ( “pirate eye” )
CETAPI_API int __stdcall PerformCalibration(long noPoints, int location, BOOL randomizedPoints, BOOL slowMode, BOOL audioFeedback, int eye, BOOL calibrationImprovement, BOOL skipBadPoints, BOOL autoCalibration, long backColor, long pointColor, const char* imageName);

//Use dwMilliseconds = -1 to wait infinite (recommend)
CETAPI_API int __stdcall WaitForCalibrationResult(int* status, BOOL* improve, DWORD dwMilliseconds);

CETAPI_API int __stdcall DataStreaming(BOOL enable);

CETAPI_API int __stdcall ClearDataBuffer();

//Use dwMilliseconds = -1 to wait infinite (not recommend)
CETAPI_API int __stdcall WaitForData(ALEADATA* data, DWORD dwMilliseconds);

CETAPI_API int __stdcall ShowStatusWindow(long posX, long posY, long size, long opacity);

CETAPI_API int __stdcall HideStatusWindow();

#ifdef __cplusplus
}
#endif
#endif /* !Py_CODECREGISTRY_H */
