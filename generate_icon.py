"""
图标生成脚本
将 SVG 转换为 ICO 和 PNG 格式
"""
import os
from pathlib import Path

def generate_icon_with_pillow():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("请先安装 Pillow: uv add pillow")
        return False
    
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for size in sizes:
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bg_size = size[0]
        corner_radius = int(bg_size * 0.1875)
        
        draw.rounded_rectangle(
            [0, 0, bg_size - 1, bg_size - 1],
            radius=corner_radius,
            fill=(30, 41, 59, 255)
        )
        
        stroke_width = max(2, int(size[0] * 0.078))
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        ring_width = int(size[0] * 0.25)
        ring_height = int(size[1] * 0.35)
        offset = int(size[0] * 0.09)
        
        bbox1 = [
            center_x - offset - ring_width,
            center_y - ring_height,
            center_x - offset + ring_width,
            center_y + ring_height
        ]
        draw.ellipse(bbox1, outline=(59, 130, 246, 255), width=stroke_width)
        
        bbox2 = [
            center_x + offset - ring_width,
            center_y - ring_height,
            center_x + offset + ring_width,
            center_y + ring_height
        ]
        draw.ellipse(bbox2, outline=(96, 165, 250, 255), width=stroke_width)
        
        center_dot_r = max(3, int(size[0] * 0.04))
        draw.ellipse(
            [center_x - center_dot_r, center_y - center_dot_r,
             center_x + center_dot_r, center_y + center_dot_r],
            fill=(59, 130, 246, 255)
        )
        
        inner_dot_r = max(1, int(size[0] * 0.02))
        draw.ellipse(
            [center_x - inner_dot_r, center_y - inner_dot_r,
             center_x + inner_dot_r, center_y + inner_dot_r],
            fill=(255, 255, 255, 255)
        )
        
        if size[0] >= 32:
            check_size = int(size[0] * 0.12)
            check_x = int(size[0] * 0.78)
            check_y = int(size[1] * 0.22)
            
            draw.ellipse(
                [check_x - check_size, check_y - check_size,
                 check_x + check_size, check_y + check_size],
                fill=(34, 197, 94, 255)
            )
            
            if size[0] >= 48:
                check_mark_size = int(check_size * 0.6)
                draw.line(
                    [(check_x - check_mark_size//2, check_y),
                     (check_x - check_mark_size//4, check_y + check_mark_size//2)],
                    fill=(255, 255, 255, 255), width=max(1, int(size[0] * 0.02))
                )
                draw.line(
                    [(check_x - check_mark_size//4, check_y + check_mark_size//2),
                     (check_x + check_mark_size//2, check_y - check_mark_size//3)],
                    fill=(255, 255, 255, 255), width=max(1, int(size[0] * 0.02))
                )
        
        images.append(img)
    
    ico_path = assets_dir / "icon.ico"
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    print(f"已生成 ICO 文件: {ico_path}")
    
    png_path = assets_dir / "icon.png"
    images[-1].save(png_path, format='PNG')
    print(f"已生成 PNG 文件: {png_path}")
    
    png_32_path = assets_dir / "icon_32.png"
    images[1].save(png_32_path, format='PNG')
    print(f"已生成 PNG (32x32) 文件: {png_32_path}")
    
    return True


if __name__ == "__main__":
    success = generate_icon_with_pillow()
    if not success:
        exit(1)