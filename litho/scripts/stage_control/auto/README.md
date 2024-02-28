## Steps to run
- Make sure *BOTH* Arduino, Camera and Motor power are connected
- run `source setup.bash`
- run `python vision_flir_reset.py`
- wait 10 seconds
- run `sudo ./setup.bash`
- run `python vision_flir_setup.py`
- run  C:\\julia\\bin\\julia --project=. --sysimage JuliaSysimage.so main.jl