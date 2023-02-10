<div align="center">
    <h1>FeeDex</h1>
</div>
<div align="center">
    <p>A MangaDex pull notification program made with Python for Windows 10 & 11</p>
</div>
<br></br>
<br></br>

## Introduction
I created this project because I was tired of forgetting to check mangas, and given that the MangaDex team has far more pressing issues than implementing an RSS feed or push notification system, I decided to take matters into my own hands.

### State of Things
At the moment, this program is a roughish beta. I've tested it enough to make sure it works, but I haven't done any extensive bug search, so expect things to break.

### Getting Help
When problems do arise, create a bug report on the issues tab.


## Functionality and Features
### First Time Use
When you're using this program for the first time, the first thing you need to do is run the `FeeDex Main.exe` program. This, as succinctly put by the title, is the primary manner of interacting with the program. Subscribing to new mangas, removing unwanted subscriptions, and other functionalities yet to be added will be all be done through it.

Once you run the program, a terminal/console window will show up. I made the menu and prompts to be as succint and clear, and the least error-prone as possible, so just read what the window shows to you and act accordingly. After doing it, in the folder that the program is located, a JSON name `manga_notification_settings.json` will appear. Make sure you leave that alone, otherwise you can mess with it in such a way that for the program to work again, you'll have to delete the JSON and start over, as if it's the first time.

### Listening for Updates
The program that will check for new chapters of subscribed mangas and throw notifications when they are updated, is `FeeDex Sonar.exe`. Unlike with main.exe, sonar will not create a terminal/console window. It runs completely on the background, so to initialize it, you need to manually start the program, or schedule Windows to run it on startup by doing the following steps:

1. Right click `FeeDex Sonar.exe`, copy, then right click an empty part of the folder and then click "paste as a shortcut";
2. Cut (Ctrl + X) the shortcut;
3. Press Win + R, then type `shell:startup`, then hit enter;
4. Paste the shortcut into the folder that just openned;
5. You're done.

### Future Features
- Feature to pull list of mangas to subscribe straight from a user's follows.
- Better G/UI. 

## Contributing
I welcome any contributions to this project, as long as the instructions contained in the code by way of comments and function's descriptions are followed; most pressingly, though, is a better UI or way of implementing a menu than how I did it.
