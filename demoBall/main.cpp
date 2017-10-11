

//#include "opencv2/objdetect/objdetect.hpp"
//#include "opencv2/highgui/highgui.hpp"
//#include "opencv2/imgproc/imgproc.hpp"
#include <cv.h>
#include <cvaux.h>
#include <highgui.h>

#include <cctype>
#include <iostream>
#include <iterator>
#include <stdio.h>
 

#include <yarp/os/all.h>
#include <yarp/sig/all.h>


using namespace yarp::os;
using namespace yarp::sig;
using namespace yarp::sig::draw;
using namespace yarp::sig::file;
using namespace std;
using namespace cv;


void send_face_center_to_yarp_port(double x, double y, double conf);

void detectAndDraw( Mat& img, CascadeClassifier& cascade,
                    CascadeClassifier& nestedCascade,
                    double scale, bool tryflip);

//string cascadeName = "haarcascade_eye.xml";
//string cascadeName = "./training/haarcascade_profileface.xml";
string cascadeName = "./training/haarcascade_frontalface_alt.xml";
BufferedPort<Bottle> targetPort;
BufferedPort<ImageOf<PixelRgb> > imagePort;  // make a port for reading images
BufferedPort<ImageOf<PixelRgb> > outPort;

int main(){

    //YARP: variable declaration
    std::cout << "Starting YARP Network" << std::endl;
    Network yarp;
    //BufferedPort<Vector> targetPositionPort;  //public the vector with the position of the face
  // Make a port for reading and writing images


    imagePort.open("/thrive/image/in");  // give the port a name
    outPort.open("/thrive/image/out");
    targetPort.open("/thrive/target/out"); 
    //targetPort.open("/tutorial/target/out");
    //Network::connect("/icubSim/cam/left","/thrive/image/in");	//Simulator Port
    Network::connect("/icub/cam/left","/thrive/image/in");	//Real Robot Port


    //OPENCV: variables declaration
    CvCapture* capture = 0;
    Mat frame, frameCopy, image;
    //const string scaleOpt = "--scale=";
    //size_t scaleOptLen = scaleOpt.length();
    //const string cascadeOpt = "--cascade=";
    //size_t cascadeOptLen = cascadeOpt.length();
    //const string nestedCascadeOpt = "--nested-cascade";
    //size_t nestedCascadeOptLen = nestedCascadeOpt.length();
    //const string tryFlipOpt = "--try-flip";
    //size_t tryFlipOptLen = tryFlipOpt.length();
    //string inputName;
    bool tryflip = false;
    //CascadeClassifier cascade, nestedCascade;
    double scale = 1;


    //LOAD the cascade file
   // cascade.load( cascadeName );

    cvNamedWindow( "result", 1 );


    //std::cout << "Connection with YARP: OK" << std::endl;


    while (1) { // repeat forever
        ImageOf<PixelRgb> *yarp_Image = imagePort.read();  //read an image
        //outImage=*yarp_image;

/*
    //Create the YARP image
    printf("Show a circle for 3 seconds...\n");
    ImageOf<PixelRgb> yarp_Image;
    printf("Creating a YARP image of a nice circle\n");
    yarp_Image.resize(300,200);
    addCircle(yarp_Image,PixelRgb(255,0,0),
              yarp_Image.width()/2,yarp_Image.height()/2,
              yarp_Image.height()/4);
    addCircle(yarp_Image,PixelRgb(255,50,50),
              yarp_Image.width()/2,yarp_Image.height()/2,
              yarp_Image.height()/5);
*/



	//IplImage *cvImage = cvCreateImage(cvSize(yarp_Image.width(), yarp_Image.height()), IPL_DEPTH_8U, 3 );
	   //Copy the YARP image in an opencv image
    	   IplImage *cvImage = cvCreateImage(cvSize(yarp_Image->width(), yarp_Image->height()), IPL_DEPTH_8U, 3 );
    	   cvCvtColor((IplImage*)yarp_Image->getIplImage(), cvImage, CV_RGB2BGR);

    //Window with the opencv image
    //printf("Showing OpenCV/IPL image\n");
    //cvNamedWindow("test",1);
    //cvShowImage("test",cvImage);

    cvWaitKey(10);

	    //OPENCV take the image and send to the detectAndDraw function
            //IplImage* iplImg = cvQueryFrame( capture );
            frame = cvImage;
            if( frame.empty() )
                break;
            if( cvImage->origin == IPL_ORIGIN_TL )
                frame.copyTo( frameCopy );
            else
                flip( frame, frameCopy, 0 );

	    //OPENCV Detect and Draw Function
            //frameCopy

            //detectAndDraw( frameCopy, cascade, nestedCascade, scale, tryflip );



       //Taking back the image from opencv to YARP
       //printf("Taking image back into YARP...\n");
       //ImageOf<PixelBgr> *yarpReturnImage;
       //yarpReturnImage->wrapIplImage(cvImage);

        //ImageOf<PixelRgb> &outImage = outPort.prepare(); //get an output image
        //outImage=*yarpReturnImage;
        //outPort.write();


    }

    cvDestroyWindow("result");

}


  void send_face_center_to_yarp_port(double x, double y, double conf)
  {
    Bottle& output = targetPort.prepare();
    output.clear();
    output.addDouble(x);
    output.addDouble(y);
    output.addDouble(conf);
    targetPort.write();
  }


