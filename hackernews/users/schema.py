import graphene

from django.contrib.auth import get_user_model

from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    user = graphene.Field(UserType,
                          username=graphene.String(),
                          email=graphene.String())
    all_users = graphene.List(UserType)

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user

    def resolve_user(self, info, **kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')

        if username is not None:
            return get_user_model().objects.get(username=username)

        if email is not None:
            return get_user_model().objects.get(email=email)

        return None

    def resolve_all_users(self, info):
        return get_user_model().objects.all()


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
