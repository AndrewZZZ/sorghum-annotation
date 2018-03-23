# sorghum-annotator
## Dependency 
  * python 3.x
  * wxpython
  * Packages you may not have:
    1. numpy
    2. scipy
    3. matplotlib
    3. lxml
    4. PIL or Pillow
    
To install all the dependencies:
```sh
pip install wxpython numpy scipy matplotlib lxml Pillow
```
For ubuntu 16.04 with GTK3 the best way to install wxPython is:
```sh
pip install -U \
-f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 \
wxPython
```
## Installation 
```sh
git clone https://github.com/Andrewzhzy/sorghum-annotator.git
python ./main.py
```
## Usage
Overall, this software is for hierarchy sorghum annotation. We assume all sorghums have only one stem and several leaves. To annotate one sorghum, you should start from the stem, then leaves.
###  Image import
To import images, put the images under the images folder.
###  Stem annotation
We assume the shape of all sorghum stems are quadrilateral. To mark out the stem, just click the 4 corners of the stem.
###  Leaves annotation
There are two set of tools to help you mark out leaves:  **magic wand** and **lasso**.
There are 3 different type of magic wand that you can use to annotate leaves:
1. New leaf

	Use this tool when you want to add a new leaf for a specific stem/sorghum. 
1. Leaf region add

	Use this tool when you want to add a region to a specific leaf area.
1. Leaf region minus

	Use this tool when you want to remove a region to a specific leaf are.

To use leaf magic wand. slide the threshold bar to adjust the threshold and click somewhere at the middle of a leaf.

Currently there's only one lasso too that you can use it for leaf region minus. To use lasso tool, select the leaf in the annotation workspace and draw the area that you want to remove from that area.

### 3. Annotation management
To remove a leaf or sorghum, select it in **Annotation** and press **DEL**.
