import cv2

# Read input video
input_video = cv2.VideoCapture('volleyball_game.mp4')

# Prepare output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_video = cv2.VideoWriter('processed_game.mp4', fourcc, 30.0, (1920, 1080))
