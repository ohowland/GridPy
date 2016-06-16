"""1 minute net load following on Diesel Generator

Drive Diesel kW to Netload_1min using Inverter kW

Netload_1min = 1min avg of (Diesel kW + Inverter kW)


"""
import threading

def netload(*args, **kwargs):
    #TODO: How to use *args and **kwargs
    """Calculate instantaneous netload

    :param args:
    :param kwargs:
    :return: netload (kW)
    """

class avg_1min(threading.Thread):
    #TODO: How do I pass the 1min avg the ability to access
    def __init__(self, reference_to_object_value, sample_rate = 1):
        threading.Thread.__init__(self)

    def run(self):
        pass
