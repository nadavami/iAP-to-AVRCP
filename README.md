# iAP to AVRCP

## What is this?
This is my terrible answer to not being able to change the current song from my steering wheel in my 2012 Hyundai Elantra.

## What does it do?
It (is supposed to) act as a bridge between Bluetooth (AVRCP) and the Apple iPod Accessory Protocol (iAP). 

## Should I use it?
No. You're honestly better off just changing the head unit in your car.

## Can I use it?
You're free to do whatever<sup>[1]</sup> you want with this. All I ask is that you don't judge me for the terrible code written within. I just wanted to change the damn song. 

<sub>1. Well almost whatever you want, just [read the license](LICENSE). <sub>
  
## How do I use it?

### Things you'll need
1. An Orange Pi Zero + MicroSD card
2. A USB Bluetooth Adapter
3. A 2012ish Hyunadi
4. [Ansible](https://docs.ansible.com/ansible/latest/index.html)
4. Lots of patience 

### Installation
1. Flash the MicroSD card with Armbian
2. Configure /boot/armbian-first-run.txt to connect to WiFi on first boot
3. SSH (user: root pass: 1234), CTRL-C to abort creating a new user (bad but we're lazy so this will all run as root)
4. apt install python3 -y
6. Edit hosts in this project file to IP of Orange Pi
7. Run playbook (ansbile-playbook ansible-playbook.yml -u root -k -i hosts)

