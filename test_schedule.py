# import schedule
#
# def job():
#     print("job executing")
#     return schedule.CancelJob
#
# def MINUTE():
#     print("every minute")
#
# schedule.every(1).minute.do(MINUTE)
# schedule.every().minute.at(":17").do(MINUTE)
# schedule.every().day.at('10:47').do(job)

#
# from apscheduler.scheduler import Scheduler
#
# sched = Scheduler()
# sched.start()
#
#
# def my_job(text):
#     print text
#
#
# txt = "print text scheduled"
#
# exec_date = date(2009, 11, 6)
#
# job = sched.add_date_job(my_job, exec_date, ['text'])
#
def myjob(txt):
    print(txt)
from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler(daemon=True)
sched.add_job(myjob, 'date', run_date='2020-11-08 11:01:30', args=['text'])
sched.start()
