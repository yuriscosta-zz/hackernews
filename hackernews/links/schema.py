import graphene

from graphene_django import DjangoObjectType
from graphql import GraphQLError

from users.schema import UserType

from .models import Link, Vote


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class CreateLink(graphene.Mutation):
    link = graphene.Field(LinkType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None

        link = Link(url=url, description=description, posted_by=user)
        link.save()

        return CreateLink(link=link)


class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged to vote!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise GraphQLError('Invalid link!')

        Vote.objects.create(user=user, link=link)

        return CreateVote(user=user, link=link)


class Query(graphene.ObjectType):
    link = graphene.Field(LinkType, id=graphene.Int())
    all_links = graphene.List(LinkType)

    vote = graphene.Field(VoteType,
                          user=graphene.String(),
                          link=graphene.Int())
    all_votes = graphene.List(VoteType)

    def resolve_link(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Link.objects.get(id=id)

        return None

    def resolve_all_links(self, info, **kwargs):
        return Link.objects.all()

    def resolve_vote(self, info, **kwargs):
        username = kwargs.get('user')
        link_id = kwargs.get('link')

        if username is not None:
            return Vote.objects.get(user__username=username)

        if link_id is not None:
            return Vote.objects.get(link__id=link_id)

        return None

    def resolve_all_votes(self, info, **kwargs):
        return Vote.objects.all()


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
