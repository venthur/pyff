The P300Layout folder contains a number of classes specifying a 
particular spatial layout (i.e., screen coordinates) of the elements 
in your visual P300 speller.  

Some standard layouts (e.g., matrix, circular) are provided here, but
you can easily make your own layout by defining a member variable 
termed 'positions', which is just a list of xy-tuples. Each tuple 
represents the screen coordinates of a single element. 

If you define your own layout, please keep in mind that the center of 
your layout has to be (0,0). Later on, your speller is centered on 
the screen by your VisualP300 instance. 