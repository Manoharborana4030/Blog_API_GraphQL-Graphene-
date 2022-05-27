
from .models import Post,Comments
from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType
import graphql_jwt


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class PostType(DjangoObjectType):
    class Meta:
        model=Post
        likes=graphene.List(UserType)
        fields = "__all__"



class PostInput(graphene.InputObjectType):
    id=graphene.ID()
    title=graphene.String()
    tag=graphene.String()
    body=graphene.String()
    header_image=graphene.String()
    author=graphene.Int()
   

class CommentsType(DjangoObjectType):
    class Meta:
        model=Comments
        fields="__all__"

class CommentsInput(graphene.InputObjectType):
    id=graphene.ID()
    post=graphene.Int()
    name=graphene.String()
    body=graphene.String()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        first_name=graphene.String(required=True)
        last_name=graphene.String(required=True)

    def mutate(self, info, username, password, email,first_name,last_name):
        user = get_user_model()(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)

class CreatePost(graphene.Mutation):
    class Arguments:
        post_data=PostInput(required=True)

    post=graphene.Field(PostType)
    
    def mutate(root, info, post_data=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not provided')
        else:
            post=Post(title=post_data.title,
            tag=post_data.tag,
            body=post_data.body,
            header_image=post_data.header_image,
            author=get_user_model().objects.get(id=post_data.author)
            )
            post.save()
        return CreatePost(post=post)

class UpdatePost(graphene.Mutation):
    class Arguments:
        post_data=PostInput(required=True)
    
    post=graphene.Field(PostType)

    @staticmethod
    def mutate(root,info,post_data=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not provided')
        else:
            post_obj=Post.objects.get(pk=post_data.id)
            if post_obj:
                post_obj.title = post_data.title
                post_obj.tag = post_data.tag
                post_obj.body = post_data.body
                post_obj.header_image = post_data.header_image
                post_obj.save()
                
                return UpdatePost(post=post_obj)
            return UpdatePost(post=None)

class DeletePost(graphene.Mutation):
    class Arguments:
       id=graphene.ID()
    post=graphene.Field(PostType)

    @staticmethod
    def mutate(root,info,id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not provided')
        else:
            post_obj=Post.objects.get(pk=id)
            post_obj.delete()
           
        return None

class CreateComments(graphene.Mutation):
    class Arguments:
        comments_data=CommentsInput(required=True)

    comments=graphene.Field(CommentsType)
    def mutate(root,info,comments_data=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not provided')
        else:
            comments=Comments(post=Post.objects.get(id=comments_data.post),
            name=comments_data.name,
            body=comments_data.body,
            )
            comments.save()
        return CreateComments(comments=comments)
class DeleteComments(graphene.Mutation):
    class Arguments:
        id=graphene.ID()
    comments=graphene.Field(CommentsType)

    @staticmethod
    def mutate(root,info,id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not provided')
        else:
            comment_obj=Comments.objects.get(pk=id)
            comment_obj.delete()
           
        return None

class CreateLikes(graphene.Mutation):
    class Arguments:
        post_id=graphene.ID(required=True)
        user_id=graphene.ID(required=True)
    like=graphene.Field(PostType)

    @staticmethod
    def mutate(root,info,like=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not provided')
        else:
            post=Post.objects.get(id=like.post_id)
            user_obj=get_user_model().objects.get(id=like.user_id)
            if post.likes.filter(id=user_obj.id).exists():
                post.likes.remove(user_obj)
            else:
                post.likes.add(user_obj)
        return None



class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user_logged=graphene.Field(UserType)
    all_post=graphene.List(PostType)
    post=graphene.Field(PostType,post_id=graphene.ID())

    def resolve_users(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not providedd')
        else:
            return get_user_model().objects.all()

    def resolve_user_logged(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not providedd')
        return user
    
    def resolve_all_post(self,info,**kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not providedd')
        return Post.objects.all()
    def resolve_post(self,info,post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('auth Token not providedd')
        return Post.objects.get(id=post_id)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_post=CreatePost.Field()
    create_comments=CreateComments.Field()
    update_post=UpdatePost.Field()
    delete_post=DeletePost.Field()
    delete_comments=DeleteComments.Field()
    create_likes=CreateLikes.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field() 


schema = graphene.Schema(query=Query, mutation=Mutation)