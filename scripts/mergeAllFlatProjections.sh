#!/bin/bash
for inputDir in "$@"; do
    submit_job.py condorSubmit --scriptExe --inputDirectory $inputDir --useAFS --vsize 6000 --filesPerJob 9999  $(basename $inputDir)-merge DevTools/Plotter/scripts/mergeFlatProjection.py
done
