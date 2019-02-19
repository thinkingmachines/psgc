import pandas as pd


def get_padding(level):
    level = int(level)
    if level > 3:
        return 0
    return 9 - 2 * level


def add_level(row):
    for level in [1, 2, 3]:
        if row["Code"].endswith("0" * get_padding(level)):
            return level
    return 4


def get_parent(padding):
    def apply(row):
        if get_padding(row["Level"]) > padding:
            return
        i = -padding if padding else None
        return row["Code"][:i].ljust(9, "0")

    return apply


def merge_level(df, level):
    padding = get_padding(level)
    df[level] = df.apply(get_parent(padding), axis=1)
    return df.merge(
        df[df["Code"] == df[level]][["Code", "Name"]].drop_duplicates("Code"),
        how="left",
        left_on=level,
        right_on="Code",
        suffixes=["", "_" + level],
        validate="m:1",
    ).drop(columns=[level])


def clean():
    df = pd.read_excel(
        "raw/PSGC_Publication_Sept2018.xlsx", sheet_name="PSGC", dtype=str
    )
    df = df[["Code", "Name"]]
    df["Level"] = df.apply(add_level, axis=1)
    df = merge_level(df, "1")
    df = merge_level(df, "2")
    df = merge_level(df, "3")
    df = merge_level(df, "4")
    df = df.merge(pd.read_csv("raw/zipcodes.csv", dtype=str), on="Code")
    df.fillna("").to_csv("psgc.csv", index=False)


if __name__ == "__main__":
    clean()
