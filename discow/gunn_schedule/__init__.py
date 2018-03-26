from discow.handlers import message_handlers

import discow.gunn_schedule.schedule as sch

message_handlers["schedule"] = sch.schedule