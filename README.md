# POTSBLIZ - Plain Old Telephone Service Beyond Local IP Stack

(C)2015 - Norbert Huffschmid

http://blog.long-exposure.net/

POTSBLIZ is licensed under GPLv3.

# Raspberry Pi basics

Download the latest Raspian Jessie image and write it to your SD-card as
described [here](http://www.raspbian.org/).

Power-on your Raspberry with keyboard, mouse and monitor connected. First make
sure that it boots to CLI and not to desktop:

	Menu->Preferences->Raspberry Pi Configuration)
	
Configure the correct keyboard layout, timezone and locale settings. Finally
expand the filesystem on your SD-card and reboot.

Update your Raspberry Pi to the latest software and firmware:

    $ sudo apt-get update
    $ sudo apt-get upgrade
    $ sudo rpi-update

# POTSBLIZ installation

All POTSBLIZ software is Open Source and available at
[Github](https://github.com/long-exposure/potsbliz-src).
For the software installation you need a git client on your Raspberry Pi:

    $ sudo apt-get install git

Installation goes like this:

    $ git clone git://github.com/long-exposure/potsbliz-src.git
    $ cd potsbliz-src
    $ chmod +x install
    $ sudo ./install

The install procedure can take more than one hour because there are lots of
packages to install and compile. Progress is visible on the terminal screen,
so be patient and leave your Raspberry Pi alone until installation is
complete.

For testing purposes you need an USB sound card, e.g.
[one of these](http://elinux.org/RPi_VerifiedPeripherals#USB_Sound_Cards)
(the Creative Sound Blaster Play worked fine) and a headset that gets connected
to it. Reboot the Raspberry Pi and listen to the audio output. After a
successful startup, a computer voice should tell you the URL of the
administration interface.

# POTSBLIZ configuration

Configuration is done via a web interface:

    http://<IP address of your Raspberry Pi>/

The admin interface is password protected. You have to enter your standard login
credentials (e.g. pi/raspberry).

There are four tabs for the configuration tasks:

## Speed dial

Speed dialing is useful especially for rotary phones as it facilitates the
dial procedure. Speed dial shortcuts are arbitrary digit combinations from
1 to 3 digits, that are mapped to the actual phone numbers.

Don't use speed dial numbers that a identical or similar to special numbers
e.g. emergency call numbers!

## Bluetooth

POTSBLIZ supports calls via your smartphone by using the bluetooth
hands-free-profile. For bluetooth connectivity your Raspberry Pi must have a
bluetooth dongle as described
[here](http://elinux.org/RPi_USB_Bluetooth_adapters). The Lindy dongle
(WLAN/Bluetooth) worked fine.

To establish a connection with your smartphone the very first time, you have to
run the pairing procedure:

* Check the "Search new devices" checkbox
* Make your smartphone visible for new bluetooth connections
* Wait until POTSBLIZ has detected your smartphone and shows it in its device list
* Press the "Connect" button
* Confirm the pairing request on your smartphone
* Wait until pairing has completed

Once a pairing process has successfully finished, POTSBLIZ will connect to your
smartphone automatically, whenever it comes within reach. As long as there is
an active bluetooth connection established, POTSBLIZ will use it for outgoing
calls, i.e. bluetooth has priority over SIP.

## SIP account

POTSBLIZ supports call setup via SIP. Enter the following data as told by your
SIP/VoIP provider:
* SIP ID
* Outgoing proxy
* Password

Modification of SIP data requires a reboot.

# First call

Calls can be received and established by the dialpad on top of the web
interface. Make sure that the USB soundcard and the headset is connected. When
you press the green call button you should hear a dialtone. After pressing the
red hangup button the dialtone should terminate.

For an internal testcall simply press # followed by the call button. You should
hear an announcement that tells the Raspberry Pi's current IP address.

## Incoming call

Make sure that you have either entered a valid SIP configuration or paired your
smartphone via bluetooth as described above.

### Incoming bluetooth call

Make sure that the bluetooth connection to your smartphone is active. (The
bluetooth configuration tab  shows a blue indicator). Lay aside your
smartphone.

Call your smartphone number from some other phone. Your smartphone will ring as
usual. Put on your headset on and press the green button. The smartphone should
terminate ringing and you should be able to talk with the caller via the
Raspberry Pi.

### Incoming SIP call

Put on your headset and call your SIP number from some other phone. You should
hear a ringtone on the headset. Press the green button and you should be able
to talk with the caller via the Raspberry Pi.

## Outgoing call

If some incoming call was successful, it makes no difference whether you
establish an outgoing call via SIP or bluetooth. Enter the destination number
on the dialpad and press the green button. The call should be established and
you should be able to talk with the called party via the Raspberry Pi.

# Call control via command line interface

There is command line tool available, that allows call setup like this:

    $ sudo potsbliz -h
    $ sudo potsbliz offhook
    $ sudo potsbliz dial 08154711
    $ sudo potsbliz onhook

POTSBLIZ has been designed strongly modular and allows easy integration of
custom plugins. The command line tool is meant as a demo, how you can integrate
your own Raspberry Pi telephone project into POTSBLIZ. The source code of the
command line tool can be found in the python/potsbliz/plugin/console directory.

# Security

Instead of "raspberry" you should choose a really SECURE password for pi
(and other sudoable users)! Be aware that your Raspberry Pi will be able to
establish arbitrary chargeable calls. You have been warned!

Whenever you have changed your pi user's password via _passwd_ or whatever,
you have to enter this new password on the admin web interface.

# Troubleshooting

In case of errors you might find valueable information in the
/var/log/messages or /var/log/syslog files.

# Disclaimer

The POTSBLIZ software is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the
[GNU General Public License](http://www.gnu.org/licenses/gpl-3.0.en.html) for
more details.
