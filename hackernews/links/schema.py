import graphene

from django.db.models import Q
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
    all_links = graphene.List(LinkType,
                              search=graphene.String(),
                              first=graphene.Int(),
                              skip=graphene.Int())

    vote = graphene.Field(VoteType,
                          id=graphene.Int())
    all_votes = graphene.List(VoteType,
                              search=graphene.String(),
                              first=graphene.Int(),
                              skip=graphene.Int())

    def resolve_link(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Link.objects.get(id=id)

        return None

    def resolve_all_links(self, info, search=None, first=None, skip=None, **kwargs):
        queryset = Link.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            queryset = queryset.filter(filter)

        if skip:
            queryset = queryset[skip:]

        if first:
            queryset = queryset[:first]

        return queryset

    def resolve_vote(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Vote.objects.get(id=id)

        return None

    def resolve_all_votes(self, info, search=None, first=None, skip=None, **kwargs):
        queryset = Vote.objects.all()

        if search:
            filter = (
                Q(user__username__icontains=search) |
                Q(link__id__icontains=search)
            )
            queryset = queryset.filter(filter)

        if skip:
            queryset = queryset[skip:]

        if first:
            queryset = queryset[:first]

        return queryset


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
