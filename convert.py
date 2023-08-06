from PIL import Image
import cv2,nfp,dfpwm,ffmpeg,sys,os,io
import soundfile as sf

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python convert.py <input video> <resolution> <fps>")
        exit(1)

    video = sys.argv[1]
    resolution = tuple(map(int, sys.argv[2].split("x")))
    fps = int(sys.argv[3])

    cap = cv2.VideoCapture(video)

    # Convert audio to dfpwm
    data = ffmpeg.input(video).output("pipe:1", format='wav').run(capture_stdout=True, capture_stderr=True)[0]
    data, samplerate = sf.read(io.BytesIO(data))
    audio_data = dfpwm.convert_audio(data, samplerate)
    with open('audio.dfpwm', 'wb') as f:
        f.write(audio_data.getvalue())

    # Calculate frame skip
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_skip = int(original_fps / fps)

    # Read frames
    frames = []
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if frame_count % frame_skip == 0:
                frames.append(frame)
            frame_count += 1
        else:
            break

    # Resize frames
    frames = [cv2.resize(frame, resolution) for frame in frames]

    # Convert frames to nfp
    nfp_frames = []
    for frame in frames:
        nfp_frames.append(nfp.img_to_nfp(Image.fromarray(frame)))

    # Write nfp frames to file
    with open("video.nfv", "wt") as f:
        f.write(f"{resolution[0]} {resolution[1]} {fps}\n")
        f.write("\n".join(nfp_frames))