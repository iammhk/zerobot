# test_music.py - Testing music playback with IPC
import asyncio
import sys
import shutil

async def test():
    print(f"Checking for mpv: {shutil.which('mpv')}")
    url = "https://music.youtube.com/watch?v=0_L_m0_L_m0" # Some random music url
    ipc_path = r"\\.\pipe\zerobot-mpv-test" if sys.platform == "win32" else "/tmp/zerobot-mpv-test"
    args = ["mpv", url, "--no-video", "--ytdl-format=bestaudio", "--no-terminal", f"--input-ipc-server={ipc_path}"]
    
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = 0x08000000 # CREATE_NO_WINDOW
        
    print(f"Running: {' '.join(args)}")
    try:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs
        )
        print(f"Process started with PID {process.pid}")
        
        # Wait a bit
        await asyncio.sleep(10)
        
        if process.returncode is not None:
            stdout, stderr = await process.communicate()
            print(f"Process exited early with code {process.returncode}")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
        else:
            print("Process still running. Music should be playing.")
            # Try to stop it
            if sys.platform == "win32":
                 import subprocess as sp
                 sp.run(["taskkill", "/F", "/T", "/PID", str(process.pid)])
            else:
                 process.terminate()
            print("Cleanup done.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
