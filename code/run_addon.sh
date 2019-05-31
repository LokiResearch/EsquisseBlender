: ${1?"Usage: $0 blend_file"}


case "$OSTYPE" in
  darwin*)  blender_path=/Applications/blender.app/Contents/MacOS/ ;; 
  linux*)   echo "please set the blender path for LINUX" ;;
  bsd*)     echo "please set the blender path for BSD" ;;
  msys*)    echo "please set the blender path for WINDOWS" ;;
  *)        echo "please set the blender path for $OSTYPE" ;;
esac


# --background
# blend_folder=../scene_tests
# for blend_file in $blend_folder/*.blend
# do
#     $blender_path/blender $blend_file -p 700 0 2500 2880 -P start_addon.py 
# done



$blender_path/blender $1 -p 700 0 2500 2880 -P start_addon.py
# $blender_path/blender $1 -p 700 0 1500 2000 -P start_addon.py
# $blender_path/blender $1 -P start_addon.py
