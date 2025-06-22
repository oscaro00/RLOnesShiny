import polars as pl

def get_lowest_groups(df_groups: pl.DataFrame, lst_groups: list) -> list:
    lst_lower_groups = []
    lst_groups_copy = lst_groups.copy()

    while len(lst_groups_copy) > 0:
        curr_group = lst_groups_copy[0]

        lst_child_groups = (
            df_groups
            .filter(pl.col('parent_group') == curr_group)
            .select('child_group')
            .to_series()
            .to_list()
        )

        if lst_child_groups == [None]:
            lst_groups_copy.pop(0)
            lst_lower_groups.append(curr_group)
        else:
            lst_groups_copy.pop(0)
            lst_groups_copy.extend([group for group in lst_child_groups if group is not None])
    
    return lst_lower_groups
