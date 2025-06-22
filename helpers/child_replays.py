import polars as pl

def get_lowest_groups(df_groups: pl.DataFrame, lst_groups: list) -> list:
    lst_lower_groups = []

    while len(lst_groups) > 0:
        curr_group = lst_groups[0]
        print(f'curr_group: {curr_group}')

        lst_child_groups = (
            df_groups
            .filter(pl.col('parent_group') == curr_group)
            .select('child_group')
            .to_series()
            .to_list()
        )
        print(f'lst_child_groups: {lst_child_groups}')

        if lst_child_groups == [None]:
            lst_groups.pop(0)
            lst_lower_groups.append(curr_group)
        else:
            lst_groups.pop(0)
            lst_groups.extend(lst_child_groups)
        
        print(f'updated lst_groups: {lst_groups}')
        print(f'lst_lower_groups: {lst_lower_groups}')
    
    return lst_lower_groups
