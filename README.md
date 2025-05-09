# iRemoteEngineer

iRemoteEngineer is a tool to follow, analyze and plan your races in iRacing. Launch the server app on the device of driver that's currently racing and enjoy variety of tools in any place in the world through your browser.

<div align="center">
    <a href="https://www.buymeacoffee.com/iRemoteEngineer">
        <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee">
    </a>
</div>


### How to use 

1. Download the [latest release](https://github.com/matto0O/iRemoteEngineer/releases). Make sure to keep *_internal* in the same directory as the app itself.
2. Launch the app.
3. Set your ngrok authentication token in *Settings* tab. Create your free ngrok account [here](https://dashboard.ngrok.com/signup).
4. Configure all the intervals of data transfer - the more often the data changes, the more internet may be consumed. 
5. If you want to see how the tool looks, select *Start test server*. Otherwise, if you have your iRacing session running, select *Start server*. <br>**Warning**: Your firewall / antivirus *may* block the app, as it exposes your iRacing data to the internet. If you deny the internet access, you will be only able to run the UI within your local network. For those of you that are concerned about the dangers of it (rightly so), the code is fully public.
6. Once the server is running, you will get a server URL address to connect to in step 5. Also, a console may appear. I am working to fix it, but for now, please, don't close it as it shuts down the server.
7. Launch the [UI service](https://iremoteengineer.onrender.com/) in your device of choice - same or different PC, mobile phone or a tablet. Once on the page, enter the URL you got in your server app and hit *Connect*.
8. Remember to set Max Cars to 63 to gather data about all the cars on the track. You can find it in iRacing graphic settings:
<div align="center">
    <img src="screenshots/maxCars.png" alt="Max Cars in graphic settings" style="max-height: 500px;">
</div>
9. Enjoy all the data widgets available.


### Tools on offer

* standings and in-real time tracker

<div align="center">
    <img src="screenshots/trackstrip.png" alt="Standings and Tracker" style="max-height: 500px;">
</div>

* fuel calculator

<div align="center">
    <img src="screenshots/fuel.png" alt="Fuel Calculator" style="max-height: 500px;">
</div>

* current weather monitoring

<div align="center">
    <img src="screenshots/weather.png" alt="Weather" style="max-height: 500px;">
</div>

* tyre data

<div align="center">
    <img src="screenshots/tyres.png" alt="Tyre data" style="max-height: 500px;">
</div>

* event tracker

<div align="center">
    <img src="screenshots/events.png" alt="Events" style="max-height: 500px;">
</div>

* remote pit settings

<div align="center">
    <img src="screenshots/pit.png" alt="Pit commands" style="max-height: 500px;">
</div>