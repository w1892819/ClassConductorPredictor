from django.db import models
from django.utils import timezone

class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    behaviour_points = models.IntegerField(default=0)
    merits = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name} ({self.student_id})'
    
    @property
    def behavior_score(self):
        return self.merits - self.behaviour_points
        
class BehaviorHistory(models.Model):
    student = models.ForeignKey(Student, related_name='behavior_history', on_delete=models.CASCADE) # CASCADE ensures that when a student is deleted, their behavior history is also deleted.
    date = models.DateTimeField(default=timezone.now)
    behavior_score = models.IntegerField()
    
    class Meta:
        ordering = ['-date']
        
