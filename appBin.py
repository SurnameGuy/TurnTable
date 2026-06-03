import webview, yt_dlp, mpv, threading, random, locale
from os import environ as osEnviron
from os import _exit as os_Exit
from os import path as osPath
from sys import platform as sysPlatform
from sys import argv as sysArgv
from time import sleep
from sys import _MEIPASS as sys_MEIPASS
from os import path as osPath

try:
    locale.setlocale(locale.LC_NUMERIC, 'C')
except Exception:
    pass

def resource_path(relative_path):
    try:
        basePath = sys_MEIPASS
    except Exception:
        basePath = osPath.abspath(".")

    return os.path.join(base_path, relative_path)

if sysPlatform.startswith('linux'):
    import ctypes
    try:
        ctypes.CDLL('libX11.so.6').XSetWMProperties
    except Exception:
        pass

osEnviron["QT_LOGGING_RULES"] = "qt.accessibility.atspi.warning=false,qt.qpa.services.*=false"
osEnviron["LC_NUMERIC"] = "C.UTF-8"
osEnviron["LC_ALL"] = "C.UTF-8"

baseDir = osPath.dirname(osPath.abspath(__file__))
hissFile = osPath.join(baseDir, "assets", "hiss.mp3")
crackleFile = osPath.join(baseDir, "assets", "crackle.mp3")

vinylFilter = "lowpass=f=6000,highpass=f=80,equalizer=f=200:width_type=h:width=400:gain=2,equalizer=f=4000:width_type=h:width=2500:gain=-5"

def mpvLogger(logLevel, component, message):
    if logLevel in ['error', 'fatal']:
        print(f"[MPV -> {component}] {logLevel.upper()}: {message}")
player = mpv.MPV(video=False, log_handler=mpvLogger)
playerHiss = mpv.MPV(video=False, log_handler=mpvLogger)
playerCrackle = mpv.MPV(video=False, log_handler=mpvLogger)
player['audio-pitch-correction'] = 'no'
player.volume = 100
playerHiss.loop_playlist = 'inf'
playerHiss.volume = 150
playerCrackle.loop_playlist = 'inf'
playerCrackle.volume = 120

try:
    playerHiss.play(hissFile)
    playerHiss.pause = True
    
    playerCrackle.play(crackleFile)
    playerCrackle.pause = True
except Exception as e:
    print(f"[CRITICAL ERROR] Failed to load local files into MPV: {e}")

@player.property_observer('idle-active')
def observeIdle(name, value):
    if value:
        playerHiss.pause = True
        playerCrackle.pause = True
        if getattr(api, 'window', None):
            api.window.evaluate_js("onMusicStop();")

def vinylSkipLoop():
    while True:
        waitTime = random.uniform(15.0, 80.0)
        sleep(waitTime)
        
        if not player.pause and player.time_pos is not None and player.time_pos > 2.0:
            repeats = random.randint(1, 3)
            skipBackTime = random.uniform(0.5, 2.0)
            print(f"[VINYL EFFECT] Needle skipped! Repeating section of {skipBackTime:.2f}s for {repeats} times.")
            
            for _ in range(repeats):
                if player.pause:
                    break
                    
                try:
                    player.command('seek', f'-{skipBackTime:.4f}', 'relative', 'exact')
                    sleep(skipBackTime)
                except Exception as e:
                    print(f"[ERROR] Native skip failed: {e}")
                    break

def vinylPitchBendLoop():
    while True:
        waitTime = random.uniform(8.0, 16.0)
        sleep(waitTime)
        
        if not player.pause and player.time_pos is not None:
            targetSpeed = random.uniform(0.985, 1.015)
            
            if abs(targetSpeed - 1.0) < 0.004:
                continue
                            
            steps = 20          
            stepDelay = 0.03    
            
            currentSpeed = 1.0
            speedDelta = (targetSpeed - 1.0) / steps
            for _ in range(steps):
                if player.pause:
                    break
                currentSpeed += speedDelta
                player.speed = currentSpeed
                sleep(stepDelay)
            
            oscillationTime = random.uniform(1.0, 2.5)
            print(f"[VINYL EFFECT] Motor oscillation! Changing speed and pitch to {targetSpeed:.3f} for {oscillationTime} seconds!")
            sleep(oscillationTime)
            steps = 6          
            stepDelay = 0.05
            currentSpeed = 1.0
            speedDelta = (targetSpeed - 1.0) / steps
            for _ in range(steps):
                if player.pause:
                    break
                currentSpeed += speedDelta
                player.speed = currentSpeed
                sleep(stepDelay)
            
            sleep(oscillationTime)
            for _ in range(steps):
                if player.pause:
                    break
                currentSpeed -= speedDelta
                player.speed = max(0.5, currentSpeed)  
                sleep(stepDelay)
                
            player.speed = 1.0

