### Getting started with nix 
In order to get started with nix you need to only install the package manager.

Follow these instructions from the nix website: 
https://nixos.org/download/

If you are on wsl and are simply using a root as users do the multiuser installation. 
After installation is completed edit this file with you prefered text editor.

``` nano /etc/nix/nix.conf```
or 
``` vi /etc/nix/nix.conf```

Then added this line to the file:
```experimental-features = nix-command flakes```


### After the above^ steps are done:

You need to access the directory called `deploy/nix` where flake.nix is located

you can do this by  

```
cd deploy/nix

nix develop .
```
