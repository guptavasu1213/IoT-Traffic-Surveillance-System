from PIL import Image, ImageStat


def brightness( im_file ):
   im = Image.open(im_file).convert('L')
   stat = ImageStat.Stat(im)
   return stat.rms[0]

print(brightness('luminous-photos/vlcsnap-2020-07-19-18h41m57s936.png'))
print(brightness('luminous-photos/vlcsnap-2020-07-19-18h42m28s554.png'))
print(brightness('luminous-photos/vlcsnap-2020-07-19-18h42m36s613.png'))