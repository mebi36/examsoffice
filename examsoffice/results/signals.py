from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from results.models import Result, Student
from datetime import datetime

MODEL_WATCHLIST = (Result, Student)

for model in MODEL_WATCHLIST:
    # @receiver(pre_save, sender=model)
    # def result_pre_save(sender, instance, **kwargs):
    #     print("Before saving: ", instance.id)
    #     print("Before Result is updated: ", instance.__dict__, "by ", datetime.now())
        

    @receiver(post_save, sender=model)
    def results_save(sender, instance, created, **kwargs):
        if created:
            print("New result added: ", instance.id)
        else:
            print("Result updated: ", instance.id, instance.__dict__, "by ", datetime.now(), instance.__str__)
    

# @receiver(pre_save, sender=Student)
# def student_pre_save(sender, instance, **kwargs):
#     print("Before saving: ", instance.id)
#     print("Before Result is updated: ", sender.objects.get(id=instance.id).__dict__, "by ", datetime.now())
    

# @receiver(post_save, sender=Result)
# def student_save(sender, instance, created, **kwargs):
#     if created:
#         print("New result added: ", instance.id)
#     else:
#         print("Result updated: ", instance.id, instance.__dict__, "by ", datetime.now(), instance.__str__)
    
