# Creating Bus Routes Using CNN

Source code and output of my MSc Dissertation for my AI MSc in the University of Edinburgh (2018/19).
It received a grade of 77/100 (A3). Further information can be found in the report file.

## Abstract

Due to the increased demand for bus service in recent years, bus agencies are
forced to constantly improve their network through costly and time-consuming procedures. In our research, we propose two methodologies which, given an image of
the available road network, automatically generate bus routes. The first method implements the Generative Adversarial Network (GAN) architecture of pix2pix.
Its target is to generate plausible images of bus routes given a road network image.
The second method aims to determine which pixels in the road network image belong to a bus route using a convolutional auto-encoder called U-Net. Our results
show that the GAN is unable to create plausible routes due to the imbalance of foreground/background in the target images. The average travel time of random trips using
the routes generated by U-Net is only about 1 minute longer (3% higher) of the average
travel time using manually designed routes. Its test set precision is 19% and recall is
44%. In the process of creating our dataset of bus route images, we also produce the
first clean bus route dataset in the General Transit Feed Specification (GTFS) format.