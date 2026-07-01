#!/bin/bash

# download_dataset.sh
# Downloads the IndustryShapes benchmark dataset in BOP format and organizes it 
# appropriately for the BOP Toolkit evaluation.

TARGET_DIR="data/bop_h3"

DOWNLOAD_CLASSIC=false
DOWNLOAD_EXTENDED=false
DOWNLOAD_MODELS=false

if [ "$#" -eq 0 ]; then
    DOWNLOAD_CLASSIC=true
    DOWNLOAD_EXTENDED=true
    DOWNLOAD_MODELS=true
else
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --classic) DOWNLOAD_CLASSIC=true ;;
            --extended) DOWNLOAD_EXTENDED=true ;;
            --models) DOWNLOAD_MODELS=true ;;
            --all) 
                DOWNLOAD_CLASSIC=true
                DOWNLOAD_EXTENDED=true
                DOWNLOAD_MODELS=true
                ;;
            *) echo "Unknown parameter passed: $1"; exit 1 ;;
        esac
        shift
    done
fi

echo "================================================================"
echo " Downloading IndustryShapes Datasets"
echo "================================================================"

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR" || exit

if [ "$DOWNLOAD_CLASSIC" = true ]; then
    echo "1. Downloading IS_Classic Test Set..."
    wget -nc -O IS_Classic.zip "https://huggingface.co/datasets/POSE-Lab/IndustryShapes/resolve/main/bop_format/IndustryShapes_Classic_test.zip?download=true"
fi

if [ "$DOWNLOAD_EXTENDED" = true ]; then
    echo "2. Downloading IS_Extended Test Set..."
    wget -nc -O IS_Extended.zip "https://huggingface.co/datasets/POSE-Lab/IndustryShapes/resolve/main/bop_format/IndustryShapes_Extended_test.zip?download=true"
fi

if [ "$DOWNLOAD_MODELS" = true ]; then
    echo "3. Downloading CAD Models..."
    wget -nc -O CAD_Models.zip "https://huggingface.co/datasets/POSE-Lab/IndustryShapes/resolve/main/bop_format/IndustryShapes_cad_models.zip?download=true"
fi

echo "================================================================"
echo " Extracting and Organizing..."
echo "================================================================"

# Unzip quietly
if [ "$DOWNLOAD_CLASSIC" = true ] && [ -f "IS_Classic.zip" ]; then
    unzip -qo IS_Classic.zip
fi

if [ "$DOWNLOAD_EXTENDED" = true ] && [ -f "IS_Extended.zip" ]; then
    unzip -qo IS_Extended.zip
fi

if [ "$DOWNLOAD_MODELS" = true ] && [ -f "CAD_Models.zip" ]; then
    unzip -qo CAD_Models.zip
fi

# The BOP toolkit parser requires dataset names to be purely alphanumeric/lowercase.
# We rename the extracted folders to match the strict convention.
echo "Renaming folders to lowercase (isclassic, isextended) for BOP toolkit compatibility..."

# Assuming the zip extracts into a folder named IS_Classic (or similar)
# We will use wildcards or explicit checks if the folder name is known
if [ -d "IS_Classic" ]; then
    mv IS_Classic isclassic
elif [ -d "IndustryShapes_Classic_test" ]; then
    mv IndustryShapes_Classic_test isclassic
fi

if [ -d "IS_Extended" ]; then
    mv IS_Extended isextended
elif [ -d "IndustryShapes_Extended_test" ]; then
    mv IndustryShapes_Extended_test isextended
fi

# The models are typically required inside the dataset folder for metrics like ADD
if [ -d "models" ] || [ -d "IndustryShapes_cad_models" ] || [ -d "IndustryShapes_textured_cad_models" ]; then
    MODEL_DIR="models"
    [ -d "IndustryShapes_textured_cad_models" ] && MODEL_DIR="IndustryShapes_textured_cad_models"
    [ -d "IndustryShapes_cad_models" ] && MODEL_DIR="IndustryShapes_cad_models"
    
    echo "Linking CAD models to dataset directories..."
    if [ -d "isclassic" ]; then
        ln -sfn "../$MODEL_DIR" isclassic/models
        ln -sfn "../$MODEL_DIR" isclassic/models_eval
    fi
    if [ -d "isextended" ]; then
        ln -sfn "../$MODEL_DIR" isextended/models
        ln -sfn "../$MODEL_DIR" isextended/models_eval
    fi
fi

# Optional: clean up zip files to save space
# rm IS_Classic.zip IS_Extended.zip CAD_Models.zip

echo "================================================================"
echo "✅ Dataset Download and Setup Complete!"
echo ""
echo "You can now export your BOP_PATH like this:"
echo "export BOP_PATH=\$(pwd)"
echo "================================================================"
