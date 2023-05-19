import sys
import pandas as pd
import numpy as np

df = pd.read_csv(sys.argv[1])
print(df)

# 必須なカラム名は以下
# root_dir p_index mode puckid pinid sample_name wavelength raster_vbeam raster_hbeam att_raster hebi_att exp_raster dist_raster loopsize score_min score_max maxhits total_osc
# osc_width ds_vbeam ds_hbeam exp_ds dist_ds dose_ds offset_angle reduced_fact ntimes meas_name cry_min_size_um cry_max_size_um hel_full_osc hel_part_osc raster_roi warm_time

essential_cols = "root_dir p_index mode puckid pinid sample_name wavelength raster_vbeam raster_hbeam att_raster hebi_att exp_raster dist_raster loopsize score_min score_max maxhits total_osc osc_width ds_vbeam ds_hbeam exp_ds dist_ds dose_ds offset_angle reduced_fact ntimes meas_name cry_min_size_um cry_max_size_um hel_full_osc hel_part_osc raster_roi warm_time".split()


print(essential_cols)

# CSVファイル一行、つまり、pandasのDataFrameの一行ずつについて必須カラムがあるかどうかを調べる
for index, row in df.iterrows():
    for col in essential_cols:
        if col not in row:
            print("NG")
            print(row)
            sys.exit(1)

print("Required columns are OK")

# オプションフラグは以下
# zoomcap_flag
# cover_scan_flag
# ln2_flag
# ago_flag
# 条件
# ago_flag　があるときには ago_offsetがないといけない

option_flag = "zoomcap_flag cover_scan_flag ln2_flag ago_flag".split()

# CSVファイル一行、つまり、pandasのDataFrameの一行ずつについてオプションフラグがあるかどうかを調べる
# また条件を満たすかどうかも調べる
 
for index, row in df.iterrows():
    print(f"row index: {index}")
    for col in option_flag:
        if col in row:
            if col == "ago_flag":
                if "ago_offset" not in row:
                    print("Complicated cases")
            else:
                print(f"optional flag {col} is OK")
        else:
            print(f"{col} is not in row")