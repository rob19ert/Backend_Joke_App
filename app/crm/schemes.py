from marshmallow import Schema, fields

from app.web.schemes import OkResponseSchema


class UserRegisterSchema(Schema):
    name = fields.String(required=True)
    mail = fields.String(required=True)
    password = fields.String(required=True)
    is_admin = fields.Boolean(required=True)

class UserLoginSchema(Schema):
    mail = fields.String(required=True)
    password = fields.String(required=True)


class UserSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.Str(required=True)
    mail = fields.Str(required=True)
    is_admin = fields.Boolean(required=True)
    is_moderator = fields.Boolean(required=True)

class GetUserResponseSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.Str(required=True)
    mail = fields.Str(required=True)

class ListGetUserResponse(OkResponseSchema):
    data = fields.Nested(GetUserResponseSchema)

#Данные которые мы отправляем пользователю на его запрос получить Get
class TopicSchema(Schema):
    id = fields.Integer(required=True)
    title = fields.Str(required=True)
    count = fields.Integer(required=True)

class GetJokeRequestSchema(Schema):

    text = fields.Str(required=True)



# Данные, которые мы получаем от пользователя на его запрос отправить Post
class AddTopicSchema(Schema):
    title = fields.Str(required=True)

class AddJokeSchema(Schema):
    text = fields.Str(required=True)
    topic_id = fields.Integer(required=True)

class ListTopicSchema(OkResponseSchema):
    data = fields.Nested(TopicSchema, many=True)

class GetJokeResponseSchema(OkResponseSchema):
    data = fields.Nested(GetJokeRequestSchema, many=True)