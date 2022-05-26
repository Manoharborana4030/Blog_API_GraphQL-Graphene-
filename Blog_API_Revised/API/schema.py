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
        fields = "__all__"

class PostInput(graphene.InputObjectType):
    id=graphene.ID()
    title=graphene.String()
    tag=graphene.String()
    body=graphene.String()
    post_date=graphene.String()
    header_image=graphene.String()

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
        post=Post(title=post_data.title,
        tag=post_data.tag,
        body=post_data.body,
        post_date=post_data.post_date,
        header_image=post_data.header_image
        )
        post.save()
        return CreatePost(post=post_data)


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user_logged=graphene.Field(UserType)

    def resolve_users(self, info):
        return get_user_model().objects.all()
    # def resolve_user_logged(self,info,username):
    #     return get_user_model().objects.filter(username=username)
    def resolve_user_logged(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_post=CreatePost.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)