from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=200,default='My_bloggg')
    author=models.ForeignKey(User, on_delete= models.CASCADE)
    body=models.TextField()
    post_date=models.DateField(auto_now_add=True)
    likes=models.ManyToManyField(User,related_name='blog_posts')
    header_image=models.ImageField(null=True,blank=True,upload_to="images/")

    def total_likes(self):
        return self.likes.count()
    def __str__(self) -> str:
        return self.title + '  |  '+str(self.author)

    def get_absolute_url(self):
        #return reverse("article-details", args=(str(self.id)))
        return reverse('home')
    
class Comments(models.Model):
    post=models.ForeignKey(Post,related_name='comments', on_delete= models.CASCADE)
    name=models.CharField(max_length=255)
    body=models.TextField()
    date_added=models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return '%s - %s' %(self.post.title,self.name)