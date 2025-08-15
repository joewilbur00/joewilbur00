# Melanoma Detection with a Convolutional Neural Network 

This project uses a dataset of melanoma images to detect whether it is benign or malignant. I built two Convolutional Neural Networks (CNNs) and used transfer learning techniques to build another model on top of a pretrained one. 

## Key Components
- Used torchvision transformations on training and testing images to feed throught neural networks. 
- Built a simple 3 block CNN with Stochastic Gradient Descent as the optimizer and CrossEntropyLoss as the loss function. 
- Built a second model that implements Dropout, a Learning Rate Scheduler and Early Stopping using the same architecture, optimizer and loss function as before.
- Used a pretrained model (resnet18) and unforze the classifier head to pass training and testing images through. 

## Purpose
To predict whether an image of melanoma is benign or malignant.

## Tools Used
- Python (Numpy, Matplotlib, PyTorch, SciKit-Learn)
- Convultional Neural Network and pretrained resnet18 model
