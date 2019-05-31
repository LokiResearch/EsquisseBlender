

# How to install

## 1] Installing dependencies

### 1.1] CGAL
Esquisse uses [CGAL](https://www.cgal.org) to export SVG files.
We need to build a wrapper to call specific functions in python.
#### Installing CGAL
* Install CGAL using HomeBrew or MacPorts on your computer
#### Building the wrapper
* Install swig using HomeBrew or MacPorts on your computer
* go in folder **wrapper_cgal** and run Makefile
**Warning:** Be carefull to match the python version called by Makefile and the python version of Blender
#### Install the wrapper into Esquisse
* copy **mycgal.py** and **mycgal.so** into **/code/Esquisse/cgal**

### 1.2] svg.path
Esquisse uses [svg.path](https://pypi.org/project/svg.path/) to export SVG files.
#### Getting svg.path
* Install svg.path using pip
#### Installing Polygon3 into Esquisse
* Copy **parser.py** and **path.py** into the folder **/code/Esquisse/svg**.



### 1.3] Polygon3
Esquisse uses [Polygon3](https://pypi.org/project/Polygon3/) to export SVG files.
#### Getting Polygon3
* Install Polygon3 using pip
**Warning:** Be carefull to match the python version of Polygon3 and the python version of Blender
#### Installing Polygon3 into Esquisse
* Copy **Polygon.so, Utils.py** and **__init__.py**  into the folder **code/Esquisse/Polygon**.


### 1.4] OpenCV
Esquisses uses [OpenCV](https://pypi.org/project/pyopencv/) to manipulate images.
#### Getting OpenCV
* Install pyopencv using pip
#### Installing Polygon3 into Esquisse
* Copy the content of folder **cv2**  from the pip installation into the folder **/code/Esquisse/cv2**.


### 1.5] LeapMotion (optional)
Esquisses uses [LeapMotion](https://www.leapmotion.com) to manipulate 3D hands.
#### Getting LeapMotion library
* Download **Leap.h**, **LeapMath.h**, **Leap.i** and **libLeap.dylib** from the LeapMotion website.
* Put these file into **wrapper_LeapMotion**
#### Building the wrapper
* go in folder **wrapper_LeapMotion** and run Makefile
**Warning:** Be carefull to match the python version called by Makefile and the python version of Blender
#### Installing the wrapper into Esquisse
* copy **Leap.py**, **libLeap.dylib** and **Leap.so** into **/code/Esquisse/LeapMotion**


## 2] Installing the add-on in Blender  
### Creating the add-on
Simply create a zip of the **code/Esquisse** folder
### Installing the add-on in Blender
Open Blender preferences (Cmd ,) and Add-ons tab. Click on "Install Add-on from file"  and choose created the zip file.
Then click on the checkbox to enable Esquisse  
**Warning:** if Esquisse was already installed in Blender, first de-install it by clicking the remove button. It is not compulsory but you can experience side-effects otherwise.


# If you know nothing about Blender

* Watch the [Selection tool](https://cloud.blender.org/p/blender-inside-out/560414b7044a2a00c4a6da9b) video tutorial (first half)
* then watch the [Transform tool](https://cloud.blender.org/p/blender-inside-out/560414b7044a2a00c4a6da9c) video tutorial








