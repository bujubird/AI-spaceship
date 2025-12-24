from PIL import Image, ImageChops

def process_ship_image(input_path, output_path, target_size=(90, 90)):
    # 1. 開啟圖片
    img = Image.open(input_path).convert("RGBA")
    
    # 2. 自動裁切背景 (Auto-Crop)
    # 取得左上角的顏色當作背景色
    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100) # 增強對比以過濾雜訊
    bbox = diff.getbbox()
    
    if bbox:
        img_cropped = img.crop(bbox)
        print(f"原始內容大小: {img_cropped.size}")
    else:
        print("無法偵測到物件，請確認背景是否為純色")
        return

    # 3. 計算放大倍率 (保持比例)
    # 我們希望長邊能夠撐滿 90 像素
    width, height = img_cropped.size
    max_dim = max(width, height)
    scale_factor = target_size[0] / max_dim
    
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    # 4. 執行放大 (關鍵：使用 NEAREST 保持像素風格)
    img_resized = img_cropped.resize((new_width, new_height), resample=Image.NEAREST)
    
    # 5. 建立新的 90x90 畫布並置中貼上
    # 這裡預設背景為透明 (0,0,0,0)，如果需要黑色背景可改成 (0,0,0,255)
    final_img = Image.new("RGBA", target_size, (0, 0, 0, 0)) 
    
    # 計算置中位置
    paste_x = (target_size[0] - new_width) // 2
    paste_y = (target_size[1] - new_height) // 2
    
    final_img.paste(img_resized, (paste_x, paste_y))
    
    # 6. 存檔 (存為 BMP 以符合您的需求)
    final_img.save(output_path)
    print(f"已儲存處理後的圖片至: {output_path}")

# 使用範例
# 請將 'enemy_ship00.jpg' 換成你的檔案路徑
process_ship_image('enemy_ship00.jpg', 'enemy_ship00_fixed.bmp')