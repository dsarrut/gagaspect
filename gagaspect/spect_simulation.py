#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from helpers_spect_simulation import make_spect_simulation
from helpers_cmd_line import *

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("json_param", nargs=1)
@click.option("--angle", default=None, help="Spect angle if one single angle")
@click.option(
    "--nogaga",
    is_flag=True,
    default=False,
    help="Do not consider garf info in the json file",
)
@click.option(
    "--nogarf",
    is_flag=True,
    default=False,
    help="Do not consider garf info in the json file",
)
@common_simu_options
def go(
    json_param, output_folder, visu, angle, threads, rad, activity_bq, nogaga, nogarf
):
    # get the param dic structure
    param = read_json_param(json_param)

    # update param from command line
    update_param(param, visu, threads, activity_bq, rad)

    # start transcript
    param.output_folder = Transcript.start(output_folder)

    # angle
    param.angle = angle

    # gaga ? garf ?
    if nogaga:
        param["gaga_pth"] = ""
    if nogarf:
        param["garf_pth"] = ""

    # print param
    print(json.dumps(param, indent=4, sort_keys=False))

    # create the simu
    sim = make_spect_simulation(param)

    # run
    sim.initialize()
    sim.start()

    # print stats at the end
    stats = sim.get_actor("Stats")
    print(stats)
    print(stats.user_info.output)

    # stop transcript
    Transcript.stop()

    # needed ?
    if not nogarf:
        gate.delete_run_manager_if_needed(sim)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
