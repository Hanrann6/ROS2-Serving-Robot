import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/rann/projects/ROS2-Serving-Robot/install/cafe_serving_robot'
