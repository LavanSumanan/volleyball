import tkinter as tk
from tkinter import filedialog
import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
import threading
import os


WIDTH = 1280
HEIGHT = 720


def find_max_video_number(folder_path):
    max_number = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            # Extract the number from the filename
            try:
                number = int(filename.split('.')[0])
                max_number = max(max_number, number)
            except ValueError:
                continue  # Ignore files that don't follow the "x.mp4" format
    return max_number


print('current active clip #', find_max_video_number("vids/model/train/active"))
print('current dead clip #', find_max_video_number("vids/model/train/dead"))


def play_video(video_path):
    def draw_frame(cap):
        ret, frame = cap.read()
        if not ret:
            return False

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = tk.PhotoImage(
            master=canvas, data=cv2.imencode('.ppm', frame)[1].tobytes())
        canvas.image = frame
        canvas.create_image(0, 0, image=frame, anchor=tk.NW)
        # Update timestamp in textbox
        current_pos = cap.get(cv2.CAP_PROP_POS_MSEC) / \
            1000  # Current timestamp in seconds
        timestamp_var.set(f"Timestamp: {current_pos:.2f} seconds")
        return True

    def update_frame():
        nonlocal cap, playing
        while playing:
            if not paused:
                shouldExit = not draw_frame(cap)
                if shouldExit:
                    break
            root.update()

    def on_key(event):
        nonlocal cap, mode, left, right
        if event.char == 'q':
            cap.release()
            cv2.destroyAllWindows()  # Destroy all OpenCV windows (if any)
            root.quit()
            root.destroy()
        elif event.keysym == "space":
            toggle_play_pause()
        elif event.char == 'p':
            rewind_slow()
        elif event.char == '[':
            rewind_fast()
        elif event.char == ']':
            forward_fast()
        elif event.char == '\\':
            forward_slow()
        elif event.char == 'a':
            if mode == 'active':
                mode = 'dead'
            else:
                mode = 'active'
            mode_var.set(f'Current mode: {mode}')
        elif event.char == 'd':
            current_pos = cap.get(cv2.CAP_PROP_POS_MSEC)
            left = current_pos
            left_var.set(f'left ts: {left/1000:.2f}s')
        if event.char == 'f':
            current_pos = cap.get(cv2.CAP_PROP_POS_MSEC)
            right = current_pos
            right_var.set(f"right ts: {current_pos/1000:.2f}s")
        elif event.keysym == 'Return':
            save()

    def save():
        nonlocal left, right
        print('ENTERED SAVE with ', left, right)
        # fix bug where left is negative when it starts at t=0 + convert to seconds
        t1 = max(0, left) / 1000
        t2 = right / 1000

        print('CALCULATED t1 and t2 as ', t1, t2)
        print('condition', t2 > t1)

        if t2 > t1:
            output_path = f"vids/model/train/{mode}/{find_max_video_number(f'vids/model/train/{mode}') + 1}.mp4"
            with VideoFileClip(video_path) as video:
                new = video.subclipped(t1, t2)
                new.write_videofile(output_path, audio_codec='aac')
            print(f"Output saved to {output_path}")
        else:
            print(
                f"Invalid timestamps: {left, right}.\n\
                Press 'd' and 'f' to mark timestamps.")

    def set_frame(new_frame):
        nonlocal cap
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        draw_frame(cap)
        root.update()

    def rewind_fast():
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        new_frame = max(0, current_frame - 100)  # Move one hundred frames back
        set_frame(new_frame)

    def rewind_slow():
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        new_frame = max(0, current_frame - 20)  # Move twenty frames back
        set_frame(new_frame)

    def forward_slow():
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        new_frame = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1,
                        current_frame + 20)  # Move twenty frames forward
        set_frame(new_frame)

    def forward_fast():
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        new_frame = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1,
                        current_frame + 100)  # Move one hundred frames forward
        set_frame(new_frame)

    root = tk.Tk()
    root.title("Video Player")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    # Add textbox to display current timestamp
    timestamp_var = tk.StringVar()
    timestamp_var.set("Timestamp: 0.00 seconds")
    timestamp_label = tk.Label(
        root, textvariable=timestamp_var, font=("Helvetica", 12))
    timestamp_label.pack(side=tk.RIGHT)

    mode = 'dead'
    mode_var = tk.StringVar()
    mode_var.set(f'Current mode: {mode}')
    mode_label = tk.Label(
        root, textvariable=mode_var, font=("Helvetica", 12))
    mode_label.pack(side=tk.RIGHT)

    right = 0
    right_var = tk.StringVar()
    right_var.set(f'right ts: {right/1000:.2f}s')
    right_label = tk.Label(
        root, textvariable=right_var, font=("Helvetica", 12))
    right_label.pack(side=tk.RIGHT)

    left = 0
    left_var = tk.StringVar()
    left_var.set(f'left ts: {left/1000:.2f}s')
    left_label = tk.Label(
        root, textvariable=left_var, font=("Helvetica", 12))
    left_label.pack(side=tk.RIGHT)

    play_button = tk.Button(root, text="Play/Pause (SPACE)",
                            command=lambda: toggle_play_pause())
    play_button.pack(side=tk.LEFT)
    rewind_slow_button = tk.Button(
        root, text="R (P)", command=rewind_slow)
    rewind_slow_button.pack(side=tk.LEFT)
    rewind_button = tk.Button(
        root, text="RR ([)", command=rewind_fast)
    rewind_button.pack(side=tk.LEFT)
    forward_button = tk.Button(
        root, text="FF (])", command=forward_fast)
    forward_button.pack(side=tk.LEFT)
    forward_slow_button = tk.Button(
        root, text="F (\)", command=forward_slow)
    forward_slow_button.pack(side=tk.LEFT)

    toggle_mode_button = tk.Button(
        root, text="Toggle Mode (A)", command=lambda: on_key('a'))
    toggle_mode_button.pack(side=tk.LEFT)

    left_button = tk.Button(
        root, text="Left (D)", command=lambda: on_key('d'))
    left_button.pack(side=tk.LEFT)
    right_button = tk.Button(
        root, text="Right (F)", command=lambda: on_key('f'))
    right_button.pack(side=tk.LEFT)
    save_button = tk.Button(
        root, text="Save (Return)", command=save)
    save_button.pack(side=tk.LEFT)

    playing = True
    paused = False

    def toggle_play_pause():
        nonlocal paused
        paused = not paused

    root.bind("<Key>", on_key)

    cap = cv2.VideoCapture(video_path)

    threading.Thread(target=update_frame, daemon=True).start()

    root.mainloop()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # filename = filedialog.askopenfilename(title="Select Video File", filetypes=[
    #                                       ("Video Files", "*.mp4;*.avi;*.mov;*.M4V")])
    filename = 'vids/model/train/raw/IMG_4768.M4V'

    if filename:
        play_video(filename)
