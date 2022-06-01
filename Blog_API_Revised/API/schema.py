
from .models import Post,Comments,AccessToken
from django.contrib.auth import get_user_model,authenticate
import graphene
from graphene_django import DjangoObjectType
import graphql_jwt
from graphql_jwt.shortcuts import get_token


#Auth Decorator
def authenticate_role(func):
    def wrap(self,info,**kwargs):
        auth_header = info.context.META.get('HTTP_AUTHORIZATION')
        if auth_header is None:
            raise Exception('auth Token not providedd')
        else:
            new_token=auth_header.replace("JWT","").replace(" ","")
            if AccessToken.objects.filter(token_id=new_token).exists():
                return func(self,info,**kwargs)
            raise Exception("Please Login Again you'r logged out!!!!")
    return wrap


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
class TokenType(DjangoObjectType):
    class Meta:
        model=AccessToken
        fields=['token_id','user']

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
    msg=graphene.String()
    @authenticate_role
    def mutate(root, info, post_data=None):
        post=Post(title=post_data.title,
        tag=post_data.tag,
        body=post_data.body,
        header_image=post_data.header_image,
        author=get_user_model().objects.get(id=post_data.author)
        )
        post.save()
        msg=" Blog Created Succefully"
        return CreatePost(post=post,msg=msg)


class storeToken(graphene.Mutation):
    class Arguments:
        username=graphene.String(required=True)
        password=graphene.String(required=True)
    token = graphene.Field(TokenType)
    msg=graphene.String()
    def mutate(self,info,username,password):
        token=''
        if not get_user_model().objects.filter(username=username).exists():
            return storeToken(token=None, msg="invalid username")
        valid_user = authenticate(username=username,password=password)
        if valid_user:
            user_obj=get_user_model().objects.get(username=username)
            if get_user_model().objects.filter(id=user_obj.id).exists():
                if AccessToken.objects.filter(user_id=user_obj.id).exists():
                    token_obj=AccessToken.objects.get(user_id=user_obj.id)
                    print(token_obj,"@@@@@@@@@@@@@@@@@@@@@@@@")
                    return storeToken(token=token_obj,)
                else:
                    user = get_user_model().objects.get(id=user_obj.id)
                    token = get_token(user)
                    token_obj=AccessToken(token_id=token,user=get_user_model().objects.get(id=user_obj.id))
                    token_obj.save()
                    return storeToken(token=token_obj)
            else:
                raise Exception('User ID not exits!!!!')
        else:
            return storeToken(token=None,msg="Invalid Credentials")

class UpdatePost(graphene.Mutation):
    class Arguments:
        post_data=PostInput(required=True)
    
    post=graphene.Field(PostType)
    msg=graphene.String()

    @staticmethod
    @authenticate_role
    def mutate(root,info,post_data=None):
        user = info.context.user
        post_obj=Post.objects.get(pk=post_data.id)
        if post_obj:
            post_obj.title = post_data.title
            post_obj.tag = post_data.tag
            post_obj.body = post_data.body
            post_obj.header_image = post_data.header_image
            post_obj.save()
            msg="Blog Updated Succefully"
            return UpdatePost(post=post_obj,msg=msg)
        msg="opps!! Something went Wrong!!!!"
        return UpdatePost(post=None,msg=msg)

class DeletePost(graphene.Mutation):
    class Arguments:
       id=graphene.ID()
    msg=graphene.String()

    @staticmethod
    @authenticate_role
    def mutate(root,info,id):
        post_obj=Post.objects.get(pk=id)
        post_obj.delete()
        msg="Blog Deleted Succefully"
        return DeletePost(msg=msg)

class CreateComments(graphene.Mutation):
    class Arguments:
        comments_data=CommentsInput(required=True)

    comments=graphene.Field(CommentsType)
    msg=graphene.String()
    @authenticate_role
    def mutate(root,info,comments_data=None):
        comments=Comments(post=Post.objects.get(id=comments_data.post),
        name=comments_data.name,
        body=comments_data.body,
        )
        comments.save()
        msg="Thank You For your comment"
        return CreateComments(comments=comments,msg=msg)
class DeleteComments(graphene.Mutation):
    class Arguments:
        id=graphene.ID()
    msg=graphene.String()

    @staticmethod
    @authenticate_role
    def mutate(root,info,id):
        comment_obj=Comments.objects.get(pk=id)
        comment_obj.delete()
        msg="Comment deleted Succefully"
        return DeleteComments(msg=msg)

class Logout(graphene.Mutation):
    class Arguments:
        id=graphene.ID()
    msg = graphene.String()

    @staticmethod
    def mutate(root,info,id):
        obj=AccessToken.objects.get(user_id=id)
        obj.delete()
        msg='succfully logout'
        return Logout(msg=msg)

class CreateLikes(graphene.Mutation):
    class Arguments:
        post_id=graphene.ID(required=True)
        user_id=graphene.ID(required=True)
    like=graphene.Field(PostType)
    msg=graphene.String()

    @staticmethod
    @authenticate_role
    def mutate(root,info,post_id,user_id):
        post=Post.objects.get(id=post_id)
        user_obj=get_user_model().objects.get(id=user_id)
        if post.likes.filter(id=user_obj.id).exists():
            post.likes.remove(user_obj)
            msg="Like Removed Succefully "

        else:
            post.likes.add(user_obj)
            msg="Liked Succefully"
        return CreateLikes(like=post,msg=msg)

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user_logged=graphene.Field(UserType)
    all_post=graphene.List(PostType)
    post=graphene.Field(PostType,post_id=graphene.ID())
    @authenticate_role
    def resolve_users(self, info):
        return get_user_model().objects.all()



    @authenticate_role
    def resolve_all_post(self,info,**kwargs): 
        return Post.objects.all()
        
    @authenticate_role
    def resolve_post(self,info,post_id):
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
    revoke_token = graphql_jwt.Revoke.Field()
    store_token=storeToken.Field()
    logout=Logout.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)