//------------------------
//Detect and Draw Function
//------------------------
void detectAndDraw( Mat& img, CascadeClassifier& cascade,
                    CascadeClassifier& nestedCascade,
                    double scale, bool tryflip )
{

    double face_X = 0;
    double face_Y = 0;
    double face_conf = 0;
    int i = 0;
    double t = 0;
    vector<Rect> faces, faces2;
    const static Scalar colors[] =  { CV_RGB(0,0,255),
        CV_RGB(0,128,255),
        CV_RGB(0,255,255),
        CV_RGB(0,255,0),
        CV_RGB(255,128,0),
        CV_RGB(255,255,0),
        CV_RGB(255,0,0),
        CV_RGB(255,0,255)} ;
    Mat gray, smallImg( cvRound (img.rows/scale), cvRound(img.cols/scale), CV_8UC1 );

    cvtColor( img, gray, CV_BGR2GRAY );
    resize( gray, smallImg, smallImg.size(), 0, 0, INTER_LINEAR );
    equalizeHist( smallImg, smallImg );

    t = (double)cvGetTickCount();
    cascade.detectMultiScale( smallImg, faces,
        1.1, 2, 0
        |CV_HAAR_FIND_BIGGEST_OBJECT
        |CV_HAAR_DO_ROUGH_SEARCH
        |CV_HAAR_SCALE_IMAGE
        ,
        Size(30, 30) );

    if( tryflip )
    {
        flip(smallImg, smallImg, 1);
        cascade.detectMultiScale( smallImg, faces2,
                                 1.1, 2, 0
                                 |CV_HAAR_FIND_BIGGEST_OBJECT
                                 |CV_HAAR_DO_ROUGH_SEARCH
                                 |CV_HAAR_SCALE_IMAGE
                                 ,
                                 Size(30, 30) );
        for( vector<Rect>::const_iterator r = faces2.begin(); r != faces2.end(); r++ )
        {
            faces.push_back(Rect(smallImg.cols - r->x - r->width, r->y, r->width, r->height));
        }
    }

    t = (double)cvGetTickCount() - t;


    for( vector<Rect>::const_iterator r = faces.begin(); r != faces.end(); r++, i++ )
    {
        Mat smallImgROI;
        vector<Rect> nestedObjects;
        Point center;
        Scalar color = colors[i%8];
        int radius;

        double aspect_ratio = (double)r->width/r->height;

        if( 0.75 < aspect_ratio && aspect_ratio < 1.3 )
        {
            center.x = cvRound((r->x + r->width*0.5)*scale);
            center.y = cvRound((r->y + r->height*0.5)*scale);
            radius = cvRound((r->width + r->height)*0.25*scale);
            circle( img, center, radius, color, 3, 8, 0 );
        }
        else
            rectangle( img, cvPoint(cvRound(r->x*scale), cvRound(r->y*scale)),
                       cvPoint(cvRound((r->x + r->width-1)*scale), cvRound((r->y + r->height-1)*scale)),
                       color, 3, 8, 0);

	//Faces Detected!!!
	face_X = center.x;
	face_Y = center.y;
	face_conf = 1;
	std::cout << "There is a face at X: " << center.x << "; Y: " << center.y << std::endl;
        send_face_center_to_yarp_port(face_X, face_Y, face_conf);

        smallImgROI = smallImg(*r);

/*
        nestedCascade.detectMultiScale( smallImgROI, nestedObjects,
            1.1, 2, 0
            |CV_HAAR_FIND_BIGGEST_OBJECT
            |CV_HAAR_DO_ROUGH_SEARCH
            //|CV_HAAR_DO_CANNY_PRUNING
            |CV_HAAR_SCALE_IMAGE
            ,
            Size(30, 30) );

        for( vector<Rect>::const_iterator nr = nestedObjects.begin(); nr != nestedObjects.end(); nr++ )
        {
            center.x = cvRound((r->x + nr->x + nr->width*0.5)*scale);
            center.y = cvRound((r->y + nr->y + nr->height*0.5)*scale);
            radius = cvRound((nr->width + nr->height)*0.25*scale);
            circle( img, center, radius, color, 3, 8, 0 );

        }
*/


    }

    	printf( "detection time = %g ms\n", t/((double)cvGetTickFrequency()*1000.) );
	//Send the position of the face on a YARP port
        //send_face_center_to_yarp_port(face_X, face_Y, face_conf);


    cv::imshow( "result", img );


}

















