from typing import Dict, Any

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.requests import Request

from dependencies.filter.exception import DateEmptyError
from dependencies.filter.model import QueryFilter
from common.app.code.exception import (ChannelCodeNotFoundError, NeighborTypeCodeNotFoundError,
                                       SpeakerTypeCodeNotFoundError,
                                       ComplainTypeCodeNotFoundError)
from common.app.code.service import CodeService
from common.exception.common import DateFormatException
from common.util.date import yesterday, diff_times, add_times, isYYYYMMDD


@inject
def get_query_filter(request: Request,
                     config: Dict[str, Any] = Depends(Provide['config']),
                     code_service: CodeService = Depends(Provide['common.code.service']),
                     ) -> QueryFilter:
    cnf_filter = config.get('app').get('filter')
    cnv_tp_cd = list(map(lambda c: c.code, code_service['CNV_TP_CD'].codes))
    speaker_tp_cd = list(map(lambda c: c.code, code_service['SPEAKER_TP_CD'].codes))
    neighbor_tp_cd = list(map(lambda c: c.code, code_service['NBR_TP_CD'].codes))

    qf = QueryFilter(**request.query_params)
    qf.time_unit = cnf_filter.get('timeUnit', 'month') if qf.time_unit is None else qf.time_unit
    qf.max_period = int(cnf_filter.get('maxPeriod', 12)) if qf.max_period is None else qf.max_period

    # set param 1. date
    if qf.end_dt is None:
        qf.end_dt = yesterday()
        # end_dt가 설정되지 않은 채 max_period를 넘어가면 max_period 까지로 맞춤
        if qf.start_dt and diff_times(qf.end_dt, qf.start_dt, qf.time_unit) > qf.max_period:
            qf.end_dt = add_times(qf.start_dt, qf.max_period, qf.time_unit)
    if qf.start_dt is None:  # max_period 만큼 조회
        qf.start_dt = add_times(qf.end_dt, -qf.max_period, qf.time_unit)
    if qf.end_dt is None and qf.start_dt is None:
        raise DateEmptyError()

    if not isYYYYMMDD(qf.start_dt):
        raise DateFormatException(qf.start_dt)
    if not isYYYYMMDD(qf.end_dt):
        raise DateFormatException(qf.end_dt)

    # set param 2. channel codes
    if qf.channels is None:
        qf.channel_types = cnv_tp_cd
    else:
        qf.channel_types = qf.channels.split(',')
        for ch in qf.channel_types:
            if ch not in cnv_tp_cd:
                raise ChannelCodeNotFoundError(cnv_tp_cd)

    # set param 3. neighbor
    if qf.neighbor not in neighbor_tp_cd:
        raise NeighborTypeCodeNotFoundError(neighbor_tp_cd)

    # set param 4. speaker type
    if qf.speakers is None:
        qf.speaker_types = speaker_tp_cd
    else:
        qf.speaker_types = qf.speakers.split(',')
        for ch in qf.speaker_types:
            if ch not in qf.speaker_types:
                raise SpeakerTypeCodeNotFoundError(qf.speaker_types)

    # set param 5. complain
    if qf.complain is None:
        qf.complain_types = None
    else:
        qf.complain_types = qf.complain.split(',')
        for ch in qf.complain_types:
            if ch not in ['Y', 'N']:
                raise ComplainTypeCodeNotFoundError(['Y', 'N'])

    if qf.search_category is None:
        qf.search_category = "phonenum"

    return qf
