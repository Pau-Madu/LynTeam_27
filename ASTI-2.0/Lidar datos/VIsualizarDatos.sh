#!/bin/bash
echo "Vamos a visualizar los datos del lidar en metros"
ros2 topic echo /scan --field ranges | python3 -c "import sys; [print(x.strip(', ')) for line in sys.stdin for x in line.replace('[','').replace(']','').split() if 'nan' not in x]"
