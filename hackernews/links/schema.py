import graphene

from graphene_django import DjangoObjectType

from .models import Link


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class CreateLink(graphene.Mutation):
    link = graphene.Field(LinkType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        link = Link(url=url, description=description)
        link.save()

        return CreateLink(link=link)


class Query(graphene.ObjectType):
    link = graphene.Field(LinkType, id=graphene.Int())
    all_links = graphene.List(LinkType)

    def resolve_link(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Link.objects.get(id=id)

        return None

    def resolve_all_links(self, info, **kwargs):
        return Link.objects.all()


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
