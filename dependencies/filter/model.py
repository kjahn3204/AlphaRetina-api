from typing import Any

from rcore.model.base import ModelBase


class QueryFilter(ModelBase):
    start_dt: str | None = None
    end_dt: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    time_unit: str | None = None
    max_period: int | None = None
    channels: str | None = None
    neighbor: str = 'CNV'
    speakers: str | None = None
    complain: str | None = None
    keywords: str | None = None
    in_phonenum: str | None = None

    use_like: bool | None = True
    search_category: str | None = None
    ca_no: str | None = None
    rn: str | None = None

    voc_tp_cd: str | None = None
    lrg_category: str | None = None
    mdl_category: str | None = None
    sml_category: str | None = None
    lifecycles: str | None = None
    cstmr_act_cd: str | None = None

    edge_limit: str | None = None
    page_count: bool | None = False

    _selected_channel_types: Any = None
    _selected_neighbor_type: Any = None
    _selected_speaker_types: Any = None
    _selected_complain_types: Any = None

    @property
    def channel_types(self):
        return self._selected_channel_types

    @channel_types.setter
    def channel_types(self, values):
        self._selected_channel_types = values

    @property
    def speaker_types(self):
        return self._selected_speaker_types

    @speaker_types.setter
    def speaker_types(self, values):
        self._selected_speaker_types = values

    @property
    def complain_types(self):
        return self._selected_complain_types

    @complain_types.setter
    def complain_types(self, values):
        self._selected_complain_types = values

    @property
    def keyword_list(self):
        if self.keywords is None:
            return None
        return self.keywords.split(',')

    @property
    def voc_tp_cd_list(self):
        if self.voc_tp_cd is None:
            return None
        return self.voc_tp_cd.split(',')

    @property
    def lrg_category_list(self):
        if self.lrg_category is None:
            return None
        return self.lrg_category.split(',')

    @property
    def mdl_category_list(self):
        if self.mdl_category is None:
            return None
        return self.mdl_category.split(',')

    @property
    def sml_category_list(self):
        if self.sml_category is None:
            return None
        return self.sml_category.split(',')

    @property
    def lifecycles_list(self):
        if self.lifecycles is None:
            return None
        return self.lifecycles.split(',')

    @property
    def cstmr_act_cd_list(self):
        if self.cstmr_act_cd is None:
            return None
        return self.cstmr_act_cd.split(',')

    @property
    def get_edge_limit(self):
        if self.edge_limit is None:
            return 4
        else:
            return int(self.edge_limit)
