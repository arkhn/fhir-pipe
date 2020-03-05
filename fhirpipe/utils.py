def new_col_name(script_name, init_col):
    if isinstance(init_col, tuple):
        if init_col[1]:
            return f"{script_name}_{'_'.join(init_col[0])}_{'_'.join(init_col[1])}"
        else:
            return f"{script_name}_{'_'.join(init_col[0])}"
    return f"{script_name}_{init_col}"
