#Standard library modules
import time, uuid
from functools import partial

#Third-party modules
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

#Custom modules

UPDATE_PERIOD = 0.5

class MetaSingleton(type):
    _instances={}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Tasks(metaclass=MetaSingleton):
    def _update_task(self,task_id):
        update_value = self.tasks[task_id].task.update_value
        if update_value != None:
            self.tasks[task_id].extern_func_update(update_value)
        self.tasks[task_id].is_updating = False

    def _finish_task(self,task_id):
        return_value = self.tasks[task_id].task.return_value
        if return_value != None:
            self.tasks[task_id].extern_func_return(return_value)
        del self.tasks[task_id]
  
    def set(self, task_id, task_object, func_update, func_return):
        if "tasks" not in self.__dict__:
            self.tasks = {}

        if task_id in self.tasks.keys():
            old_task = self.tasks[task_id]
            old_task.terminate()
            old_task.wait()

        if task_id not in self.tasks.keys():
            newTask = TaskUpdater(task_id, task_object, func_update, func_return)
            newTask.sig_update.textChanged.connect(self._update_task)
            newTask.finished.connect(partial(self._finish_task,newTask.task_id))
            newTask.start()        
            self.tasks[newTask.task_id] = newTask

class TaskUpdater(QThread):    
    def __init__(self, task_id, task_object, func_update, func_return,parent=None):
        super().__init__(parent)
        if task_id != None:
            self.task_id = task_id
        else:
            self.task_id = str(uuid.uuid4().int)

        self.extern_func_update = func_update
        self.extern_func_return = func_return

        self.task = task_object
        self.task.finished.connect(self.finish)

        self.is_updating = False
        self.is_finished = False
        self.sig_update = QLineEdit()
        self.sig_return = QLineEdit()

    def run(self):
        self.task.start()
        while self.is_finished == False:
            time.sleep(UPDATE_PERIOD)
            if self.is_updating == False:
                self.is_updating = True
                self.update_value = self.task.update_value
                self.sig_update.textChanged.emit(self.task_id)

    def finish(self):
        self.is_finished = True
       
class AbstractTask(QThread):    
    def __init__(self, *args, parent=None):
        super().__init__(parent)
        self.args = args
        self.update_value = None
        self.return_value = None

    def run(self):
        #print(self.args)
        #for i in range(1000):
        #    time.sleep(0.1)
        #    self.update_value = str(i)
        #self.return_value = "finished"
        #return None
        pass
