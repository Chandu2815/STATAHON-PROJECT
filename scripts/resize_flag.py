from PIL import Image
src = 'app/static/images/indian_flag_waving.jpg'
dst = 'app/static/images/indian_flag_waving@2x.png'
img = Image.open(src).convert('RGBA')
size = max(img.size)
bg = Image.new('RGBA', (size, size), (255,255,255,0))
bg.paste(img, ((size - img.width)//2, (size - img.height)//2))
out = bg.resize((240,240), Image.LANCZOS)
out.save(dst, format='PNG', optimize=True)
print('saved', dst)
