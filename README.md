# Computer-Network-Lab-Video-streaming-application
## Folders description
- **Basic** folder contains the code for basic functions (setup, play, pause and tear down)
- **MyExtend1**  contains the extension 1 which calculates some basic statistics like : Data loss rate, total transmitted data, data transmission rate and total time taken 
- **MyExtend2** contains the extension 2 which is merging the set up and play button as well as functions into one button called **PLAY** which means that we remove the SETUP button and the user can now play the video by only using the PLAY button. 

- **MyExtend3** contains the extension 3 which gives a short description about streaming information and many more.

- **MyExtend4** contains the extension 4 which adds move backward and forward buttons (as per the instruction) and a bonus restart button, along with a video progress indicator.



## How to run
1.  First make sure all the files are in the same folder.  
2. Open your terminal and initiate the server by typing the command:
 ```
 python Server.py server_port
 ```
 
 Where **server_port**  is the connection port and you can choose whatever port you want as long as it is > 1024. For example : 
```
python Server.py 8000
```

3. Open another terminal and initiate the client launcher by the command : 

```
python ClientLauncher.py IP_address server_port client_port movie.Mjpeg
```

Again **server_port** is the same port you use for the command above. **client_port** must also be larger than 1024. **IP_address** is the IP address of your running computer. 
For example : 
```
python ClientLauncher.py 192.168.100.4 8000 1234 movie.Mjpeg
```
