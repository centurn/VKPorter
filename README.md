VKPorter - backup script
========================

Script to back up vk.com alums&wall&comments - based on fork http://meamka.me/VKPorter/
Generates html for each album and for wall, including posts, descriptions, and comments


## Prerequisites

Before you can start using VKPorter you have to install some python libraries if you don't have it.

    $ pip install -r requirements.txt


* ProgressBar ([https://pypi.python.org/pypi/progressbar](https://pypi.python.org/pypi/progressbar))
* Requests ([https://github.com/kennethreitz/requests](https://github.com/kennethreitz/requests))
* VK_API ([https://github.com/python273/vk_api](https://github.com/python273/vk_api))


## Usage

Synopsis:

    $ vkporter.py [-h] [-v] [-b] [-a] [-w] [-o OUTPUT] username

See also `vkporter --help`.

### Examples

$python2.7 vkporter.py -o ../target_dir username -id <numerical vk id> -b

Back up everything (1 folder for each album and for wall)

$python2.7 vkporter.py -o ../target_dir username -id <numerical vk id> -a <album id>

Generate html and download photos for specific album

$python2.7 vkporter.py -o ../target_dir username -id <numerical vk id> -w

Export wall (only)

