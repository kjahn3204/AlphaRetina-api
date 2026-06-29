from typing import List

from dependencies.filter.model import QueryFilter


class Querybuilder:
    def __init__(self):
        pass

    def build(self, qf: QueryFilter, sort: bool = False, keyword: bool = True, customer: bool = True,
              add_join: List[str] | None = None, group_by: List[str] | None = None, shuffle: bool = False):
        ## sort 를 True 로 설정할 경우 사용하는 repo에서 select문에 C.START_DTTM를 꼭 포함 시켜야함.

        voc_tp_cd = qf.voc_tp_cd_list
        lrg_category = qf.lrg_category_list
        mdl_category = qf.mdl_category_list
        sml_category = qf.sml_category_list
        lifecycles = qf.lifecycles_list
        cstmr_act_cd = qf.cstmr_act_cd_list
        channels = qf.channel_types

        ##default query
        if qf.start_dt == qf.end_dt:
            date_query = f"BASE_DT = '{qf.start_dt}'"
        else:
            date_query = f"BASE_DT BETWEEN '{qf.start_dt}' AND '{qf.end_dt}'"
        channels_query = f" AND CNV_TP_CD IN ('" + "','".join(channels) + "')" if channels is not None else ''

        if qf.start_time is not None and qf.end_time is not None:
            time_query = f" AND DATE_FORMAT(START_DTTM,'%H') between '{qf.start_time}' and '{qf.end_time}'"
        else:
            time_query = ''

        ##voc query
        voc_tp_cd_query = '' if voc_tp_cd is None else f" AND V.VOC_TP_CD IN ('" + "','".join(voc_tp_cd) + "')"
        lrg_category_query = '' if lrg_category is None else f" OR V.VOC_LRGCAT_CD IN ('" + "','".join(lrg_category) + "')"
        mdl_category_query = '' if mdl_category is None else f" OR V.VOC_MDLCAT_CD IN ('" + "','".join(mdl_category) + "')"
        sml_category_query = '' if sml_category is None else f" OR V.VOC_SMLCAT_CD IN ('" + "','".join(sml_category) + "')"
        category_query = ''.join([lrg_category_query, mdl_category_query, sml_category_query])

        ##mot query
        lifecycles_query = '' if lifecycles is None else f" OR L.MOT_LFCYCL_CD IN ('" + "','".join(lifecycles) + "')"
        cstmr_act_cd_query = '' if cstmr_act_cd is None else f" OR M.MOT_CSTMR_ACTN_TP_CD IN ('" + "','".join(
            cstmr_act_cd) + "')"
        mot_query = ''.join([lifecycles_query, cstmr_act_cd_query])

        mot_join = '' if mot_query == '' else f'''
                    INNER JOIN (
                        SELECT M.VOC_SMLCAT_CD
                          FROM KNE_TBM_MOT_MAPPER L
                          INNER JOIN (
                               SELECT MOT_CSTMR_ACTN_TP_CD
                                    , VOC_SMLCAT_CD
                                 FROM KNE_TBM_MOT_VOC_MAPPER
                          ) M ON L.MOT_CSTMR_ACTN_TP_CD = M.MOT_CSTMR_ACTN_TP_CD
                        WHERE 1=0  {'OR 1=1' if mot_query == '' else mot_query}
                     ) M ON V.VOC_SMLCAT_CD = M.VOC_SMLCAT_CD
                '''

        # voc_needs = ''.join([lrg_category_query, mdl_category_query, sml_category_query, voc_tp_cd_query, mot_join])

        voc_join =f'''
                    LEFT JOIN (
                        SELECT CNV_ID, VOC_TP_CD, VOC_LRGCAT_CD, VOC_MDLCAT_CD, VOC_SMLCAT_CD, HSHLD_ID
                        FROM NI_TBM_VOC                          
                    ) V ON C.ID = V.CNV_ID
                '''
        ##keyword query
        if keyword and qf.keywords is not None:
            if sort:
                keyword_query = ' + '.join(
                    map(lambda k: f"if(MATCH(TOKENS) AGAINST('{k}' IN BOOLEAN MODE), 1, 0)", qf.keyword_list))
            else:
                key_join = " ".join(qf.keyword_list)
                keyword_query = f"MATCH(TOKENS) AGAINST('{key_join}' IN BOOLEAN MODE)"
            keyword_select = f", {keyword_query} as POINT"
            keyword_query = f" POINT > 0"

        else:
            keyword_query = " 1=1"

        ##sort query : 키워드도, sort옵션도 모두 고려해야함.
        if qf.keyword_list is not None and sort:
            sort_query = "ORDER BY POINT DESC, C.START_DTTM DESC"
        elif qf.keyword_list is not None and shuffle:
            sort_query = "ORDER BY POINT DESC"
        elif sort:
            sort_query = "ORDER BY C.START_DTTM DESC"
        else:
            sort_query = ""

        if group_by is not None:
            if keyword_query != "":
                group_by.append("POINT")
            group_query = "GROUP BY " + ",".join(group_by)
        else:
            group_query = ""

        query = f"""
                 , C.POINT
              FROM (SELECT * {', 1 as POINT' if qf.keyword_list is None else keyword_select}
                      FROM NI_TBM_CNVSTN
                     WHERE {date_query}{channels_query}{time_query}
                 ) as C
              {'LEFT JOIN KNE_TBM_CSTMR CT ON C.CSTMR_ID = CT.ID' if customer else ''}
              {voc_join}
              {mot_join}
              {'' if add_join is None else ' '.join(add_join)}
             WHERE {keyword_query}{voc_tp_cd_query} AND (
                     1=0 {'OR 1=1' if category_query == '' else category_query}
             )
             {group_query}
             {sort_query} 
        """
        return query
