from PIL import Image
import math

# 原始太空船圖片
img_path = "ChatGPT Image 2025年11月20日 下午08_00_43.png" # 請確保檔名正確
img = Image.open(img_path).convert("RGBA")

# 1. 計算新的統一畫布大小
# 為了讓旋轉後的圖片不被裁切且不縮放，畫布大小應該是圖片的「對角線」長度
w, h = img.size
diagonal = int(math.ceil(math.sqrt(w**2 + h**2))) #畢氏定理算出對角線
canvas_size = (diagonal, diagonal) 
cx, cy = canvas_size[0] // 2, canvas_size[1] // 2

# 旋轉設定
num_directions = 16
angle_step = 360 / num_directions

print(f"原始尺寸: {img.size}")
print(f"新生成的畫布尺寸 (足以容納旋轉): {canvas_size}")

for i in range(num_directions):
    angle = i * angle_step

    # 創建透明背景 (使用計算出的足夠大的尺寸)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    
    # 2. 旋轉圖片
    # expand=True 會自動擴大旋轉後的邊界以容納整張圖
    rotated = img.rotate(angle, expand=True, resample=Image.Resampling.NEAREST)
    
    # 3. 移除 resize 步驟，直接計算置中座標
    rx, ry = rotated.size
    paste_pos = (cx - rx // 2, cy - ry // 2)
    
    # 貼上圖片
    canvas.paste(rotated, paste_pos, rotated)
    
    # 儲存為 PNG
    canvas.save(f"ship_{i:02d}.png", format="PNG")

print("16 張俯視太空船透明 PNG（保持原始比例）已生成完成！")