class Api:
    def __init__(self):
        self.window = None
        
    def onDOMContentLoaded(self):
        if len(sysArgv) > 1:
            return {'url': sysArgv[1]}
        
    def processURL(self, inputValue):
        if "watch?v=" in inputValue:
            inputValue = inputValue.split("&list=")[0].split("&index=")[0]
        
        ydlOpts = {'format': 'bestaudio', 'quiet': True, 'js_runtimes': {'node': {'path': None}}}

        try:
            with yt_dlp.YoutubeDL(ydlOpts) as ytdl:
                info = ytdl.extract_info(inputValue, download=False)
                audioUrl = info['url']
                thumbnailUrl = info.get('thumbnail')  
            
            player.command('af', 'set', vinylFilter) 
            player.play(audioUrl)
            player.pause = False
            
            playerHiss.pause = False
            playerCrackle.pause = False
            
            
            return {'status': True, 'message': '', 'thumbnail': thumbnailUrl}
        except Exception as e:
            print(f"[ERROR YTDL/MPV] {str(e)}")
            return {'status': False, 'message': f'Error: {str(e)}'}
            
    def togglePause(self):
        player.pause = not player.pause
        playerHiss.pause = player.pause
        playerCrackle.pause = player.pause
                
        if self.window:
            if player.pause:
                self.window.evaluate_js("onMusicStop();")
            else:
                self.window.evaluate_js("onMusicPlaying();")
                
    def searchYouTube(self, query):
        query = query.strip()
        if not query:
            return []
        if query.startswith("http://") or query.startswith("https://") or ".com/" in query or "youtube.com" in query or "youtu.be" in query:
            return []
        
        ydlOpts = {
            'format': 'bestaudio', 
                'quiet': True, 
                'extract_flat': True,
                'js_runtimes': {'node': {'path': None}}
        }
        
        try:
            with yt_dlp.YoutubeDL(ydlOpts) as ytdl:
                info = ytdl.extract_info(f"ytsearch10:{query}", download=False)
                results = []
                
                if 'entries' in info:
                    for entry in info['entries']:
                        videoID = entry.get('id')
                        results.append({
                            'title': entry.get('title'),
                                'url': f"https://www.youtube.com/watch?v={videoID}",
                                'thumbnail': f"https://img.youtube.com/vi/{videoID}/mqdefault.jpg",
                                'channelName': entry.get('uploader') or entry.get('channel')
                        })
                return results
        except Exception as e:
            print(f'[ERROR] Error while searching videos: {str(e)}')
            return []

def onAppClose():
    os_Exit(0)

if __name__ == '__main__':
    api = Api()
    skipThread = threading.Thread(target=vinylSkipLoop, daemon=True)
    skipThread.start()
    pitchThread = threading.Thread(target=vinylPitchBendLoop, daemon=True)
    pitchThread.start()
    window = webview.create_window('TurnTable', 'index.html', js_api=api, width=600, height=400)
    api.window = window
    
    def onStart():
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        
        qtApp = QApplication.instance()
        if qtApp:
            qtApp.setApplicationName('turntable')
            qtApp.setDesktopFileName('.turntable_temp.desktop')
            iconPath = osPath.join(baseDir, 'assets', 'icon.png')
            if osPath.exists(iconPath):
                qtApp.setWindowIcon(QIcon(iconPath))
                
    window.events.closed += onAppClose
    webview.start(onStart, gui='qt')
