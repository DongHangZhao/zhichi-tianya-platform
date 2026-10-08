'''
Author: your name
Date: 2026-01-11 02:46:11
LastEditTime: 2026-01-11 02:46:11
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\simple_thumbnail_generator.py
'''
# -*- coding: utf-8 -*-
"""
简化版的视频缩略图生成器，仅使用OpenCV和Pillow，无需Flask依赖
"""
import os
import cv2
import random
from PIL import Image


def extract_frame_as_thumbnail(video_path, output_path, frame_number=None):
    """
    从视频中提取指定帧作为缩略图
    
    Args:
        video_path: 视频文件路径
        output_path: 输出缩略图路径
        frame_number: 要提取的帧号，如果为None则随机选择
    """
    try:
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"无法打开视频文件: {video_path}")
            return False
        
        # 获取视频总帧数
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if total_frames <= 0:
            print(f"视频文件无帧数据: {video_path}")
            cap.release()
            return False
        
        # 如果未指定帧号，则随机选择一个中间段的帧
        if frame_number is None:
            # 选择视频中间80%部分的随机帧，避免开头结尾的黑屏
            start_frame = int(total_frames * 0.1)
            end_frame = int(total_frames * 0.9)
            frame_number = random.randint(start_frame, end_frame)
        else:
            frame_number = min(frame_number, total_frames - 1)
        
        # 设置视频读取位置到指定帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # 读取帧
        ret, frame = cap.read()
        if not ret:
            print(f"无法读取视频帧: {video_path}, 帧号: {frame_number}")
            cap.release()
            return False
        
        # 转换BGR到RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 转换为PIL图像
        pil_image = Image.fromarray(frame_rgb)
        
        # 调整尺寸（保持原始宽高比，但限制最大尺寸）
        max_size = (400, 400)
        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 保存图像
        pil_image.save(output_path, 'JPEG', quality=85, optimize=True)
        
        cap.release()
        print(f"成功从视频 {video_path} 提取第 {frame_number} 帧作为缩略图: {output_path}")
        return True
    except Exception as e:
        print(f"提取缩略图时出错 {video_path}: {str(e)}")
        return False


def generate_thumbnails_for_real_videos():
    """为现有的真实视频生成缩略图"""
    videos_dir = os.path.join('static', 'uploads', 'videos')
    
    # 获取所有真实视频文件
    real_videos = []
    for filename in os.listdir(videos_dir):
        if filename.startswith('real_video_') and filename.endswith('.mp4'):
            real_videos.append(filename)
    
    print(f"找到 {len(real_videos)} 个真实视频文件:")
    for video in real_videos:
        print(f"  - {video}")
    
    # 为每个视频生成缩略图
    for video_filename in real_videos:
        video_path = os.path.join(videos_dir, video_filename)
        
        # 生成缩略图文件名
        base_name = os.path.splitext(video_filename)[0]
        thumb_filename = f"{base_name}_auto_thumb.jpg"
        thumb_path = os.path.join(videos_dir, thumb_filename)
        
        print(f"\n正在为视频 {video_filename} 生成缩略图...")
        if extract_frame_as_thumbnail(video_path, thumb_path):
            print(f"✓ 成功生成缩略图: {thumb_filename}")
        else:
            print(f"✗ 生成缩略图失败: {thumb_filename}")


if __name__ == '__main__':
    print("开始为真实视频生成缩略图...")
    generate_thumbnails_for_real_videos()
    print("\n缩略图生成完成！")