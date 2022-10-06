#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import opengate as gate
import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("stat_files", nargs=-1)
def go(stat_files):
    print(f'Reading {len(stat_files)} stats files')

    stat = gate.read_stat_file(stat_files[0])
    for file in stat_files[1:]:
        s = gate.read_stat_file(file)
        stat.counts.run_count += s.counts.run_count
        stat.counts.event_count += s.counts.event_count
        stat.counts.track_count += s.counts.track_count
        stat.counts.step_count += s.counts.step_count
        stat.counts.duration += s.counts.duration
        if stat.user_info.track_types_flag and s.user_info.track_types_flag:
            for t in stat.counts.track_types:
                if t in s.counts.track_types:
                    stat.counts.track_types[t] = int(stat.counts.track_types[t]) + int(
                        s.counts.track_types[t]
                    )

    print(stat)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
