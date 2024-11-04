import requests

# URL of the video
url = "https://vdownload-45.sb-cd.com/1/2/12347394-720p.mp4?secure=CSKZNGcbaiqZ53ZSYeEaNA,1730609795&m=45&d=1&_tid=12347394"

# Send a GET request to the URL
response = requests.get(url, stream=True)

# Check if the request was successful
if response.status_code == 200:
    # Open a local file for writing the video
    with open('downloaded_video.mp4', 'wb') as file:
        # Stream the content in chunks to avoid memory overload
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print("Video downloaded successfully!")
else:
    print(f"Failed to download video. Status code: {response.status_code}")
