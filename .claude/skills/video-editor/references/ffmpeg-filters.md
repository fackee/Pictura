# FFmpeg Filter Parameters Quick Reference

## Cutting and Concatenation

### trim / atrim (segment extraction)
```
trim=start=<seconds>:end=<seconds>        Video segment
atrim=start=<seconds>:end=<seconds>       Audio segment
```

### concat (concatenation)
```
[v1][a1][v2][a2]concat=n=2:v=1:a=1[outv][outa]
n=number of segments, v=number of video streams, a=number of audio streams
```

---

## Transitions (xfade)

```
[in1][in2]xfade=transition=<type>:duration=<seconds>:offset=<seconds>
```

**offset** = first segment duration - transition duration (accumulated for multiple segments)

| Parameter value | Effect |
|-----------------|--------|
| `fade` | Cross dissolve |
| `fadeblack` | Fade through black |
| `fadewhite` | Fade through white |
| `dissolve` | Random pixel dissolve |
| `wipeleft/right/up/down` | Four-direction wipe |
| `slideleft/right/up/down` | Four-direction slide |
| `circleopen/close` | Circle expand/collapse |
| `zoomin` | Zoom in |

### Audio crossfade (acrossfade)
```
[a1][a2]acrossfade=d=<seconds>
```

---

## Text and Subtitles

### drawtext
```
drawtext=text='content':fontfile=<path>:fontsize=<size>:fontcolor=<color>
  :x=<expression>:y=<expression>
  :shadowx=2:shadowy=2:shadowcolor=black@0.6
  :enable='between(t,<start>,<end>)'
```

**Position expressions:**
- Horizontal center: `x=(w-text_w)/2`
- Bottom center: `y=h-text_h-50`
- Top right: `x=w-text_w-20:y=20`

**Color formats:** `white`, `yellow`, `#FF0000`, `red@0.8` (with opacity)

### subtitles (burn SRT)
```
subtitles=<file_path>
subtitles=<path>:force_style='FontSize=24,PrimaryColour=&Hffffff'
```

### ass (burn ASS)
```
ass=<file_path>
```

---

## Audio Processing

### volume
```
volume=<ratio>            # 1.0=original, 0.5=half, 2.0=double
volume=<dB>dB            # e.g., volume=6dB
```

### afade (fade in/out)
```
afade=t=in:ss=0:d=<seconds>           Fade in
afade=t=out:st=<start_seconds>:d=<seconds>   Fade out
```

### amix (multi-track mixing)
```
[a1][a2]amix=inputs=2:duration=first:dropout_transition=3
```
- `duration=first`: Use first stream's duration
- `duration=longest`: Use longest duration

### afftdn (noise reduction)
```
afftdn=nr=12:nf=-50:tn=1
```
- `nr`: Noise reduction amount (dB), 0~97, default 12
- `nf`: Noise floor (dBFS), default -50
- `tn=1`: Auto-track noise

### acompressor (dynamic compression)
```
acompressor=threshold=0.125:ratio=6:attack=5:release=50
```

---

## Color Correction

### eq (brightness/contrast/saturation)
```
eq=brightness=<-1~1>:contrast=<0~2>:saturation=<0~3>:gamma=<0.1~10>
```

### colortemperature (color temperature)
```
colortemperature=temperature=<Kelvin>
```
- Neutral: 6500K
- Warm (yellow): 3000~5000K
- Cool (blue): 8000~12000K

### curves (tone curves/presets)
```
curves=preset=<preset_name>
```
Built-in presets: `vintage`, `cross_process`, `darker`, `increase_contrast`,
`lighter`, `linear_contrast`, `medium_contrast`, `negative`,
`strong_contrast`, `color_negative`

Custom curves (red/green/blue channels):
```
curves=r='0/0 0.5/0.6 1/1':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.4 1/1'
```

### colorbalance (color balance)
```
colorbalance=rs=<-1~1>:gs=0:bs=0:rm=0:gm=0:bm=0:rh=0:gh=0:bh=0
```
- `s`=shadows, `m`=midtones, `h`=highlights
- `r/g/b`=red/green/blue channels

### lut3d (LUT file)
```
lut3d=file=<.cube_file_path>
```
Supports `.cube`, `.3dl`, `.dat` formats.

---

## Picture-in-Picture and Overlay

### overlay (picture-in-picture)
```
[bg][ovl]overlay=x=<expression>:y=<expression>:enable='between(t,<s>,<e>)'
```

**Common positions:**
- Top left: `x=10:y=10`
- Top right: `x=W-w-10:y=10`
- Bottom right: `x=W-w-10:y=H-h-10`
- Center: `x=(W-w)/2:y=(H-h)/2`

(Uppercase W/H = background size, lowercase w/h = overlay size)

**Dynamic position (keyframe linear interpolation example):**
```
x='if(lt(t,0),10,if(lt(t,3),10+(200-10)*t/3,200))'
```

### scale
```
scale=w=<width>:h=-1           Scale to specified width maintaining aspect ratio
scale=iw*0.25:ih*0.25       Scale down proportionally to 25%
scale=320:240               Force specific dimensions
```

### colorchannelmixer (adjust alpha opacity)
```
format=rgba,colorchannelmixer=aa=<0.0~1.0>
```

### zoompan (zoom pan animation, Ken Burns effect)
```
zoompan=z='min(zoom+0.001,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=250
```
- `z`: Zoom factor expression (from 1.0 to maximum)
- `d`: Duration in frames

---

## Video Basic Parameters

### Frame rate
```
-r 30              Output frame rate
fps=fps=30         Filter approach
```

### Resolution
```
scale=1920:1080
scale=1920:-1      Maintain aspect ratio
```

### Encoding format
```
-c:v libx264 -crf 23 -preset fast    H.264 encoding (universal)
-c:v libx265 -crf 28                  H.265 encoding (smaller size)
-c:v copy                              No re-encoding (fast, same format only)
-c:a aac -b:a 128k                     AAC audio
```

### Common output parameter combination
```
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k output.mp4
```
