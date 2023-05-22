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
# racket_offset
# racket_offset があればオフセットしてセンタリング→ループサイズのSSROXをやる

option_flags = "zoomcap_flag cover_scan_flag ln2_flag racket_offset roi_offset roi_v roi_h".split()

# CSVファイル一行、つまり、pandasのDataFrameの一行ずつについてオプションフラグがあるかどうかを調べる
# また条件を満たすかどうかも調べる
 
for index, row in df.iterrows():
    print(f"row index: {index}")
    # 各行ごとに optional_flags のカラムがあるかどうかを確認していく
    # optional_flagsの内容によって、確認するべき事項がある
    # racket_offset は loopsize よりも小さい値でなければ致命的なエラー
    # racket_offset は　正の数
    # roi_offset, roi_v, roi_h は正の数であり、これらは同時に３つ定義されていなければならない
    # つまり、roi_offsetがあるならば、roi_v, roi_hもある
    # 逆に、roi_v, roi_hがあるならば、roi_offsetもある
    for flag in option_flags:
        if flag in row:
            print(f"flag {flag} is found")
            if flag == "racket_offset":
                print(f"racket_offset is {row[flag]}")
                # 致命的なエラー
                if row[flag] >= row["loopsize"]:
                    print(f"racket_offset {row[flag]} is larger than loopsize {row['loopsize']}")
                    sys.exit(1)
                if row[flag] < 0:
                    print(f"racket_offset {row[flag]} is negative")
                    sys.exit(1)
            else:
                print(f"flag is {flag}")
            if flag == "roi_offset":
                if "roi_v" not in row or "roi_h" not in row:
                    print(f"NG:roi_offset is defined but roi_v or roi_h is not defined")
                    sys.exit(1)
                else:
                    print(f"OKAY: roi_offset is defined and roi_v, roi_h are also defined")
        else:
            print(f"flag {flag} is not found")