"""FFmpeg film looks shared by the storyboard and the shot renderer.
past    - black and white archival: high contrast, lifted blacks, heavy grain, vignette
present - warm highlights / teal shadows, slightly lower saturation, soft roll-off, light grain
night   - like present but keeps the warm lamps, deeper blacks
"""
LOOKS = {
    'past': ("hue=s=0,eq=contrast=1.3:brightness=-0.02,"
             "curves=all='0/0.05 0.3/0.25 0.7/0.75 1/0.92',noise=alls=16:allf=t+u,vignette=PI/3.6"),
    'present': ("eq=contrast=1.08:saturation=0.9:gamma=0.98,"
                "colorbalance=rs=-0.05:gs=-0.01:bs=0.06:rm=0.02:bm=-0.02:rh=0.06:gh=0.02:bh=-0.05,"
                "curves=all='0/0.03 0.25/0.22 0.75/0.79 1/0.95',noise=alls=7:allf=t+u,vignette=PI/4.5"),
    'night': ("eq=contrast=1.12:saturation=0.95:gamma=0.95,"
              "colorbalance=rs=-0.04:bs=0.07:rh=0.05:bh=-0.04,"
              "curves=all='0/0.02 0.3/0.24 0.75/0.8 1/0.96',noise=alls=8:allf=t+u,vignette=PI/4"),
}
