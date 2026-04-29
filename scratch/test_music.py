# test_music.py - Script to test MusicTool functionality
# This is a temporary script to verify that the agent can search and play music.

import asyncio
import os
import sys

# Add the project root to sys.path so we can import zerobot
sys.path.append(os.getcwd())

from zerobot.agent.tools.music import MusicTool

async def main():
    tool = MusicTool()
    
    print("Searching for 'Trains by Porcupine Tree'...")
    search_result = await tool.execute(action="search", query="Trains by Porcupine Tree")
    print(search_result)
    
    # Try to extract the first video ID
    import re
    match = re.search(r"ID: ([a-zA-Z0-9_-]+)", search_result)
    if match:
        video_id = match.group(1)
        print(f"\nFound video ID: {video_id}. Starting playback...")
        play_result = await tool.execute(action="play", video_id=video_id)
        print(play_result)
        
        print("\nMusic should be playing now. Waiting 10 seconds before stopping...")
        await asyncio.sleep(10)
        
        print("Stopping playback...")
        stop_result = await tool.execute(action="stop")
        print(stop_result)
    else:
        print("\nCould not find a video ID in search results.")

if __name__ == "__main__":
    asyncio.run(main())
