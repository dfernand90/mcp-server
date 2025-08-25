
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ColorClip
import os
import json
import random

def files_from_directory(directory_path):
        file_list = []
        try:
            # Get all entries (files and directories) in the specified path
            for entry in os.listdir(directory_path):
                full_path = os.path.join(directory_path, entry)
                # Check if the entry is a file
                if os.path.isfile(full_path):
                    file_list.append(full_path)
        except FileNotFoundError:
            print(f"Error: Directory not found at '{directory_path}'")
        except Exception as e:
            print(f"An error occurred: {e}")
        return file_list

def video_assmbly(script_id, help_script_id = None):
    script_path = f"./scripts/{script_id}/script_object.json"
    output_file_path = f"./scripts/{script_id}/presentation.mp4"
    # Load JSON
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenes = data.get("scenes", {})

    # Prepare final video clips
    final_clips = []

    video_folder_path = f"./scripts/{script_id}/video"
    # extract all videos of the path in list   

    video_clips_path = files_from_directory(video_folder_path)
    video_clips = []
    try:
        for video_path in video_clips_path:
            print(f'video path: {video_path}')
            video_clip = VideoFileClip(video_path)
            video_clips.append(video_clip)
    except Exception as e:
        print(f"error unpacking assets of script {script_id} because of {e} \n proceeding with general assets id: {help_script_id}")      

    if help_script_id:
        helper_video_folder_path = f"./scripts/{help_script_id}/video"
        helper_video_clips_path = files_from_directory(helper_video_folder_path)
        for video_path in helper_video_clips_path:
            print(f'video path: {video_path}')
            video_clip = VideoFileClip(video_path)
            video_clips.append(video_clip)

    for scene_number, scene_data in scenes.items():        
    #for scene_number, scene_data in list(scenes.items())[:1]:

        scene_audio = scene_data.get('narration')
        scene_video = scene_data.get('video') 
        captions = scene_audio.get('narration')
        video_path = scene_video.get('video path')
        audio_path = scene_audio.get('audio path')
        duration = scene_data.get('duration')
        print(f"Processing scene: {scene_number}")
        print(f"Video path: {video_path},\n Audio path: {audio_path},\n Duration: {duration}")
        print("-" * 40)
        if not os.path.exists(audio_path):
            print(f"Missing files for scene: {scene_number}")
            continue

        #video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)

        # Loop video to match audio duration
        #loop_count = int(duration // video_clip.duration) + 1
        video_clips_scene =[]
        # pick loop_count random videos from video_clips    
        total_duration = 0
        while total_duration < duration:
            index = random.randint(0, len(video_clips) - 1)
            clip = video_clips[index]
            video_clips_scene.append(clip)
            total_duration += clip.duration

        looped_video = concatenate_videoclips(video_clips_scene).subclipped(0, duration)

        # Split narration into lines
        caption_lines = captions.strip().split('\n') if '\n' in captions else captions.strip().split('. ')
        caption_clips = []

        # Calculate caption box height (20% of video height)
        caption_height = int(looped_video.size[1] * 0.2)
        caption_width = int(looped_video.size[1] * 0.8)

        # Create background box
        background = ColorClip(size=(caption_width, caption_height), color=(0, 0, 0))
        background = background.with_opacity(0.6).with_duration(duration).with_position(('center', 'bottom'))
        
        
        # Calculate proportional durations
        char_counts = [len(line.strip()) for line in caption_lines]
        total_chars = sum(char_counts)
        start_time = 0

        for i, line in enumerate(caption_lines):
            line_duration = (char_counts[i] / total_chars) * duration
            end_time = start_time + line_duration

            line_clip = TextClip(
                'verdana',
                line.strip(),
                font_size=24,
                color='white',                
                method='caption',
                size=(caption_width, caption_height)
            ).with_start(start_time).with_end(end_time).with_position(('center', 'bottom'))
            caption_clips.append(line_clip)
            start_time = end_time

        # Combine background and text lines
        caption_layer = [background] + caption_clips

        # Overlay captions on video
        video_with_caption = CompositeVideoClip([looped_video] + caption_layer)

        # Set audio
        final_video = video_with_caption.with_audio(audio_clip)
        final_clips.append(final_video)

    # Combine all scenes
    if final_clips:
        final_video = concatenate_videoclips(final_clips)
        final_video.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
        print(f"✅ Video created: {output_file_path}")
    else:
        print("No valid scenes to process.")

if __name__ == "__main__":
    script_id_2 = 2865556207773740
    #script_id = 3505613520637456
    script_id = 7763706767490112
    video_assmbly(script_id, help_script_id =script_id_2)