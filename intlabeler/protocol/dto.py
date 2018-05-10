"""Module Doc
"""
import intlabeler.const.payload as payload
import intlabeler.const.msg as const_msg
from intlabeler.base.dto import AsDict
from collections import namedtuple
import inspect
import json
import uuid


def get_id():
    return str(uuid.uuid4())
#Containers for messages
class Data(namedtuple("Data", [ payload.TASK_ID, 
                                payload.X, 
                                payload.LABEL_NAME, 
                                payload.TITLE, 
                                payload.LABEL_TYPE,
                                payload.Y, 
                              ]), AsDict):
    pass

class Error(namedtuple("Error", [ const_msg.ERROR_TITLE, 
                                  const_msg.ERROR_DESC, 
                              ]), AsDict):
    pass


class Message(namedtuple("Message", [const_msg.TYPE, const_msg.PAYLOAD, const_msg.REPLY_ID, const_msg.ID]), AsDict):
    """This class have a payload - see data field
    """
    __slots__ = ()
    def __new__(cls, *args, **kwargs):
        args_list = inspect.getargspec(super(Message, cls).__new__).args[len(args)+1:]
        #params = {key: kwargs.get(key) for key in args_list + kwargs.keys()}
        params = {key: kwargs.get(key) for key in args_list + list(kwargs)}
        return super(Message, cls).__new__(cls, *args, **params) 

#Task
