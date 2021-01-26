# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

: ${1?"Usage: $0 <.blend file>"}


case "$OSTYPE" in
  darwin*)  blender_path=/Applications/blender_2.79.app/Contents/MacOS/ ;; 
  linux*)   echo "please set the blender path for LINUX" ;;
  bsd*)     echo "please set the blender path for BSD" ;;
  msys*)    echo "please set the blender path for WINDOWS" ;;
  *)        echo "please set the blender path for $OSTYPE" ;;
esac

$blender_path/blender $1 -P start_addon.py