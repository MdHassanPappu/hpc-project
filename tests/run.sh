module load env/testing/2023b

module load devel/ReFrame/4.7.4-GCCcore-13.2.0

# rm -rf ~/hpc-project/scripts/bind_*.sh
rm -rf ~/hpc-project/reframe-output/*
rm -rf ~/hpc-project/stage/*
rm -f ~/hpc-project/reports/osu-benchmark.json

reframe --config-file ulhpc.py --checkpath 4.1-OSU-BENCHMARK-ONESIDE-TEST.py --name 'OSUPlacementTest' --run --report-file=reports/osu-benchmark.json
