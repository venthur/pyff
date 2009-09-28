The P300VisualElement folder contains a number of classes specifying a 
particular visual element (such as a letter or a bitmap) that can be used
in your P300 speller.

The standard elements provided here should be fine for most applications.
If you want to define your own element, though, use the suggestions provided
below.

All elements are derived from the base class VisualElement. This class 
implements the basic functionality for any kind of element that is used in a 
P300 paradigm. If you define your own subclass, it should inherit from
VisualElement.  
Note that each instance of VisualElement (or one of its subclasses) represents
exactly one element (eg, the letter "A"). If your P300 speller consists of a
6x6 matrix of elements, you will thus need 36 instances.

VisualElement uses the pygame engine. It is derived from the pygame class Sprite. 
A Sprite is a very versatile graphical object that has an image property (self.image) 
specifying how it looks like and a rect property (self.rect) specifying its size 
and position.

Starting from this, VisualElement introduces the concept of a STATE. In
each P300 paradigm, the elements change from one state into another when they 
are highlighted. For instance, in the classical P300 paradigm, elements consist
of letters and each letter can take one of two different states. Usually, the 
letter is in state 0, which means that it is not flashed and has a dark 
color. When it is flashed, the letter turns to state 1 for the duration of the 
flash.

The VisualElement class provides a generalization of this principle. It allows 
to use

* any kind of element (not only letters)
* any number and combination of features (not only color, but also size, orientation etc)
* any number of states (in particular, more than the two classical states)

### For each state, a separate image and rect is provided. If the state
is changed, self.image and and self.rect are simply set to the values of 
the corresponding state.


How to use a subclass in your P300 speller
------------------------------------------
Most functionality is automatized. In fact, all you need to do is to before using
an element is to specify the states. 

To USE these elements in your own P300 speller, the steps are as follows:

* Make a new instance of your visual element. 
  Specify the position of the center of the element and some basic features
  that are not changed during the flashes, for instance:
  my_letter = P300Text(text="A",size=10,pos=(100,100))
* Specify the distinct states by using set_states, for instance:
  Read the description of the function set_states in the 
  VisualElement class for more details

How to define your own subclass
-------------------------------
If you define your own subclass, you can best start off by copying one of the 
existing classes. Then you have to
* Override the __init__ method, provided standard values and setting your 
  own member variables
* Override the refresh method wherein you specify the graphical object according
  to specific features
If you finished your new class, run TestIt.py to test it ;)
