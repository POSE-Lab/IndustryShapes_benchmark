# IndustryShapes: An RGB-D dataset for 6D object pose estimation of industrial assembly components and tools

This repository aggregates code for all methods used to evaluate the [IndustryShapes dataset](https://huggingface.co/datasets/POSE-Lab/IndustryShapes) that we introduce in our NeurIPS 2025 submission on the Datasets and Benchmarks track. IndustryShapes is an RGB-D dataset of industrial tools and components designed for both instance-level and novel object 6d pose estimation approaches that features diverse modalities, including static onboarding sequences, complexity of scenes, and meticulous annotations. Indicative samples from training and test scenes can be seen in the figures below. For evaluation, we selected representative state-of-the-art instance-based ([EPOS](https://github.com/thodan/epos), [DOPE](https://github.com/NVlabs/Deep_Object_Pose)) and novel object methods ([FoundPose](https://github.com/facebookresearch/foundpose), [FoundationPose](https://github.com/NVlabs/FoundationPose)). 


## Overview

## Download the dataset
### Using the Hugging Face CLI

```
from datasets import load_dataset
ds = load_dataset("POSE-Lab/IndustryShapes")
```
Note that in the dataset hosted in hf each sample corresponds to one object pose. The train split consists of the IndustryShapes Classic Train set and the Onboardings. The test split consists of the IndustryShapes Classic Test and Extended test sets. 
## Download the dataset in BOP format

Additionally, we provide the data in BOP format inside the ```bop_fromat``` folder which contains:
```
bop_format
├── IndustryShapes_Classic_test.zip
├── IndustryShapes_Classic_train.zip
├── IndustryShapes_Extended_test.zip
├── IndustryShapes_Onboardings_static.zip
└── IndustryShapes_cad_models.zip
```

## Training



## Evaluation



## Pre-trained Models

You can download pretrained models for the instance-based methods here:

- [IndustryShapes weights](https://ntuagr-my.sharepoint.com/:f:/g/personal/mpateraki_ntua_gr/EiOD3lZqKeBLmtQoIF1Rc14BeuKMcOA5jpf7FJMSHOWUWg) 
The `dope` folder includes 5 weights files `obj_<obj_id>.pth`. For EPOS, you should use all files in the `epos` folder. 

## Results

The evaluated methods achieve the following performance on our dataset:

[placeholder]

| Model name         | Top 1 Accuracy  | Top 5 Accuracy |
| ------------------ |---------------- | -------------- |
| My awesome model   |     85%         |      95%       |
 
## Synthetic image generation

We have made the code used for producing the synthetic scenes in our dataset available in a separate GitHub repository [here](https://github.com/POSE-Lab/6DL-PoseGenerator). Please refer to that repository for further instructions. 

