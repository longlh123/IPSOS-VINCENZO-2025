import pandas as pd

class DatasetTransformer:
    def __init__(self, data: pd.DataFrame, config: dict):
        self.raw_data = data.copy()
        self.config = config
        self.data = None

    def transform(self) -> pd.DataFrame:
        self.data = self.raw_data
        self.data = self.data[self.config.get('used-cols', [])].copy()

        self._replaced_columns()
        self._renamed_columns()
        self._wide_to_long()
        self._stack()
        self._drop_na_columns()

        return self.data

    def _replaced_columns(self):
        replaced_map = self.config.get('replaced-columns', {})

        if replaced_map:
            for name, value in replaced_map.items():
                self.data[name] = value
    
    def _renamed_columns(self):
        rename_map = self.config.get('renamed-columns', {})

        if rename_map:
            self.data.rename(columns=rename_map, inplace=True)

    def _wide_to_long(self):
        wtl_map = self.config.get("wide-to-long", {})

        if wtl_map:
            stubnames = list(wtl_map.get('stubnames', {}).keys())
            i = wtl_map.get('i-cols', [])
            j = wtl_map.get('j-col', '')

            self.data = pd.wide_to_long(
                self.data,
                stubnames=stubnames,
                i = i,
                j = j,
                sep='###',
                suffix='\\d+'
            ).reset_index()

            self.data = self.data.drop(columns=[j])
    
    def _stack(self):
        stack_map = self.config.get('stack', {})

        if stack_map:
            if "renamed-columns" in stack_map.keys():
                renamed_columns = stack_map.get('renamed-columns', {})
            
            index_list = stack_map.get('group-by', [])  

            self.data = self.data.set_index(index_list).stack().reset_index()
            self.data.columns = self.data.columns.map(str)
            self.data.rename(columns=renamed_columns, inplace=True)

            if "replaced-categories" in stack_map.keys():
                self.data = self.data.replace(stack_map.get('replaced-categories', {}))


    def _drop_na_columns(self):
        drop_columns = self.config.get('drop-na-columns', [])

        if drop_columns:
            self.data.dropna(subset=drop_columns, inplace=True)
