# test_music_v2.py - Testing music playback with simplified IPC name
import asyncio
import sys
import shutil
import os

async def test():
    print(f"Checking for mpv: {shutil.which('mpv')}")
    url = "https://music.youtube.com/watch?v=0_L_m0_L_m0"
    
    # Use simple name for mpv arg
    ipc_name = "zerobot-mpv-test" if sys.platform == "win32" else "/tmp/zerobot-mpv-test"
    # Use full path for pipe access
    ipc_full_path = rf"\\.\pipe\{ipc_name}" if sys.platform == "win32" else ipc_name
    
    args = ["mpv", url, "--no-video", "--ytdl-format=bestaudio", "--no-terminal", f"--input-ipc-server={ipc_name}"]
    
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = 0x08000000
        
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
        
        # Wait for mpv to initialize and create the pipe
        await asyncio.sleep(5)
        
        if process.returncode is not None:
            stdout, stderr = await process.communicate()
            print(f"Process exited early with code {process.returncode}")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return

        print(f"Checking for pipe at {ipc_full_path}...")
        if sys.platform == "win32":
             # In Python on Windows, you can't easily 'exists' a pipe with Path.exists()
             # We try to open it
             try:
                 with open(ipc_full_path, 'w') as f:
                     print("Pipe found and writable!")
             except Exception as e:
                 print(f"Pipe not found or not writable: {e}")
        else:
             import Path
             print(f"Socket exists: {os.path.exists(ipc_full_path)}")

        # Wait a bit more
        await asyncio.sleep(5)
        
        # Cleanup
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
