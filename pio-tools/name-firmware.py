Import("env")

import os
import shutil
import pathlib
import tasmotapiolib
from os.path import join
from colorama import Fore, Back, Style
from datetime import datetime

def bin_map_copy(source, target, env):
    firsttarget = pathlib.Path(target[0].path)
    now = datetime.now().strftime('%Y_%m%d_%H%M%S')
    # get locations and file names based on variant
    map_file = tasmotapiolib.get_final_map_path(env)
    bin_file = tasmotapiolib.get_final_bin_path(env)
    one_bin_file = bin_file
    firmware_name = env.subst("$BUILD_DIR/${PROGNAME}.bin")

    if env["PIOPLATFORM"] == "espressif32":
        if("safeboot" in firmware_name):
            SAFEBOOT_SIZE = firsttarget.stat().st_size
            if SAFEBOOT_SIZE > 851967:
                print(Fore.RED + "!!! Tasmota safeboot size is too big with {} bytes. Max size is 851967 bytes !!! ".format(
                        SAFEBOOT_SIZE
                    )
                )
        if("safeboot" not in firmware_name):
            factory_tmp = pathlib.Path(firsttarget).with_suffix("")
            factory = factory_tmp.with_suffix(factory_tmp.suffix + ".factory.bin")
            one_bin_tmp = pathlib.Path(bin_file).with_suffix("")
            one_bin_file = one_bin_tmp.with_suffix(one_bin_tmp.suffix + ".factory_"+now+ ".bin")

    # check if new target files exist and remove if necessary
    for f in [map_file, bin_file, one_bin_file]:
        if f.is_file():
            f.unlink()
    
    bin_file_directory = os.path.dirname(bin_file)
    for file in os.listdir(bin_file_directory):
        full_path = os.path.join(bin_file_directory, file)
        if file.endswith(".bin"):
            os.remove(full_path)
            #print(f"Deleted file: {full_path}")
    
    # copy firmware.bin and map to final destination
    shutil.copy(firsttarget, bin_file)
    original_bin_file = bin_file
    new_bin_file = os.path.join(os.path.dirname(bin_file), f'tasmota32c3_{now}.bin')
    os.rename(original_bin_file, new_bin_file)

    if env["PIOPLATFORM"] == "espressif32":
        # the map file is needed later for firmware-metrics.py
        shutil.copy(tasmotapiolib.get_source_map_path(env), map_file)
        if("safeboot" not in firmware_name):
            shutil.copy(factory, one_bin_file)
    else:
        map_firm = join(env.subst("$BUILD_DIR")) + os.sep + "firmware.map"
        shutil.copy(tasmotapiolib.get_source_map_path(env), map_firm)
        shutil.move(tasmotapiolib.get_source_map_path(env), map_file)
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", bin_map_copy)
