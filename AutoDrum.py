import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import librosa
import librosa.display
import IPython.display as ipd
from glob import glob
import sounddevice as sd
import scipy.io.wavfile

#Interact with the user
print("Hey! Thanks for using this tool, I hope it will help you out, but first we need to settle some things:")
path = input("First, tell me the path of your audio file: ")
svol = float(input("How loud should the snare sound? (it multiplies the default volume): "))
kvol = float(input("How loud should the kick sound? (it multiplies the default volume): "))
hvol = float(input("How loud should the hi-hat sound? (it multiplies the default volume): "))
pattern = input("Give a pattern of drums divided by spaces and write the value of the drum sounds at the same time (none=000, snare=001, kick=010, hihat=100): ").split(" ")

#Initialize
guitar, rate = librosa.load(path)
kick, krate = librosa.load("kick.wav")
snare, srate = librosa.load("snare.wav")
hihat, hrate = librosa.load("hi-hat.wav")
notes = []

#Change the sr with volume so it doesnt mess up the pitch --> we dont need that if you really think bout it
def changeVolume(audio, sr, multiplier):
    for i in range(len(audio)):
        audio[i]=audio[i]*multiplier
    return audio

snare = changeVolume(snare, srate, svol)
kick = changeVolume(kick, krate, kvol)
hihat = changeVolume(hihat, hrate, hvol)
#Normalize volume for any guitar records
guitar = changeVolume(guitar, rate, 0.8/np.max(guitar))#default 0.8

#Normalize sample rates
def normalizeSR(audio, sr, new_sr):
    changeRate = round(sr/new_sr)
    new_audio = []
    i=0
    while i < len(audio):
        new_audio.append(audio[i])
        i+=changeRate 
    return new_audio

if rate<srate and rate<krate and rate<hrate:
    snare = normalizeSR(snare, srate, rate)
    srate = rate
    kick = normalizeSR(kick, krate, rate)
    krate = rate
    hihat = normalizeSR(hihat, hrate, rate)
    hrate = rate
elif srate<rate and srate<krate and srate<hrate:
    guitar = normalizeSR(guitar, rate, srate)
    rate = srate
    kick = normalizeSR(kick, krate, srate)
    krate = srate
    hihat = normalizeSR(hihat, hrate, srate)
    hrate = srate
elif krate<rate and krate<srate and krate<hrate:
    snare = normalizeSR(snare, srate, krate)
    srate = krate
    guitar = normalizeSR(guitar, rate, krate)
    rate = krate
    hihat = normalizeSR(hihat, hrate, krate)
    hrate = krate
elif hrate<rate and hrate<srate and hrate<krate:
    snare = normalizeSR(snare, srate, hrate)
    srate = hrate
    guitar = normalizeSR(guitar, rate, hrate)
    rate = hrate
    kick = normalizeSR(kick, krate, hrate)
    krate = hrate

def merge(original, tomerge, position):
    for i in range(len(tomerge)):
        try:
            original[position+i]=(original[position+i]+tomerge[i])/2#Try avarage instead of the bigger value

        except:
            return original
    return original

#Trim
kick = kick[1000:3000]
snare = snare[1800:5000]
hihat = hihat[:4000]

i=0
while i < len(guitar):
    #Detect notes
    try:
        if(abs(guitar[i+1])-abs(guitar[i])>0.1):
            if len(notes)!=0:
                notes.append(round((notes[len(notes)-1]+i)/2)) #Add mid-note drum
            notes.append(i)
            i+=round(2000*(rate/22050)) #2000 seems kinda perfect and multiply so can handle lower/higher samplerates
        i+=5
    except:
        break

print("Number of detected notes: "+str(len(notes)))

#Fill in the notes
patternLength = len(pattern)
for i in range(len(notes)-1):
    if pattern[i%patternLength][2] == "1":
        guitar = merge(guitar, snare, notes[i])
    if pattern[i%patternLength][1] == "1":
        guitar = merge(guitar, kick, notes[i])
    if pattern[i%patternLength][0] == "1":
        guitar = merge(guitar, hihat, notes[i])

sd.default.samplerate = rate
sd.play(guitar)

pd.Series(guitar).plot(figsize=(10, 5),
                       lw=1,
                       title='Raw Audio Example')
plt.show(block=False)

save = input("Now you can hear and see the result. Are you satisfied with it?[y/n] ")

if save=="n":
    print("I'm sorry to hear that. Maybe you should try to use a better quality audio or change some settings. See you next time!")
else:
    print("I hoped to hear that! You can find your fresh audio here: "+path.split(".wav")[0]+"_AutoDrummed.wav")
    scipy.io.wavfile.write(path.split(".wav")[0]+"_AutoDrummed.wav", rate, guitar)

#TO-DO:
# - testing (kinda nice for now)
# - same sample rate for all audio lines --> getting messy, and kind of useless (due to same samplerate), but I think its kinda working
# - more responsivity (same volume) --> done yaaay
# - hi-hats --> done yaaay
# - nth notes for kicks, snares and hi-hats (doing it) --> done
# - clean up code --> done
# - userfriendly modifications --> more customable (done)
# - make a new wav file from it and save it (kinda okay, maybe a bit loud)
# - advanced customisation (freaking done)
# - finishing touches to make it public (need to download the 3 drum wav with this code)