from pytube import YouTube

yt = YouTube('https://youtu.be/7mkZVj4Hmsk?si=400C3m0ZfOgYeuOJ')
stream = yt.streams.get_highest_resolution()
stream.download()
